# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import random
from typing import Optional, Any
from enum import Enum


class EventSeverity(str, Enum):
    INFO = "info"
    OBJECTIVE = "objective"
    TOWER = "tower"
    INHIBITOR = "inhibitor"
    ACE = "ace"
    TEAMFIGHT = "teamfight"
    NEXUS = "nexus"
    MATCH_END = "match_end"
    HIGHLIGHT = "highlight"


NARRATION_TEMPLATES = {
    "kill": [
        "{killer} takes down {victim}!",
        "{killer} eliminates {victim}!",
        "{killer} secures the kill on {victim}!",
        "{victim} falls to {killer}!",
        "{killer} outplays {victim} for the kill!",
        "What a play by {killer} to take out {victim}!",
        "{killer} catches {victim} out of position!",
        "{victim} is eliminated by {killer}!",
    ],
    "first_blood": [
        "First Blood! {killer} from {team} eliminated {victim}!",
        "First Blood goes to {team}! {killer} eliminated {victim}!",
        "{killer} secures First Blood for {team} and eliminated {victim}!",
        "And there it is - First Blood! {killer} eliminated {victim}!",
        "First Blood: {killer} from {team} eliminated {victim}!",
    ],
    "double_kill": [
        "DOUBLE KILL for {killer}!",
        "{killer} picks up a double kill!",
        "Two down for {killer}!",
        "{killer} is on fire with a double kill!",
    ],
    "ace": [
        "ACE! {team} wipes out the entire enemy team!",
        "It's an ace for {team}! All five down!",
        "{team} achieves a full team wipe!",
        "Complete annihilation! {team} aces the fight!",
        "All five members down - {team} takes the ace!",
    ],
    "dragon": [
        "{team} secures the dragon!",
        "{team} takes control of the dragon pit!",
        "Dragon goes to {team}!",
        "{team} claims the dragon buff!",
        "That's {number} dragons for {team} now!",
        "{team} continues their dragon dominance!",
    ],
    "herald": [
        "{team} takes down the Rift Herald!",
        "Rift Herald secured by {team}!",
        "{team} claims the herald!",
        "The eye of the herald belongs to {team}!",
    ],
    "baron": [
        "BARON NASHOR! {team} secures the big objective!",
        "{team} takes down Baron Nashor!",
        "Baron buff goes to {team}!",
        "A huge Baron for {team}!",
        "{team} dominates the Baron pit!",
        "Game-changing Baron for {team}!",
    ],
    "grubs": [
        "{team} clears the void grubs!",
        "Void grubs secured by {team}!",
        "{team} takes the grubs!",
    ],
    "steal": [
        "STOLEN! {player} from {team} steals the objective!",
        "What a steal by {player}!",
        "{player} with the clutch steal!",
        "Incredible! {player} steals it away!",
        "{team} wasn't expecting that - {player} steals the objective!",
    ],
    "tower": [
        "{team} destroys a {lane} tower!",
        "Tower down! {team} takes the {lane} turret!",
        "{team} pushes down the {lane} tower!",
        "Another tower falls - {team} takes {lane}!",
        "{team} secures the {lane} tower!",
    ],
    "first_tower": [
        "FIRST TOWER! {team} claims first tower gold!",
        "{team} takes down the first tower of the game!",
        "First tower goes to {team}!",
    ],
    "inhibitor": [
        "{team} destroys the {lane} inhibitor!",
        "INHIBITOR DOWN! {team} takes {lane}!",
        "Huge push by {team} - {lane} inhibitor falls!",
        "{team} breaks through the {lane} inhibitor!",
        "The {lane} base is exposed - inhibitor down to {team}!",
    ],
    "nexus_tower": [
        "{team} destroys a nexus tower!",
        "Base tower down for {team}!",
        "{team} is at the doorstep - nexus tower falls!",
    ],
    "nexus": [
        "NEXUS DESTROYED! {team} wins the game!",
        "Victory for {team}! The Nexus falls!",
        "{team} wins as the Nexus falls!",
        "It's over! {team} wins the game!",
        "GG! {team} wins!",
        "{team} wins and secures the Nexus!",
    ],
    "nothing": [
        "Teams continue to farm and position...",
        "A quiet moment as both teams set up vision...",
        "Both teams playing it safe for now...",
        "The map is relatively calm...",
        "Teams are taking their time to scale...",
        "Farming patterns continue across the map...",
    ],
    "skirmish": [
        "A small skirmish breaks out!",
        "Trading blows in the {lane}!",
        "Some tension building here...",
        "Players testing each other's limits...",
        "{team} looks to make a play!",
    ],
    "teamfight": [
        "TEAMFIGHT! Both teams engage!",
        "It's a full 5v5!",
        "Everyone's here - massive teamfight!",
        "The fight we've been waiting for!",
        "Both teams fully committed!",
    ],
}


def get_player_name(player: Any) -> str:
    """Extract player nickname or fallback to full name."""
    if hasattr(player, "nick_name") and player.nick_name:
        return player.nick_name
    if hasattr(player, "player"):
        p = player.player
        if hasattr(p, "nick_name") and p.nick_name:
            return p.nick_name
        if hasattr(p, "first_name") and hasattr(p, "last_name"):
            return f"{p.first_name} {p.last_name}"
    return "Unknown Player"


def get_team_name(team: Any) -> str:
    """Extract team name."""
    if hasattr(team, "name"):
        return team.name
    if hasattr(team, "team") and hasattr(team.team, "name"):
        return team.team.name
    return "Unknown Team"


def narrate_kill(
    killer: Any,
    victim: Any,
    killer_team: Any,
    is_first_blood: bool = False,
    is_double: bool = False,
) -> tuple[str, EventSeverity]:
    """Generate narration for a kill."""
    if is_first_blood:
        template = random.choice(NARRATION_TEMPLATES["first_blood"])
        text = template.format(
            killer=get_player_name(killer),
            victim=get_player_name(victim),
            team=get_team_name(killer_team),
        )
        return text, EventSeverity.HIGHLIGHT

    if is_double:
        template = random.choice(NARRATION_TEMPLATES["double_kill"])
        text = template.format(killer=get_player_name(killer))
        return text, EventSeverity.HIGHLIGHT

    template = random.choice(NARRATION_TEMPLATES["kill"])
    text = template.format(
        killer=get_player_name(killer),
        victim=get_player_name(victim),
    )
    return text, EventSeverity.INFO


def narrate_ace(team: Any) -> tuple[str, EventSeverity]:
    """Generate narration for an ace."""
    template = random.choice(NARRATION_TEMPLATES["ace"])
    text = template.format(team=get_team_name(team))
    return text, EventSeverity.ACE


def narrate_objective(
    obj_type: str,
    team: Any,
    player: Optional[Any] = None,
    is_steal: bool = False,
    count: Optional[int] = None,
) -> tuple[str, EventSeverity]:
    """Generate narration for jungle objectives."""
    if is_steal and player:
        template = random.choice(NARRATION_TEMPLATES["steal"])
        text = template.format(
            player=get_player_name(player),
            team=get_team_name(team),
        )
        return text, EventSeverity.HIGHLIGHT

    templates = NARRATION_TEMPLATES.get(obj_type.lower(), [])
    if not templates:
        templates = ["{team} secures the objective!"]

    template = random.choice(templates)

    kwargs = {"team": get_team_name(team)}
    if count is not None:
        kwargs["number"] = count

    text = template.format(**kwargs)
    return text, EventSeverity.OBJECTIVE


def narrate_tower(
    team: Any,
    lane: str,
    is_first_tower: bool = False,
    is_nexus_tower: bool = False,
) -> tuple[str, EventSeverity]:
    """Generate narration for tower destruction."""
    if is_first_tower:
        template = random.choice(NARRATION_TEMPLATES["first_tower"])
        text = template.format(team=get_team_name(team))
        return text, EventSeverity.HIGHLIGHT

    if is_nexus_tower:
        template = random.choice(NARRATION_TEMPLATES["nexus_tower"])
        text = template.format(team=get_team_name(team))
        return text, EventSeverity.TOWER

    template = random.choice(NARRATION_TEMPLATES["tower"])
    text = template.format(team=get_team_name(team), lane=lane)
    return text, EventSeverity.TOWER


def narrate_inhibitor(team: Any, lane: str) -> tuple[str, EventSeverity]:
    """Generate narration for inhibitor destruction."""
    template = random.choice(NARRATION_TEMPLATES["inhibitor"])
    text = template.format(team=get_team_name(team), lane=lane)
    return text, EventSeverity.INHIBITOR


def narrate_nexus(team: Any) -> tuple[str, EventSeverity]:
    """Generate narration for nexus destruction (game end)."""
    template = random.choice(NARRATION_TEMPLATES["nexus"])
    text = template.format(team=get_team_name(team))
    return text, EventSeverity.MATCH_END


def narrate_nothing() -> tuple[str, EventSeverity]:
    """Generate narration for quiet moments."""
    template = random.choice(NARRATION_TEMPLATES["nothing"])
    return template, EventSeverity.INFO


def narrate_skirmish(
    team: Optional[Any] = None, lane: Optional[str] = None
) -> tuple[str, EventSeverity]:
    """Generate narration for small skirmishes."""
    template = random.choice(NARRATION_TEMPLATES["skirmish"])
    kwargs = {}
    if team:
        kwargs["team"] = get_team_name(team)
    if lane:
        kwargs["lane"] = lane
    text = template.format(**kwargs) if kwargs else template
    return text, EventSeverity.INFO


def narrate_teamfight() -> tuple[str, EventSeverity]:
    """Generate narration for major teamfights."""
    template = random.choice(NARRATION_TEMPLATES["teamfight"])
    return template, EventSeverity.TEAMFIGHT
