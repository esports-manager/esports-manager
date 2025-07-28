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
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import date

from esm.models.champion import Champion
from esm.models.moba_team import MobaTeam
from esm.models.match import Match, MatchStatus, MatchType, MatchFormat
from esm.models.pick_ban_phase import PickBanPhase, PickBanMode, PickBanState
from esm.models.moba_player import PlayerRole


@pytest.fixture(name="teams")
def teams_fixture(session_fixture: Session):
    """Create test teams."""
    blue_team = MobaTeam(name="Blue Team", short_name="BLU", region="NA")
    red_team = MobaTeam(name="Red Team", short_name="RED", region="EU")

    session_fixture.add(blue_team)
    session_fixture.add(red_team)
    session_fixture.commit()

    return [blue_team, red_team]


@pytest.fixture(name="champions")
def champions_fixture(session_fixture: Session):
    """Create test champions."""
    champions = []

    # Create 5 champions for each role (TOP, JUNGLE, MID, ADC, SUPPORT)
    for i, role in enumerate(
        [
            PlayerRole.TOP,
            PlayerRole.JUNGLE,
            PlayerRole.MID,
            PlayerRole.ADC,
            PlayerRole.SUPPORT,
        ]
    ):
        for j in range(1, 6):
            champion = Champion(
                name=f"{role.value.capitalize()} Champion {j}",
                title=f"The {role.value.capitalize()} {j}",
                primary_role=role,
                secondary_role=None,
                difficulty=5,
                release_date=date(2023, 1, 15),
                description=f"A test champion for {role.value}",
            )
            session_fixture.add(champion)
            champions.append(champion)

    session_fixture.commit()
    return champions


@pytest.fixture(name="match")
def match_fixture(session_fixture: Session, teams):
    """Create a test match."""
    match = Match(
        home_team_id=teams[0].id,
        away_team_id=teams[1].id,
        scheduled_date=date(2023, 8, 15),
        match_type=MatchType.REGULAR_SEASON,
        match_format=MatchFormat.BO3,
        status=MatchStatus.SCHEDULED,
    )
    session_fixture.add(match)
    session_fixture.commit()
    return match


@pytest.fixture(name="pick_ban_phase")
def pick_ban_phase_fixture(session_fixture: Session, match, teams):
    """Create a test pick/ban phase."""
    phase = PickBanPhase(
        match_id=match.id,
        map_number=1,
        blue_side_team_id=teams[0].id,
        red_side_team_id=teams[1].id,
    )
    session_fixture.add(phase)
    session_fixture.commit()
    return phase


def test_create_pick_ban_phase(client_fixture: TestClient, match, teams):
    """Test creating a pick/ban phase."""
    phase_data = {
        "match_id": match.id,
        "map_number": 2,
        "blue_side_team_id": teams[0].id,
        "red_side_team_id": teams[1].id,
        "user_team_id": teams[0].id,
        "mode": "user_participates",
    }

    response = client_fixture.post("/api/pick-ban-phases/", json=phase_data)
    assert response.status_code == 201
    data = response.json()

    assert data["match_id"] == match.id
    assert data["map_number"] == 2
    assert data["blue_side_team_id"] == teams[0].id
    assert data["red_side_team_id"] == teams[1].id
    assert data["user_team_id"] == teams[0].id
    assert data["mode"] == "user_participates"
    assert data["state"] == "not_started"

    # Verify phase was created in DB
    get_response = client_fixture.get(f"/api/pick-ban-phases/{data['id']}")
    assert get_response.status_code == 200


def test_get_pick_ban_phases(client_fixture: TestClient, pick_ban_phase):
    """Test retrieving pick/ban phases."""
    response = client_fixture.get("/api/pick-ban-phases/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 1
    assert any(phase["id"] == pick_ban_phase.id for phase in data)


def test_get_pick_ban_phase_by_id(client_fixture: TestClient, pick_ban_phase):
    """Test retrieving a pick/ban phase by ID."""
    response = client_fixture.get(f"/api/pick-ban-phases/{pick_ban_phase.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == pick_ban_phase.id
    assert data["match_id"] == pick_ban_phase.match_id
    assert data["map_number"] == pick_ban_phase.map_number
    assert data["blue_side_team_id"] == pick_ban_phase.blue_side_team_id
    assert data["red_side_team_id"] == pick_ban_phase.red_side_team_id
    assert data["state"] == "not_started"


def test_update_pick_ban_phase(client_fixture: TestClient, pick_ban_phase):
    """Test updating a pick/ban phase."""
    update_data = {
        "mode": "user_delegates",
        "user_team_id": pick_ban_phase.red_side_team_id,
    }

    response = client_fixture.patch(
        f"/api/pick-ban-phases/{pick_ban_phase.id}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == pick_ban_phase.id
    assert data["mode"] == "user_delegates"
    assert data["user_team_id"] == pick_ban_phase.red_side_team_id

    # Verify changes in DB
    get_response = client_fixture.get(f"/api/pick-ban-phases/{pick_ban_phase.id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["mode"] == "user_delegates"
    assert get_data["user_team_id"] == pick_ban_phase.red_side_team_id


def test_delete_pick_ban_phase(client_fixture: TestClient, pick_ban_phase):
    """Test deleting a pick/ban phase."""
    response = client_fixture.delete(f"/api/pick-ban-phases/{pick_ban_phase.id}")
    assert response.status_code == 204

    # Verify deletion
    get_response = client_fixture.get(f"/api/pick-ban-phases/{pick_ban_phase.id}")
    assert get_response.status_code == 404


def test_start_pick_ban_phase(client_fixture: TestClient, pick_ban_phase, teams):
    """Test starting a pick/ban phase."""
    start_data = {"user_team_id": teams[0].id, "mode": "user_participates"}

    response = client_fixture.post(
        f"/api/pick-ban-phases/{pick_ban_phase.id}/start", json=start_data
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == pick_ban_phase.id
    assert data["state"] == "ban_phase_1"
    assert data["user_team_id"] == teams[0].id
    assert data["mode"] == "user_participates"
    assert data["pick_ban_data"] is not None
    assert "current_team" in data["pick_ban_data"]
    assert "current_action" in data["pick_ban_data"]
    assert data["start_time"] is not None
    assert data["end_time"] is None


def test_make_selection(
    client_fixture: TestClient,
    pick_ban_phase,
    teams,
    champions,
    session_fixture: Session,
):
    """Test making a selection in the pick/ban phase."""
    # First, start the pick/ban phase
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams[0].id, mode=PickBanMode.USER_PARTICIPATES
    )
    session_fixture.commit()

    selection_data = {
        "champion_id": champions[0].id,
        "role": "top"
        if pick_ban_phase.get_pick_ban_data()["current_action"] == "pick"
        else None,
    }

    response = client_fixture.post(
        f"/api/pick-ban-phases/{pick_ban_phase.id}/select", json=selection_data
    )
    assert response.status_code == 200
    data = response.json()

    # Get the current state of the phase
    phase_data = pick_ban_phase.get_pick_ban_data()
    team = phase_data["current_team"]
    action = phase_data["current_action"]

    # The selection should now be in the appropriate list (picks or bans)
    # Note: After making a selection, the turn switches to the next team
    # So we need to check the opposite team of the current "team" value
    # which is the team that just made a selection
    if action == "ban":
        if team == "red":  # If current team is red, blue just made a selection
            assert champions[0].id in data["pick_ban_data"]["blue_bans"]
        else:  # If current team is blue, red just made a selection
            assert champions[0].id in data["pick_ban_data"]["red_bans"]
    else:  # pick
        if team == "blue":
            assert champions[0].id in data["pick_ban_data"]["blue_picks"]
            assert (
                data["pick_ban_data"]["blue_role_assignments"][str(champions[0].id)]
                == "top"
            )
        else:
            assert champions[0].id in data["pick_ban_data"]["red_picks"]
            assert (
                data["pick_ban_data"]["red_role_assignments"][str(champions[0].id)]
                == "top"
            )


def test_switch_champion(
    client_fixture: TestClient,
    pick_ban_phase,
    teams,
    champions,
    session_fixture: Session,
):
    """Test switching a champion in the pick/ban phase."""
    # First, start the pick/ban phase and make a pick
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams[0].id, mode=PickBanMode.USER_PARTICIPATES
    )

    # Skip to pick phase
    pick_ban_phase.state = PickBanState.PICK_PHASE_1
    data = pick_ban_phase.get_pick_ban_data()
    data["current_action"] = "pick"
    data["current_team"] = "blue"

    # Add champion to picks
    data["blue_picks"].append(champions[0].id)
    data["blue_role_assignments"][str(champions[0].id)] = "top"
    pick_ban_phase.set_pick_ban_data(data)

    session_fixture.commit()

    # Now test the champion switch
    switch_data = {
        "old_champion_id": champions[0].id,
        "new_champion_id": champions[5].id,  # Use a different champion
        "role": "top",
    }

    response = client_fixture.post(
        f"/api/pick-ban-phases/{pick_ban_phase.id}/switch", json=switch_data
    )
    assert response.status_code == 200
    data = response.json()

    # Verify the champion was switched
    assert champions[0].id not in data["pick_ban_data"]["blue_picks"]
    assert champions[5].id in data["pick_ban_data"]["blue_picks"]
    assert data["pick_ban_data"]["blue_role_assignments"][str(champions[5].id)] == "top"
    assert str(champions[0].id) not in data["pick_ban_data"]["blue_role_assignments"]


def test_assign_role(
    client_fixture: TestClient,
    pick_ban_phase,
    teams,
    champions,
    session_fixture: Session,
):
    """Test assigning a role to a champion."""
    # First, start the pick/ban phase and make a pick
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams[0].id, mode=PickBanMode.USER_PARTICIPATES
    )

    # Skip to pick phase and add champion to picks
    pick_ban_phase.state = PickBanState.PICK_PHASE_1
    data = pick_ban_phase.get_pick_ban_data()
    data["current_action"] = "pick"
    data["current_team"] = "blue"
    data["blue_picks"].append(champions[0].id)
    pick_ban_phase.set_pick_ban_data(data)

    session_fixture.commit()

    # Now test role assignment
    role_data = {
        "champion_id": champions[0].id,
        "role": "jungle",  # Change role from default top
    }

    response = client_fixture.post(
        f"/api/pick-ban-phases/{pick_ban_phase.id}/assign-role", json=role_data
    )
    assert response.status_code == 200
    data = response.json()

    # Verify the role was assigned
    assert (
        data["pick_ban_data"]["blue_role_assignments"][str(champions[0].id)] == "jungle"
    )


def test_ai_make_selection(
    client_fixture: TestClient,
    pick_ban_phase,
    teams,
    champions,
    session_fixture: Session,
):
    """Test AI making a selection."""
    # First, start the pick/ban phase in delegate mode
    pick_ban_phase.start_pick_ban_phase(
        user_team_id=teams[0].id, mode=PickBanMode.USER_DELEGATES
    )
    session_fixture.commit()

    response = client_fixture.post(
        f"/api/pick-ban-phases/{pick_ban_phase.id}/ai-select"
    )
    assert response.status_code == 200
    data = response.json()

    # Check that AI made a selection
    phase_data = data["pick_ban_data"]
    if phase_data["current_action"] == "ban":
        assert len(phase_data["blue_bans"]) > 0 or len(phase_data["red_bans"]) > 0
    else:  # pick
        assert len(phase_data["blue_picks"]) > 0 or len(phase_data["red_picks"]) > 0


def test_complete_pick_ban_phase(
    client_fixture: TestClient, pick_ban_phase, teams, session_fixture: Session
):
    """Test completing a pick/ban phase."""
    # First, start the pick/ban phase
    pick_ban_phase.start_pick_ban_phase(user_team_id=teams[0].id)

    # Set state to simulate completed selections
    pick_ban_phase.state = PickBanState.PICK_PHASE_2
    data = pick_ban_phase.get_pick_ban_data()
    data["blue_picks"] = [1, 2, 3, 4, 5]
    data["red_picks"] = [6, 7, 8, 9, 10]
    data["blue_bans"] = [11, 12, 13, 14, 15]
    data["red_bans"] = [16, 17, 18, 19, 20]
    data["blue_role_assignments"] = {
        "1": "top",
        "2": "jungle",
        "3": "mid",
        "4": "bot",
        "5": "support",
    }
    data["red_role_assignments"] = {
        "6": "top",
        "7": "jungle",
        "8": "mid",
        "9": "bot",
        "10": "support",
    }
    pick_ban_phase.set_pick_ban_data(data)

    session_fixture.commit()

    response = client_fixture.post(f"/api/pick-ban-phases/{pick_ban_phase.id}/complete")
    assert response.status_code == 200
    data = response.json()

    # Verify the phase was completed
    assert data["state"] == "completed"
    assert data["end_time"] is not None


def test_get_pick_ban_phases_by_match(
    client_fixture: TestClient, pick_ban_phase, match
):
    """Test getting all pick/ban phases for a match."""
    response = client_fixture.get(f"/api/pick-ban-phases/match/{match.id}")
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 1
    assert any(phase["id"] == pick_ban_phase.id for phase in data)
    assert all(phase["match_id"] == match.id for phase in data)


def test_get_available_champions(
    client_fixture: TestClient,
    pick_ban_phase,
    teams,
    champions,
    session_fixture: Session,
):
    """Test getting available champions for selection."""
    # First, start the pick/ban phase
    pick_ban_phase.start_pick_ban_phase(user_team_id=teams[0].id)
    session_fixture.commit()

    # Get the current state
    phase_data = pick_ban_phase.get_pick_ban_data()
    team = phase_data["current_team"]
    team_id = (
        pick_ban_phase.blue_side_team_id
        if team == "blue"
        else pick_ban_phase.red_side_team_id
    )
    action = phase_data["current_action"]

    response = client_fixture.get(
        f"/api/pick-ban-phases/{pick_ban_phase.id}/available-champions?team_id={team_id}&action={action}"
    )
    assert response.status_code == 200
    data = response.json()

    # Verify we get a list of champions
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
    assert "primary_role" in data[0]
