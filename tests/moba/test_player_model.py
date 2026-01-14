import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from esm.models.moba.player import MobaPlayerBase, MobaPlayerRole, MobaPlayer
from esm.models.moba.player_contract import MobaPlayerContract


@pytest.fixture
def player() -> MobaPlayerBase:
    return MobaPlayerBase(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )


@pytest.fixture
def player_instance(player) -> MobaPlayer:
    return MobaPlayer(
        first_name=player.first_name,
        last_name=player.last_name,
        date_of_birth=player.date_of_birth,
        nationality=player.nationality,
        role=player.role,
    )


async def test_create_moba_player(player: MobaPlayerBase):
    assert player.first_name == "Test"
    assert player.last_name == "Player"
    assert player.date_of_birth == date(2005, 1, 1)
    assert player.nationality == "Test"
    assert player.role == MobaPlayerRole.TOP
    assert player.mechanics == 50
    assert player.knowledge == 50
    assert player.agility == 50
    assert player.reflexes == 50
    assert player.accuracy == 50
    assert player.aggression == 50
    assert player.concentration == 50
    assert player.teamwork == 50
    assert player.concentration == 50
    assert player.decisions == 50
    assert player.vision == 50
    assert player.farming == 50
    assert player.communication == 50
    assert player.morale == 50
    assert player.form == 50


async def test_update_moba_player(player: MobaPlayerBase):
    player.first_name = "Updated"
    assert player.first_name == "Updated"


async def test_moba_player_role_assignment(player: MobaPlayerBase):
    roles = list(MobaPlayerRole)
    for role in roles:
        player.role = role
        assert player.role == role


async def test_create_moba_player_instance(player_instance: MobaPlayer, session: AsyncSession):
    session.add(player_instance)
    await session.commit()
    await session.refresh(player_instance)
    assert player_instance.id is not None
    assert player_instance.created_at is not None
    assert await session.get(MobaPlayer, player_instance.id) == player_instance


async def test_moba_player_instance_add_contract(
    player_instance: MobaPlayer, session: AsyncSession
):
    assert len(player_instance.contracts) == 0
    contract = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    player_instance.add_contract(contract)
    session.add(player_instance)
    await session.commit()
    await session.refresh(player_instance, ["contracts"])
    assert len(player_instance.contracts) == 1
    assert player_instance.contracts[0] == contract
    assert await session.get(MobaPlayerContract, contract.id) == contract


async def test_add_more_than_one_active_contract(
    player_instance: MobaPlayer, session: AsyncSession
):
    contract1 = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    contract2 = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=2,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    player_instance.add_contract(contract1)
    player_instance.add_contract(contract2)
    assert player_instance.current_contract == contract2
    assert not contract1.is_active
    assert contract2.is_active


async def test_moba_player_contract_history(player_instance: MobaPlayer, session: AsyncSession):
    contract1 = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=1,
        start_date=date(2023, 1, 1),
        end_date=date(2023, 12, 31),
        salary=1000,
        is_active=False,
    )
    contract2 = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=2,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        salary=1000,
        is_active=False,
    )
    contract3 = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=3,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    player_instance.add_contract(contract1)
    player_instance.add_contract(contract2)
    player_instance.add_contract(contract3)
    session.add(player_instance)
    await session.commit()
    await session.refresh(player_instance, ["contracts"])
    assert len(player_instance.contracts) == 3
    assert player_instance.contracts[0] == contract1
    assert player_instance.contracts[1] == contract2
    assert player_instance.contracts[2] == contract3
    assert await session.get(MobaPlayerContract, contract1.id) == contract1
    assert await session.get(MobaPlayerContract, contract2.id) == contract2
    assert await session.get(MobaPlayerContract, contract3.id) == contract3
    assert player_instance.current_contract == contract3


async def test_raises_error_end_date_before_start_date(
    player_instance: MobaPlayer, session: AsyncSession
):
    contract = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2024, 12, 31),
        salary=1000,
        is_active=True,
    )
    player_instance.add_contract(contract)
    with pytest.raises(IntegrityError):
        session.add(player_instance)
        await session.commit()
        await session.refresh(player_instance)


async def test_raises_error_salary_negative(player_instance: MobaPlayer, session: AsyncSession):
    contract = MobaPlayerContract(
        player_id=player_instance.id,
        team_id=1,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=-1,
        is_active=True,
    )
    player_instance.add_contract(contract)
    with pytest.raises(IntegrityError):
        session.add(player_instance)
        await session.commit()
        await session.refresh(player_instance)
