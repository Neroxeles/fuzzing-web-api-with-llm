import os, sys
from datetime import datetime
import torch
from model.StarCoder import (
  Phase,
  StarCoder,
  instantiate_model
)
import re
from timeit import default_timer as timer
from util.util import (
  load_yml_file,
  write_yml_file,
  write_str_into_file,
  print_gpu_utilization,
  md5,
  save_md5,
  dir_exists,
  get_file_content
)
from util.Logger import (
  Logger,
  make_logger
)
import util.testApi as testApi
from util.codegenApi import generate_client_script
Log: Logger

###########################################################################
# PHASE I - Generate ClientAPI
###########################################################################
def generate_properties(config: dict[str, any]) -> None:
  """Phase I - Generate ClientAPI"""
  Log.content("## Start generation process\n")
  # setup output dirs
  output_dir = config['api_client_lib_path']
  os.makedirs(output_dir, exist_ok=True)
  # Load Specification (OAS)
  oas_complete = load_yml_file(filepath=config['oas-file'])
  # Use Swagger Codegen API to create a client python script
  Log.content("- Calling the Swagger Codegen API to create the client... ")
  generate_client_script(
    base_url=config['base-url'],
    language="python",
    spec=oas_complete,
    output=output_dir,
    verify=config['verify']
  )
  Log.content("done\n")
  # execute 'pip install' to install the library
  Log.content("- Run pip install to install the library... ")
  os.system(f"pip install {config['api_client_lib_path']}")
  Log.content("done\n")
  # TODO FUTURE WORK: generate util/testApi.py automatically

###########################################################################
# PHASE II - Generate Type Generators
###########################################################################
def generate_type_generators(model: StarCoder, config: dict[str, any]) -> None:
  """Phase II - Generate Type Generators"""
  # setup output dirs
  generated_code_dir: str = config['output-dir'] + "/generated-code"
  generated_prompts_dir: str = config['output-dir'] + "/generated-prompts"
  os.makedirs(generated_code_dir, exist_ok=True)
  os.makedirs(generated_prompts_dir, exist_ok=True)

  # get all functions from the 'testApi' modul (not used yet)
  func_list = []
  for func in dir(testApi):
    if "api_" in func:
      func_list.append(func)
  # Define all possible sequences that point to an empty solution (not used yet)
  empty_solutions = ["pass", "insert code here", "# Solution here"]

  # load OAS and get properties
  oas_complete = load_yml_file(filepath=config['oas-file'])
  properties = []
  for path in oas_complete['paths']:
    # paths
    for http_method in oas_complete['paths'][path]:
      prop = {
        "path": path,
        "method": http_method,
        "items": []
      }
      # url parameters
      try:
        for item in oas_complete['paths'][path][prop["method"]]['parameters']:
          prop["items"].append({
            "name": item['name'],
            "schema": item['schema']
          })
      except:
        pass
      # requestBody properties
      try:
        for item in oas_complete['paths'][path][prop["method"]]['requestBody']['content']['application/json']['schema']['properties']:
          prop["items"].append({
            "name": item,
            "schema": oas_complete['paths'][path][prop["method"]]['requestBody']['content']['application/json']['schema']['properties'][item]
          })
      except:
        pass
      # append if parameters exists
      if prop["items"]:
        properties.append(prop)

  counter = 0
  for property in properties:
    counter += 1
    # Build input prompt
    Log.content("- Apply prompt template... ")
    model.apply_template(
      template_path=config['template'],
      property=property,
      generated_prompts_dir=generated_prompts_dir,
      save_file_name="prompt-p{:0>{}}".format(counter, 2) + ".md"
    )
    Log.content("done\n")
    loop = 0
    while loop < config['loops']:
      loop += 1
      # Generate Type Generators
      Log.content("- Generate content for " + "\"prompt-{:0>{}}".format(counter, 2) + ".md\":\n")
      outputs, output_tokens = model.generate()
      for output in outputs:
        write_str_into_file(
          content=output.split("```")[0],
          directory=generated_code_dir,
          filename="snip-p{:0>{}}-b{:0>{}}".format(counter, 2, loop, 2) + ".py",
          mode="a"
        )
      if (output_tokens <= 20) or (len(get_file_content(generated_code_dir+"/snip-p{:0>{}}-b{:0>{}}".format(counter, 2, loop, 2) + ".py")) < 20):
        Log.content("  - Empty solution found. Repeat process...\n")
        loop -= 1
        continue
  #TODO FUTURE WORK: Automatically merge created Python files into one file

###########################################################################
#TODO PHASE III - Testing
###########################################################################
def generate_generator() -> None:
  """Phase III - Testing"""
  pass


###########################################################################
# MAIN
###########################################################################
if __name__ == "__main__":
  # load configurations
  if len(sys.argv) != 1:
    config_filepath = str(sys.argv[1])
  else:
    print("Please enter the path to a configuration file.")
    print("e.g. 'python3 main.py \"/content/fuzzing-web-api-with-llm/configs/config-files/default-colab.yml\"'")
    exit(0)
  config_dict = load_yml_file(config_filepath)
  config_general: dict[str, any] = config_dict['general']
  config_model: dict[str, any] = config_dict['model']
  config_phase_i: dict[str, any] = config_dict['phase-i']
  config_phase_ii: dict[str, any] = config_dict['phase-ii']

  config_general['api_client_lib_path'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/library"
  config_general['output-dir'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/" + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  os.makedirs(config_general['output-dir'], exist_ok=True)
  Log = make_logger(filepath=config_general['output-dir'] + "/logger.md")

  try:
    # execute PHASE I
    Log.content("# Phase I\n")
    checksum = md5(config_general['oas-file'])
    if (
      ((config_phase_i['oas-checksum'] != checksum) or
      not dir_exists(config_general['api_client_lib_path'])) and
      config_phase_i['execute']
    ):
      os.system(f"rm -r {config_general['api_client_lib_path']}")
      config_phase_i.update(config_general)
      Log.content("## Initialized with ...\n")
      Log.content("```json\n{\n")
      for key in config_phase_i:
        Log.content(f"  \"{key}\": \"{config_phase_i[key]}\",\n")
      Log.content("}\n```\n")
      start = timer()
      generate_properties(config=config_phase_i)
      end = timer()
      save_md5(
        filepath=config_filepath,
        checksum=checksum
      )
      Log.content("## Execution time\n")
      Log.content(f"- start = {start}\n")
      Log.content(f"- end = {end}\n")
      Log.content(f"- passed time = {end - start} seconds\n")
    else:
      Log.content("Skipped\n")
      Log.content("- Required files are already available and up to date\n- or the configuration file specifies that the process should be skipped.\n")

    # execute PHASE II
    if config_phase_ii['execute']:
      # Instantiate tokenizer & model
      Log.content("# Instantiate tokenizer & model\n")
      gpu_load = print_gpu_utilization()
      Log.content("## Initialized with ...\n")
      Log.content("```json\n{\n")
      for key in config_model:
        Log.content(f"  \"{key}\": \"{config_model[key]}\",\n")
      Log.content("}\n```\n")
      start = timer()
      starcoder_model = instantiate_model(config=config_model, logger= Log)
      end = timer()
      Log.content("## Execution time\n")
      Log.content(f"- start = {start}\n")
      Log.content(f"- end = {end}\n")
      Log.content(f"- passed time = {end - start} seconds\n")
      Log.content("## GPU load\n")
      Log.content(f"- before model is loaded = {gpu_load} MB\n")
      Log.content(f"- after model is loaded = {print_gpu_utilization()} MB\n")
      Log.content(f"- difference = {print_gpu_utilization() - gpu_load} MB\n")

      # generate content
      Log.content("# Phase II\n")
      config_phase_ii.update(config_general)
      generate_type_generators(model=starcoder_model, config=config_phase_ii)
    #TODO execute PHASE III
  except Exception as error:
    Log.content("# Exception during execution\n")
    Log.content(f"{error}")
  finally:
    Log.content("# Process is terminated\n")
    try:
      Log.content("Free memory\n")
      del starcoder_model
      torch.cuda.empty_cache()
    except Exception as error:
      Log.content("## Free memory exception\n")
      Log.content(f"{error}")