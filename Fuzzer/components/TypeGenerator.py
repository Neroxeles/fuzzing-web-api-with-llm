import os
from util.util import (
    load_yml_file,
    get_file_content,
    write_str_into_file
)
import json
from model.ModelForCausalLM import Model

class TypeGenerator():
    def __init__(
            self,
            output_dir: str,
            oas_location: str,
            template_location: str,
            scope: dict,
            model: Model,
            eos: list[str],
            min_chars: int,
            max_resamples: int
        ) -> None:
        self.output_dir_code: str = output_dir + "/generated-code"
        self.output_dir_prompt: str = output_dir + "/generated-prompts"
        self.oas_location: str = oas_location
        self.template_location: str = template_location
        self.scope: dict = load_yml_file(scope)
        self.model: Model = model
        self.eos: list[str] = eos
        self.min_chars: int = min_chars
        self.max_resamples = max_resamples
  
    def type_generator(self) -> bool:
        """This component generates subprograms. Each subprogram generates random values for an api endpoint."""
        # create output dirs
        os.makedirs(self.output_dir_code, exist_ok=True)
        os.makedirs(self.output_dir_prompt, exist_ok=True)

        # load oas and replace references
        oas = self.__load_oas()
        # load endpoints
        endpoints = self.__load_selected_endpoints(oas)
        # split into smaller parts
        parts = self.__split_into_parts(endpoints)
        # create prompts
        prompts = self.__create_prompts(parts)
        # create subprograms
        subprograms = self.__generate_subprograms(prompts)
        # resample strategies
        self.__resample_strategies(subprograms, prompts)
        # check for missing imports
        self.__add_missing_imports(subprograms)

        return True
    
    def __load_selected_endpoints(self, oas: dict) -> dict:
        """Load every endpoint that has to be generated by an LLM"""
        # get endpoints
        endpoints = {}
        for path in oas["paths"]: # paths
            if str(path) in self.scope:
                endpoints[str(path)] = {}
                for http_method in oas["paths"][path]: # http methods
                    if http_method in self.scope[path]:
                        endpoints[str(path)][http_method] = oas["paths"][path][http_method]
        return endpoints
    
    def __split_into_parts(self, endpoints: dict) -> list[str]:
        """Split the selected oas endpoints in smaller parts and return them as json strings."""
        parts = []
        for endpoint in endpoints:
            for http_method in endpoints[endpoint]:
                parts.append(json.dumps({endpoint: endpoints[endpoint][http_method]}))
        return parts
    
    def __create_prompts(self, parts: list[str]) -> list[str]:
        """Use the given template and the created parts to create the prompt."""
        prompts = []
        for part in parts:
            prompts.append(get_file_content(filepath=self.template_location).replace("<!-- insert list here -->", part))
        return prompts
    
    def __generate_subprograms(self, prompts: list[str]) -> list[str]:
        """Use the given LLM to generate subprograms. Each subprogram generates a random value for an parameter."""
        file_paths = []
        for p_idx, prompt in enumerate(prompts):
            outputs = self.model.generate(prompt=prompt)
            for o_idx, output in enumerate(outputs):
                filename = "snip-p{:0>{}}-b{:0>{}}".format(p_idx, 2, o_idx, 2) + ".py"
                file_paths.append(filename)
                write_str_into_file(
                    content=output,
                    directory=self.output_dir_code,
                    filename=filename,
                    mode="w"
                )
        return file_paths
    
    def __resample_strategies(self, subprograms: list[str], prompts: list[str]):
        """Executes resamples when certain conditions apply"""
        for idx, subprogram in enumerate(subprograms):
            max_resamples = self.max_resamples
            # resample strategy
            while max_resamples:
                # if file is empty or functionname not found
                # do a resample
                file_content = get_file_content(f"{self.output_dir_code}/{subprogram}")
                if (len(file_content) < self.min_chars) or "functionname" not in file_content:
                    max_resamples -= 1
                    output = self.model.generate(prompt=prompts[idx], use_batch_size=False)[0]
                    write_str_into_file(
                        content=output,
                        directory=self.output_dir_code,
                        filename=subprogram,
                        mode="w"
                    )
                else:
                    break

    def __add_missing_imports(self, subprograms: list[str]):
        """checks if any file uses functions from libraries that aren't imported."""
        common_packages = ["random", "re", "string"]
        changes = False
        for subprogram in subprograms:
            with open(f"{self.output_dir_code}/{subprogram}", "r") as f:
                data = f.read()
                for common_package in common_packages:
                    if (f"{common_package}." in data) and not (f"import {common_package}" in data):
                        data = f"import {common_package}\n{data}"
                        changes = True
            if changes:
                with open(f"{self.output_dir_code}/{subprogram}", "w") as f:
                    f.write(data)
        return changes
    
    def __load_oas(self) -> dict:
        oas = load_yml_file(filepath=self.oas_location)
        oas = self.__update_sections(oas=oas, key="responses", remove_key=True)
        oas = self.__update_sections(oas=oas, key="application/xml", remove_key=True)
        oas = self.__update_sections(oas=oas, key="application/x-www-form-urlencoded", remove_key=True)
        oas = self.__update_sections(oas=oas, key="security", remove_key=True)
        oas = self.__update_sections(oas=oas, key="operationId", remove_key=True)
        oas = self.__update_sections(oas=oas, key="tags", remove_key=True)
        oas = self.__update_sections(oas=oas, key="$ref")
        return oas
    
    def __update_sections(self, oas, key, remove_key=False) -> dict:
        while True:
            path = self.__find_key_path(oas, key)
            if path is None:
                break
            oas = self.__update_nested_dict(
                            data=oas,
                            path=path,
                            new_value=None if remove_key else self.__get_value_by_path(oas, path)
                        )
        return oas

    def __update_nested_dict(self, data, path, new_value):
        # Referenz auf das aktuelle Level im Dictionary setzen
        current = data
        # Alle Schlüssel im Pfad durchgehen, bis auf den letzten
        for key in path[:-2]:
            # Gehe eine Ebene tiefer, falls der Schlüssel existiert
            current = current.get(key, {})
        # Setze den neuen Wert am letzten Schlüssel im Pfad
        if new_value is None:
            try:
                del current[path[-2]][path[-1]]
            except IndexError:
                del current[path[0]]
        else:
            current[path[-2]] = self.__get_value_by_path(data, new_value[2:].split('/'))
        return data

    def __get_value_by_path(self, data, path):
        current = data
        for key in path:
            current = current[key]
        return current

    def __find_key_path(self, data: dict, search_key: str, path: str=None) -> str:
        if path is None:
            path = []
        # Wenn data ein Dictionary ist, durchsuche die Keys
        if isinstance(data, dict):
            for key, value in data.items():
                # Erweitere den Pfad mit dem aktuellen Key
                new_path = path + [key]
                if key == search_key:
                    return new_path  # Pfad gefunden und zurückgegeben
                # Falls der Wert selbst ein Dictionary oder eine Liste ist, rufe find_key_path rekursiv auf
                result = self.__find_key_path(value, search_key, new_path)
                if result is not None:
                    return result
        # Wenn data eine Liste ist, durchsuche die einzelnen Elemente
        elif isinstance(data, list):
            for index, item in enumerate(data):
                # Indizes zur Pfadliste hinzufügen, um Positionen in Listen anzugeben
                new_path = path + [index]
                result = self.__find_key_path(item, search_key, new_path)
                if result is not None:
                    return result

        # Wenn der Key nicht gefunden wurde, gebe None zurück
        return None