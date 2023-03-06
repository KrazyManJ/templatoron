import os
import os.path as path

ROOT = os.getcwd()
APP = path.join(__file__, path.pardir, path.pardir)

CONFIG_FILE = path.join(ROOT, "configuration.json")
TEMPLATES_FOLDER = path.join(ROOT, "templates")
FONTS_FOLDER = path.join(APP, "fonts")


def design_file(fileName: str) -> str: return os.path.join(APP, "design", fileName)


def listdirfullpath(pth: str) -> list[str]: return [path.join(pth, p) for p in os.listdir(pth)]


def initFilesOrFolders():
    os.makedirs(TEMPLATES_FOLDER, exist_ok=True)
    if not path.exists(CONFIG_FILE): open(CONFIG_FILE,"w").write("{}")



initFilesOrFolders()
