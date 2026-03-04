# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import pytest
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from esm.models.moba.champion import (
    MobaChampionBase,
    MobaChampion,
    MobaChampionDifficulty,
    MobaChampionRole,
    MobaChampionType,
    MobaChampionTier,
)


@pytest.fixture
def champion() -> MobaChampionBase:
    return MobaChampionBase(
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


@pytest.fixture
def champion_instance(champion) -> MobaChampion:
    return MobaChampion(
        name=champion.name,
        description=champion.description,
        release_date=champion.release_date,
        primary_role=champion.primary_role,
        secondary_role=champion.secondary_role,
        champion_type1=champion.champion_type1,
        champion_type2=champion.champion_type2,
        difficulty=champion.difficulty,
        strength=champion.strength,
    )


async def test_create_moba_champion(champion: MobaChampionBase):
    assert champion.name == "Test Champion"
    assert champion.description == "Test Champion Description"
    assert champion.release_date == date(2025, 1, 1)
    assert champion.primary_role == MobaChampionRole.TOP
    assert champion.secondary_role == MobaChampionRole.JUNGLE
    assert champion.champion_type1 == MobaChampionType.ASSASSIN
    assert champion.champion_type2 == MobaChampionType.TANK
    assert champion.difficulty == MobaChampionDifficulty.EASY
    assert champion.strength == 50
    assert champion.image_path is None


async def test_update_moba_champion(champion: MobaChampionBase):
    champion.name = "Updated"
    assert champion.name == "Updated"


async def test_moba_champion_role_assignment(champion: MobaChampionBase):
    roles = list(MobaChampionRole)
    for role in roles:
        champion.primary_role = role
        assert champion.primary_role == role


async def test_moba_champion_type_assignment(champion: MobaChampionBase):
    types = list(MobaChampionType)
    for type in types:
        champion.champion_type1 = type
        assert champion.champion_type1 == type

    types = list(MobaChampionType)
    for type in types:
        champion.champion_type2 = type
        assert champion.champion_type2 == type


async def test_moba_champion_difficulty_assignment(champion: MobaChampionBase):
    difficulties = list(MobaChampionDifficulty)
    for difficulty in difficulties:
        champion.difficulty = difficulty
        assert champion.difficulty == difficulty


async def test_moba_champion_get_tier(champion: MobaChampionBase):
    assert champion.champion_tier == MobaChampionTier.D


async def test_moba_champion_instance(
    session: AsyncSession, champion_instance: MobaChampion
):
    session.add(champion_instance)
    await session.commit()
    await session.refresh(champion_instance)
    assert champion_instance.id is not None
    assert champion_instance.created_at is not None
    assert await session.get(MobaChampion, champion_instance.id) == champion_instance
    assert champion_instance.champion_tier == MobaChampionTier.D
