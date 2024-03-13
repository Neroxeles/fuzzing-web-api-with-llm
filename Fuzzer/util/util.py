import os
import yaml
from pynvml import *

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


###########################################################################
# GPU stats
###########################################################################

def print_gpu_utilization():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.")


def print_summary(result):
    print(f"Time: {result.metrics['train_runtime']:.2f}")
    print(f"Samples/second: {result.metrics['train_samples_per_second']:.2f}")
    print_gpu_utilization()