import requests
import json
import zipfile

def generate_client_script(base_url: str, language: str, spec: dict, output: str, verify: bool = True) -> None:
  url = base_url + f"generate"
  body = {
    "options":  {},
    # "swaggerUrl": "https://petstore.swagger.io/v2/swagger.json" # <-- when loaded from an online file
    "spec": spec, # <-- when loaded from a local file
    "lang": language,
    "type": "CLIENT",
    "codegenVersion" : "V3"
  }
  data = json.dumps(body)
  header = {'content-type': 'application/json'}
  r = requests.post(
    url=url,
    data=data,
    headers=header,
    verify=verify
  )
  with open(output + "/library.zip", 'wb') as f:
    f.write(r.content)
  with zipfile.ZipFile(output + "/library.zip", 'r') as zip_ref:
    zip_ref.extractall(output)