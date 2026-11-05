# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Tests for the game agnostic tournament listing."""

from httpx import AsyncClient

from esm.models.game import Game

MOBA_TOURNAMENT = {
    "name": "LCK Summer 2025",
    "abbreviation": "LCK 2025",
    "type": "regional",
    "format": "league",
    "tier": "league",
    "start_date": "2025-06-01",
    "end_date": "2025-08-10",
    "location": "korea",
}

BGMI_TOURNAMENT = {
    "name": "Battlegrounds Mobile India Series 2025",
    "abbreviation": "BGIS 2025",
    "type": "national",
    "format": "league",
    "tier": "major",
    "start_date": "2025-07-01",
    "end_date": "2025-08-15",
    "location": "india",
    "game_mode": "squad",
}


async def _create_moba(client: AsyncClient, **overrides) -> dict:
    response = await client.post(
        "/api/moba/tournaments/", json={**MOBA_TOURNAMENT, **overrides}
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_bgmi(client: AsyncClient, **overrides) -> dict:
    response = await client.post(
        "/api/bgmi/tournaments/", json={**BGMI_TOURNAMENT, **overrides}
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_list_tournaments_from_every_game(
    client: AsyncClient, default_games: dict[str, Game]
):
    bgmi = await _create_bgmi(client)
    moba = await _create_moba(client)

    response = await client.get("/api/tournaments/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2

    by_name = {tournament["name"]: tournament for tournament in data}
    bgmi_summary = by_name[bgmi["name"]]
    assert bgmi_summary["game_id"] == default_games["bgmi"].id
    assert bgmi_summary["game_slug"] == "bgmi"
    assert bgmi_summary["game_name"] == "BGMI"
    assert bgmi_summary["system"] == "bgmi"
    assert bgmi_summary["url"] == f"/tournaments/bgmi/{bgmi_summary['id']}"

    moba_summary = by_name[moba["name"]]
    assert moba_summary["game_slug"] == "league-of-legends"
    assert moba_summary["system"] == "moba"
    assert moba_summary["url"] == f"/tournaments/{moba_summary['id']}"

    # Default sorting is start date, newest first.
    assert data[0]["name"] == BGMI_TOURNAMENT["name"]


async def test_filter_tournaments_by_game(
    client: AsyncClient, default_games: dict[str, Game]
):
    await _create_bgmi(client)
    await _create_moba(client)

    bgmi_only = await client.get("/api/tournaments/?game=bgmi")
    assert [t["system"] for t in bgmi_only.json()] == ["bgmi"]

    moba_only = await client.get("/api/tournaments/?game=league-of-legends")
    assert [t["system"] for t in moba_only.json()] == ["moba"]

    unknown_game = await client.get("/api/tournaments/?game=valorant")
    assert unknown_game.status_code == 200
    assert unknown_game.json() == []


async def test_tournament_filters_and_sorting(
    client: AsyncClient, default_games: dict[str, Game]
):
    await _create_bgmi(client, name="BGIS 2025", tier="major")
    await _create_bgmi(
        client, name="BGMI Open", tier="amateur", start_date="2025-09-01"
    )
    await _create_moba(client, name="LCK Summer 2025", tier="league")

    by_tier = await client.get("/api/tournaments/?tier=amateur")
    assert [t["name"] for t in by_tier.json()] == ["BGMI Open"]

    by_system = await client.get("/api/tournaments/?game=bgmi&search=open")
    assert [t["name"] for t in by_system.json()] == ["BGMI Open"]

    ascending = await client.get("/api/tournaments/?sort=start_date&direction=asc")
    assert [t["name"] for t in ascending.json()] == [
        "LCK Summer 2025",
        "BGIS 2025",
        "BGMI Open",
    ]

    by_name = await client.get("/api/tournaments/?sort=name&direction=asc")
    assert [t["name"] for t in by_name.json()] == [
        "BGIS 2025",
        "BGMI Open",
        "LCK Summer 2025",
    ]


async def test_tournament_pagination(
    client: AsyncClient, default_games: dict[str, Game]
):
    for index in range(3):
        await _create_bgmi(
            client, name=f"BGMI Cup {index}", start_date=f"2025-0{index + 1}-01"
        )

    first_page = await client.get("/api/tournaments/?per_page=2&page=1")
    second_page = await client.get("/api/tournaments/?per_page=2&page=2")

    assert len(first_page.json()) == 2
    assert len(second_page.json()) == 1
    assert not set(t["id"] for t in first_page.json()) & set(
        t["id"] for t in second_page.json()
    )


async def test_invalid_filter_returns_400(
    client: AsyncClient, default_games: dict[str, Game]
):
    response = await client.get("/api/tournaments/?tier=bogus")
    assert response.status_code == 400
    assert "Invalid tier" in response.json()["detail"]


async def test_tournaments_render_as_htmx_partial(
    client: AsyncClient, default_games: dict[str, Game]
):
    created = await _create_bgmi(client)

    response = await client.get(
        "/api/tournaments/?game=bgmi", headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert created["name"] in response.text
    assert "BGMI" in response.text
    assert f"/tournaments/bgmi/{created['id']}" in response.text


async def test_moba_listing_still_works(
    client: AsyncClient, default_games: dict[str, Game]
):
    moba = await _create_moba(client)
    await _create_bgmi(client)

    response = await client.get("/api/moba/tournaments/")
    assert response.status_code == 200
    assert [t["id"] for t in response.json()] == [moba["id"]]
    assert response.json()[0]["game_name"] == "League of Legends"

    partial = await client.get("/api/moba/tournaments/", headers={"HX-Request": "true"})
    assert partial.status_code == 200
    assert moba["name"] in partial.text


async def test_bgmi_listing_renders_as_htmx_partial(
    client: AsyncClient, default_games: dict[str, Game]
):
    bgmi = await _create_bgmi(client)
    await _create_moba(client)

    response = await client.get(
        "/api/bgmi/tournaments/", headers={"HX-Request": "true"}
    )
    assert response.status_code == 200
    assert bgmi["name"] in response.text
    assert MOBA_TOURNAMENT["name"] not in response.text
