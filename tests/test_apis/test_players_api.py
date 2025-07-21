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
from esm.models.moba_player import PlayerRole, ContractStatus


def test_get_players(client_fixture: TestClient):
    """Test getting all players"""
    response = client_fixture.get("/api/players")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_player_by_id(client_fixture: TestClient):
    """Test getting a single player by ID"""
    # First create a player
    player_data = {
        "name": "Faker",
        "full_name": "Lee Sang-hyeok",
        "nationality": "Korea",
        "role": PlayerRole.MID.value,
        "date_of_birth": "1996-05-07",
        "contract_status": ContractStatus.SIGNED.value,
    }
    create_response = client_fixture.post("/api/players", json=player_data)
    assert create_response.status_code == 201
    player_id = create_response.json()["id"]

    # Now get the player by ID
    response = client_fixture.get(f"/api/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["id"] == player_id
    assert response.json()["name"] == "Faker"


def test_create_player(client_fixture: TestClient):
    """Test creating a new player"""
    player_data = {
        "name": "Faker",
        "full_name": "Lee Sang-hyeok",
        "nationality": "Korea",
        "role": PlayerRole.MID.value,
        "date_of_birth": "1996-05-07",
        "contract_status": ContractStatus.SIGNED.value,
        "mechanics": 95,
        "game_knowledge": 99,
        "team_fighting": 90,
        "champion_pool_size": 94,
        "laning": 92,
    }

    response = client_fixture.post("/api/players", json=player_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Faker"
    assert response.json()["role"] == PlayerRole.MID.value
    assert "id" in response.json()


def test_update_player(client_fixture: TestClient):
    """Test updating an existing player"""
    # First create a player
    player_data = {
        "name": "Jeong Ji-hoon",
        "nickname": "Chovy",
        "nationality": "Korea",
        "role": PlayerRole.MID.value,
        "date_of_birth": "2001-03-03",
        "contract_status": ContractStatus.SIGNED.value,
    }
    create_response = client_fixture.post("/api/players", json=player_data)
    player_id = create_response.json()["id"]

    # Now update the player
    update_data = {
        "mechanics": 94,
        "team_play": 88,
        "contract_status": ContractStatus.TRANSFER_LISTED.value,
    }

    response = client_fixture.patch(f"/api/players/{player_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["mechanics"] == 94
    assert response.json()["contract_status"] == ContractStatus.TRANSFER_LISTED.value


def test_delete_player(client_fixture: TestClient):
    """Test deleting a player"""
    # First create a player
    player_data = {
        "name": "Kim Min-seong",
        "nickname": "Lava",
        "nationality": "Korea",
        "role": PlayerRole.MID.value,
        "date_of_birth": "1998-01-23",
        "contract_status": ContractStatus.FREE_AGENT.value,
    }
    create_response = client_fixture.post("/api/players", json=player_data)
    player_id = create_response.json()["id"]

    # Delete the player
    delete_response = client_fixture.delete(f"/api/players/{player_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client_fixture.get(f"/api/players/{player_id}")
    assert get_response.status_code == 404


def test_get_players_by_role(client_fixture: TestClient):
    """Test filtering players by role"""
    # Create players with different roles
    mid_player = {
        "name": "MidLaner",
        "full_name": "Mid Player",
        "nationality": "USA",
        "role": PlayerRole.MID.value,
        "date_of_birth": "2000-01-01",
        "contract_status": ContractStatus.SIGNED.value,
    }
    client_fixture.post("/api/players", json=mid_player)

    top_player = {
        "name": "TopLaner",
        "full_name": "Top Player",
        "nationality": "USA",
        "role": PlayerRole.TOP.value,
        "date_of_birth": "2000-01-01",
        "contract_status": ContractStatus.FREE_AGENT.value,
    }
    client_fixture.post("/api/players", json=top_player)

    # Get only mid laners
    response = client_fixture.get(f"/api/players?role={PlayerRole.MID.value}")
    assert response.status_code == 200
    players = response.json()
    assert len(players) >= 1
    # All returned players should be mid laners
    for player in players:
        assert player["role"] == PlayerRole.MID.value
