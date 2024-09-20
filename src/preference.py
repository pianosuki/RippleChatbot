from enum import Enum


class Preference(Enum):
    AUTO_BEATCONNECT = 0, ["on", "off"]
    DM_LAST = 1, ["on", "off"]

    def __init__(self, id_: int, values: list):
        self.id = id_
        self._value_ = values
