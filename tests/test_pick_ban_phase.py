#      eSports Manager - A free and open source eSports management simulation game
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
import pytest
from datetime import datetime, date
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from esm.models.pick_ban_phase import (
    PickBanPhase,
    PickBanMode,
    PickBanState,
    PickBanAction,
)
from esm.models.match import Match, MatchType, MatchFormat, MatchStatus
from esm.models.moba_team import MobaTeam
from esm.models.moba_player import PlayerRole
from esm.models.champion import Champion


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a SQLite in-memory database engine for testing."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a new database session for testing."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="teams")
def teams_fixture(session):
    """Create two test teams."""
    team1 = MobaTeam(
        name="Blue Team",
        short_name="BLU",
        region="EU",
        founding_date=date(2020, 1, 1),
    )
    team2 = MobaTeam(
        name="Red Team",
        short_name="RED",
        region="NA",
        founding_date=date(2020, 1, 1),
    )
    session.add(team1)
    session.add(team2)
    session.commit()
    return {"blue": team1, "red": team2}


@pytest.fixture(name="champions")
def champions_fixture(session):
    """Create test champions for each role."""
    champions = []

    # Create multiple champions for each role
    for i, role in enumerate(
        [
            PlayerRole.TOP,
            PlayerRole.JUNGLE,
            PlayerRole.MID,
            PlayerRole.ADC,
            PlayerRole.SUPPORT,
        ]
    ):
        # Create 5 champions per role for testing options (need at least 20 for all tests)
        for j in range(1, 6):
            champ = Champion(
                name=f"{role.value.capitalize()} Champion {j}",
                title=f"The {role.value.capitalize()} {j}",
                primary_role=role,
                difficulty=5 + j,  # Varying difficulties
                release_date=date(2020, 1, 1),
            )
            champions.append(champ)
            session.add(champ)

    session.commit()
    return champions


@pytest.fixture(name="match")
def match_fixture(session, teams):
    """Create a test match."""
    match = Match(
        home_team_id=teams["blue"].id,
        away_team_id=teams["red"].id,
        scheduled_date=datetime.now(),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        status=MatchStatus.SCHEDULED,
    )
    session.add(match)
    session.commit()
    return match


@pytest.fixture(name="pick_ban_phase")
def pick_ban_phase_fixture(session, match, teams):
    """Create a test pick/ban phase."""
    pick_ban = PickBanPhase(
        match_id=match.id,
        map_number=1,
        blue_side_team_id=teams["blue"].id,
        red_side_team_id=teams["red"].id,
    )
    session.add(pick_ban)
    session.commit()
    return pick_ban


def test_pick_ban_phase_creation(pick_ban_phase):
    """Test creating a pick/ban phase."""
    assert pick_ban_phase.id is not None
    assert pick_ban_phase.state == PickBanState.NOT_STARTED
    assert pick_ban_phase.mode == PickBanMode.USER_PARTICIPATES
    assert pick_ban_phase.start_time is None
    assert pick_ban_phase.end_time is None


def test_pick_ban_data_initialization(pick_ban_phase):
    """Test initializing pick/ban data."""
    data = pick_ban_phase.get_pick_ban_data()

    assert "blue_picks" in data
    assert "blue_bans" in data
    assert "red_picks" in data
    assert "red_bans" in data
    assert "blue_role_assignments" in data
    assert "red_role_assignments" in data

    # Lists should be empty initially
    assert len(data["blue_picks"]) == 0
    assert len(data["blue_bans"]) == 0
    assert len(data["red_picks"]) == 0
    assert len(data["red_bans"]) == 0


def test_start_pick_ban_phase_user_participates(pick_ban_phase, teams):
    """Test starting pick/ban phase with user participation."""
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams["blue"].id, mode=PickBanMode.USER_PARTICIPATES
    )

    assert pick_ban_phase.state == PickBanState.BAN_PHASE_1
    assert pick_ban_phase.mode == PickBanMode.USER_PARTICIPATES
    assert pick_ban_phase.user_team_id == teams["blue"].id
    assert pick_ban_phase.start_time is not None

    data = pick_ban_phase.get_pick_ban_data()
    assert data["current_action"] == "ban"
    assert data["current_team"] == "blue"


def test_start_pick_ban_phase_user_delegates(pick_ban_phase):
    """Test starting pick/ban phase with user delegation."""
    pick_ban_phase.start_pick_ban_phase(mode=PickBanMode.USER_DELEGATES)

    assert pick_ban_phase.state == PickBanState.BAN_PHASE_1
    assert pick_ban_phase.mode == PickBanMode.USER_DELEGATES
    assert pick_ban_phase.user_team_id is None
    assert pick_ban_phase.start_time is not None


def test_get_available_champions(session, pick_ban_phase, champions):
    """Test getting available champions for selection."""
    pick_ban_phase.start_pick_ban_phase()

    # Initially all champions should be available
    available = pick_ban_phase.get_available_champions(
        session, pick_ban_phase.blue_side_team_id, PickBanAction.BAN
    )
    assert len(available) == len(champions)

    # Ban a champion
    data = pick_ban_phase.get_pick_ban_data()
    data["blue_bans"].append(champions[0].id)
    pick_ban_phase.set_pick_ban_data(data)

    # Now one less champion should be available
    available = pick_ban_phase.get_available_champions(
        session, pick_ban_phase.blue_side_team_id, PickBanAction.BAN
    )
    assert len(available) == len(champions) - 1
    assert champions[0].id not in [champ["id"] for champ in available]


def test_make_selection_ban(pick_ban_phase, champions):
    """Test making a ban selection."""
    pick_ban_phase.start_pick_ban_phase()

    # Make a ban selection
    result = pick_ban_phase.make_selection(champions[0].id)
    assert result is True

    data = pick_ban_phase.get_pick_ban_data()
    assert champions[0].id in data["blue_bans"]
    assert data["current_team"] == "red"  # Should have switched to red team
    assert data["current_action"] == "ban"  # Still in ban phase


def test_make_selection_pick(pick_ban_phase, champions):
    """Test making a pick selection with role."""
    pick_ban_phase.start_pick_ban_phase()

    # Skip to pick phase (simple approach for testing)
    pick_ban_phase.state = PickBanState.PICK_PHASE_1
    data = pick_ban_phase.get_pick_ban_data()
    data["current_action"] = "pick"
    pick_ban_phase.set_pick_ban_data(data)

    # Make a pick selection with role
    result = pick_ban_phase.make_selection(champions[0].id, "top")
    assert result is True

    data = pick_ban_phase.get_pick_ban_data()
    assert champions[0].id in data["blue_picks"]
    assert data["blue_role_assignments"][str(champions[0].id)] == "top"


def test_switch_champion(pick_ban_phase, champions):
    """Test switching a champion."""
    pick_ban_phase.start_pick_ban_phase()

    # Skip to pick phase and make a selection
    pick_ban_phase.state = PickBanState.PICK_PHASE_1
    data = pick_ban_phase.get_pick_ban_data()
    data["current_action"] = "pick"
    data["blue_picks"].append(champions[0].id)
    data["blue_role_assignments"][str(champions[0].id)] = "top"
    pick_ban_phase.set_pick_ban_data(data)

    # Switch the champion
    result = pick_ban_phase.switch_champion(champions[0].id, champions[1].id, "top")
    assert result is True

    data = pick_ban_phase.get_pick_ban_data()
    assert champions[0].id not in data["blue_picks"]
    assert champions[1].id in data["blue_picks"]
    assert data["blue_role_assignments"][str(champions[1].id)] == "top"
    assert str(champions[0].id) not in data["blue_role_assignments"]


def test_assign_role(pick_ban_phase, champions):
    """Test assigning a role to a champion."""
    pick_ban_phase.start_pick_ban_phase()

    # Skip to pick phase and make a selection
    pick_ban_phase.state = PickBanState.PICK_PHASE_1
    data = pick_ban_phase.get_pick_ban_data()
    data["current_action"] = "pick"
    data["blue_picks"].append(champions[0].id)
    pick_ban_phase.set_pick_ban_data(data)

    # Assign a role
    result = pick_ban_phase.assign_role(champions[0].id, "mid")
    assert result is True

    data = pick_ban_phase.get_pick_ban_data()
    assert data["blue_role_assignments"][str(champions[0].id)] == "mid"

    # Change the role
    result = pick_ban_phase.assign_role(champions[0].id, "top")
    assert result is True

    data = pick_ban_phase.get_pick_ban_data()
    assert data["blue_role_assignments"][str(champions[0].id)] == "top"


def test_get_next_action(pick_ban_phase, teams):
    """Test getting the next action in sequence."""
    pick_ban_phase.start_pick_ban_phase(user_team_id=teams["blue"].id)

    action = pick_ban_phase.get_next_action()
    assert action["team"] == "blue"
    assert action["action"] == "ban"
    assert action["state"] == PickBanState.BAN_PHASE_1.value
    assert action["user_turn"] is True  # It's user's turn as they are blue team


def test_ai_make_selection(session, pick_ban_phase, champions, teams):
    """Test AI making a selection."""
    pick_ban_phase.start_pick_ban_phase(user_team_id=teams["blue"].id)

    # Set current team to red (opponent) for AI to act
    data = pick_ban_phase.get_pick_ban_data()
    data["current_team"] = "red"
    pick_ban_phase.set_pick_ban_data(data)

    result = pick_ban_phase.ai_make_selection(session)
    assert "error" not in result
    assert result["action"] == "ban"
    assert result["team"] == "red"
    assert "champion_id" in result

    # Check that the AI made a ban
    data = pick_ban_phase.get_pick_ban_data()
    assert len(data["red_bans"]) == 1


def test_user_delegates_full_pick_ban(session, pick_ban_phase, champions):
    """Test full delegation of pick/ban phase to AI."""
    pick_ban_phase.start_pick_ban_phase(mode=PickBanMode.USER_DELEGATES)

    # Let AI complete the entire pick/ban phase
    while pick_ban_phase.state != PickBanState.COMPLETED:
        result = pick_ban_phase.ai_make_selection(session)
        if "error" in result:
            break

    # Check that the phase was completed
    data = pick_ban_phase.get_pick_ban_data()
    assert len(data["blue_picks"]) == 5
    assert len(data["red_picks"]) == 5
    assert len(data["blue_bans"]) == 5
    assert len(data["red_bans"]) == 5
    assert len(data["blue_role_assignments"]) == 5
    assert len(data["red_role_assignments"]) == 5

    # Verify roles were assigned properly
    all_roles = {"top", "jungle", "mid", "bot", "support"}
    blue_roles = set(data["blue_role_assignments"].values())
    red_roles = set(data["red_role_assignments"].values())

    assert blue_roles == all_roles
    assert red_roles == all_roles


def test_complete_pick_ban_phase(pick_ban_phase, champions):
    """Test completing the pick/ban phase manually."""
    pick_ban_phase.start_pick_ban_phase()

    # Set up data to simulate completed pick/ban
    data = pick_ban_phase.get_pick_ban_data()

    # Add picks and bans
    for i in range(5):
        data["blue_picks"].append(champions[i].id)
        data["blue_role_assignments"][str(champions[i].id)] = [
            "top",
            "jungle",
            "mid",
            "bot",
            "support",
        ][i]
        data["red_picks"].append(champions[i + 5].id)
        data["red_role_assignments"][str(champions[i + 5].id)] = [
            "top",
            "jungle",
            "mid",
            "bot",
            "support",
        ][i]
        data["blue_bans"].append(champions[i + 10].id)
        data["red_bans"].append(champions[i + 10].id)

    pick_ban_phase.set_pick_ban_data(data)

    # Complete the phase
    result = pick_ban_phase.complete_pick_ban_phase()
    assert result is True
    assert pick_ban_phase.state == PickBanState.COMPLETED
    assert pick_ban_phase.end_time is not None


def test_pick_ban_progression(pick_ban_phase, champions):
    """Test the full progression of a pick/ban phase."""
    pick_ban_phase.start_pick_ban_phase()

    # Ban phase 1 (3 bans each)
    for i in range(6):
        champion_id = champions[i].id
        pick_ban_phase.make_selection(champion_id)

    # Should now be in pick phase 1
    assert pick_ban_phase.state == PickBanState.PICK_PHASE_1

    # Pick phase 1 (3 picks each)
    for i in range(6):
        champion_id = champions[i + 6].id
        role = ["top", "jungle", "mid"][i % 3]
        pick_ban_phase.make_selection(champion_id, role)

    # Should now be in ban phase 2
    assert pick_ban_phase.state == PickBanState.BAN_PHASE_2

    # Ban phase 2 (2 bans each)
    for i in range(4):
        champion_id = champions[i + 12].id
        pick_ban_phase.make_selection(champion_id)

    # Should now be in pick phase 2
    assert pick_ban_phase.state == PickBanState.PICK_PHASE_2

    # Pick phase 2 (2 picks each)
    for i in range(4):
        champion_id = champions[i + 16].id
        role = ["bot", "support"][i % 2]
        pick_ban_phase.make_selection(champion_id, role)

    # Should now be completed
    assert pick_ban_phase.state == PickBanState.COMPLETED
    assert pick_ban_phase.end_time is not None


def test_scenario_user_participation(session, pick_ban_phase, teams, champions):
    """Test scenario: User participates in pick/ban phase."""
    # User chooses to participate
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams["blue"].id, mode=PickBanMode.USER_PARTICIPATES
    )

    # Get initial state
    next_action = pick_ban_phase.get_next_action()
    assert next_action["user_turn"] is True

    # User bans a champion
    pick_ban_phase.make_selection(champions[0].id)

    # AI bans a champion
    pick_ban_phase.ai_make_selection(session)

    # User bans again
    next_action = pick_ban_phase.get_next_action()
    assert next_action["user_turn"] is True
    pick_ban_phase.make_selection(champions[1].id)

    # Verify bans were recorded
    data = pick_ban_phase.get_pick_ban_data()
    assert len(data["blue_bans"]) == 2
    assert len(data["red_bans"]) == 1


def test_scenario_user_delegates(session, pick_ban_phase, teams, champions):
    """Test scenario: User delegates pick/ban phase to AI."""
    # User chooses to delegate
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams["blue"].id, mode=PickBanMode.USER_DELEGATES
    )

    # Let AI handle picks and bans
    for _ in range(10):  # Run some AI selections
        if pick_ban_phase.state == PickBanState.COMPLETED:
            break
        pick_ban_phase.ai_make_selection(session)

    # Verify progress
    data = pick_ban_phase.get_pick_ban_data()
    assert (
        len(data["blue_bans"])
        + len(data["red_bans"])
        + len(data["blue_picks"])
        + len(data["red_picks"])
        > 0
    )


def test_scenario_champion_switching(pick_ban_phase, champions):
    """Test scenario: Champion switching before lock-in."""
    pick_ban_phase.start_pick_ban_phase()

    # Skip to pick phase
    pick_ban_phase.state = PickBanState.PICK_PHASE_1
    data = pick_ban_phase.get_pick_ban_data()
    data["current_action"] = "pick"
    data["current_team"] = "blue"

    # Pre-select champions for each role (manually add to data without state transitions)
    champion_ids = []
    roles = ["top", "jungle", "mid", "bot", "support"]

    # Directly add champions to the blue_picks array instead of using make_selection
    # This bypasses the state transition logic that would limit us to 3 picks
    for i in range(5):
        champion_id = champions[i].id
        champion_ids.append(champion_id)
        data["blue_picks"].append(champion_id)
        data["blue_role_assignments"][str(champion_id)] = roles[i]

    # Save the modified data
    pick_ban_phase.set_pick_ban_data(data)

    # Get current data
    data = pick_ban_phase.get_pick_ban_data()
    assert len(data["blue_picks"]) == 5

    # Switch a champion
    pick_ban_phase.switch_champion(champion_ids[0], champions[10].id, "top")

    # Verify switch
    data = pick_ban_phase.get_pick_ban_data()
    assert champion_ids[0] not in data["blue_picks"]
    assert champions[10].id in data["blue_picks"]
    assert data["blue_role_assignments"][str(champions[10].id)] == "top"

    # Rearrange roles
    pick_ban_phase.assign_role(champion_ids[1], "top")
    pick_ban_phase.assign_role(champions[10].id, "jungle")

    # Verify rearrangement
    data = pick_ban_phase.get_pick_ban_data()
    assert data["blue_role_assignments"][str(champion_ids[1])] == "top"
    assert data["blue_role_assignments"][str(champions[10].id)] == "jungle"
