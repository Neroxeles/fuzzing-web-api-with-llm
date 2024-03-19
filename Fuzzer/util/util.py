import os
import yaml
from pynvml import *
import json

###########################################################################
# Write & read files
###########################################################################

def load_yml_file(filepath: str) -> dict[str, any]:
  """Load the yml file."""
  with open(filepath, "r") as f:
    object = yaml.load(f, Loader=yaml.FullLoader)
  return object

def write_yml_file(oas: dict[str, any], directory: str, filename: str) -> None:
  with open(f"{directory}/{filename}", "w") as f:
    f.write(yaml.dump(oas))

def get_file_content(filepath: str) -> str:
  with open(filepath) as f:
    data = f.read()
  return data

def write_str_into_file(content: str, directory: str, filename: str, mode: str) -> None:
  with open(f"{directory}/{filename}", mode=mode) as f:
    f.write(content)

def write_dict_to_file(dictionary: dict, directory: str, filename: str) -> None:
  with open(f"{directory}/{filename}", "w") as f:
    json.dump(dictionary, f)

def load_dict_from_file(filepath: str) -> dict:
  with open(filepath, "r") as f:
    data = json.load(f)
  return data

###########################################################################
# GPU stats
###########################################################################

def print_gpu_utilization() -> int:
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    return int(info.used//1024**2)


def print_summary(result):
    print(f"Time: {result.metrics['train_runtime']:.2f}")
    print(f"Samples/second: {result.metrics['train_samples_per_second']:.2f}")
    print_gpu_utilization()