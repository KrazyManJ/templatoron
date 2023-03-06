import pyvscode
from showinfm import show_in_file_manager

from app.src.jetbrains_ides import is_ide_installed, IDEs, open_file_in_ide

CHECK_DATA = [
    ("Nothing", "nothing", lambda: True), ("File Explorer", "file_explorer", lambda: True),
    ("Visual Studio Code", "vscode", lambda: pyvscode.is_present()),
    ("PyCharm", "pycharm", lambda: is_ide_installed(IDEs.PYCHARM)),
    ("PhpStorm", "phpstorm", lambda: is_ide_installed(IDEs.PHPSTORM)),
    ("IntelliJ IDEA", "idea", lambda: is_ide_installed(IDEs.INTELLIJ))
]

OPEN_DATA = {
    "File Explorer": lambda output, singleFolder, allFiles: show_in_file_manager(allFiles, False),
    "Visual Studio Code": lambda output, singleFolder, allFiles: pyvscode.open_folder(
        *([output, allFiles] if len(allFiles) > 1 else [singleFolder])),
    "PyCharm": lambda output, singleFolder, allFiles: open_file_in_ide(IDEs.PYCHARM, allFiles),
    "IntelliJ IDEA": lambda output, singleFolder, allFiles: open_file_in_ide(IDEs.INTELLIJ, allFiles),
    "PhpStorm": lambda output, singleFolder, allFiles: open_file_in_ide(IDEs.PHPSTORM, allFiles)
}
