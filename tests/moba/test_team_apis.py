# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import date
from esm.models.moba.team import MobaTeam
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.player_contract import MobaPlayerContract


def test_get_teams_empty(client: TestClient):
    response = client.get("/api/moba/teams")
    assert response.status_code == 200
    assert response.json() == []


def test_get_teams(client: TestClient, session: Session):
    team = MobaTeam(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    response = client.get("/api/moba/teams")
    assert response.status_code == 200
    assert response.json()[0]["id"] == team.id
    assert response.json()[0]["name"] == team.name
    assert response.json()[0]["nationality"] == team.nationality
    assert response.json()[0]["region"] == team.region
    assert response.json()[0]["description"] == team.description
    assert response.json()[0]["logo_path"] == team.logo_path


def test_get_team_by_id(client: TestClient, session: Session):
    team = MobaTeam(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    response = client.get(f"/api/moba/teams/{team.id}")
    assert response.status_code == 200
    assert response.json()["id"] == team.id
    assert response.json()["name"] == team.name
    assert response.json()["nationality"] == team.nationality
    assert response.json()["region"] == team.region
    assert response.json()["description"] == team.description
    assert response.json()["logo_path"] == team.logo_path


def test_get_team_by_id_not_found(client: TestClient):
    response = client.get("/api/moba/teams/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


def test_create_team(client: TestClient, session: Session):
    response = client.post(
        "/api/moba/teams",
        json={
            "name": "Test Team",
            "nationality": "Test",
            "region": "Test",
            "description": "Test",
            "logo_path": "test-logo.png",
        },
    )
    assert response.status_code == 201
    team = session.get(MobaTeam, response.json()["id"])
    assert isinstance(team, MobaTeam)
    assert team.name == "Test Team"
    assert team.nationality == "Test"
    assert team.region == "Test"
    assert team.description == "Test"
    assert team.logo_path == "test-logo.png"


def test_update_team(client: TestClient, session: Session):
    team = MobaTeam(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    response = client.patch(
        f"/api/moba/teams/{team.id}",
        json={
            "name": "Updated Team",
            "nationality": "Test",
            "region": "Test",
            "description": "Test",
            "logo_path": "test-logo.png",
        },
    )
    assert response.status_code == 200
    team = session.get(MobaTeam, response.json()["id"])
    assert isinstance(team, MobaTeam)
    assert team.name == "Updated Team"
    assert team.nationality == "Test"
    assert team.region == "Test"
    assert team.description == "Test"
    assert team.logo_path == "test-logo.png"


def test_delete_team(client: TestClient, session: Session):
    team = MobaTeam(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    response = client.delete(f"/api/moba/teams/{team.id}")
    assert response.status_code == 204
    team = session.get(MobaTeam, team.id)
    assert team is None


def test_get_team_players(client: TestClient, session: Session):
    team = MobaTeam(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )
    session.add(team)
    session.commit()
    session.refresh(team)
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    contract = MobaPlayerContract(
        player_id=player.id,
        team_id=team.id,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    team.add_player(player, contract)
    session.add(team)
    session.commit()
    session.refresh(team)
    response = client.get(f"/api/moba/teams/{team.id}/players")
    assert response.status_code == 200
    assert response.json()[0]["id"] == player.id
    assert response.json()[0]["first_name"] == player.first_name
    assert response.json()[0]["last_name"] == player.last_name


def test_add_player_to_team(client: TestClient, session: Session):
    team = MobaTeam(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(team)
    session.add(player)
    session.commit()
    session.refresh(team)
    session.refresh(player)
    response = client.post(
        "/api/moba/teams/add-player/",
        json={
            "contract": {
                "team_id": team.id,
                "player_id": player.id,
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "salary": 1000,
                "is_active": True,
            }
        },
    )
    assert response.status_code == 201
    assert response.json()["id"] == team.id
    t = session.get(MobaTeam, team.id)
    assert t.current_players[0].id == player.id
