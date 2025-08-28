from typing import Optional
from esm.models.moba.events.event import MobaEventBase, MobaEventType, MobaJungleType
from esm.models.moba.events.nothing_event import MobaNothingEvent
from esm.models.moba.events.fight_event import MobaFightEvent
from esm.models.moba.events.jungle_event import MobaJungleEvent
from esm.models.moba.events.tower_event import MobaTowerEvent
from esm.models.moba.events.inhibitor_event import MobaInhibitorEvent
from esm.models.moba.events.nexus_event import MobaNexusEvent

EVENT_MAP = {
    MobaEventType.NOTHING_EVENT: MobaNothingEvent,
    MobaEventType.FIGHT_EVENT: MobaFightEvent,
    MobaEventType.JUNGLE_EVENT: MobaJungleEvent,
    MobaEventType.TOWER_EVENT: MobaTowerEvent,
    MobaEventType.INHIBITOR_EVENT: MobaInhibitorEvent,
    MobaEventType.NEXUS_EVENT: MobaNexusEvent,
}


def get_event_from_type(
    event_type: MobaEventType, jungle_type: Optional[MobaJungleType] = None
) -> MobaEventBase:
    event_class = EVENT_MAP.get(event_type)
    if not event_class:
        raise ValueError(f"Unknown event type: {event_type}")

    if event_class == MobaJungleEvent:
        return event_class(jungle_type=jungle_type)

    return event_class()
