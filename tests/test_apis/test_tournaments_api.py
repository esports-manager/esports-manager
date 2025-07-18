"""
Tests for the Tournaments API endpoints.
"""

from fastapi.testclient import TestClient
import pytest
from datetime import date

from esm.models.tournament import TournamentType, TournamentFormat, TeamRegion


@pytest.fixture
def create_test_teams(client_fixture: TestClient):
    """Create test teams for tournament registrations"""
    team1_data = {
        "name": "T1",
        "region": TeamRegion.KR.value,
        "founded_date": date(2019, 2, 25).isoformat(),
    }
    team2_data = {
        "name": "Cloud9",
        "region": TeamRegion.NA.value,
        "founded_date": date(2013, 1, 1).isoformat(),
    }

    team1_response = client_fixture.post("/api/teams", json=team1_data)
    team2_response = client_fixture.post("/api/teams", json=team2_data)

    return {"team1": team1_response.json(), "team2": team2_response.json()}


def test_get_tournaments(client_fixture: TestClient):
    """Test getting all tournaments"""
    response = client_fixture.get("/api/tournaments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_tournament_by_id(client_fixture: TestClient):
    """Test getting a single tournament by ID"""
    # First create a tournament
    tournament_data = {
        "name": "LCK Summer 2025",
        "tournament_type": TournamentType.LEAGUE.value,
        "tournament_format": TournamentFormat.ROUND_ROBIN.value,
        "start_date": "2025-06-01",
        "end_date": "2025-08-15",
        "region": TeamRegion.KR.value,
        "prize_pool": 100000.0,
    }
    create_response = client_fixture.post("/api/tournaments", json=tournament_data)
    assert create_response.status_code == 201
    tournament_id = create_response.json()["id"]

    # Now get the tournament by ID
    response = client_fixture.get(f"/api/tournaments/{tournament_id}")
    assert response.status_code == 200
    assert response.json()["id"] == tournament_id
    assert response.json()["name"] == "LCK Summer 2025"


def test_create_tournament(client_fixture: TestClient):
    """Test creating a new tournament"""
    tournament_data = {
        "name": "LCS Summer 2025",
        "tournament_type": TournamentType.LEAGUE.value,
        "tournament_format": TournamentFormat.ROUND_ROBIN.value,
        "start_date": "2025-06-01",
        "end_date": "2025-08-15",
        "region": TeamRegion.NA.value,
        "prize_pool": 75000.0,
        "description": "North American League Championship Series Summer Split",
    }

    response = client_fixture.post("/api/tournaments", json=tournament_data)
    assert response.status_code == 201
    assert response.json()["name"] == "LCS Summer 2025"
    assert response.json()["tournament_type"] == TournamentType.LEAGUE.value
    assert "id" in response.json()


def test_update_tournament(client_fixture: TestClient):
    """Test updating an existing tournament"""
    # First create a tournament
    tournament_data = {
        "name": "LEC Summer 2025",
        "tournament_type": TournamentType.LEAGUE.value,
        "tournament_format": TournamentFormat.ROUND_ROBIN.value,
        "start_date": "2025-06-01",
        "end_date": "2025-08-15",
        "region": TeamRegion.EU.value,
        "prize_pool": 80000.0,
    }
    create_response = client_fixture.post("/api/tournaments", json=tournament_data)
    tournament_id = create_response.json()["id"]

    # Now update the tournament
    update_data = {
        "prize_pool": 90000.0,
        "description": "European League Championship Summer Split",
    }

    response = client_fixture.patch(
        f"/api/tournaments/{tournament_id}", json=update_data
    )
    assert response.status_code == 200
    assert response.json()["prize_pool"] == 90000.0
    assert response.json()["description"] == "European League Championship Summer Split"


def test_delete_tournament(client_fixture: TestClient):
    """Test deleting a tournament"""
    # First create a tournament
    tournament_data = {
        "name": "LPL Summer 2025",
        "tournament_type": TournamentType.LEAGUE.value,
        "tournament_format": TournamentFormat.ROUND_ROBIN.value,
        "start_date": "2025-06-01",
        "end_date": "2025-08-15",
        "region": TeamRegion.CN.value,
        "prize_pool": 120000.0,
    }
    create_response = client_fixture.post("/api/tournaments", json=tournament_data)
    tournament_id = create_response.json()["id"]

    # Delete the tournament
    delete_response = client_fixture.delete(f"/api/tournaments/{tournament_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client_fixture.get(f"/api/tournaments/{tournament_id}")
    assert get_response.status_code == 404


def test_add_team_to_tournament(client_fixture: TestClient, create_test_teams):
    """Test adding a team to a tournament"""
    teams = create_test_teams

    # Create a tournament
    tournament_data = {
        "name": "MSI 2025",
        "tournament_type": TournamentType.INTERNATIONAL.value,
        "tournament_format": TournamentFormat.GROUP_KNOCKOUT.value,
        "start_date": "2025-05-01",
        "end_date": "2025-05-15",
        "region": TeamRegion.OTHER.value,
        "prize_pool": 250000.0,
    }
    create_response = client_fixture.post("/api/tournaments", json=tournament_data)
    tournament_id = create_response.json()["id"]

    # Add team1 to the tournament
    register_data = {"team_id": teams["team1"]["id"], "seed": 1, "group": "A"}
    register_response = client_fixture.post(
        f"/api/tournaments/{tournament_id}/teams", json=register_data
    )
    assert register_response.status_code == 200

    # Get tournament teams
    teams_response = client_fixture.get(f"/api/tournaments/{tournament_id}/teams")
    assert teams_response.status_code == 200
    tournament_teams = teams_response.json()
    assert len(tournament_teams) == 1
    assert tournament_teams[0]["id"] == teams["team1"]["id"]


def test_get_tournament_standings(client_fixture: TestClient, create_test_teams):
    """Test getting tournament standings"""
    teams = create_test_teams

    # Create a tournament
    tournament_data = {
        "name": "Worlds 2025",
        "tournament_type": TournamentType.INTERNATIONAL.value,
        "tournament_format": TournamentFormat.GROUP_KNOCKOUT.value,
        "start_date": "2025-10-01",
        "end_date": "2025-11-15",
        "region": TeamRegion.OTHER.value,
        "prize_pool": 500000.0,
    }
    create_response = client_fixture.post("/api/tournaments", json=tournament_data)
    tournament_id = create_response.json()["id"]

    # Add both teams to the tournament
    client_fixture.post(
        f"/api/tournaments/{tournament_id}/teams",
        json={"team_id": teams["team1"]["id"], "seed": 1},
    )
    client_fixture.post(
        f"/api/tournaments/{tournament_id}/teams",
        json={"team_id": teams["team2"]["id"], "seed": 2},
    )

    # Get tournament standings (will be empty as no matches yet)
    standings_response = client_fixture.get(
        f"/api/tournaments/{tournament_id}/standings"
    )
    assert standings_response.status_code == 200
    standings = standings_response.json()
    assert isinstance(standings, list)


def test_create_season(client_fixture: TestClient):
    """Test creating a new season"""
    season_data = {
        "name": "2025 Season",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "description": "The 2025 competitive season",
    }

    response = client_fixture.post("/api/seasons", json=season_data)
    assert response.status_code == 201
    assert response.json()["name"] == "2025 Season"
    assert "id" in response.json()


def test_add_tournament_to_season(client_fixture: TestClient):
    """Test adding a tournament to a season"""
    # Create a season
    season_data = {
        "name": "2025 Season",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
    }
    season_response = client_fixture.post("/api/seasons", json=season_data)
    season_id = season_response.json()["id"]

    # Create a tournament
    tournament_data = {
        "name": "MSI 2025",
        "tournament_type": TournamentType.INTERNATIONAL.value,
        "tournament_format": TournamentFormat.GROUP_KNOCKOUT.value,
        "start_date": "2025-05-01",
        "end_date": "2025-05-15",
        "region": TeamRegion.OTHER.value,
        "prize_pool": 250000.0,
    }
    tournament_response = client_fixture.post("/api/tournaments", json=tournament_data)
    tournament_id = tournament_response.json()["id"]

    # Add tournament to season
    update_data = {"season_id": season_id}
    response = client_fixture.patch(
        f"/api/tournaments/{tournament_id}", json=update_data
    )
    assert response.status_code == 200
    assert response.json()["season_id"] == season_id

    # Get all tournaments in season
    response = client_fixture.get(f"/api/seasons/{season_id}/tournaments")
    assert response.status_code == 200
    tournaments = response.json()
    assert len(tournaments) == 1
    assert tournaments[0]["id"] == tournament_id
