import os
import torch

from transformers import (
  AutoModelForCausalLM,
  AutoTokenizer,
  PreTrainedTokenizer,
  PreTrainedTokenizerFast,
  StoppingCriteria,
  StoppingCriteriaList,
  BitsAndBytesConfig
)
from timeit import default_timer as timer
from util.util import (
  load_dict_from_file
)

from huggingface_hub import login

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # disable warning

# https://discuss.huggingface.co/t/implimentation-of-stopping-criteria-list/20040
class EndOfFunctionCriteria(StoppingCriteria):
  def __init__(self, start_length: int, eos: list[str], tokenizer: (PreTrainedTokenizer | PreTrainedTokenizerFast), *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.start_length = start_length
    self.eos = eos
    self.tokenizer = tokenizer
    self.end_length = {}

  def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
    """Returns true if all generated sequences contain any of the end-of-function strings."""
    # decode generated content
    decoded_generations = self.tokenizer.batch_decode(
      # slices the input_ids tensor to consider only the generated content starting from self.start_length.
      # This is because the initial tokens might include prompts or special tokens that are not part of the actual generated content.
      input_ids[:, self.start_length :], clean_up_tokenization_spaces=False
    )
    done = []
    # loop over each generated string inside decoded_generations
    for index, decoded_generation in enumerate(decoded_generations):
      # For each decoded generation, it checks if any of the end-of-function strings (self.eos) are present in the decoded text.
      # This is done using a list comprehension.
      finished = any([stop_string in decoded_generation for stop_string in self.eos])
      # If any end-of-function string is found in the decoded text (finished is True),
      # and the index is not already in self.end_length, then it proceeds to calculate
      # the length of the generated content up to the stop string.
      if (finished and index not in self.end_length):
        for stop_string in self.eos:
          if stop_string in decoded_generation:
            # Calculate the length of the generated content up to the stop string
            self.end_length[index] = len(
                input_ids[
                    index,  # get length of actual generation
                    self.start_length : -len(
                        self.tokenizer.encode(
                            stop_string,
                            add_special_tokens=False,
                            return_tensors="pt",
                        )[0]
                    ),
                ]
            )
      done.append(finished)
    # Finally, it returns True if all generated sequences contain at least one of the stop strings,
    # otherwise it returns False. The done list keeps track of whether each generation is finished
    # (i.e., contains at least one stop string).
    if all(done):
      print(f"{len(decoded_generation)} generated Tokens", end="\n")
    else:
      print(f"{len(decoded_generation)} generated Tokens", end="\r")
    return all(done)

class Model:
  def __init__(
      self,
      token: str,
      device_map_path: str = None,
      offload_folder: str = "offload",
      load_in: str = "bfloat16",
      checkpoint: str = "bigcode/starcoder2-15b",
      cache_dir:str = None,
      device: str = "cuda",
      batch_size: int = 1,
      temperature: float = 1,
      top_k: int = 0,
      top_p: float = 0,
      do_sample: bool = True,
      num_beams: int = None,
      num_beam_groups: int = None,
      penalty_alpha: float = None,
      diversity_penalty: float = None,
      max_new_tokens: int = 512,
      eos: list[str] = []
    ) -> None:
    """Initialize any model for causal LMs"""
    # hugging face login with token
    login(token=token)

    self.device = device
    self.eos = eos

    # configs to load the model
    kwargs = {}
    if load_in == "4bit":
      quantization_config = BitsAndBytesConfig(load_in_4bit=True)
      kwargs['quantization_config'] = quantization_config
    elif load_in == "8bit":
      quantization_config = BitsAndBytesConfig(load_in_8bit=True)
      kwargs['quantization_config'] = quantization_config
    else:
      kwargs['torch_dtype'] = torch.bfloat16
    if cache_dir:
      kwargs['cache_dir'] = cache_dir
    if device_map_path == "auto":
      kwargs['device_map'] = "auto"
    elif device_map_path:
      kwargs['device_map'] = load_dict_from_file(device_map_path)
    # load from pretrained
    self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    self.model = (
      AutoModelForCausalLM.from_pretrained(
        checkpoint,
        offload_folder=offload_folder,
        offload_state_dict=True,
        **kwargs
      )
    )
    self.__get_layer_information()
    
    # configs to use the model
    self.model_kwargs = {
      'max_new_tokens': max_new_tokens,
      'output_scores': True,
      'return_dict_in_generate': True,
      'repetition_penalty': 1.0,
      'pad_token_id': self.tokenizer.eos_token_id,
    }
    if temperature:
      self.model_kwargs['temperature'] = max(temperature, 0.01)
    if top_p:
      self.model_kwargs['top_p'] = top_p
    if top_k:
      self.model_kwargs['top_k'] = top_k
    if batch_size:
      self.model_kwargs['num_return_sequences'] = batch_size
    if do_sample:
      self.model_kwargs['do_sample'] = do_sample
    if num_beams:
      self.model_kwargs['num_beams'] = num_beams
    if num_beam_groups:
      self.model_kwargs['num_beam_groups'] = num_beam_groups
    if penalty_alpha:
      self.model_kwargs['penalty_alpha'] = penalty_alpha
    if diversity_penalty:
      self.model_kwargs['diversity_penalty'] = diversity_penalty

  @torch.inference_mode()
  def generate(self, prompt, use_batch_size:bool=True) -> list[str]:
    """Generates Output (e.g. Python Code-Snippets)"""
    if not use_batch_size:
        self.model_kwargs['num_return_sequences'] = 1
    #TODO experiment with padding and truncation strategies
    # Converts a string to a sequence of ids (integer), using the tokenizer and vocabulary.
    input_tokens: torch.Tensor = self.tokenizer.encode(
      text=prompt,
      return_tensors="pt",
      padding=False,
      truncation=False
    ).to(self.device)

    # Define the criteria for when the generator should stop
    stopping_criteria = StoppingCriteriaList([
      EndOfFunctionCriteria(
        start_length=len(input_tokens[0]),
        eos=self.eos,
        tokenizer=self.tokenizer
      )
    ])

    raw_outputs = self.model.generate(
      input_tokens,
      stopping_criteria=stopping_criteria,
      **self.model_kwargs
    )

    gen_seqs = raw_outputs.sequences[:, len(input_tokens[0]) :]
    # clean_up_tokenization_spaces=False prevents a tokenizer edge case which can result in spaces being removed around punctuation
    gen_strs = self.tokenizer.batch_decode(
      gen_seqs, skip_special_tokens=False, clean_up_tokenization_spaces=False
    )
    # removes eos tokens
    outputs = []
    for output in gen_strs:
      min_index = 10000
      for eos in self.eos:
        if eos in output:
          min_index = min(min_index, output.index(eos))
      outputs.append(output[:min_index])
    return outputs
  
  def __get_layer_information(self):
    layer_sizes_gb = {}
    for name, param in self.model.named_parameters:
      layer_size_gb = param.numel() * param.element_size() / 1024**3
      layer_sizes_gb[name] = layer_size_gb
    
    for layer_name, size_gb in layer_sizes_gb.items():
      print(f"{layer_name}: {size_gb:.4f} GB")