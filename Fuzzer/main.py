import os, sys
from datetime import datetime
import torch
from model.StarCoder import (
  Phase,
  StarCoder,
  instantiate_model
)
from util.util import (
  load_yml_file,
  write_yml_file
)
import util.Logger as Logger

###########################################################################
# PHASE I - Generate Properties
###########################################################################
def generate_properties(model: StarCoder, config: dict[str, any]):
  """Phase I - Generate Properties"""
  # setup output dirs
  output_dir = str(config['output-dir']) + "/" + str(config['name']) + "/" + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
  oas_output_dir = output_dir + "/oas-parts"
  str_output_dir = output_dir + "/phase-i/input-strings"
  llm_output_dir = output_dir + "/phase-i/generated-output"
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
    # Build input prompt
    model.apply_chat_template(
      phase=Phase.PHASE_1,
      oas_path=f"{oas_output_dir}/{oas_part}",
      save_output_dir=str_output_dir,
      save_file_name=f"part-{counter}.md"
    )
    #TODO Generate Properties
    outputs = model.generate()
    while(any(empty_solution in outputs for empty_solution in empty_solutions)):
      outputs = model.generate()
    for output in outputs:
      Logger.section_title("Generator Output")
      Logger.content("Output", output)
  #TODO Merge produced python files into one file

###########################################################################
#TODO PHASE II - Generate Type Generators
###########################################################################
def generate_type_generators():
  pass

###########################################################################
#TODO PHASE III - Generate Generator
###########################################################################
def generate_generator():
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
    print("e.g. 'python3 main.py \"/content/fuzzing-web-api-with-llm/config/experimental/default-colab.yml\"'")
    exit(0)
  config_dict = load_yml_file(config_filepath)
  config_general: dict[str, any] = config_dict['general']
  config_model: dict[str, any] = config_dict['model']
  config_phase_i: dict[str, any] = config_dict['phase-i']

  # Create a StarCoder instance
  try:
    starcoder_model = instantiate_model(config=config_model)

    # execute PHASE I
    config_phase_i.update(config_general)
    generate_properties(model=starcoder_model, config=config_phase_i)

    #TODO execute PHASE II

    #TODO execute PHASE III
  except Exception as error:
    print("Something went wrong")
    print(error)
  finally:
    print("Free memory")
    del starcoder_model
    torch.cuda.empty_cache()