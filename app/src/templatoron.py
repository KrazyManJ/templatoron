import json
import os
import re
from enum import Enum
from os import PathLike

import jsonschema
from cryptography.fernet import Fernet

from tokens import FERNET_KEY

FERNET = Fernet(FERNET_KEY)
EXT = ".json"
ENC = "latin-1"
VAR_PREFIX = "@#"
ILLEGAL_CHARS = '[^\\\\/:*?"<>|]*'

SCHEMA_PATH = os.path.join(__file__, os.path.pardir, "templatoron_schema.json")


def parse_variable_values(txt: str, variable_values: dict[str,str]):
    for k, v in variable_values.items():
        txt = txt.replace(f"{VAR_PREFIX}{k}", v)
    return txt

class TemplatoronResponse(Enum):
    OK = 0
    ALREADY_EXIST = 1
    ACCESS_DENIED = 2
    VARIABLES_MISSING = 3

class TemplatoronObject:
    name: str = "Unnamed"
    structure: dict = {}
    variables: list[dict[str,str]] = []
    icon: str = ""

    @staticmethod
    def __sort_dict(data):
        def custom_sort(key):
            value = data[key]
            if isinstance(value, dict):
                return 0
            else:
                return 1
        sorted_keys = sorted(data.keys(), key=custom_sort)
        sorted_dict = {}
        for key in sorted_keys:
            value = data[key]
            if isinstance(value, dict):
                sorted_dict[key] = TemplatoronObject.__sort_dict(value)
            else:
                sorted_dict[key] = value

        return sorted_dict

    @staticmethod
    def is_valid_file(
            path: str | bytes | PathLike
    ):
        if not os.path.exists(path):
            return False
        if not os.path.isfile(path):
            return False
        if not path.endswith(EXT):
            return False
        try:
            jsonschema.validate(json.load(open(path,encoding=ENC)), json.load(open(SCHEMA_PATH,encoding=ENC)))
        except:
            return False
        return True

    @staticmethod
    def from_file(
            path: str | bytes | PathLike
    ):
        if not TemplatoronObject.is_valid_file(path):
            raise Exception("Is not Templatoron file!")

        def decypt(d: dict):
            if set(d.keys()) == {'displayname', 'id'} or set(d.keys()) == {'name','icon','structure','variables'}: return d
            r = {}
            for k, v in d.items():
                r[k] = FERNET.decrypt(v.encode(ENC)).decode(ENC) if type(v) == str else v
            return r

        R = TemplatoronObject()
        data: dict = json.load(open(path, "r", encoding=ENC), object_hook=decypt)
        R.name = data.get("name","Unnamed")
        R.icon = data.get("icon","")
        R.structure = data.get("structure", {})
        R.variables = data.get("variables", [])
        return R

    @staticmethod
    def from_scaning_folder(
            folder: str | bytes | PathLike,
            include_folder: bool = True
    ):
        variables = set({})

        def var_finder(txt: str):
            for r in re.findall(f"(?<={VAR_PREFIX})[a-z_A-Z]+", txt):
                variables.add(r)
            return txt

        def folder_scan(parent):
            r = {}
            for i, val in enumerate(os.listdir(parent)):
                pth = var_finder(os.path.join(parent, val))
                r[val] = folder_scan(pth) if os.path.isdir(pth) else var_finder(open(pth, "r", encoding=ENC).read())
            return r



        R = TemplatoronObject()
        R.structure = TemplatoronObject.__sort_dict({os.path.basename(folder): folder_scan(folder)})
        R.variables = [{"id":a,"displayname":a} for a in variables]
        return R

    def save(
            self,
            path: str | bytes | PathLike
    ):
        def encrypt(data):
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = FERNET.encrypt(v.encode(ENC)).decode(ENC)
                elif isinstance(v, dict):
                    encrypt(v)
            return data

        RESULT = {
            "name": self.name,
            "icon": self.icon,
            "variables": self.variables,
            "structure": TemplatoronObject.__sort_dict(encrypt(self.structure))
        }
        print(TemplatoronObject.__sort_dict(self.structure))
        json.dump(RESULT, open(path if path.endswith(EXT) else path + EXT, "w", encoding=ENC), indent=4, sort_keys=False)

    def create_project(
            self,
            output_path: str | bytes | PathLike,
            **variable_values: str
    ) -> TemplatoronResponse:
        def file_creator(parent, file_or_folder_dict: dict):
            for k, v in file_or_folder_dict.items():
                fname = os.path.join(parent, parse_variable_values(k, variable_values))
                if type(v) is dict:
                    os.mkdir(fname)
                    file_creator(fname, v)
                elif type(v) is str:
                    open(fname, "w", encoding=ENC).write(parse_variable_values(v, variable_values))

        srcvarset = set([a["id"] for a in self.variables])
        varset = set(variable_values.keys())
        if os.path.exists(os.path.join(output_path,parse_variable_values(list(self.structure.keys())[0],variable_values))):
            return TemplatoronResponse.ALREADY_EXIST
        if varset != srcvarset:
            return TemplatoronResponse.VARIABLES_MISSING
        try:
            os.makedirs(output_path,exist_ok=True)
            file_creator(output_path, self.structure)
        except PermissionError as e:
            return TemplatoronResponse.ACCESS_DENIED
        return TemplatoronResponse.OK

    def is_var_used_in_file_system(self,varid: str):
        if varid not in [i["id"] for i in self.variables]:
            return False
        def file_name_checker(data_dict: dict):
            for k, v in data_dict.items():
                if k.__contains__(VAR_PREFIX+varid):
                    return True
                if type(v) is dict:
                    if file_name_checker(v):
                        return True
            return False
        return file_name_checker(self.structure)