import os


def desktop_path():
    if os.name == "nt":
        return os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    return os.path.expanduser("~/Desktop")

def terminal_command(command):
    if os.name == "nt":
        return f'cmd.exe /c {command}'
    else:
        return f'/bin/sh -c gnome-terminal -- bash -c "{command}"'

def open_terminal_command_build(commands: list[str]):
    if os.name == "nt":
        return f"cmd.exe /c start /wait cmd /c {' & '.join(commands)}"
    else:
        return f'/bin/sh -c gnome-terminal --wait -- bash -c "{";".join(commands)}"'