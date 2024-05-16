import os, sys
from datetime import datetime
import torch
from model.ModelForCausalLM import (
  Model,
  instantiate_model
)
from timeit import default_timer as timer
from util.util import (
  load_yml_file,
  write_str_into_file,
  print_gpu_utilization,
  md5,
  save_md5,
  dir_exists,
  get_file_content,
  add_missing_imports,
  check_core_functionality
)
from util.Logger import (
  Logger,
  make_logger
)
from util.dataCollector import (
  TableBuilder,
  make_table_builder
)
from util.codegenApi import generate_client_script
Log: Logger
TableB: TableBuilder
meta_data_collector: dict
data_collector: dict = {'filename': [], 'input-tokens': [], 'output-tokens': [], 'time-in-sec': []}

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
def generate_type_generators(model: Model, config: dict[str, any]) -> None:
  """Phase II - Generate Type Generators"""
  # setup output dirs
  generated_code_dir: str = config['output-dir'] + "/generated-code"
  generated_prompts_dir: str = config['output-dir'] + "/generated-prompts"
  os.makedirs(generated_code_dir, exist_ok=True)
  os.makedirs(generated_prompts_dir, exist_ok=True)

  # load OAS and get necessary properties
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
      # append if property has parameters
      if prop["items"]:
        properties.append(prop)
  TableB.set_total_properties(len(properties))
  meta_data_collector['total-properties'] = len(properties)
  TableB.part_1()

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
    resamplings = 0
    retries = 0
    while loop < config['loops']:
      loop += 1
      # Generate Code-Snippets
      Log.content("- Generate content for " + "\"prompt-{:0>{}}".format(counter, 2) + ".md\":\n")
      outputs, output_tokens, input_tokens, sec = model.generate()
      for output in outputs:
        filename = "snip-p{:0>{}}-b{:0>{}}".format(counter, 2, loop, 2) + ".py"
        write_str_into_file(
          content=output,
          directory=generated_code_dir,
          filename=filename,
          mode="w"
        )
        break
      # Resampling if empty file/solution or missing core functions
      if ((output_tokens <= config['min-tokens']) or
          (len(get_file_content(f"{generated_code_dir}/{filename}")) < config['min-characters']) or
          check_core_functionality(f"{generated_code_dir}/{filename}")):
        Log.content("  - Empty solution or missing functionality.")
        if retries != config['max-retries']:
          Log.content(" Repeat process...\n")
          resamplings += 1
          loop -= 1
          retries += 1
          data_collector['filename'].append(filename.replace(".py", "") + "-failed")
          data_collector['input-tokens'].append(input_tokens)
          data_collector['output-tokens'].append(output_tokens)
          data_collector['time-in-sec'].append(sec)
          continue
        else:
          Log.content(" Maximum number of repetitions reached\n")
      retries = 0
      # add missing imports
      if config['add-missing-imports']:
        if add_missing_imports(f"{generated_code_dir}/{filename}"):
          Log.content("  - Added missing imports\n")
      TableB.part_2(
        filename=filename.replace(".py", ""),
        etok=input_tokens,
        atok=output_tokens,
        sec=sec,
        resamplings=resamplings
      )
      data_collector['filename'].append(filename.replace(".py", ""))
      data_collector['input-tokens'].append(input_tokens)
      data_collector['output-tokens'].append(output_tokens)
      data_collector['time-in-sec'].append(sec)
  #TODO FUTURE WORK: Automatically merge created Python files into one script

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
    print("e.g. 'python3 main.py \"/content/fuzzing-web-api-with-llm/configs/config-files/colab-default.yml\"'")
    exit(0)
  config_dict = load_yml_file(config_filepath)
  config_general: dict[str, any] = config_dict['general']
  config_model: dict[str, any] = config_dict['model']
  config_phase_i: dict[str, any] = config_dict['phase-i']
  config_phase_ii: dict[str, any] = config_dict['phase-ii']

  config_general['api_client_lib_path'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/library"
  date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  config_general['output-dir'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/" + date_time
  os.makedirs(config_general['output-dir'], exist_ok=True)
  os.makedirs(config_general['output-dir']+"/data", exist_ok=True)
  Log = make_logger(filepath=config_general['output-dir'] + "/logger.md")
  TableB = make_table_builder(
    loops=config_dict['phase-ii']['loops'],
    date_time=date_time,
    filepath=config_general['output-dir']+"/data/"
  )
  TableB.part_3(
    model=config_model['checkpoint'],
    loaded_in=config_model['load-in'],
    batch_size=config_phase_ii['loops'],
    temperature=config_model['temperature'],
    top_k=config_model['top-k'],
    top_p=config_model['top-p']
  )
  meta_data_collector = {
    "oas-file": config_general['oas-file'].split("/")[-1],
    "prompt-file": config_phase_ii['template'].split("/")[-1],
    "checkpoint": config_model['checkpoint'],
    "device": config_model['device'],
    "device-map": config_model['device-map'],
    "load-in": config_model['load-in'],
    "batch-size": config_model['batch-size'],
    "loops": config_phase_ii['loops'],
    "do-sample": config_model['do-sample'],
    "temperature": config_model['temperature'],
    "num-beams": config_model['num-beams'],
    "num-beam-groups": config_model['num-beam-groups'],
    "penalty-alpha": config_model['penalty-alpha'],
    "diversity-penalty": config_model['diversity-penalty'],
    "top-k": config_model['top-k'],
    "top-p": config_model['top-p'],
    "max-new-tokens": config_model['max-new-tokens'],
    "eos": config_model['eos'],
    "min-tokens": config_model['min-tokens'],
    "min-characters": config_model['min-characters'],
    "max-retries": config_model['max-retries'],
    "add-missing-imports": config_model['add-missing-imports'],
    "execute-phase-i": config_phase_i['execute'],
    "swagger-codegen-base-url": config_phase_i['base-url'],
    "verify-ssl": config_phase_i['verify'],
    "execute-phase-ii": config_phase_ii['execute'],
    "date-time": date_time
  }


  try:
    Log.system(filepath=config_general['output-dir'] + "/system-information.md")
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
      meta_data_collector['phase-i-executed-in-sec'] = end - start
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
      model = instantiate_model(config=config_model, logger=Log)
      end = timer()
      Log.content("## Execution time\n")
      Log.content(f"- start = {start}\n")
      Log.content(f"- end = {end}\n")
      meta_data_collector['instanciated-in-sec'] = end - start
      Log.content(f"- passed time = {meta_data_collector['instanciated-in-sec']} seconds\n")
      Log.content("## GPU load\n")
      Log.content(f"- before model is loaded = {gpu_load} MB\n")
      Log.content(f"- after model is loaded = {print_gpu_utilization()} MB\n")
      meta_data_collector['used-gpu-in-mb'] = print_gpu_utilization() - gpu_load
      Log.content(f"- difference = {meta_data_collector['used-gpu-in-mb']} MB\n")

      # generate content
      Log.content("# Phase II\n")
      config_phase_ii.update(config_general)
      config_phase_ii.update(config_model)
      generate_type_generators(model=model, config=config_phase_ii)
      TableB.write_csv_meta_data(meta_data_collector)
      TableB.write_csv_data(data_collector)
    #TODO execute PHASE III
  except Exception as error:
    Log.content("# Exception during execution\n")
    Log.content(f"{error}")
  finally:
    Log.content("# Process is terminated\n")
    try:
      Log.content("Free memory\n")
      del model
      torch.cuda.empty_cache()
    except Exception as error:
      Log.content("## Free memory exception\n")
      Log.content(f"{error}")