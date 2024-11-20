import os, shutil
from util.util import (
    write_str_into_file,
    load_yml_file
)
import re

# Aktuelle Schwierigkeiten:
# Aktuell werden alle Parameter/Properties verwendet (sogar optionale, die nicht unbedingt möglich sind oder sogar probleme verursachen)
# Aktuell werden für alle Props/Parameter zufällige Werte erzeugt
# Es muss ein Config File erstellt werden...
# Für jeden Endpunkt müssen Eigenschafften klar definiert sein... *crying in corner*
# Kann ich das Config Datei Format von ObST verwenden?

# Listen sind ebenfalls problematisch und nicht implementiert.

# Aktuell geht auch nur application/json format...

class TestToolBuilder:
    def __init__(
            self,
            oas_location: str,
            output_dir: str,
            scope: str,
            device_map: str,
            config_filepath: str,
            generated_files: str,
            set_range: int = 1000,
            host: str = None
        ) -> None:
        self.output_dir: str = output_dir
        self.range = set_range
        self.oas_location = oas_location
        self.oas = load_yml_file(oas_location)
        self.scope_location = scope
        self.scope = load_yml_file(scope)
        self.host = host
        self.generated_files = generated_files
        self.config_filepath = config_filepath
        self.device_map = device_map

    def build_test_tool(self):
        """This functions uses previously generated files and libraries to build a test-tool."""
        # copy & create files
        self.__copy_and_create_files()

        # prepare config.yml
        self.__prepare_config_file()
        # prepare apiFunctions.py
        api_endpoints = self.__prepare_api_caller()
        # prepare sqlFunctions.py (tracker)
        self.__prepare_sql_functions()
        # prepare main.py
        self.__prepare_main(api_endpoints)

    def __copy_and_create_files(self):
        # create folders
        os.makedirs(self.output_dir + "/util", exist_ok=True)
        os.makedirs(self.output_dir + "/profile", exist_ok=True)
        for file in os.listdir(self.generated_files):
            filename = file.replace("-", "")[:7] + ".py"
            shutil.copyfile(self.generated_files + f"/{file}", self.output_dir + f"/util/{filename}")
        shutil.copyfile(self.config_filepath, self.output_dir + f"/profile/configs_generation_tool.yml")
        shutil.copyfile(self.scope_location, self.output_dir + f"/profile/scope.yml")
        shutil.copyfile(self.oas_location, self.output_dir + f"/profile/oas.yml")
        if self.device_map:
            shutil.copyfile(self.device_map, self.output_dir + f"/profile/device_map.yml")
        write_str_into_file(
            content="",
            directory=self.output_dir,
            filename="/__init__.py",
            mode="w"
        )
        write_str_into_file(
            content="",
            directory=self.output_dir + "/util",
            filename="/__init__.py",
            mode="w"
        )
    
    def __prepare_api_caller(self) -> int:
        if self.host == None:
            self.host = self.oas["servers"][0]['url']
        content = "from __future__ import print_function\n"\
            "import swagger_client\n"\
            "from swagger_client.rest import ApiException\n"\
            "import yaml\n"\
            "import inspect\n"\
            "import time\n"\
            "import random\n\n"\
            "# Custom APIClient to log the request method, path, parameters, and body\n"\
            "class CustomApiClient(swagger_client.ApiClient):\n"\
            "  def request(self, method, url, query_params=None, headers=None, post_params=None, body=None, *args, **kwargs):\n"\
            "    # Capture the HTTP method, path, parameters, and request body\n"\
            "    self.last_method = method\n"\
            "    self.last_url = url\n"\
            "    self.last_query_params = query_params\n"\
            "    self.last_body = body\n"\
            "    self.last_header = headers\n"\
            "    self.last_post_params = post_params\n"\
            "    self.last_request_timestamp = time.time_ns()\n"\
            "    try:\n"\
            "      # Proceed with the actual request\n"\
            "      request = super().request(method, url, query_params, headers, post_params, body , *args, **kwargs)\n"\
            "      self.last_response_timestamp = time.time_ns()\n"\
            "      self.last_time_difference = self.last_response_timestamp - self.last_request_timestamp\n"\
            "      return request\n"\
            "    except Exception as e:\n"\
            "      self.last_response_timestamp = time.time_ns()\n"\
            "      self.last_time_difference = self.last_response_timestamp - self.last_request_timestamp\n"\
            "      raise\n\n"\
            "class ApiCalls():\n"\
            "  def __init__(self) -> None:\n"\
            "    configuration = swagger_client.Configuration()\n"\
            f"    configuration.host = '{self.host}'\n"\
            "    self.custom_api_client = CustomApiClient(configuration)\n"\
            "    with open(__file__[:-15] + r\"config.yml\", \"r\") as f:\n"\
            "      self.configs = yaml.load(f, Loader=yaml.FullLoader)\n\n"
        api_endpoints = 0
        for path in self.oas["paths"]:
            for method in self.oas["paths"][path]:
                parameters = []
                properties = []
                api_endpoints += 1
                try:
                    parameters_in_url = self.__search_dict(self.oas, f"paths|{path}|{method}|parameters")
                    for param in parameters_in_url:
                        parameters.append({
                            'name':"para_" + re.sub(r"(\w)([A-Z])", r"\1_\2", param['name']).lower(),
                            'type':param['schema']['type']
                        })
                except:
                    pass
                try:
                    properties_in_request_body = self.__search_dict(self.oas, f"paths|{path}|{method}|requestBody|content|application/json|schema|properties")
                    for prop in properties_in_request_body:
                        properties.append({
                            'name':"prop_" + re.sub(r"(\w)([A-Z])", r"\1_\2", prop).lower(),
                            'type':properties_in_request_body[prop]['type']
                        })
                except:
                    pass
                func_params = "self,"
                for parameter in parameters:
                    func_params += parameter['name']
                    if parameter['type'] == "integer":
                        func_params += ": int,"
                    elif parameter['type'] == "string":
                        func_params += ": str,"
                    else:
                        func_params += ": any,"
                for property in properties:
                    func_params += property['name']
                    if property['type'] == "integer":
                        func_params += ": int,"
                    elif property['type'] == "string":
                        func_params += ": str,"
                    else:
                        func_params += ": any,"
                func_name = path.replace("/","_")[1:].replace("{","").replace("}","")
                body_var_name = ""
                pieces = func_name.split("_")
                for idx, piece in enumerate(pieces):
                    if len(pieces) - idx > 2:
                        continue
                    body_var_name += piece.capitalize()
                body_var_name += "Body("
                try:
                    body_var_name = self.__search_dict(self.oas, f"paths|{path}|{method}|requestBody|content|application/json|schema|$ref").split("/")[-1] + "("
                except:
                    pass
                for property in properties:
                    body_var_name += property['name'][5:] + "=" + property['name'] + ","
                body_var_name = body_var_name[:-1] + ")"
                content += f"  def api_{func_name}_{method}({func_params[:-1]}):\n"
                try:
                    content += f"    api_instance = swagger_client.{''.join(word.capitalize() for word in self.oas['paths'][path][method]['tags'][0].split('_'))}Api(self.custom_api_client)\n"
                except:
                    content += "    api_instance = swagger_client.DefaultApi(self.custom_api_client)\n"
                if parameters:
                    content += f"    _, _, _, locals = inspect.getargvalues(inspect.currentframe())\n"
                    content += f"    pargs = self.__prep_parameter_args(locals, \"{path}\", \"{method}\")\n"
                if properties:
                    content += f"    if self.configs[\"{path}\"][\"{method}\"][\"requestBody\"][\"require_lvl\"] != 0 and True if self.configs[\"{path}\"][\"{method}\"][\"requestBody\"][\"require_lvl\"] == 2 else random.randint(0, 1):\n"
                    content += "      bargs = {\"body\":" + f"swagger_client.{body_var_name}" + "}\n"
                content += f"    try:\n"
                try:
                    content += "      api_instance." + re.sub(r"(\w)([A-Z])", r"\1_\2", self.__search_dict(self.oas, f"paths|{path}|{method}|operationId")).lower() + "("
                except:
                    content += f"      api_instance.{func_name}_{method}("
                # for parameter in parameters:
                #     content += f"{parameter['name'][5:]}={parameter['name']},"
                # if properties:
                #     content += f"body=body"
                if parameters:
                    content += "**pargs,"
                if properties:
                    content += "**bargs,"
                if parameters or properties:
                    content = content[:-1]
                content += ")\n"
                content += f"      return api_instance.api_client\n"
                content += f"    except ApiException as e:\n"
                content += f'      print("Exception when calling DefaultApi->api_{func_name}_{method}: %s\\n" % e)\n      return e\n\n'
        content += "  def __prep_parameter_args(self, locals: dict, path: str, method: str) -> dict:\n"\
            "    args = {}\n"\
            "    for local in locals:\n"\
            '      if "para_" in local and "parameters" in self.configs[path][method]:\n'\
            '        for para in self.configs[path][method]["parameters"]:\n'\
            '          if para["name"] == local[5:] and (para["required_lvl"] != 0 and (True if para["required_lvl"] == 2 else random.randint(0, 1))):\n'\
            '            args[para["name"]] = para["use_value"] if para["use_value"] != None else locals[local]\n'\
            "    return args\n\n"\
            "def make_api_caller():\n  return ApiCalls()"
        write_str_into_file(
            content=content,
            directory=self.output_dir,
            filename="/apiFunctions.py",
            mode="w"
        )
        return api_endpoints

    def __prepare_main(self, api_endpoints: int):
        content = "from apiFunctions import make_api_caller\n"
        content += self.__prepare_imports()
        content += "import random\nfrom sqlFunctions import SQLite\nimport yaml, json\nimport os\n\n"\
            'if __name__ == "__main__":\n'\
            "  api_caller = make_api_caller()\n"\
            "  tracker = SQLite()\n\n"\
            "  with open(os.path.dirname(__file__) + \"/profile/oas.yml\", \"r\") as f:\n"\
            "    oas = yaml.load(f, Loader=yaml.FullLoader)\n"\
            "  with open(os.path.dirname(__file__) + \"/config.yml\", \"r\") as f:\n"\
            "    configs_test_tool = yaml.load(f, Loader=yaml.FullLoader)\n"\
            "  with open(os.path.dirname(__file__) + \"/profile/scope.yml\", \"r\") as f:\n"\
            "    scope = yaml.load(f, Loader=yaml.FullLoader)\n"\
            "  with open(os.path.dirname(__file__) + \"/profile/configs_generation_tool.yml\", \"r\") as f:\n"\
            "    configs_generation_tool = yaml.load(f, Loader=yaml.FullLoader)\n"\
            "  try:\n"\
            "    device_map = None\n"\
            "    with open(os.path.dirname(__file__) + \"/profile/device_map.yml\", \"r\") as f:\n"\
            "      device_map = yaml.load(f, Loader=yaml.FullLoader)\n"\
            "  except:\n"\
            "    pass\n\n"\
            "  tracker.create_tables()\n"\
            "  tracker.init(process_id=1, program_version=1.0, program_name=\"test-tool-generator\", oas_version=oas['openapi'], oas_title=oas['info']['title'], api_version=oas['info']['version'], url=oas['servers'][0]['url'], configs_test_tool=json.dumps(configs_test_tool), scope=json.dumps(scope), configs_generation_tool=json.dumps(configs_generation_tool), device_map=json.dumps(device_map) if device_map else None)\n\n"\
            f"  for i in range(0, {self.range}):\n"
        generators = os.listdir(self.output_dir + "/util")
        generators.sort()
        generators.pop(0)
        content += f"    select = random.randint(0, {len(generators)-1})\n"
        idx = 0
        for path in self.oas["paths"]:
            if path not in self.scope:
                continue
            for method in self.oas["paths"][path]:
                if method not in self.scope[path]:
                    continue
                if not generators:
                    break
                content += f"    if select == {idx}:\n"
                func_name = path.replace("/","_")[1:].replace("{","").replace("}","")
                if ("requestBody" in self.oas['paths'][path][method]) or ("parameters" in self.oas['paths'][path][method]):
                    content += f"      response = api_caller.api_{func_name}_{method}(**{generators.pop(0)[:-3]}())\n"
                else:
                    content += f"      response = api_caller.api_{func_name}_{method}()\n"
                idx += 1
        content += f"    try:\n"
        content += f"      tracker.execute_tracker_query(process_id=1, request_timestamp=api_caller.custom_api_client.last_request_timestamp, response_timestamp=api_caller.custom_api_client.last_response_timestamp, time_difference=api_caller.custom_api_client.last_time_difference, url=api_caller.custom_api_client.last_url, method=api_caller.custom_api_client.last_method, query_parameter=api_caller.custom_api_client.last_query_params, post_parameter=api_caller.custom_api_client.last_post_params, request_body=api_caller.custom_api_client.last_body, response_body=response.last_response.data, request_header=api_caller.custom_api_client.last_header, response_header=response.headers if hasattr(response, 'headers') else None, statuscode=response.last_response.status, reason=response.last_response.reason, error=None)\n"
        content += f"    except:\n"
        content += "      headers = {}\n"
        content += "      for element in response.headers._container:\n"
        content += "        headers[response.headers._container[element][0]] = response.headers._container[element][1]\n"
        content += f"      tracker.execute_tracker_query(process_id=1, request_timestamp=api_caller.custom_api_client.last_request_timestamp, response_timestamp=api_caller.custom_api_client.last_response_timestamp, time_difference=api_caller.custom_api_client.last_time_difference, url=api_caller.custom_api_client.last_url, method=api_caller.custom_api_client.last_method, query_parameter=api_caller.custom_api_client.last_query_params, post_parameter=api_caller.custom_api_client.last_post_params, request_body=api_caller.custom_api_client.last_body, response_body=response.body, request_header=api_caller.custom_api_client.last_header, response_header=headers, statuscode=response.status, reason=response.reason, error=None)\n"\
            "    tracker.commit()\n"\
            "  tracker.close_connection()"
        write_str_into_file(
            content=content,
            directory=self.output_dir,
            filename="/main.py",
            mode="w"
        )

    def __prepare_imports(self) -> str:
        content = ""
        files = os.listdir(self.output_dir + "/util")
        files.sort()
        files.pop(0)
        for file in files:
            content += f"from util.{file[:-3]} import get_dict_with_random_values as {file[:-3]}\n"
        return content
    
    def __prepare_sql_functions(self):
        content = "import sqlite3\nimport json\n\n"\
            "class SQLite:\n"\
            "  def __init__(self) -> None:\n"\
            "    self.con = sqlite3.connect('tracker.db')\n"\
            "    self.cur = self.con.cursor()\n\n"\
            "  def init(self, process_id: int, program_version: str, program_name: str, oas_version: str, oas_title: str, api_version: str, url: str, configs_test_tool: str, scope: str, configs_generation_tool: str, device_map: str) -> None:\n"\
            "    sql = \"INSERT INTO process(process_id, program_version, program_name, oas_version, oas_title, api_version, url, configs_test_tool, scope, configs_generation_tool, device_map) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\"\n"\
            "    try:\n"\
            "      self.cur.execute(sql, (process_id, program_version, program_name, oas_version, oas_title, api_version, url, configs_test_tool, scope, configs_generation_tool, device_map))\n"\
            "      self.con.commit()\n\n"\
            "    except sqlite3.IntegrityError:\n"\
            "      pass\n\n"\
            "  def create_tables(self):\n"\
            '    self.cur.execute("""\n'\
            "    CREATE TABLE IF NOT EXISTS process (\n"\
            "      process_id INTEGER PRIMARY KEY,\n"\
            "      program_version TEXT NOT NULL,\n"\
            "      program_name TEXT NOT NULL,\n"\
            "      oas_version TEXT NOT NULL,\n"\
            "      oas_title TEXT NOT NULL,\n"\
            "      api_version TEXT NOT NULL,\n"\
            "      url TEXT NOT NULL,\n"\
            "      configs_test_tool TEXT NOT NULL,\n"\
            "      scope TEXT NOT NULL,\n"\
            "      configs_generation_tool TEXT NOT NULL,\n"\
            "      device_map TEXT\n"\
            "    );\n"\
            '    """)\n'\
            '    self.cur.execute("""\n'\
            "    CREATE TABLE IF NOT EXISTS tracker (\n"\
            "      id INTEGER PRIMARY KEY,\n"\
            "      process_id INTEGER NOT NULL,\n"\
            "      request_timestamp UNSIGNED BIG INT,\n"\
            "      response_timestamp UNSIGNED BIG INT,\n"\
            "      time_difference UNSIGNED BIG INT,\n"\
            "      url TEXT NOT NULL,\n"\
            "      method TEXT NOT NULL,\n"\
            "      query_parameter TEXT,\n"\
            "      post_parameter TEXT,\n"\
            "      request_body TEXT,\n"\
            "      response_body TEXT,\n"\
            "      request_header TEXT,\n"\
            "      response_header TEXT,\n"\
            "      statuscode INTEGER,\n"\
            "      reason TEXT,\n"\
            "      error TEXT,\n"\
            "      FOREIGN KEY (process_id) REFERENCES process (process_id)\n"\
            "    );\n"\
            '    """)\n\n'\
            "  def execute_tracker_query(\n"\
            "    self,\n"\
            "    process_id: int,\n"\
            "    request_timestamp: int,\n"\
            "    response_timestamp: int,\n"\
            "    time_difference: int,\n"\
            "    url: str,\n"\
            "    method: str,\n"\
            "    query_parameter: list,\n"\
            "    post_parameter: list,\n"\
            "    request_body: str,\n"\
            "    response_body: str,\n"\
            "    request_header: dict,\n"\
            "    response_header: dict,\n"\
            "    statuscode: int,\n"\
            "    reason: str,\n"\
            "    error: str\n"\
            "  ):\n"\
            "    sql = \"INSERT INTO tracker(process_id, request_timestamp, response_timestamp, time_difference, url, method, query_parameter, post_parameter, request_body, response_body, request_header, response_header, statuscode, reason, error) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)\"\n\n"\
            "    json_query_parameter = json.dumps(query_parameter) if query_parameter else None\n"\
            "    json_post_parameter = json.dumps(post_parameter) if post_parameter else None\n"\
            "    json_request_header = json.dumps(request_header) if request_header else None\n"\
            "    json_response_header = json.dumps(response_header) if response_header else None\n\n"\
            "    self.cur.execute(sql, (process_id, request_timestamp, response_timestamp, time_difference, url, method, json_query_parameter, json_post_parameter, request_body, response_body, json_request_header, json_response_header, statuscode, reason, error))\n\n"\
            "  def close_connection(self):\n"\
            "    self.con.close()\n\n"\
            "  def commit(self):\n"\
            "    self.con.commit()"
        write_str_into_file(
            content=content,
            directory=self.output_dir,
            filename="/sqlFunctions.py",
            mode="w"
        )
        return

    def __prepare_config_file(self):
        content = "# required_lvl = 0 -> do not use\n# required_lvl = 1 -> can be used\n# required_lvl = 2 -> must be used\n"
        for path in self.oas['paths']:
            content += f"{path}:\n"
            for method in self.oas['paths'][path]:
                content += f"  {method}:\n"
                try:
                    parameters = self.__search_dict(self.oas, f"paths|{path}|{method}|parameters")
                    content += f"    parameters:\n"
                    for parameter in parameters:
                        content += f"      - name: {parameter['name']}\n"
                        if "required" in parameter:
                            content += f"        required_lvl: {2 if parameter['required'] == True else 0}\n"
                        else:
                            content += f"        required_lvl: 1\n"
                        content += f"        use_value: \n"
                except:
                    pass
                try:
                    if "required" in self.__search_dict(self.oas, f"paths|{path}|{method}|requestBody"):
                        content += f"    requestBody:\n"
                        content += f"      required_lvl: {2 if self.oas['paths'][path][method]['requestBody']['required'] == True else 0}\n"
                    else:
                        content += f"    requestBody:\n"
                        content += f"      required_lvl: 1\n"
                except:
                    pass
        write_str_into_file(
            content=content,
            directory=self.output_dir,
            filename="/config.yml",
            mode="w"
        )
    
    def __search_dict(self, dictionary: dict, path: str) -> dict | str:
        keys = path.split("|")

        temp = dictionary
        for key in keys:
            try:
                temp = temp[key]
            except:
                if "$ref" in temp:
                    temp = self.__search_dict(dictionary, temp["$ref"].replace("/", "|")[2:])[key]
                else:
                    raise AttributeError
        return temp