# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from esm.models.bgmi.tournament import BgmiTournament
from esm.models.game import Game
from esm.models.moba.team import MobaTeam

MINIMAL_PAYLOAD = {
    "name": "BGMI Pro Series 2025",
    "abbreviation": "BGPS",
    "type": "international",
    "format": "league",
    "tier": "major",
    "start_date": "2025-07-01",
    "end_date": "2025-08-15",
    "location": "India",
}


async def _create_tournament(client: AsyncClient, **overrides) -> dict:
    payload = {**MINIMAL_PAYLOAD, **overrides}
    response = await client.post("/api/bgmi/tournaments/", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_bgmi_tournament_defaults(
    client: AsyncClient, default_games: dict[str, Game]
):
    data = await _create_tournament(client)

    assert data["name"] == MINIMAL_PAYLOAD["name"]
    assert data["game_id"] == default_games["bgmi"].id
    assert data["game_mode"] == "squad"
    assert data["map_pool"] == ["erangel", "miramar", "sanhok", "vikendi"]
    assert data["points_per_kill"] == 1
    assert data["placement_points"]["1"] == 10
    assert data["placement_points"]["8"] == 1
    assert data["teams_per_lobby"] == 16
    assert data["match_count"] == 6


async def test_create_bgmi_tournament_with_custom_rules(
    client: AsyncClient, default_games: dict[str, Game]
):
    data = await _create_tournament(
        client,
        game_mode="duo",
        map_pool=["erangel", "livik"],
        points_per_kill=2,
        placement_points={"1": 15, "2": 12, "3": 10},
        teams_per_lobby=25,
        match_count=8,
        default_color="#FF9900",
    )

    assert data["game_mode"] == "duo"
    assert data["map_pool"] == ["erangel", "livik"]
    assert data["points_per_kill"] == 2
    assert data["placement_points"] == {"1": 15, "2": 12, "3": 10}
    assert data["teams_per_lobby"] == 25
    assert data["match_count"] == 8
    assert data["default_color"] == "#FF9900"


async def test_create_bgmi_tournament_requires_registered_game(
    client: AsyncClient,
):
    response = await client.post("/api/bgmi/tournaments/", json=MINIMAL_PAYLOAD)

    assert response.status_code == 404
    assert "/api/games" in response.json()["detail"]


async def test_create_bgmi_tournament_rejects_non_battle_royale_game(
    client: AsyncClient, default_games: dict[str, Game]
):
    response = await client.post(
        "/api/bgmi/tournaments/",
        json={**MINIMAL_PAYLOAD, "game_id": default_games["league-of-legends"].id},
    )

    assert response.status_code == 400
    assert "bgmi" in response.json()["detail"]


async def test_create_bgmi_tournament_unknown_game(
    client: AsyncClient, default_games: dict[str, Game]
):
    response = await client.post(
        "/api/bgmi/tournaments/", json={**MINIMAL_PAYLOAD, "game_id": 9999}
    )
    assert response.status_code == 404


async def test_create_bgmi_tournament_invalid_game_mode(
    client: AsyncClient, default_games: dict[str, Game]
):
    response = await client.post(
        "/api/bgmi/tournaments/", json={**MINIMAL_PAYLOAD, "game_mode": "quintet"}
    )
    assert response.status_code == 422


async def test_list_bgmi_tournaments(
    client: AsyncClient, default_games: dict[str, Game]
):
    await _create_tournament(client, name="BGIS 2025", game_mode="squad")
    await _create_tournament(client, name="BGMI Solo Cup", game_mode="solo")

    response = await client.get("/api/bgmi/tournaments/")
    assert response.status_code == 200
    assert len(response.json()) == 2

    squads = await client.get("/api/bgmi/tournaments/?game_mode=squad")
    assert [t["name"] for t in squads.json()] == ["BGIS 2025"]

    search = await client.get("/api/bgmi/tournaments/?search=solo")
    assert [t["name"] for t in search.json()] == ["BGMI Solo Cup"]

    invalid = await client.get("/api/bgmi/tournaments/?tier=bogus")
    assert invalid.status_code == 400


async def test_get_update_and_delete_bgmi_tournament(
    client: AsyncClient, default_games: dict[str, Game]
):
    created = await _create_tournament(client)
    tournament_id = created["id"]

    fetched = await client.get(f"/api/bgmi/tournaments/{tournament_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == created["name"]

    updated = await client.patch(
        f"/api/bgmi/tournaments/{tournament_id}",
        json={"name": "BGMI Pro Series 2026", "match_count": 10, "game_mode": "squad"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "BGMI Pro Series 2026"
    assert updated.json()["match_count"] == 10

    deleted = await client.delete(f"/api/bgmi/tournaments/{tournament_id}")
    assert deleted.status_code == 204
    assert (
        await client.get(f"/api/bgmi/tournaments/{tournament_id}")
    ).status_code == 404


async def test_tournament_participants(
    client: AsyncClient, session: AsyncSession, default_games: dict[str, Game]
):
    created = await _create_tournament(client)
    tournament_id = created["id"]

    team = MobaTeam(name="Godlike Esports", region="India")
    session.add(team)
    await session.commit()
    await session.refresh(team)

    added = await client.post(
        f"/api/bgmi/tournaments/{tournament_id}/teams", json={"team_id": team.id}
    )
    assert added.status_code == 204

    # Adding the same team twice is a no-op.
    again = await client.post(
        f"/api/bgmi/tournaments/{tournament_id}/teams", json={"team_id": team.id}
    )
    assert again.status_code == 204

    teams = await client.get(f"/api/bgmi/tournaments/{tournament_id}/teams")
    assert teams.status_code == 200
    assert [t["name"] for t in teams.json()] == ["Godlike Esports"]

    removed = await client.delete(
        f"/api/bgmi/tournaments/{tournament_id}/teams/{team.id}"
    )
    assert removed.status_code == 204
    assert (
        await client.get(f"/api/bgmi/tournaments/{tournament_id}/teams")
    ).json() == []


async def test_delete_tournament_removes_participants(
    client: AsyncClient, session: AsyncSession, default_games: dict[str, Game]
):
    created = await _create_tournament(client)
    tournament_id = created["id"]

    team = MobaTeam(name="Team SouL", region="India")
    session.add(team)
    await session.commit()
    await session.refresh(team)

    await client.post(
        f"/api/bgmi/tournaments/{tournament_id}/teams", json={"team_id": team.id}
    )
    await client.delete(f"/api/bgmi/tournaments/{tournament_id}")

    remaining = await session.get(BgmiTournament, tournament_id)
    assert remaining is None
