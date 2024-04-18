# fuzzing-web-api-with-llm
Automatic generation of test cases for web APIs using large language models

## Use on Google Colab

```bash
!rm -r /content/sample_data
!rm -r /content/fuzzing-web-api-with-llm
!git clone -b codellama https://github.com/Neroxeles/fuzzing-web-api-with-llm.git

!pip install PyYAML torch transformers accelerate nvidia-ml-py3 huggingface_hub
!pip install --upgrade transformers
# when loading in 8bit
!pip install -i https://pypi.org/simple/ bitsandbytes

!rm -r /content/offload
!python3 /content/fuzzing-web-api-with-llm/Fuzzer/main.py "/content/fuzzing-web-api-with-llm/configs/config-files/colab-default.yml"

!zip -r /content/file.zip /content/fuzzing-web-api-with-llm/output
```