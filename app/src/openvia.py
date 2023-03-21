import pyvscode
from showinfm import show_in_file_manager

import pyjetbrains
from pyjetbrains import IDE

CHECK_DATA = [
    ("Nothing", "nothing", lambda: True), ("File Explorer", "file_explorer", lambda: True),
    ("Visual Studio Code", "vscode", lambda: pyvscode.is_present()),
    ("PyCharm", "pycharm", lambda: pyjetbrains.is_installed(IDE.PYCHARM)),
    ("PhpStorm", "phpstorm", lambda: pyjetbrains.is_installed(IDE.PHPSTORM)),
    ("IntelliJ IDEA", "idea", lambda: pyjetbrains.is_installed(IDE.INTELLIJ_IDEA))
]

OPEN_DATA = {
    "File Explorer": lambda output, singleFolder, allFiles: show_in_file_manager(allFiles, False),
    "Visual Studio Code": lambda output, singleFolder, allFiles: pyvscode.open_folder(
        *([output, allFiles] if len(allFiles) > 1 else [singleFolder])),
    "PyCharm": lambda _, __, allFiles: pyjetbrains.open(IDE.PYCHARM, *allFiles),
    "IntelliJ IDEA": lambda _, __, allFiles: pyjetbrains.open(IDE.INTELLIJ_IDEA, *allFiles),
    "PhpStorm": lambda _, __, allFiles: pyjetbrains.open(IDE.PHPSTORM, *allFiles)
}
