from typing import Any


class Logger:
    def __init__(self, name: str):
        self.name = name

    def log(self, data: Any):
        print(f"[{self.name}] {str(data).rstrip()}\n")
