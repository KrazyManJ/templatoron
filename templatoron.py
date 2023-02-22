import json
import os
import re
from os import PathLike

import jsonschema
from cryptography.fernet import Fernet

from tokens import FERNET_KEY

FERNET = Fernet(FERNET_KEY)
EXT = ".json"
ENC = "latin-1"

SCHEMA_PATH = os.path.join(__file__,os.path.pardir,"templatoron_schema.json")

class TemplatoronObject:
    name: str = "Unnamed"
    structure: dict = {}
    variables: list[dict[str,str]] = []
    icon: str = ""

    @staticmethod
    def __sort_dict(d):
        if not isinstance(d, dict):
            return d
        sorted_items = sorted(d.items(), key=lambda x: isinstance(x[1], dict))
        return {k: TemplatoronObject.__sort_dict(v) for k, v in sorted_items}

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
            for r in re.findall("(?<=@#)[a-z_A-Z]+", txt):
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
            "structure": encrypt(TemplatoronObject.__sort_dict(self.structure))
        }
        json.dump(RESULT, open(path if path.endswith(EXT) else path + EXT, "w", encoding=ENC), indent=4)

    def create_project(
            self,
            output_path: str | bytes | PathLike,
            **variable_values: str
    ):
        def var_parser(txt: str):
            for k, v in variable_values.items():
                txt = txt.replace(f"@#{k}", v)
            return txt

        def file_creator(parent, file_or_folder_dict: dict):
            for k, v in file_or_folder_dict.items():
                fname = os.path.join(parent, var_parser(k))
                if type(v) is dict:
                    os.mkdir(fname)
                    file_creator(fname, v)
                elif type(v) is str:
                    open(fname, "w", encoding=ENC).write(var_parser(v))

        srcvarset = set([a["id"] for a in self.variables])
        varset = set(variable_values.keys())
        if varset != srcvarset:
            raise Exception("Missing variables: " + ", ".join(srcvarset.difference(varset)))
        file_creator(output_path, self.structure)
