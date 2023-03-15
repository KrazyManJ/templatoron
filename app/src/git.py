import subprocess
import os


def is_installed():
    try:
        result = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        result.stdout.decode()
    except Exception:
        return False
    return True


def already_init(dir_path):
    return os.path.exists(os.path.join(dir_path, '.git'))

def init(dir_path):
    if not is_installed():
        return
    if not already_init(dir_path):
        subprocess.run(['git', 'init'], cwd=dir_path, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
