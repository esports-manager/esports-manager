"""
Tests for the Matches API endpoints.
"""

from fastapi.testclient import TestClient
import pytest
from datetime import date, datetime

from esm.models.match import MatchStatus, MatchType, MatchFormat
from esm.models.moba_team import TeamRegion


@pytest.fixture
def create_test_teams(client_fixture: TestClient):
    """Create test teams for matches"""
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


def test_get_matches(client_fixture: TestClient):
    """Test getting all matches"""
    response = client_fixture.get("/api/matches")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_match_by_id(client_fixture: TestClient, create_test_teams):
    """Test getting a single match by ID"""
    # First create a match
    teams = create_test_teams
    match_data = {
        "home_team_id": teams["team1"]["id"],
        "away_team_id": teams["team2"]["id"],
        "scheduled_date": datetime(2025, 7, 20, 18, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LoL Park, Seoul",
        "status": MatchStatus.SCHEDULED.value,
    }
    create_response = client_fixture.post("/api/matches", json=match_data)
    assert create_response.status_code == 201
    match_id = create_response.json()["id"]

    # Now get the match by ID
    response = client_fixture.get(f"/api/matches/{match_id}")
    assert response.status_code == 200
    assert response.json()["id"] == match_id
    assert response.json()["venue"] == "LoL Park, Seoul"


def test_create_match(client_fixture: TestClient, create_test_teams):
    """Test creating a new match"""
    teams = create_test_teams
    match_data = {
        "home_team_id": teams["team1"]["id"],
        "away_team_id": teams["team2"]["id"],
        "scheduled_date": datetime(2025, 7, 25, 19, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO5.value,
        "venue": "LCS Studio, Los Angeles",
        "status": MatchStatus.SCHEDULED.value,
    }

    response = client_fixture.post("/api/matches", json=match_data)
    assert response.status_code == 201
    assert response.json()["home_team_id"] == teams["team1"]["id"]
    assert response.json()["match_format"] == MatchFormat.BO5.value
    assert "id" in response.json()


def test_update_match(client_fixture: TestClient, create_test_teams):
    """Test updating an existing match"""
    # First create a match
    teams = create_test_teams
    match_data = {
        "home_team_id": teams["team1"]["id"],
        "away_team_id": teams["team2"]["id"],
        "scheduled_date": datetime(2025, 8, 5, 18, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LoL Park, Seoul",
        "status": MatchStatus.SCHEDULED.value,
    }
    create_response = client_fixture.post("/api/matches", json=match_data)
    match_id = create_response.json()["id"]

    # Update the match to in-progress
    update_data = {"status": MatchStatus.IN_PROGRESS.value}

    response = client_fixture.patch(f"/api/matches/{match_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == MatchStatus.IN_PROGRESS.value

    # Complete the match
    update_data = {
        "status": MatchStatus.COMPLETED.value,
        "home_team_score": 2,
        "away_team_score": 1,
        "completed_date": datetime(2025, 8, 5, 20, 30, 0).isoformat(),
    }

    response = client_fixture.patch(f"/api/matches/{match_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == MatchStatus.COMPLETED.value
    assert response.json()["home_team_score"] == 2
    assert response.json()["away_team_score"] == 1


def test_delete_match(client_fixture: TestClient, create_test_teams):
    """Test deleting a match"""
    # First create a match
    teams = create_test_teams
    match_data = {
        "home_team_id": teams["team1"]["id"],
        "away_team_id": teams["team2"]["id"],
        "scheduled_date": datetime(2025, 8, 10, 18, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LoL Park, Seoul",
        "status": MatchStatus.SCHEDULED.value,
    }
    create_response = client_fixture.post("/api/matches", json=match_data)
    match_id = create_response.json()["id"]

    # Delete the match
    delete_response = client_fixture.delete(f"/api/matches/{match_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client_fixture.get(f"/api/matches/{match_id}")
    assert get_response.status_code == 404


def test_get_matches_by_team(client_fixture: TestClient, create_test_teams):
    """Test filtering matches by team ID"""
    teams = create_test_teams

    # Create two matches with different teams
    match1_data = {
        "home_team_id": teams["team1"]["id"],
        "away_team_id": teams["team2"]["id"],
        "scheduled_date": datetime(2025, 9, 5, 18, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LoL Park, Seoul",
        "status": MatchStatus.SCHEDULED.value,
    }
    client_fixture.post("/api/matches", json=match1_data)

    match2_data = {
        "home_team_id": teams["team2"]["id"],
        "away_team_id": teams["team1"]["id"],
        "scheduled_date": datetime(2025, 9, 15, 18, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LCS Studio, Los Angeles",
        "status": MatchStatus.SCHEDULED.value,
    }
    client_fixture.post("/api/matches", json=match2_data)

    # Get matches for team1
    response = client_fixture.get(f"/api/matches?team_id={teams['team1']['id']}")
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) >= 2  # Should have at least the two we just created

    # All matches should involve team1
    for match in matches:
        assert (
            match["home_team_id"] == teams["team1"]["id"]
            or match["away_team_id"] == teams["team1"]["id"]
        )


def test_get_upcoming_matches(client_fixture: TestClient, create_test_teams):
    """Test getting upcoming matches"""
    teams = create_test_teams

    # Create a past match (completed)
    past_match_data = {
        "home_team_id": teams["team1"]["id"],
        "away_team_id": teams["team2"]["id"],
        "scheduled_date": datetime(2025, 6, 5, 18, 0, 0).isoformat(),
        "completed_date": datetime(2025, 6, 5, 20, 30, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LoL Park, Seoul",
        "status": MatchStatus.COMPLETED.value,
        "home_team_score": 2,
        "away_team_score": 1,
    }
    client_fixture.post("/api/matches", json=past_match_data)

    # Create a future match (scheduled)
    future_match_data = {
        "home_team_id": teams["team2"]["id"],
        "away_team_id": teams["team1"]["id"],
        "scheduled_date": datetime(2025, 10, 15, 18, 0, 0).isoformat(),
        "match_type": MatchType.REGULAR_SEASON.value,
        "match_format": MatchFormat.BO3.value,
        "venue": "LCS Studio, Los Angeles",
        "status": MatchStatus.SCHEDULED.value,
    }
    client_fixture.post("/api/matches", json=future_match_data)

    # Get upcoming matches
    response = client_fixture.get("/api/matches/upcoming")
    assert response.status_code == 200
    matches = response.json()

    # All matches should be scheduled or in_progress
    for match in matches:
        assert match["status"] in [
            MatchStatus.SCHEDULED.value,
            MatchStatus.IN_PROGRESS.value,
        ]
