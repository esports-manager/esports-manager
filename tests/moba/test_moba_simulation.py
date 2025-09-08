import random
from datetime import date

import pytest

from esm.models.moba.moba_match_simulation import MobaMatchSimulation
from esm.models.moba.moba_match_state import MobaMatchStatus
from esm.models.moba.team_simulation import MobaTeamSimulation
from esm.models.moba.player_simulation import MobaPlayerSimulation
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.champion import (
    MobaChampion,
    MobaChampionRole,
    MobaChampionType,
    MobaChampionDifficulty,
)
from esm.models.moba.team import MobaTeam
from esm.models.moba.events.event import MobaEventType, MobaJungleType
from esm.models.moba.moba_match_state import JUNGLE_OBJECTIVES
from esm.models.moba.events.jungle_event import MobaJungleEvent


def build_player(
    role: MobaPlayerRole, nick: str, farming: int = 50
) -> MobaPlayerSimulation:
    player = MobaPlayer(
        first_name=nick,
        last_name="Test",
        nick_name=nick,
        date_of_birth=date(2000, 1, 1),
        role=role,
        farming=farming,
    )
    # Champion that fits the role
    champ = MobaChampion(
        name=f"{role.value}_champ",
        release_date=date(2010, 1, 1),
        primary_role=MobaChampionRole[role.name],
        champion_type1=MobaChampionType.MAGE,
        difficulty=MobaChampionDifficulty.MEDIUM,
        strength=50,
    )
    return MobaPlayerSimulation(player=player, champion=champ)


def build_team_sim(team_name: str, farming: int = 50) -> MobaTeamSimulation:
    team = MobaTeam(name=team_name)
    players = [
        build_player(MobaPlayerRole.TOP, f"{team_name}_top", farming),
        build_player(MobaPlayerRole.JUNGLE, f"{team_name}_jg", farming),
        build_player(MobaPlayerRole.MID, f"{team_name}_mid", farming),
        build_player(MobaPlayerRole.ADC, f"{team_name}_adc", farming),
        build_player(MobaPlayerRole.SUPPORT, f"{team_name}_sup", farming),
    ]
    return MobaTeamSimulation(team=team, players=players)


def build_match(farming1: int = 50, farming2: int = 50) -> MobaMatchSimulation:
    t1 = build_team_sim("Alpha", farming1)
    t2 = build_team_sim("Beta", farming2)
    sim = MobaMatchSimulation(team1=t1, team2=t2)
    sim.state.update_jungle_objectives()
    return sim


def test_farming_and_death_timer_tick() -> None:
    sim = build_match()
    # Pre-2:00, no farming
    sim.state.time = 100
    p = sim.team1.players[3]  # ADC
    base_farm = p.farm
    sim._tick_after_event(60)
    assert p.farm == base_farm

    # Post-2:00, but dead -> no farm and timer decreases
    p.death_timer = 30
    sim.state.time = 180
    sim._tick_after_event(15)
    assert p.death_timer == 15
    assert p.farm == base_farm

    # Alive and farming applies: ADC base 10 cs/min, farming=50 -> 10 per 60s
    p.death_timer = 0
    sim._tick_after_event(60)
    assert p.farm == base_farm + 10


def test_fight_event_first_blood_and_death_timer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sim = build_match()
    # Use 1v1 to control randomness
    killer = build_player(MobaPlayerRole.MID, "Killer")
    victim = build_player(MobaPlayerRole.MID, "Victim")
    sim.team1.players = [killer]
    sim.team2.players = [victim]

    # Force team1 to be favored and time at 10:00 for death timer scaling
    sim.team1.state.win_probability = 1.0
    sim.team2.state.win_probability = 0.0
    sim.state.time = 600

    # Make fight deterministic: ensure kills happen and count is 1
    monkeypatch.setattr(random, "random", lambda: 0.0)
    monkeypatch.setattr(random, "randint", lambda a, b: 1)

    ev = sim._instantiate_event(MobaEventType.FIGHT_EVENT, None)
    sim._execute_event(ev)

    assert sim.state.first_blood is True
    # Death timer should scale: 10 + 2 * minutes (minutes=10) -> 30
    assert victim.death_timer >= 30
    # Commentary should include first blood and elimination lines
    joined = "\n".join(sim.commentary_log)
    assert "First Blood" in joined
    assert "eliminated" in joined


def test_jungle_event_herald_converts_tower(monkeypatch: pytest.MonkeyPatch) -> None:
    sim = build_match()
    # Ensure objectives are available by advancing time beyond first spawns
    sim.state.time = JUNGLE_OBJECTIVES[MobaJungleType.RIFT_HERALD]["first_spawn_at"]
    sim.state.update_jungle_objectives()
    herald = next(
        o for o in sim.state.jungle_objectives if o.type == MobaJungleType.RIFT_HERALD
    )
    herald.refresh(sim.state.time)

    # Make it deterministic
    monkeypatch.setattr(
        MobaJungleEvent,
        "get_team_to_win_objective",
        lambda self: (sim.team1, sim.team2, False),
    )

    before = sim.team2.towers_remaining

    ev = sim._instantiate_event(MobaEventType.JUNGLE_EVENT, MobaJungleType.RIFT_HERALD)
    sim._execute_event(ev)

    after = sim.team2.towers_remaining
    assert after == before - 1

    # Objective should be on cooldown
    herald = next(
        o for o in sim.state.jungle_objectives if o.type == MobaJungleType.RIFT_HERALD
    )
    assert herald.available is False
    assert herald.next_spawn_at > sim.state.time - ev.duration


def test_nexus_event_ends_match(monkeypatch: pytest.MonkeyPatch) -> None:
    sim = build_match()
    # Make nexus attack conditions true for team1 by zeroing enemy base towers and one inhibitor
    sim.team2.state.towers.base = 0
    sim.team2.state.inhibitors.top = 0

    # Ensure NEXUS is chosen when enabled
    def choose_nexus(candidates, weights=None, k=1):
        for c in candidates:
            if c[0] == MobaEventType.NEXUS_EVENT:
                return [c]
        return [candidates[0]]

    monkeypatch.setattr(random, "choices", choose_nexus)

    sim.run_until_end(max_steps=5)
    assert sim.state.status == MobaMatchStatus.ENDED
    assert sim.state.winner in (1, 2)
    assert any("wins" in line or "Nexus" in line for line in sim.commentary_log)
