from model.CodeLlama2 import CodeLlama2
from model.StarCoder import StarCoder
from util.Logger import Logger

def instantiate_model(config: dict, logger: Logger) -> StarCoder | CodeLlama2:
  kwargs = {
    "checkpoint":config['checkpoint'],
    "device":config['device'],
    "device_map_path":config['device-map'],
    "offload_folder":config['offload-folder'],
    "logger":logger,
    "batch_size":config['batch-size'],
    "temperature":config['temperature'],
    "top_k":config['top-k'],
    "top_p":config['top-p'],
    "do_sample":config['do-sample'],
    "cache_dir":config['cache-dir'],
    "load_in":config['load-in']
  }
  if "codellama/CodeLlama" in kwargs['checkpoint']:
    return CodeLlama2(**kwargs)
  elif "bigcode/starcoder" in kwargs['checkpoint']:
    return StarCoder(**kwargs)
  else:
    return None