import json
import os.path as path
from typing import Union, List, Dict, Callable

from app.src import systemsupport, pather, openvia

JsonType = Union[None, bool, int, float, str, List['JsonType'], Dict[str, 'JsonType']]


class ConfigurationInput:

    def __init__(self, name: str, typeDef: type | Union[type], default: JsonType,
                 pred: Callable[[JsonType], bool] = lambda x: True):
        self.name = name
        self.typeDef = typeDef
        self.default = default
        self.pred = pred

    def load(self, data: dict[str, JsonType]):
        val = data.get(self.name, self.default)
        if not isinstance(val, self.typeDef):
            return self.default
        if not self.pred(val):
            return self.default
        return val


CONFIGURATION = [
    ConfigurationInput("output_path", str, systemsupport.desktop_path(), lambda x: path.exists(x) and path.isdir(x)),
    ConfigurationInput("default_var_values", dict, {}),
    ConfigurationInput("close_app", bool, False),
    ConfigurationInput("init_git", bool, False),
    ConfigurationInput("open_via", str, "Nothing", lambda x: x in [name for name, icon, pred in openvia.CHECK_DATA if pred])
]


def load():
    R = {}
    data: dict = json.load(open(pather.CONFIG_FILE, "r"))
    for line in CONFIGURATION:
        R[line.name] = line.load(data)
    return R


def save(data: dict):
    json.dump(data, open(pather.CONFIG_FILE, "w"),sort_keys=True,indent=4)
