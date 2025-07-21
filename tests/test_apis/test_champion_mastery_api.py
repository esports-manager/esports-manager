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

from esm.models.champion_mastery import ChampionMastery
from esm.models.champion import Champion
from esm.models.moba_player import MobaPlayer, PlayerRole


@pytest.fixture(name="test_player")
def player_fixture(session_fixture: Session):
    """Create a test player."""
    player = MobaPlayer(
        name="TestPlayer",
        full_name="Test Player",
        nationality="Testland",
        role=PlayerRole.MID,
        salary=50000,
        date_of_birth=date(2000, 1, 1),
    )
    session_fixture.add(player)
    session_fixture.commit()
    return player


@pytest.fixture(name="test_champion")
def champion_fixture(session_fixture: Session):
    """Create a test champion."""
    champion = Champion(
        name="Test Champion",
        title="The Tester",
        primary_role=PlayerRole.MID,
        difficulty=7,
        release_date=date(2023, 1, 15),
    )
    session_fixture.add(champion)
    session_fixture.commit()
    return champion


@pytest.fixture(name="test_mastery")
def mastery_fixture(
    session_fixture: Session, test_player: MobaPlayer, test_champion: Champion
):
    """Create a test champion mastery."""
    mastery = ChampionMastery(
        player_id=test_player.id,
        champion_id=test_champion.id,
        mastery_level=75,
        games_played=100,
        wins=60,
        losses=40,
        kda_ratio=3.5,
        is_comfort_pick=True,
        notes="Player's main champion",
    )
    session_fixture.add(mastery)
    session_fixture.commit()
    return mastery


def test_create_champion_mastery(
    client_fixture: TestClient, test_player: MobaPlayer, test_champion: Champion
):
    """Test creating a champion mastery."""
    mastery_data = {
        "player_id": test_player.id,
        "champion_id": test_champion.id,
        "mastery_level": 80,
        "games_played": 120,
        "wins": 70,
        "losses": 50,
        "kda_ratio": 4.2,
        "is_comfort_pick": True,
        "notes": "Very skilled with this champion",
    }

    response = client_fixture.post("/api/champion-masteries/", json=mastery_data)
    assert response.status_code == 201
    data = response.json()

    assert data["player_id"] == test_player.id
    assert data["champion_id"] == test_champion.id
    assert data["mastery_level"] == 80
    assert data["games_played"] == 120
    assert data["win_rate"] == 58.333333333333336  # Calculated field (70/120 * 100)

    # Verify mastery was created in DB
    get_response = client_fixture.get(f"/api/champion-masteries/{data['id']}")
    assert get_response.status_code == 200


def test_get_champion_masteries(
    client_fixture: TestClient, test_mastery: ChampionMastery
):
    """Test retrieving champion masteries."""
    response = client_fixture.get("/api/champion-masteries/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) >= 1
    assert any(mastery["id"] == test_mastery.id for mastery in data)

    # Check calculated win_rate field
    mastery = next(m for m in data if m["id"] == test_mastery.id)
    assert mastery["win_rate"] == 60.0  # 60/100 * 100


def test_get_champion_mastery_by_id(
    client_fixture: TestClient, test_mastery: ChampionMastery
):
    """Test retrieving a champion mastery by ID."""
    response = client_fixture.get(f"/api/champion-masteries/{test_mastery.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == test_mastery.id
    assert data["player_id"] == test_mastery.player_id
    assert data["champion_id"] == test_mastery.champion_id
    assert data["mastery_level"] == 75
    assert data["games_played"] == 100
    assert data["win_rate"] == 60.0


def test_update_champion_mastery(
    client_fixture: TestClient, test_mastery: ChampionMastery
):
    """Test updating a champion mastery."""
    update_data = {
        "mastery_level": 85,
        "games_played": 150,
        "wins": 90,
        "notes": "Updated notes",
    }

    response = client_fixture.patch(
        f"/api/champion-masteries/{test_mastery.id}", json=update_data
    )
    assert response.status_code == 200
    data = response.json()

    assert data["mastery_level"] == 85
    assert data["games_played"] == 150
    assert data["wins"] == 90
    assert data["notes"] == "Updated notes"
    assert data["win_rate"] == 60.0  # 90/150 * 100

    # Verify mastery was updated in DB
    get_response = client_fixture.get(f"/api/champion-masteries/{test_mastery.id}")
    assert get_response.json()["mastery_level"] == 85


def test_delete_champion_mastery(
    client_fixture: TestClient, test_mastery: ChampionMastery
):
    """Test deleting a champion mastery."""
    response = client_fixture.delete(f"/api/champion-masteries/{test_mastery.id}")
    assert response.status_code == 204

    # Verify mastery was deleted
    get_response = client_fixture.get(f"/api/champion-masteries/{test_mastery.id}")
    assert get_response.status_code == 404


def test_get_player_champion_masteries(
    client_fixture: TestClient,
    test_player: MobaPlayer,
    test_champion: Champion,
    test_mastery: ChampionMastery,
):
    """Test getting champion masteries for a specific player."""
    # Create another champion and mastery for the same player
    second_champion_data = {
        "name": "Second Champion",
        "title": "The Second",
        "primary_role": "top",
        "difficulty": 6,
        "release_date": "2023-02-20",
    }
    champion_response = client_fixture.post(
        "/api/champions/", json=second_champion_data
    )
    second_champion_id = champion_response.json()["id"]

    second_mastery_data = {
        "player_id": test_player.id,
        "champion_id": second_champion_id,
        "mastery_level": 60,
        "games_played": 50,
        "wins": 25,
        "losses": 25,
        "is_comfort_pick": False,
    }
    client_fixture.post("/api/champion-masteries/", json=second_mastery_data)

    # Get masteries for this player
    response = client_fixture.get(f"/api/champion-masteries/player/{test_player.id}")
    assert response.status_code == 200
    data = response.json()

    # Should have both masteries
    assert len(data) == 2

    # Filter by minimum mastery level
    response = client_fixture.get(
        f"/api/champion-masteries/player/{test_player.id}?min_mastery_level=70"
    )
    assert response.status_code == 200
    data = response.json()

    # Should only have the first mastery (level 75)
    assert len(data) == 1
    assert data[0]["mastery_level"] >= 70
    assert data[0]["champion_id"] == test_champion.id

    # Filter by comfort pick
    response = client_fixture.get(
        f"/api/champion-masteries/player/{test_player.id}?is_comfort_pick=true"
    )
    assert response.status_code == 200
    data = response.json()

    # Should only have comfort picks
    assert len(data) == 1
    assert data[0]["is_comfort_pick"] is True
    assert data[0]["champion_id"] == test_champion.id


def test_get_champion_player_masteries(
    client_fixture: TestClient, test_player: MobaPlayer, test_champion: Champion
):
    """Test getting player masteries for a specific champion."""
    # Create another player and mastery for the same champion
    second_player_data = {
        "name": "Player2",
        "full_name": "Second Player",
        "nationality": "Testland",
        "role": "jungle",
        "salary": 45000,
        "date_of_birth": "2001-02-15",
    }
    player_response = client_fixture.post("/api/players/", json=second_player_data)
    second_player_id = player_response.json()["id"]

    second_mastery_data = {
        "player_id": second_player_id,
        "champion_id": test_champion.id,
        "mastery_level": 40,
        "games_played": 20,
        "wins": 10,
        "losses": 10,
        "is_comfort_pick": False,
    }
    client_fixture.post("/api/champion-masteries/", json=second_mastery_data)

    # Get masteries for this champion
    response = client_fixture.get(
        f"/api/champion-masteries/champion/{test_champion.id}"
    )
    assert response.status_code == 200
    data = response.json()

    # Should have both masteries
    assert len(data) == 2

    # Filter by minimum mastery level
    response = client_fixture.get(
        f"/api/champion-masteries/champion/{test_champion.id}?min_mastery_level=50"
    )
    assert response.status_code == 200
    data = response.json()

    # Should only have the first mastery (level 75)
    assert len(data) == 1
    assert data[0]["mastery_level"] >= 50
    assert data[0]["player_id"] == test_player.id


def test_get_specific_player_champion_mastery(
    client_fixture: TestClient, test_player: MobaPlayer, test_champion: Champion
):
    """Test getting specific player-champion mastery."""
    response = client_fixture.get(
        f"/api/champion-masteries/player/{test_player.id}/champion/{test_champion.id}"
    )
    assert response.status_code == 200
    data = response.json()

    assert data["player_id"] == test_player.id
    assert data["champion_id"] == test_champion.id
    assert data["mastery_level"] == 75
    assert data["win_rate"] == 60.0

    # Try with non-existent combination
    response = client_fixture.get("/api/champion-masteries/player/999/champion/999")
    assert response.status_code == 404
