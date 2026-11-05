# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.models.bgmi.tournament import BgmiTournament
from esm.models.game import Game, GameGenre, TournamentSystem
from esm.models.tournament import TournamentFormat, TournamentTier, TournamentType
from esm.services.games import ensure_default_games


async def test_default_games_are_seeded_once(session: AsyncSession):
    created = await ensure_default_games(session)
    slugs = {game.slug for game in created}
    assert slugs == {"league-of-legends", "bgmi"}

    # Running the seeding again must not duplicate the built-in games.
    assert await ensure_default_games(session) == []

    result = await session.execute(select(Game))
    assert len(result.scalars().all()) == 2


async def test_bgmi_game_definition(default_games: dict[str, Game]):
    bgmi = default_games["bgmi"]

    assert bgmi.name == "BGMI"
    assert bgmi.genre is GameGenre.BATTLE_ROYALE
    assert bgmi.tournament_system is TournamentSystem.BGMI
    assert bgmi.team_size == 4
    assert bgmi.is_active is True
    assert default_games["league-of-legends"].tournament_system is (
        TournamentSystem.MOBA
    )


async def test_list_games(client: AsyncClient, default_games: dict[str, Game]):
    response = await client.get("/api/games/")
    assert response.status_code == 200

    data = response.json()
    assert [game["name"] for game in data] == ["BGMI", "League of Legends"]
    assert data[0]["slug"] == "bgmi"
    assert data[0]["genre"] == "battle_royale"


async def test_create_game(client: AsyncClient):
    payload = {
        "name": "VALORANT",
        "abbreviation": "VAL",
        "genre": "fps",
        "publisher": "Riot Games",
        "platform": "PC",
        "team_size": 5,
        "description": "Tactical five-versus-five shooter.",
    }
    response = await client.post("/api/games/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "VALORANT"
    assert data["slug"] == "valorant"
    assert data["genre"] == "fps"
    assert data["is_active"] is True
    assert data["id"] is not None


async def test_create_game_with_explicit_slug(client: AsyncClient):
    response = await client.post(
        "/api/games/", json={"name": "Counter Strike 2", "slug": "cs2", "genre": "fps"}
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "cs2"


async def test_create_game_duplicate_slug(
    client: AsyncClient, default_games: dict[str, Game]
):
    response = await client.post(
        "/api/games/",
        json={"name": "Battlegrounds Mobile India", "slug": "bgmi", "genre": "fps"},
    )
    assert response.status_code == 409
    assert "bgmi" in response.json()["detail"]


async def test_create_game_duplicate_name(
    client: AsyncClient, default_games: dict[str, Game]
):
    response = await client.post("/api/games/", json={"name": "BGMI", "genre": "fps"})
    assert response.status_code == 409


async def test_create_game_normalizes_messy_slug(client: AsyncClient):
    response = await client.post(
        "/api/games/",
        json={"name": "Rocket League", "slug": "Rocket League!", "genre": "sports"},
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "rocket-league"


async def test_create_game_invalid_slug(client: AsyncClient):
    response = await client.post(
        "/api/games/", json={"name": "Bad Game", "slug": "!!!", "genre": "fps"}
    )
    assert response.status_code == 422


async def test_get_game_by_id_and_slug(
    client: AsyncClient, default_games: dict[str, Game]
):
    bgmi = default_games["bgmi"]

    by_id = await client.get(f"/api/games/{bgmi.id}")
    assert by_id.status_code == 200
    assert by_id.json()["slug"] == "bgmi"

    by_slug = await client.get("/api/games/by-slug/bgmi")
    assert by_slug.status_code == 200
    assert by_slug.json()["id"] == bgmi.id

    missing = await client.get("/api/games/9999")
    assert missing.status_code == 404


async def test_update_game(client: AsyncClient, default_games: dict[str, Game]):
    bgmi = default_games["bgmi"]

    response = await client.patch(
        f"/api/games/{bgmi.id}",
        json={"name": "BGMI (India)", "description": "Updated description"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "BGMI (India)"


async def test_update_game_slug_conflict(
    client: AsyncClient, default_games: dict[str, Game]
):
    bgmi = default_games["bgmi"]

    response = await client.patch(
        f"/api/games/{bgmi.id}", json={"slug": "league-of-legends"}
    )
    assert response.status_code == 409


async def test_filter_games(client: AsyncClient, default_games: dict[str, Game]):
    by_genre = await client.get("/api/games/?genre=battle_royale")
    assert [game["slug"] for game in by_genre.json()] == ["bgmi"]

    by_system = await client.get("/api/games/?tournament_system=moba")
    assert [game["slug"] for game in by_system.json()] == ["league-of-legends"]

    by_search = await client.get("/api/games/?search=league")
    assert [game["slug"] for game in by_search.json()] == ["league-of-legends"]

    invalid = await client.get("/api/games/?genre=bogus")
    assert invalid.status_code == 400


async def test_delete_game(client: AsyncClient, default_games: dict[str, Game]):
    created = await client.post("/api/games/", json={"name": "Dota 2", "genre": "moba"})
    game_id = created.json()["id"]

    response = await client.delete(f"/api/games/{game_id}")
    assert response.status_code == 204
    assert (await client.get(f"/api/games/{game_id}")).status_code == 404


async def test_delete_game_with_tournaments_conflicts(
    client: AsyncClient, session: AsyncSession, default_games: dict[str, Game]
):
    bgmi = default_games["bgmi"]
    session.add(
        BgmiTournament(
            name="BGMI Invitational",
            game_id=bgmi.id,
            type=TournamentType.INTERNATIONAL,
            format=TournamentFormat.LEAGUE,
            tier=TournamentTier.MINOR,
        )
    )
    await session.commit()

    response = await client.delete(f"/api/games/{bgmi.id}")
    assert response.status_code == 409
    assert "tournaments" in response.json()["detail"]
