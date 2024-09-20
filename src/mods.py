from enum import Enum

MOD_NAMES = {
    "-Easy": "EZ",
    "-NoFail": "NF",
    "-HalfTime": "HT",
    "-SpunOut": "SO",
    "+Hidden": "HD",
    "+SuddenDeath": "SD",
    "+Perfect": "PF",
    "+HardRock": "HR",
    "+DoubleTime": "DT",
    "+Nightcore": "NC",
    "+Flashlight": "FL",
    "~Relax~": "RX",
    "~Autopilot~": "AP",
    "|Autoplay|": "AT",
    "|Cinema|": "CM",
    "|1K|": "1K",
    "|2K|": "2K",
    "|3K|": "3K",
    "|4K|": "4K",
    "|5K|": "5K",
    "|6K|": "6K",
    "|7K|": "7K",
    "|8K|": "8K",
    "|9K|": "9K",
    "|10K|": "10K",
    "|12K|": "12K",
    "|14K|": "14K",
    "|16K|": "16K",
    "|18K|": "18K",
    "|20K|": "20K"
}


class ModBitwise(Enum):
    NF = 0
    EZ = 1
    HD = 3
    HR = 4
    SD = 5
    DT = 6
    RX = 7
    HT = 8
    NC = 9
    FL = 10
    SO = 12
    PF = 14
    FI = 20

    @classmethod
    def bitwise_to_list(cls, mods: int) -> list[str]:
        mod_list = []

        for name, member in cls.__members__.items():
            if mods & (1 << member.value):
                mod_list.append(name)

        return mod_list
