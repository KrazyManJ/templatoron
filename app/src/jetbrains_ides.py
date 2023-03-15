import os
import subprocess
from dataclasses import dataclass
from enum import Enum

JETBRAINS_FOLDER = os.path.join(os.path.abspath(r"C:\\"), "Program Files", "JetBrains")


@dataclass
class IDE:
    name: str
    exe: str


class IDEs(Enum):
    PYCHARM = IDE("PyCharm", "pycharm64")
    INTELLIJ = IDE("IntelliJ IDEA", "idea64")
    PHPSTORM = IDE("PhpStorm", "phpstorm64")


def jetbrains_ide_path(ide: IDEs):
    ide_folder = os.path.join(JETBRAINS_FOLDER, [i for i in os.listdir(JETBRAINS_FOLDER) if ide.value.name in i][0])
    exe = os.path.join(ide_folder, "bin", f"{ide.value.exe}.exe")
    return exe


def open_file_in_ide(ide: IDEs, paths: list[str]):
    subprocess.Popen([jetbrains_ide_path(ide), ",".join(paths)],creationflags=subprocess.CREATE_NO_WINDOW)


def is_ide_installed(ide: IDEs):
    return os.path.exists(jetbrains_ide_path(ide))