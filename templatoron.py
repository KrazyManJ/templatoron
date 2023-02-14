import json
import os
import re
from os import PathLike

import jsonschema
from cryptography.fernet import Fernet

from tokens import FERNET_KEY

fernet = Fernet(FERNET_KEY)


def generate_templatoron_file_from_folder(
        folder: str | bytes | PathLike,
        output_projecter_file: str | bytes | PathLike,
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
            r[val] = folder_scan(pth) \
                if os.path.isdir(pth) \
                else fernet.encrypt(var_finder(open(pth, "r").read()).encode("utf-8")).decode("utf-8")
        return r

    STRUCTURE = {os.path.basename(folder): folder_scan(folder)} if include_folder else folder_scan(folder)
    json.dump({"variables": list(variables), "structure": STRUCTURE}, open(output_projecter_file, "w"), indent=4)


def create_files_from_templatoron_file(
        file: str | bytes | PathLike,
        output_path: str | bytes | PathLike,
        **variable_values
):
    def parse_json_func(d: dict):
        r = {}
        for k, v in d.items():
            r[k] = fernet.decrypt(v.encode("utf-8")).decode("utf-8") if type(v) == str else v
        return r

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
                open(fname, "w").write(var_parser(v))

    if not os.path.exists(file):
        raise FileNotFoundError(f"File \"{file}\" does not exist!")
    if not file.endswith(".json"):
        raise Exception("File is not templatoron file (.json)!")
    data: dict = json.load(open(file, "r"), object_hook=parse_json_func)
    verify_templatoron_json(data)
    srcvarset = set(data.get("variables", []))
    varset = set(variable_values.keys())
    if varset != srcvarset:
        raise Exception("Missing variables: " + ", ".join(srcvarset.difference(varset)))
    file_creator(output_path, data.get("structure", {}))


def verify_templatoron_json(data: dict):
    jsonschema.validate(data, json.load(open("templatoron_schema.json")))
