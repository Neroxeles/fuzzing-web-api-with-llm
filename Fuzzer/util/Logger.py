import platform
import subprocess
import re

class Logger:
  def __init__(self, filepath: str):
    self.filepath = filepath

  def content(self, content: str):
    print(f"{content}", end="")
    with open(self.filepath, "a") as f:
      f.write(content)

  def system(self, filepath):
    content = f"# About the system\n"
    content += f"## from python package 'platform':\n"
    content += f"- system: {platform.system()}\n"
    content += f"- architecture: {platform.architecture().__str__()}\n"
    content += f"- machine: {platform.machine()}\n"
    content += f"- processor: {platform.processor()}\n"
    content += f"- node: {platform.node()}\n"
    content += f"- platform: {platform.platform()}\n"
    content += f"- release: {platform.release()}\n"
    content += f"- libc_ver: {platform.libc_ver().__str__()}\n"
    content += f"- freedesktop_os_release:\n"
    for entry in platform.freedesktop_os_release():
      content += f"  - {entry}: {platform.freedesktop_os_release()[entry]}\n"
    content += f"- version: {platform.version()}\n"
    content += f"- python_version: {platform.python_version()}\n"
    shell_output = (subprocess.check_output("lscpu", shell=True).strip()).decode()
    outputs = re.split("\n", shell_output)
    output_as_dict = {}
    for output in outputs:
      key_value = re.split(":", output)
      output_as_dict[key_value[0]] = re.findall(r"[\w]{1,}[\s\S]{0,}", key_value[1])[0]
    content += f"## from subprocess.check_output('lscpu', shell=True):\n"
    content += "|<div style='width:3cm'></div>|   |\n"
    content += f"|---|---|\n"
    for entry in output_as_dict:
      content += f"| {entry} | {output_as_dict[entry]} |\n"
    content += f"## from subprocess.check_output('nvidia-smi', shell=True):\n"
    shell_output = (subprocess.check_output("nvidia-smi", shell=True).strip()).decode()
    content += f"{shell_output}\n"
    content += f"## from subprocess.check_output('cat /proc/cpuinfo', shell=True):\n"
    shell_output = (subprocess.check_output("cat /proc/cpuinfo", shell=True).strip()).decode()
    content += f"{shell_output}\n"
    content += f"## from subprocess.check_output('cat /proc/meminfo', shell=True):\n"
    shell_output = (subprocess.check_output("cat /proc/meminfo", shell=True).strip()).decode()
    content += f"{shell_output}\n"
    content += f"## from subprocess.check_output('cat /etc/*release', shell=True):\n"
    shell_output = (subprocess.check_output("cat /etc/*release", shell=True).strip()).decode()
    content += f"{shell_output}\n"
    with open(filepath, "w") as f:
      f.write(content)

def make_logger(filepath: str) -> Logger:
  return Logger(filepath)