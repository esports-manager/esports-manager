from enum import Enum, auto


class LaneError(Exception):
    pass


class Lanes(Enum):
    TOP = 0
    JG = auto()
    MID = auto()
    ADC = auto()
    SUP = auto()
