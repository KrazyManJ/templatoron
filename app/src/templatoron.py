import base64
import json
import os
import re
from enum import Enum
from os import PathLike

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
    structure: dict = {}
    variables: list[dict[str, str]] = []
    commands: list[str] = []
    icon: str = ""

    @staticmethod
    def __sort_dict(data):
        sorted_dict = {}
        for key in sorted(data.keys(), key=lambda k: 0 if isinstance(data[k], dict) else 1):
            value = data[key]
            sorted_dict[key] = TemplatoronObject.__sort_dict(value) if isinstance(value, dict) else value
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
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    def from_file(path: str | bytes | PathLike):
        if not TemplatoronObject.is_valid_file(path):
            raise Exception("Is not Templatoron file!")

        def structure_decode(d: dict):
            for k, v in d.items():
                if isinstance(v, dict):
                    d[k] = structure_decode(v)
                else:
                    d[k] = base64.b64decode(v.encode(ENC)).decode(ENC)
            return d

        R = TemplatoronObject()
        data: dict = json.load(open(path, "r", encoding=ENC))
        R.name = data.get("name", "Unnamed")
        R.icon = data.get("icon", "")
        R.structure = structure_decode(data.get("structure", {}))
        R.variables = data.get("variables", [])
        R.commands = data.get("commands", [])
        return R

    def scan(self, path, include_folder: bool = True, ignore_names: list = None):
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

        if os.path.isfile(path):
            self.structure = {os.path.basename(path): var_finder(open(path, "rb").read().decode(ENC))}
        else:
            self.structure = TemplatoronObject.__sort_dict(
                {os.path.basename(path): folder_scan(path)} if include_folder else folder_scan(path))
        self.variables = sorted([{"id": a, "displayname": a.replace("_", " ").capitalize()} for a in variables],
                                key=lambda v: v["id"])
        return self

    def save(self, path: str | bytes | PathLike):
        def encode(data):
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = base64.b64encode(v.encode(ENC)).decode(ENC)
                elif isinstance(v, dict):
                    encode(v)
            return data

        RESULT = {
            "name": self.name,
            "icon": self.icon,
            "variables": self.variables, "commands": self.commands,
            "structure": TemplatoronObject.__sort_dict(encode(self.structure))}
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

    def create_template_project(self, output_path: str | bytes | PathLike) -> TemplatoronResponse:
        def file_creator(parent, file_or_folder_dict: dict):
            for k, v in file_or_folder_dict.items():
                fname = os.path.join(parent, k)
                if type(v) is dict:
                    os.mkdir(fname)
                    file_creator(fname, v)
                elif type(v) is str:
                    open(fname, "wb").write(v.encode(ENC))

        for root_paths in self.structure.keys():
            if os.path.exists(os.path.join(output_path, root_paths)):
                return TemplatoronResponse.ALREADY_EXIST
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

    def command_path(self, output_path, **variable_values):
        if self.is_single_dir():
            return os.path.join(output_path, parse_variable_values(list(self.structure.keys())[0], variable_values))
        else:
            return output_path

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TemplatoronObject): return False

        for a1, a2 in [
            (self.structure, o.structure),
            (self.name, o.name),
            (self.variables, o.variables),
            (self.icon, o.icon),
            (self.commands, o.commands)
        ]:
            if a1 is not a2:
                print(a1, a2)
                return False
        return True

    def copy(self):
        copied_obj = TemplatoronObject()
        copied_obj.name = self.name
        copied_obj.structure = self.structure.copy()
        copied_obj.variables = self.variables.copy()
        copied_obj.commands = self.commands.copy()
        copied_obj.icon = self.icon
        return copied_obj