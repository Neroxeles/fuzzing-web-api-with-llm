import os
import yaml
from pynvml import *
import json
import hashlib

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

def add_missing_imports(filepath: str) -> bool:
  common_packages = ["random", "re", "string"]
  changes = False
  with open(filepath, "r") as f:
    data = f.read()
    for common_package in common_packages:
      if (common_package in data) and not (f"import {common_package}" in data):
        data = f"import {common_package}\n{data}"
        changes = True
  if changes:
    with open(filepath, "w") as f:
      f.write(data)
  return changes

def check_core_functionality(filepath: str) -> bool:
  missing = True
  with open(filepath, "r") as f:
    data = f.read()
    if "get_dict_with_random_values" in data:
      missing = False
  return missing


###########################################################################
# Checksum
###########################################################################

def md5(filepath: str) -> str:
  hash_md5 = hashlib.md5()
  with open(filepath, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      hash_md5.update(chunk)
  return hash_md5.hexdigest()

def save_md5(filepath: str, checksum: str) -> None:
  with open(filepath, "r") as f:
    data = f.readlines()
  for idx, line in enumerate(data):
    if "oas-checksum" in line:
      data[idx] = f"  oas-checksum: \"{checksum}\"\n"
  with open(filepath, "w") as f:
    f.writelines(data)

def dir_exists(filepath: str) -> bool:
  return os.path.isdir(filepath)

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