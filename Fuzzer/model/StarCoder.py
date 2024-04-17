import os
import torch
import enum
import re

from accelerate import (
  infer_auto_device_map,
  init_empty_weights
)
from transformers import (
  AutoConfig,
  AutoModelForCausalLM, GPTBigCodeForCausalLM,
  AutoTokenizer,
  PreTrainedTokenizer,
  PreTrainedTokenizerFast,
  StoppingCriteria,
  StoppingCriteriaList,
  BitsAndBytesConfig
)
from timeit import default_timer as timer
from util.util import (
  get_file_content,
  write_str_into_file,
  write_dict_to_file,
  load_dict_from_file
)
from util.Logger import Logger

from huggingface_hub import login

class Phase(enum.Enum):
  PHASE_1 = 1
  PHASE_2 = 2
  PHASE_3 = 3

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
        return all(done)

class StarCoder:
  def __init__(
      self,
      logger: Logger,
      device_map_path: str,
      offload_folder: str = "offload",
      load_in: str = "bfloat16",
      checkpoint: str = "bigcode/starcoder",
      cache_dir:str = None,
      device: str = "cuda",
      batch_size: int = 1,
      temperature: float = 1,
      top_k: int = 0,
      top_p: float = 0,
      do_sample: bool = True
    ) -> None:
    """Initialize the StarCoder model"""
    login()
    self.log = logger
    self.device = device
    self.batch_size = batch_size
    self.temperature = temperature
    self.top_k = top_k
    self.do_sample = do_sample
    self.top_p = top_p

    # config = AutoConfig.from_pretrained(checkpoint)
    # with init_empty_weights():
    #   empty_model = AutoModelForCausalLM.from_config(config)
    # empty_model.tie_weights()
    # device_map = infer_auto_device_map(
    #   empty_model,
    #   no_split_module_classes=["Block"],
    #   dtype="bfloat16",
    #   max_memory={0: "14GB", "cpu": "50GB"}
    # )
    # write_dict_to_file(
    #   device_map,
    #   directory="/content/fuzzing-web-api-with-llm/configs",
    #   filename="device_map.json"
    # )

    device_map = load_dict_from_file(device_map_path)
    kwargs = {}

    if load_in == "8bit":
      quantization_config = BitsAndBytesConfig(load_in_8bit=True,llm_int8_threshold=5.0)
      kwargs['quantization_config'] = quantization_config
    else:
      kwargs['torch_dtype'] = torch.bfloat16

    if cache_dir:
      kwargs['cache_dir'] = cache_dir

    self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    # In FP32 the model requires more than 60GB of RAM, you can load it in FP16 or BF16 in ~30GB, or in 8bit in ~16GB of RAM
    self.model = (
      GPTBigCodeForCausalLM.from_pretrained(
        checkpoint,
        device_map=device_map,
        offload_folder=offload_folder,
        offload_state_dict=True,
        **kwargs
      )
    )

    self.eos = []
    self.input_str = ""

  def apply_template(self, template_path: str, property: dict, generated_prompts_dir: str, save_file_name: str) -> None:
    """Build input string for the StarCoder generator"""
    # Create input string for the template
    parameters = ""
    for item in property['items']:
      parameters += "- {" + f"{item['name']}: " + "{"
      for s in item['schema']:
        if s == "description":
          continue
        parameters += f"{s}:{item['schema'][s]},"
      parameters = parameters[:-1]
      parameters += "}}\n"
    parameters = parameters[:-1]

    # set template & replace placeholder
    self.input_str = get_file_content(filepath=template_path).replace("<!-- insert list here -->", parameters)
    # save prompt
    write_str_into_file(
      content=self.input_str,
      directory=generated_prompts_dir,
      filename=save_file_name,
      mode="w"
    )
    # Define all possible sequences that point to an end of sequence
    self.eos = ["<|endoftext|>", "```"]

  @torch.inference_mode()
  def generate(self, temperature: float = 1.0, batch_size: int = 1, max_length: int = 512) -> tuple[list[str], int]:
    """Generates Output (e.g. Python Code)"""
    start = timer()
    #TODO experiment with padding and truncation strategies
    # Converts a string to a sequence of ids (integer), using the tokenizer and vocabulary.
    input_tokens: torch.Tensor = self.tokenizer.encode(
      text=self.input_str,
      return_tensors="pt",
      padding=False,
      truncation=False
    ).to(self.device)
    self.log.content(f"  - Number of Input Tokens = {len(input_tokens[0])}\n")

    stopping_criteria = StoppingCriteriaList([
      EndOfFunctionCriteria(
        start_length=len(input_tokens[0]),
        eos=self.eos,
        tokenizer=self.tokenizer
      )
    ])

    raw_outputs = self.model.generate(
      input_tokens,
      max_new_tokens = 512,
      # max_length=min(2048, len(input_tokens[0]) + 512),
      do_sample=self.do_sample,
      top_p=self.top_p,
      top_k=self.top_k,
      temperature=max(self.temperature, 0.01),
      num_return_sequences=self.batch_size,
      stopping_criteria=stopping_criteria,
      output_scores=True,
      return_dict_in_generate=True,
      repetition_penalty=1.0,
      pad_token_id=self.tokenizer.eos_token_id
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
    end = timer()
    self.log.content(f"  - Number of Output Tokens = {len(gen_seqs[0])}\n")
    self.log.content(f"  - Execution time = {end - start} seconds\n")
    return outputs, len(gen_seqs[0])

def instantiate_model(config: dict[str, any], logger: Logger) -> StarCoder:
  """Returns an instance of the StarCoder model"""
  model_obj = StarCoder(
    checkpoint=config['checkpoint'],
    device=config['device'],
    device_map_path=config['device-map'],
    offload_folder=config['offload-folder'],
    logger=logger,
    batch_size=config['batch-size'],
    temperature=config['temperature'],
    top_k=config['top-k'],
    top_p=config['top-p'],
    do_sample=config['do-sample'],
    cache_dir=config['cache-dir'],
    load_in=config['load-in']
  )
  return model_obj