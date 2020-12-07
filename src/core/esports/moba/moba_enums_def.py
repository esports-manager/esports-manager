from enum import Enum, auto


class LaneError(Exception):
    pass


class MobaEventType(Enum):
    """
    Defines the types of events that can occur during a match
    """
    NOTHING = 0
    LANE_FARM = auto()
    GANK = auto()
    LANE_FIGHT = auto()
    TEAM_FIGHT = auto()
    TOWER_ASSAULT = auto()
    JG_MAJOR = auto()
    INHIB_ASSAULT = auto()
    NEXUS_ASSAULT = auto()
    BACKDOOR = auto()


class Lanes(Enum):
    """
    Defines lanes that can be played during a MOBA match
    """
    TOP = auto()
    JG = auto()
    MID = auto()
    ADC = auto()
    SUP = auto()


class JungleMonsters(Enum):
    DRAGON = auto()
    BARON = auto()


class Towers(Enum):
    BLUE_FIRST_TOP_TOWER = auto()
    BLUE_SECOND_TOP_TOWER = auto()
    BLUE_THIRD_TOP_TOWER = auto()
    BLUE_FIRST_MID_TOWER = auto()
    BLUE_SECOND_MID_TOWER = auto()
    BLUE_THIRD_MID_TOWER = auto()
    BLUE_FIRST_BOT_TOWER = auto()
    BLUE_SECOND_BOT_TOWER = auto()
    BLUE_THIRD_BOT_TOWER = auto()
    BLUE_FIRST_NEXUS_TOWER = auto()
    BLUE_SECOND_NEXUS_TOWER = auto()
    RED_FIRST_TOP_TOWER = auto()
    RED_SECOND_TOP_TOWER = auto()
    RED_THIRD_TOP_TOWER = auto()
    RED_FIRST_MID_TOWER = auto()
    RED_SECOND_MID_TOWER = auto()
    RED_THIRD_MID_TOWER = auto()
    RED_FIRST_BOT_TOWER = auto()
    RED_SECOND_BOT_TOWER = auto()
    RED_THIRD_BOT_TOWER = auto()
    RED_FIRST_NEXUS_TOWER = auto()
    RED_SECOND_NEXUS_TOWER = auto()
