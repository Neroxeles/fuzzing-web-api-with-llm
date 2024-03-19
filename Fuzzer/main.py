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
  print_gpu_utilization
)
from util.Logger import (
  Logger,
  make_logger
)
Log: Logger

###########################################################################
# PHASE I - Generate Properties
###########################################################################
def generate_properties(model: StarCoder, config: dict[str, any]) -> None:
  """Phase I - Generate Properties"""
  Log.content("## Start generation process\n")
  # setup output dirs
  oas_output_dir = config['output-dir'] + "/oas-parts"
  str_output_dir = config['output-dir'] + "/phase-i/input-strings"
  llm_output_dir = config['output-dir'] + "/phase-i/generated-output"
  os.makedirs(oas_output_dir, exist_ok=True)
  os.makedirs(str_output_dir, exist_ok=True)
  os.makedirs(llm_output_dir, exist_ok=True)
  # Load Specification (OAS)
  oas_complete = load_yml_file(filepath=config['oas-file'])
  # Disassemble OAS into multiple parts
  # Step 1 - Disassemble
  swagger = oas_complete['swagger']
  info = oas_complete['info']
  host = oas_complete['host']
  base_path = oas_complete['basePath']
  schemes = oas_complete['schemes']
  paths = oas_complete['paths']
  security_definitions = oas_complete['securityDefinitions']
  definitions = oas_complete['definitions']
  # Step 2 - Construct smaller OAS
  counter = 0
  for key in paths:
    counter += 1
    new_info = {
      'version': info['version'],
      'title': info['title']
    }
    new_oas = {
      'swagger': swagger,
      'info': new_info,
      'host': host,
      'basePath': base_path,
      'schemes': schemes,
      'paths': {str(key): paths[key]},
      'securityDefinitions': security_definitions,
      'definitions': definitions
    }
    write_yml_file(
      oas=new_oas,
      directory=oas_output_dir,
      filename=f"part-{counter}.yml"
    )

  # Select an OAS part
  empty_solutions = ["pass", "insert code here"]
  counter = 0
  for oas_part in os.listdir(oas_output_dir):
    counter += 1
    Log.content(f"### Processing - Part {counter}\n")
    Log.content(f"- apply_chat_template: ")
    # Build input prompt
    model.apply_chat_template(
      phase=Phase.PHASE_1,
      oas_path=f"{oas_output_dir}/{oas_part}",
      save_output_dir=str_output_dir,
      save_file_name=f"part-{counter}.md"
    )
    Log.content(f"done\n")
    # Generate Properties
    Log.content(f"#### generate code ...\n")
    outputs = model.generate()
    empty_solution_found = True
    while empty_solution_found:
      empty_solution_found = False
      for output in outputs:
        # if any(empty_solution in output for empty_solution in empty_solutions):
        for empty_solution in empty_solutions:
          if any(empty_solution == word for word in output.split()):
            Log.content(f"\nfailed solution (found empty solution)\n")
            Log.content("```python\n")
            Log.content("import requests\n")
            for output in outputs:
              Log.content(f"{output}")
            Log.content("\n```\n")
            Log.content(f"#### generate code ...\n")
            outputs = model.generate()
            empty_solution_found = True
            break
        if empty_solution_found:
          break
    Log.content(f"\nsuccessful solution\n")

    Log.content("```python\n")
    Log.content("import requests\n")
    write_str_into_file(
      content="import requests",
      directory=llm_output_dir,
      filename=f"part-{counter}.py",
      mode="w"
    )
    for output in outputs:
      Log.content(f"{output}")
      write_str_into_file(
        content=output,
        directory=llm_output_dir,
        filename=f"part-{counter}.py",
        mode="a"
      )
    Log.content("\n```\n")
  #TODO Merge produced python files into one file

###########################################################################
# PHASE II - Generate Type Generators
###########################################################################
def generate_type_generators(model: StarCoder, config: dict[str, any]) -> None:
  """Phase II - Generate Type Generators"""
  oas_output_dir: str = config['output-dir'] + "/oas-parts"
  str_output_dir: str = config['output-dir'] + "/phase-ii/input-strings"
  llm_output_dir: str = config['output-dir'] + "/phase-ii/generated-output"
  os.makedirs(str_output_dir, exist_ok=True)
  os.makedirs(llm_output_dir, exist_ok=True)

  empty_solutions = ["pass", "insert code here"]
  part_file: str
  for part_file in os.listdir(oas_output_dir):
    # Select specification & corresponding program part
    oas_part_file = oas_output_dir + f"/{part_file}"
    python_part_file = llm_output_dir.replace("phase-ii", "phase-i") + "/" + part_file.replace(".md", ".py")
    # Build input prompt
    model.apply_chat_template(
      phase=Phase.PHASE_2,
      save_output_dir=str_output_dir,
      save_file_name=part_file,
      oas_path=oas_part_file,
      python_path=python_part_file
    )
    # Generate Type Generators
    outputs = model.generate()
    while(any(empty_solution in outputs for empty_solution in empty_solutions)):
      outputs = model.generate()
    for output in outputs:
      Logger.section_title(f"Generator Output - len(outputs) = {len(outputs)}")
      Logger.content("Output", output)
      write_str_into_file(
        content=output,
        directory=llm_output_dir,
        filename=part_file.replace(".md", ".py"),
        mode="a"
      )
  #TODO Merge produced python files into one file

###########################################################################
#TODO PHASE III - Generate Generator
###########################################################################
def generate_generator() -> None:
  """Phase III - Generate Generator"""
  pass


###########################################################################
# MAIN
###########################################################################
if __name__ == "__main__":
  # load configurations
  if len(sys.argv) != 1:
    config_filepath = str(sys.argv[1])
  else:
    print("Please define the path to a config file")
    print("e.g. 'python3 main.py \"/content/fuzzing-web-api-with-llm/configs/config-files/default-colab.yml\"'")
    exit(0)
  config_dict = load_yml_file(config_filepath)
  config_general: dict[str, any] = config_dict['general']
  config_model: dict[str, any] = config_dict['model']
  config_phase_i: dict[str, any] = config_dict['phase-i']

  config_general['output-dir'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/" + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  os.makedirs(config_general['output-dir'], exist_ok=True)
  Log = make_logger(filepath=config_general['output-dir'] + "/logger.md")

  try:
    Log.content("# Instantiate tokenizer & model\n")
    gpu_load = print_gpu_utilization()
    Log.content("## Initialized with ...\n")
    Log.content("```json\n{\n")
    for key in config_model:
      Log.content(f"  \"{key}\": \"{config_model[key]}\"\n")
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

    # execute PHASE I
    Log.content("# Phase I - generate properties\n")
    config_phase_i.update(config_general)
    Log.content("## Initialized with ...\n")
    Log.content("```json\n{\n")
    for key in config_phase_i:
      Log.content(f"  \"{key}\": \"{config_phase_i[key]}\"\n")
    Log.content("}\n```\n")
    start = timer()
    generate_properties(model=starcoder_model, config=config_phase_i)
    end = timer()
    Log.content("## Execution time\n")
    Log.content(f"- start = {start}\n")
    Log.content(f"- end = {end}\n")
    Log.content(f"- passed time = {end - start} seconds\n")
    # execute PHASE II
    # generate_type_generators(model=starcoder_model, config=config_general)
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