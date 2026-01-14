# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from httpx import AsyncClient
from esm.models.moba.champion import (
    MobaChampion,
    MobaChampionRole,
    MobaChampionType,
    MobaChampionDifficulty,
)


async def test_get_champions_empty(client: AsyncClient):
    response = await client.get("/api/moba/champions")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_champions(client: AsyncClient, session: AsyncSession):
    champion = MobaChampion(
        name="Test Champion",
        description="Test Champion Description",
        release_date=date(2025, 1, 1),
        primary_role=MobaChampionRole.TOP,
        secondary_role=MobaChampionRole.JUNGLE,
        champion_type1=MobaChampionType.ASSASSIN,
        champion_type2=MobaChampionType.TANK,
        difficulty=MobaChampionDifficulty.EASY,
        strength=50,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    response = await client.get("/api/moba/champions")
    assert response.status_code == 200
    assert response.json()[0]["id"] == champion.id
    assert response.json()[0]["name"] == champion.name
    assert response.json()[0]["description"] == champion.description
    assert response.json()[0]["release_date"] == champion.release_date.isoformat()
    assert response.json()[0]["primary_role"] == champion.primary_role.value
    assert response.json()[0]["secondary_role"] == champion.secondary_role.value
    assert response.json()[0]["champion_type1"] == champion.champion_type1.value
    assert response.json()[0]["champion_type2"] == champion.champion_type2.value
    assert response.json()[0]["difficulty"] == champion.difficulty.value
    assert response.json()[0]["strength"] == champion.strength


async def test_get_champion_by_id(client: AsyncClient, session: AsyncSession):
    champion = MobaChampion(
        name="Test Champion",
        description="Test Champion Description",
        release_date=date(2025, 1, 1),
        primary_role=MobaChampionRole.TOP,
        secondary_role=MobaChampionRole.JUNGLE,
        champion_type1=MobaChampionType.ASSASSIN,
        champion_type2=MobaChampionType.TANK,
        difficulty=MobaChampionDifficulty.EASY,
        strength=50,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    response = await client.get(f"/api/moba/champions/{champion.id}")
    assert response.status_code == 200
    assert response.json()["id"] == champion.id
    assert response.json()["name"] == champion.name
    assert response.json()["description"] == champion.description
    assert response.json()["release_date"] == champion.release_date.isoformat()
    assert response.json()["primary_role"] == champion.primary_role.value
    assert response.json()["secondary_role"] == champion.secondary_role.value
    assert response.json()["champion_type1"] == champion.champion_type1.value
    assert response.json()["champion_type2"] == champion.champion_type2.value
    assert response.json()["difficulty"] == champion.difficulty.value
    assert response.json()["strength"] == champion.strength


async def test_get_champion_by_id_not_found(client: AsyncClient):
    response = await client.get("/api/moba/champions/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Champion not found"}


async def test_create_champion(client: AsyncClient, session: AsyncSession):
    response = await client.post(
        "/api/moba/champions",
        json={
            "name": "Test Champion",
            "description": "Test Champion Description",
            "release_date": "2025-01-01",
            "primary_role": "top",
            "secondary_role": "jungle",
            "champion_type1": "assassin",
            "champion_type2": "tank",
            "difficulty": "easy",
            "strength": 50,
        },
    )
    assert response.status_code == 201
    champion = await session.get(MobaChampion, response.json()["id"])
    assert isinstance(champion, MobaChampion)
    assert champion.name == "Test Champion"
    assert champion.description == "Test Champion Description"
    assert champion.release_date == date(2025, 1, 1)
    assert champion.primary_role == MobaChampionRole.TOP
    assert champion.secondary_role == MobaChampionRole.JUNGLE
    assert champion.champion_type1 == MobaChampionType.ASSASSIN
    assert champion.champion_type2 == MobaChampionType.TANK
    assert champion.difficulty == MobaChampionDifficulty.EASY
    assert champion.strength == 50


async def test_update_champion(client: AsyncClient, session: AsyncSession):
    champion = MobaChampion(
        name="Test Champion",
        description="Test Champion Description",
        release_date=date(2025, 1, 1),
        primary_role=MobaChampionRole.TOP,
        secondary_role=MobaChampionRole.JUNGLE,
        champion_type1=MobaChampionType.ASSASSIN,
        champion_type2=MobaChampionType.TANK,
        difficulty=MobaChampionDifficulty.EASY,
        strength=50,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    response = await client.patch(
        f"/api/moba/champions/{champion.id}", json={"name": "Test Champion Updated"}
    )
    assert response.status_code == 200
    champion = await session.get(MobaChampion, champion.id)
    assert isinstance(champion, MobaChampion)
    assert champion.name == "Test Champion Updated"


async def test_get_champion_tier(client: AsyncClient, session: AsyncSession):
    champion = MobaChampion(
        name="Test Champion",
        description="Test Champion Description",
        release_date=date(2025, 1, 1),
        primary_role=MobaChampionRole.TOP,
        secondary_role=MobaChampionRole.JUNGLE,
        champion_type1=MobaChampionType.ASSASSIN,
        champion_type2=MobaChampionType.TANK,
        difficulty=MobaChampionDifficulty.EASY,
        strength=50,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    response = await client.get(f"/api/moba/champions/{champion.id}/tier")
    assert response.status_code == 200
    assert response.json() == champion.champion_tier.value


async def test_delete_champion(client: AsyncClient, session: AsyncSession):
    champion = MobaChampion(
        name="Test Champion",
        description="Test Champion Description",
        release_date=date(2025, 1, 1),
        primary_role=MobaChampionRole.TOP,
        secondary_role=MobaChampionRole.JUNGLE,
        champion_type1=MobaChampionType.ASSASSIN,
        champion_type2=MobaChampionType.TANK,
        difficulty=MobaChampionDifficulty.EASY,
        strength=50,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    response = await client.delete(f"/api/moba/champions/{champion.id}")
    assert response.status_code == 204
    champion = await session.get(MobaChampion, champion.id)
    assert champion is None
