import os.path
from datetime import datetime
from enum import Enum

LOG_FOLDER = "logs"


class LogType(Enum):
    INFO = " "
    WARN = " [WARN] "
    ERROR = " [ERROR] "


class FileLogger:
    logs: list[str]

    def __init__(self, name: str):
        self.logs = []
        self.date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.name = name

    def log(self, action: str, aType: LogType = LogType.INFO):
        self.logs.append(f'[{datetime.now().strftime("%H:%M:%S")}]{aType.value}{action}')

    def warn(self, action: str):
        self.log(action, LogType.WARN)

    def error(self, action: str):
        self.log(action, LogType.ERROR)

    def save(self):
        if not os.path.exists(LOG_FOLDER):
            os.mkdir(LOG_FOLDER)
        open(os.path.join(LOG_FOLDER, f'{self.date}_{self.name}.log'), "w").write("\n".join(self.logs))
