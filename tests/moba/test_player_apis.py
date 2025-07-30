from datetime import date
from sqlmodel import Session
from fastapi.testclient import TestClient
from esm.models.moba.player import (
    MobaPlayer,
    MobaPlayerRole,
)


def test_get_players_empty(client: TestClient):
    response = client.get("/api/moba/players")
    assert response.status_code == 200
    assert response.json() == []


def test_get_players(client: TestClient, session: Session):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    response = client.get("/api/moba/players")
    assert response.status_code == 200
    assert response.json()[0]["id"] == player.id
    assert response.json()[0]["first_name"] == player.first_name
    assert response.json()[0]["last_name"] == player.last_name


def test_get_player_by_id(client: TestClient, session: Session):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    response = client.get(f"/api/moba/players/{player.id}")
    assert response.status_code == 200
    assert response.json()["id"] == player.id
    assert response.json()["first_name"] == player.first_name
    assert response.json()["last_name"] == player.last_name


def test_get_player_by_id_not_found(client: TestClient):
    response = client.get("/api/moba/players/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}


def test_create_player(client: TestClient, session: Session):
    response = client.post(
        "/api/moba/players",
        json={
            "first_name": "Test",
            "last_name": "Player",
            "date_of_birth": "2005-01-01",
            "nationality": "Test",
            "role": "top",
        },
    )
    assert response.status_code == 200
    player = session.get(MobaPlayer, response.json()["id"])
    assert isinstance(player, MobaPlayer)
    assert player.first_name == "Test"
    assert player.last_name == "Player"
    assert player.date_of_birth == date(2005, 1, 1)
    assert player.nationality == "Test"
    assert player.role == MobaPlayerRole.TOP


def test_update_player(client: TestClient, session: Session):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    response = client.patch(
        f"/api/moba/players/{player.id}",
        json={
            "first_name": "Updated",
            "last_name": "Player",
            "date_of_birth": "2005-01-01",
            "nationality": "Test",
            "role": "top",
        },
    )
    assert response.status_code == 200
    player = session.get(MobaPlayer, response.json()["id"])
    assert isinstance(player, MobaPlayer)
    assert player.first_name == "Updated"
    assert player.last_name == "Player"
    assert player.date_of_birth == date(2005, 1, 1)
    assert player.nationality == "Test"
    assert player.role == MobaPlayerRole.TOP


def test_delete_player(client: TestClient, session: Session):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    response = client.delete(f"/api/moba/players/{player.id}")
    assert response.status_code == 200
    player = session.get(MobaPlayer, player.id)
    assert player is None
