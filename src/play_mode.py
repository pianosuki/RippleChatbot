from enum import Enum


class PlayMode(Enum):
    STANDARD = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3

    def get_name(self) -> str:
        return f"osu!{self.name.lower()}"
