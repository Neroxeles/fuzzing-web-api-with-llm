from util.Logger import Logger
from util.util import (
    load_yml_file
)
import os
import json
import requests
import zipfile

class SwaggerCodegen:
    def __init__(
            self,
            logger: Logger,
            configs: dict,
            oas_location: str,
            output_dir: str
        ) -> None:
        self.logger = logger
        self.oas_location = oas_location
        self.swagger_codegen_url = configs["base-url"]
        self.verify = configs["verify"]
        self.lang = configs["lang"]
        self.output_dir = output_dir

    def generate_client_api(self) -> bool:
        """This component generates an api client"""
        # create output dir
        os.makedirs(self.output_dir, exist_ok=True)
        # call swagger codegen and generate library
        if not self.__call_swagger_codegen():
            return False
        # install library
        os.system(f"pip install {self.output_dir}")
        return True
    
    def __call_swagger_codegen(self) -> bool:
        """Use swagger codegen to generate the client library"""
        url = self.swagger_codegen_url + f"generate"

        # prepare args for api call
        body = {
            "options":  {},
            "lang": self.lang,
            "type": "CLIENT",
            "codegenVersion" : "V3"
        }
        if "http" not in self.oas_location:
            # when loaded from a local file
            body["spec"] = load_yml_file(filepath=self.oas_location)
        else:
            # when loaded from an online file
            body["swaggerUrl"] = self.oas_location

        # dump dict as json
        data = json.dumps(body)
        # set content-type for json format
        header = {'content-type': 'application/json'}
        # create a POST request
        r = requests.post(
            url=url,
            data=data,
            headers=header,
            verify=self.verify
        )
        if r.status_code != 200:
            return False
        # save response data (.zip)
        with open(self.output_dir + "/library.zip", 'wb') as f:
            f.write(r.content)
        # extract zip archive
        with zipfile.ZipFile(self.output_dir + "/library.zip", 'r') as zip_ref:
            zip_ref.extractall(self.output_dir)
        return True