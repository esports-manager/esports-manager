from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient
from esm.models.moba.player import (
    MobaPlayer,
    MobaPlayerRole,
)
from esm.models.moba.champion import MobaChampion, MobaChampionRole
from esm.models.moba.champion_mastery import (
    MobaChampionMasteryTier,
)


async def test_get_players_empty(client: AsyncClient):
    response = await client.get("/api/moba/players")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_players(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    response = await client.get("/api/moba/players")
    assert response.status_code == 200
    assert response.json()[0]["id"] == player.id
    assert response.json()[0]["first_name"] == player.first_name
    assert response.json()[0]["last_name"] == player.last_name


async def test_get_player_by_id(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    response = await client.get(f"/api/moba/players/{player.id}")
    assert response.status_code == 200
    assert response.json()["id"] == player.id
    assert response.json()["first_name"] == player.first_name
    assert response.json()["last_name"] == player.last_name


async def test_get_player_by_id_not_found(client: AsyncClient):
    response = await client.get("/api/moba/players/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}


async def test_create_player(client: AsyncClient, session: AsyncSession):
    response = await client.post(
        "/api/moba/players",
        json={
            "first_name": "Test",
            "last_name": "Player",
            "date_of_birth": "2005-01-01",
            "nationality": "Test",
            "role": "top",
        },
    )
    assert response.status_code == 201
    player = await session.get(MobaPlayer, response.json()["id"])
    assert isinstance(player, MobaPlayer)
    assert player.first_name == "Test"
    assert player.last_name == "Player"
    assert player.date_of_birth == date(2005, 1, 1)
    assert player.nationality == "Test"
    assert player.role == MobaPlayerRole.TOP


async def test_update_player(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    response = await client.patch(
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
    player = await session.get(MobaPlayer, response.json()["id"])
    assert isinstance(player, MobaPlayer)
    assert player.first_name == "Updated"
    assert player.last_name == "Player"
    assert player.date_of_birth == date(2005, 1, 1)
    assert player.nationality == "Test"
    assert player.role == MobaPlayerRole.TOP


async def test_delete_player(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    response = await client.delete(f"/api/moba/players/{player.id}")
    assert response.status_code == 200
    player = await session.get(MobaPlayer, player.id)
    assert player is None


async def test_get_empty_champion_pool(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    response = await client.get(f"/api/moba/players/{player.id}/champion_pool")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_champion_pool(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    champion = MobaChampion(
        name="Test Champion",
        release_date=date(2025, 1, 1),
        description="Test Champion",
        role=MobaChampionRole.TOP,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    await session.close()
    post_response = await client.post(
        f"/api/moba/players/{player.id}/champion_pool/{champion.id}"
    )
    assert post_response.status_code == 200
    response = await client.get(
        f"/api/moba/players/{player.id}/champion_pool/{champion.id}"
    )
    expected_response = {
        "player_id": player.id,
        "champion_id": champion.id,
        "tier": MobaChampionMasteryTier.BRONZE.value,
        "points": 0,
    }
    assert response.status_code == 200
    assert response.json() == expected_response


async def test_get_champion_pool_not_found(client: AsyncClient, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    session.add(player)
    await session.commit()
    await session.refresh(player)
    champion = MobaChampion(
        name="Test Champion",
        release_date=date(2025, 1, 1),
        description="Test Champion",
        role=MobaChampionRole.TOP,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    response = await client.get(
        f"/api/moba/players/{player.id}/champion_pool/{champion.id}"
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Champion not found in pool"}
