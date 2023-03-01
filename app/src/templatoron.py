import base64
import json
import os
import re
from enum import Enum
from os import PathLike
from pathlib import Path

import jsonschema

EXT = ".json"
ENC = "latin-1"
VAR_PREFIX = "@#"
VAR_SUFFIX = "#@"
ILLEGAL_CHARS = '[^\\\\/:*?"<>|]*'

SCHEMA_PATH = os.path.join(__file__, os.path.pardir, "templatoron_schema.json")


def parse_variable_values(txt: str, variable_values: dict[str, str]):
    for k, v in variable_values.items():
        txt = txt.replace(f"{VAR_PREFIX}{k}{VAR_SUFFIX}", v)
    return txt


class TemplatoronResponse(Enum):
    OK = 0
    ALREADY_EXIST = 1
    ACCESS_DENIED = 2
    VARIABLES_MISSING = 3


class TemplatoronObject:
    name: str = "Unnamed"
    filename: str = "unnamed"
    structure: dict = {}
    variables: list[dict[str, str]] = []
    commands: list[str] = []
    icon: str = ""

    @staticmethod
    def __sort_dict(data):
        def custom_sort(k):
            v = data[k]
            if isinstance(v, dict):
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
    def is_valid_file(path: str | bytes | PathLike):
        if not os.path.exists(path):
            return False
        if not os.path.isfile(path):
            return False
        if not path.endswith(EXT):
            return False
        try:
            jsonschema.validate(json.load(open(path, encoding=ENC)), json.load(open(SCHEMA_PATH, encoding=ENC)))
        except:
            return False
        return True

    @staticmethod
    def from_file(path: str | bytes | PathLike):
        if not TemplatoronObject.is_valid_file(path):
            raise Exception("Is not Templatoron file!")

        def decypt(d: dict):
            if set(d.keys()) == {'displayname', 'id'} or set(d.keys()) == {'name', 'icon', 'structure', 'variables',
                                                                           'commands'}: return d
            r = {}
            for k, v in d.items():
                r[k] = base64.b64decode(v.encode(ENC)).decode(ENC) if type(v) == str else v
            return r

        R = TemplatoronObject()
        data: dict = json.load(open(path, "r", encoding=ENC), object_hook=decypt)
        R.name = data.get("name", "Unnamed")
        R.filename = Path(path).stem
        R.icon = data.get("icon", "")
        R.structure = data.get("structure", {})
        R.variables = data.get("variables", [])
        R.commands = data.get("commands", [])
        return R

    @staticmethod
    def from_scaning_folder_or_file(path: str | bytes | PathLike, include_folder: bool = True,
                                    ignore_names: list[str | bytes | PathLike] | None = None):
        variables = set({})
        if ignore_names is None:
            ignore_names = []

        def var_finder(txt: str):
            for r in re.findall(f"(?<={VAR_PREFIX})[a-z_A-Z]+(?={VAR_SUFFIX})", txt):
                variables.add(r)
            return txt

        def folder_scan(parent):
            r = {}
            for i, val in enumerate([p for p in os.listdir(parent) if p not in ignore_names]):
                pth = var_finder(os.path.join(parent, val))
                r[val] = folder_scan(pth) if os.path.isdir(pth) else var_finder(open(pth, "rb").read().decode(ENC))
            return r

        def is_file_only(data_dict: dict):
            return len([v for v in data_dict.values() if isinstance(v, str)]) == 0

        R = TemplatoronObject()
        if os.path.isfile(path):
            R.structure = {os.path.basename(path): var_finder(open(path, "rb").read().decode(ENC))}
        else:
            R.structure = TemplatoronObject.__sort_dict(
                {os.path.basename(path): folder_scan(path)} if include_folder else folder_scan(path))
        R.variables = sorted([{"id": a, "displayname": a.replace("_", " ").capitalize()} for a in variables],
                             key=lambda v: v["id"])
        return R

    def save(self, path: str | bytes | PathLike):
        def encrypt(data):
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = base64.b64encode(v.encode(ENC)).decode(ENC)
                elif isinstance(v, dict):
                    encrypt(v)
            return data

        RESULT = {"name": self.name, "icon": self.icon, "variables": self.variables, "commands": self.commands,
            "structure": TemplatoronObject.__sort_dict(encrypt(self.structure))}
        json.dump(RESULT, open(path if path.endswith(EXT) else path + EXT, "w", encoding=ENC), indent=4,
                  sort_keys=False)

    def create_project(self, output_path: str | bytes | PathLike, **variable_values: str) -> TemplatoronResponse:
        def file_creator(parent, file_or_folder_dict: dict):
            for k, v in file_or_folder_dict.items():
                fname = os.path.join(parent, parse_variable_values(k, variable_values))
                if type(v) is dict:
                    os.mkdir(fname)
                    file_creator(fname, v)
                elif type(v) is str:
                    open(fname, "wb").write(parse_variable_values(v, variable_values).encode(ENC))

        srcvarset = set([a["id"] for a in self.variables])
        varset = set(variable_values.keys())
        for root_paths in self.structure.keys():
            if os.path.exists(os.path.join(output_path, parse_variable_values(root_paths, variable_values))):
                return TemplatoronResponse.ALREADY_EXIST
        if varset != srcvarset:
            return TemplatoronResponse.VARIABLES_MISSING
        try:
            os.makedirs(output_path, exist_ok=True)
            file_creator(output_path, self.structure)
        except PermissionError:
            return TemplatoronResponse.ACCESS_DENIED
        return TemplatoronResponse.OK

    def is_single_dir(self):
        return len(self.structure.keys()) == 1 and isinstance(list(self.structure.values())[0], dict)

    def is_var_used_in_file_system(self, varid: str):
        if varid not in [i["id"] for i in self.variables]:
            return False

        def file_name_checker(data_dict: dict):
            for k, v in data_dict.items():
                if k.__contains__(VAR_PREFIX + varid + VAR_SUFFIX):
                    return True
                if type(v) is dict:
                    if file_name_checker(v):
                        return True
            return False

        return file_name_checker(self.structure)

    def command_path(self,output_path,**variable_values):
        if self.is_single_dir():
            return os.path.join(output_path, parse_variable_values(list(self.structure.keys())[0], variable_values))
        else:
            return output_path
