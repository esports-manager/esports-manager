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
from esm.models.moba_player import PlayerRole


@pytest.fixture(name="champion")
def champion_fixture(session_fixture: Session):
    """Create a test champion."""
    champion = Champion(
        name="Test Champion",
        title="The Tester",
        primary_role=PlayerRole.MID,
        secondary_role=PlayerRole.SUPPORT,
        difficulty=7,
        release_date=date(2023, 1, 15),
        description="A champion for testing purposes",
    )
    session_fixture.add(champion)
    session_fixture.commit()
    return champion


def test_create_champion(client_fixture: TestClient):
    """Test creating a champion."""
    champion_data = {
        "name": "New Champion",
        "title": "The New One",
        "primary_role": "mid",
        "secondary_role": "top",
        "difficulty": 5,
        "release_date": "2023-06-10",
        "description": "A new champion for testing",
        "abilities": {
            "passive": {"name": "Test Passive", "description": "Test passive ability"},
            "q": {"name": "Q Ability", "description": "Q ability description"},
        },
        "stats": {"hp": 600, "mana": 300, "attack": 70, "defense": 40},
    }

    response = client_fixture.post("/api/champions/", json=champion_data)
    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "New Champion"
    assert data["primary_role"] == "mid"
    assert data["difficulty"] == 5
    assert "abilities" in data
    assert data["abilities"]["passive"]["name"] == "Test Passive"
    assert data["stats"]["hp"] == 600

    # Verify champion was created in DB
    get_response = client_fixture.get(f"/api/champions/{data['id']}")
    assert get_response.status_code == 200


def test_get_champions(client_fixture: TestClient):
    """Test retrieving champions."""
    response = client_fixture.get("/api/champions/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 1
    assert any(champ["name"] == "Test Champion" for champ in data)


def test_get_champion_by_id(client_fixture: TestClient, champion: Champion):
    """Test retrieving a champion by ID."""
    response = client_fixture.get(f"/api/champions/{champion.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == champion.id
    assert data["name"] == "Test Champion"
    assert data["primary_role"] == "mid"
    assert data["difficulty"] == 7


def test_update_champion(client_fixture: TestClient, champion: Champion):
    """Test updating a champion."""
    update_data = {
        "name": "Updated Champion",
        "difficulty": 8,
        "abilities": {
            "passive": {
                "name": "Updated Passive",
                "description": "Updated passive ability",
            }
        },
    }

    response = client_fixture.patch(f"/api/champions/{champion.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Champion"
    assert data["difficulty"] == 8
    assert data["abilities"]["passive"]["name"] == "Updated Passive"
    assert data["primary_role"] == "mid"  # Unchanged field

    # Verify champion was updated in DB
    get_response = client_fixture.get(f"/api/champions/{champion.id}")
    assert get_response.json()["name"] == "Updated Champion"


def test_delete_champion(client_fixture: TestClient, champion: Champion):
    """Test deleting a champion."""
    response = client_fixture.delete(f"/api/champions/{champion.id}")
    assert response.status_code == 204

    # Verify champion was deleted
    get_response = client_fixture.get(f"/api/champions/{champion.id}")
    assert get_response.status_code == 404


def test_get_champion_roles(client_fixture: TestClient):
    """Test getting all champion roles."""
    response = client_fixture.get("/api/champions/roles/")
    assert response.status_code == 200
    data = response.json()

    # Check that all roles from PlayerRole enum are present
    expected_roles = ["top", "jungle", "mid", "adc", "support"]
    assert sorted(data) == sorted(expected_roles)


def test_filter_champions_by_role(client_fixture: TestClient):
    """Test filtering champions by primary role."""
    # Add a champion with different role for testing filtering
    client_fixture.post(
        "/api/champions/",
        json={
            "name": "Top Lane Champion",
            "title": "The Top",
            "primary_role": "top",
            "difficulty": 5,
            "release_date": "2023-05-15",
        },
    )

    # Filter by mid role (should include our test champion)
    response = client_fixture.get("/api/champions/?primary_role=mid")
    assert response.status_code == 200
    data = response.json()

    # Should only include mid lane champions
    assert all(champ["primary_role"] == "mid" for champ in data)
    assert any(champ["name"] == "Test Champion" for champ in data)

    # Filter by top role (should not include our test champion)
    response = client_fixture.get("/api/champions/?primary_role=top")
    assert response.status_code == 200
    data = response.json()

    # Should only include top lane champions
    assert all(champ["primary_role"] == "top" for champ in data)
    assert any(champ["name"] == "Top Lane Champion" for champ in data)
    assert not any(champ["name"] == "Test Champion" for champ in data)


def test_filter_champions_by_difficulty(client_fixture: TestClient):
    """Test filtering champions by difficulty range."""
    # Add champions with different difficulties
    client_fixture.post(
        "/api/champions/",
        json={
            "name": "Easy Champion",
            "title": "The Easy One",
            "primary_role": "support",
            "difficulty": 2,
            "release_date": "2023-05-15",
        },
    )

    client_fixture.post(
        "/api/champions/",
        json={
            "name": "Hard Champion",
            "title": "The Hard One",
            "primary_role": "jungle",
            "difficulty": 9,
            "release_date": "2023-05-15",
        },
    )

    # Filter by min difficulty
    response = client_fixture.get("/api/champions/?min_difficulty=7")
    assert response.status_code == 200
    data = response.json()

    # Should only include champions with difficulty >= 7
    assert all(champ["difficulty"] >= 7 for champ in data)
    assert any(champ["name"] == "Test Champion" for champ in data)
    assert any(champ["name"] == "Hard Champion" for champ in data)
    assert not any(champ["name"] == "Easy Champion" for champ in data)

    # Filter by max difficulty
    response = client_fixture.get("/api/champions/?max_difficulty=5")
    assert response.status_code == 200
    data = response.json()

    # Should only include champions with difficulty <= 5
    assert all(champ["difficulty"] <= 5 for champ in data)
    assert any(champ["name"] == "Easy Champion" for champ in data)
    assert not any(champ["name"] == "Test Champion" for champ in data)

    # Filter by both min and max difficulty
    response = client_fixture.get("/api/champions/?min_difficulty=5&max_difficulty=8")
    assert response.status_code == 200
    data = response.json()

    # Should only include champions with 5 <= difficulty <= 8
    assert all(5 <= champ["difficulty"] <= 8 for champ in data)
    assert any(champ["name"] == "Test Champion" for champ in data)
