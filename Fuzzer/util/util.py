import os
import yaml

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