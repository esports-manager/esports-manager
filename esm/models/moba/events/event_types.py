import enum


class MobaEventType(str, enum.Enum):
    NOTHING_EVENT: str = "nothing"
    FIGHT_EVENT: str = "fight"
    JUNGLE_EVENT: str = "jungle event"
    TOWER_EVENT: str = "tower event"
    INHIBITOR_EVENT: str = "inhibitor event"
    NEXUS_EVENT: str = "nexus event"


class MobaJungleType(str, enum.Enum):
    DRAGON: str = "dragon"
    BARON: str = "baron"
    GRUB: str = "grub"
    RIFT_HERALD: str = "rift herald"
    ATAKHAN: str = "atakhan"
