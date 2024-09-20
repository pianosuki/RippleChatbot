from enum import Enum, auto


class Command(Enum):
    HELP = auto()
    HELLO = auto()
    BYE = auto()
    PREFERENCES = auto()
    DISCORD = auto()
    LAST = auto()
