import os, sys
from datetime import datetime
from util.util import (
  load_yml_file
)
from util.Logger import (
  Logger,
  make_logger
)
from components.SwaggerCodegen import SwaggerCodegen
from components.TypeGenerator import TypeGenerator
from components.TestToolBuilder import TestToolBuilder
from model.ModelForCausalLM import Model
import torch
Log: Logger


if __name__ == "__main__":
    config_filepath = ""
    # load configurations
    if len(sys.argv) != 1:
        config_filepath = str(sys.argv[1])
    else:
        print("Please enter the path to a configuration file.")
        print("e.g. 'python3 main.py \"/content/fuzzing-web-api-with-llm/configs/config-files/default.yml\"'")
        exit(0)
    config_dict = load_yml_file(config_filepath)
    config_general: dict[str, any] = config_dict['general']

    config_general['api_client_lib_path'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/library"
    config_general['output-dir'] = str(config_general['output-dir']) + "/" + str(config_general['name']) + "/" + str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    os.makedirs(config_general['output-dir'], exist_ok=True)

    Log = make_logger(filepath=config_general['output-dir'] + "/logger.md")

    # SWAGGER CODEGEN COMPONENT
    # generate & install api client library
    SwaggerCodegen(
        logger=Log,
        configs=config_dict["swagger-codegen"],
        oas_location=config_dict["general"]["oas-location"],
        output_dir=str(config_dict["general"]['output-dir']) + "/swagger-codegen"
    ).generate_client_api()

    # INIT MODEL
    # initialize the large language model
    try:
        model = Model()
    except Exception as error:
        print(error)
        torch.cuda.empty_cache()
        exit(1)

    # TYPE GENERATOR COMPONENT
    # generate a subprogram for each given endpoint
    # that generates random values for the parameters
    TypeGenerator(
        scope=config_dict["general"]["scope-file"],
        oas_location=config_dict["general"]["oas-location"],
        template_location=config_dict["general"]["template"],
        model=model
    ).type_generator()

    # BUILD TEST-TOOL
    # Use the previously generated libraries and subprograms
    # to build the test-tool
    TestToolBuilder(
        oas_location=config_dict["general"]["oas-location"],
        scope=config_dict["general"]["scope-file"],
        output_dir=str(config_dict["general"]['output-dir']) + "/test-tool",
        generated_files=config_general['output-dir'] + '/model/code-snippets',
        set_range=10,
        config_filepath=config_filepath,
        device_map=config_dict["model"]["device-map"]
    ).build_test_tool()