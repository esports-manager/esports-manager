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
from fastapi.testclient import TestClient
from datetime import date

from esm.models.moba_team import TeamRegion


def test_get_teams(client_fixture: TestClient):
    """Test getting all teams"""
    response = client_fixture.get("/api/teams")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_team_by_id(client_fixture: TestClient):
    """Test getting a single team by ID"""
    # First create a team
    # Create the team data with a Python date object
    founded_date = date(2019, 2, 25)

    # Convert to string for JSON serialization
    team_data = {
        "name": "Test Team",
        "region": TeamRegion.KR.value,
        "founded_date": founded_date.isoformat(),
    }
    create_response = client_fixture.post("/api/teams", json=team_data)
    assert create_response.status_code == 201
    team_id = create_response.json()["id"]

    # Now get the team by ID
    response = client_fixture.get(f"/api/teams/{team_id}")
    assert response.status_code == 200
    assert response.json()["id"] == team_id
    assert response.json()["name"] == "Test Team"


def test_create_team(client_fixture: TestClient):
    """Test creating a new team"""
    # Create the team data with a Python date object
    founded_date = date(2013, 1, 1)

    # Convert to string for JSON serialization
    team_data = {
        "name": "Cloud9",
        "region": TeamRegion.NA.value,
        "founded_date": founded_date.isoformat(),
        "description": "North American esports organization",
    }

    response = client_fixture.post("/api/teams", json=team_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Cloud9"
    assert response.json()["region"] == TeamRegion.NA.value
    assert "id" in response.json()


def test_update_team(client_fixture: TestClient):
    """Test updating an existing team"""
    # First create a team
    # Create the team data with a Python date object
    founded_date = date(2009, 1, 1)

    # Convert to string for JSON serialization
    team_data = {
        "name": "TSM",
        "region": TeamRegion.NA.value,
        "founded_date": founded_date.isoformat(),
    }
    create_response = client_fixture.post("/api/teams", json=team_data)
    team_id = create_response.json()["id"]

    # Now update the team
    update_data = {
        "name": "Team SoloMid",
        "description": "North American esports organization",
    }

    response = client_fixture.patch(f"/api/teams/{team_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Team SoloMid"
    assert response.json()["description"] == "North American esports organization"
    assert response.json()["region"] == TeamRegion.NA.value  # Unchanged field


def test_delete_team(client_fixture: TestClient):
    """Test deleting a team"""
    # First create a team
    # Create the team data with a Python date object
    founded_date = date(2017, 5, 1)

    # Convert to string for JSON serialization
    team_data = {
        "name": "Gen.G",
        "region": TeamRegion.KR.value,
        "founded_date": founded_date.isoformat(),
    }
    create_response = client_fixture.post("/api/teams", json=team_data)
    team_id = create_response.json()["id"]

    # Delete the team
    delete_response = client_fixture.delete(f"/api/teams/{team_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client_fixture.get(f"/api/teams/{team_id}")
    assert get_response.status_code == 404


def test_get_team_roster(client_fixture: TestClient):
    """Test getting a team's roster"""
    # First create a team
    # Create the team data with a Python date object
    founded_date = date(2004, 7, 23)

    # Convert to string for JSON serialization
    team_data = {
        "name": "Fnatic",
        "region": TeamRegion.EU.value,
        "founded_date": founded_date.isoformat(),
    }
    create_response = client_fixture.post("/api/teams", json=team_data)
    team_id = create_response.json()["id"]

    # Get the roster (will be empty for a new team)
    response = client_fixture.get(f"/api/teams/{team_id}/roster")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
