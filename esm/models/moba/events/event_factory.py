from typing import Optional
from esm.models.moba.events.event import MobaEventBase, MobaEventType, MobaJungleType
from esm.models.moba.events.nothing_event import MobaNothingEvent
from esm.models.moba.events.fight_event import MobaFightEvent
from esm.models.moba.events.jungle_event import MobaJungleEvent
from esm.models.moba.events.tower_event import MobaTowerEvent
from esm.models.moba.events.inhibitor_event import MobaInhibitorEvent
from esm.models.moba.events.nexus_event import MobaNexusEvent

EVENT_MAP = {
    MobaEventType.NOTHING_EVENT: {
        "type": MobaNothingEvent,
        "points": 0,
    },
    MobaEventType.FIGHT_EVENT: {
        "type": MobaFightEvent,
        "points": 10,
    },
    MobaEventType.JUNGLE_EVENT: {
        "type": MobaJungleEvent,
        "points": 15,
    },
    MobaEventType.TOWER_EVENT: {
        "type": MobaTowerEvent,
        "points": 10,
    },
    MobaEventType.INHIBITOR_EVENT: {
        "type": MobaInhibitorEvent,
        "points": 12,
    },
    MobaEventType.NEXUS_EVENT: {
        "type": MobaNexusEvent,
        "points": 0,
    },
}


def get_event_from_type(
    event_type: MobaEventType, jungle_type: Optional[MobaJungleType] = None
) -> MobaEventBase:
    event_class = EVENT_MAP.get(event_type).get("type")
    if not event_class:
        raise ValueError(f"Unknown event type: {event_type}")

    if event_class == MobaJungleEvent:
        return event_class(
            jungle_type=jungle_type, points=EVENT_MAP[event_type]["points"]
        )

    return event_class(points=EVENT_MAP[event_type]["points"])
