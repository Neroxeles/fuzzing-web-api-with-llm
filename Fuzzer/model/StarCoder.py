import os
import torch
import enum
import re

from transformers import (
  AutoModelForCausalLM, GPTBigCodeForCausalLM,
  AutoTokenizer,
  PreTrainedTokenizer,
  PreTrainedTokenizerFast,
  StoppingCriteria,
  StoppingCriteriaList
)

from util.util import (
  get_file_content,
  write_str_into_file
)
import util.Logger as Logger

from huggingface_hub import login

class Phase(enum.Enum):
  PHASE_1 = 1
  PHASE_2 = 2
  PHASE_3 = 3

os.environ["TOKENIZERS_PARALLELISM"] = "false"  # disable warning

# https://discuss.huggingface.co/t/implimentation-of-stopping-criteria-list/20040
# & ChatGPT explained it as well
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
      input_ids[:, self.start_length :]
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
  def __init__(self, checkpoint: str = "bigcode/starcoder", device: str = "cuda") -> None:
    """Initialize the StarCoder model"""
    login()
    Logger.section_title("Instantiate Tokenizer & Model")
    self.device = device
    self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
    self.model = (
      GPTBigCodeForCausalLM.from_pretrained(checkpoint)
                              .to(torch.bfloat16)
                              .to(self.device)
    )
    Logger.content("Tokenizer configuration from pretrained", self.tokenizer.pretrained_init_configuration)
    Logger.content("Model configuration from pretrained", self.tokenizer.pretrained_init_configuration)
    self.eos = []
    self.input_str = ""

  def apply_chat_template(self, phase: Phase, oas_path: str, save_output_dir: str, save_file_name: str) -> None:
    """Build input string for the StarCoder generator"""
    # sentinel_tokens = [
    #   "<fim_prefix>", "<fim_middle>", "<fim_suffix>", "<fim_pad>",
    #   "<reponame>", "<filename>", "<empty_output>", "<|endoftext|>"
    # ]
    sentinel_tokens = {
      'fn': '<filename>'
    }
    if phase == Phase.PHASE_1:
      oas_str_input = get_file_content(oas_path)
      file_number = re.findall(r'\d+', oas_path)[-1]
      #TODO tool_str_input = get_file_content("path/to/tool/file")
      self.input_str = f"```\n{oas_str_input}```\nUse the OpenAPI specification above to generate API requests with Python code.\n{sentinel_tokens['fn']}program/requests_{file_number}.py\nimport requests"
      write_str_into_file(
        content=self.input_str,
        directory=save_output_dir,
        filename=save_file_name
      )
      self.eos = ["<|endoftext|>", "Use the OpenAPI specification", "import requests"]
    
    if phase == Phase.PHASE_2:
      pass
    if phase == Phase.PHASE_3:
      pass

  @torch.inference_mode()
  def generate(self, temperature: float = 1.0, batch_size: int = 1, max_length: int = 512) -> list[str]:
    """Generates Output (e.g. Python Code)"""
    #TODO experiment with padding and truncation strategies
    # Converts a string to a sequence of ids (integer), using the tokenizer and vocabulary.
    input_tokens: torch.Tensor = self.tokenizer.encode(
      text=self.input_str,
      return_tensors="pt",
      padding=False,
      truncation=False
    ).to(self.device)
    Logger.content("Number of Tokens produced", f"Size = {input_tokens.size}\nLen = {len(input_tokens[0])}")

    stopping_criteria = StoppingCriteriaList([
      EndOfFunctionCriteria(
        start_length=len(input_tokens[0]),
        eos=self.eos,
        tokenizer=self.tokenizer
      )
    ])

    raw_outputs = self.model.generate(
      input_tokens,
      max_length=min(1024, len(input_tokens[0]) + 512), #TODO modify
      do_sample=True,
      top_p=1.0,
      temperature=max(temperature, 0.01),
      num_return_sequences=batch_size,
      stopping_criteria=stopping_criteria,
      output_scores=True,
      return_dict_in_generate=True,
      repetition_penalty=1.0,
      pad_token_id=self.tokenizer.eos_token_id
    )

    #TODO What? o.O
    gen_seqs = raw_outputs.sequences[:, len(input_tokens[0]) :]
    gen_strs = self.tokenizer.batch_decode(
      gen_seqs, skip_special_tokens=False
    )
    # removes eos tokens
    outputs = []
    for output in gen_strs:
      min_index = 10000 #TODO What? o.=
      for eos in self.eos:
        if eos in output:
          min_index = min(min_index, output.index(eos))
      outputs.append(output[:min_index])
    return outputs

def instantiate_model(config: dict[str, any]) -> StarCoder:
  """Returns a instance of the StarCoder model"""
  model_obj = StarCoder(
    checkpoint=config['checkpoint'],
    device=config['device']
  )
  return model_obj