import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from esm.models.moba.team import MobaTeam, MobaTeamBase
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.player_contract import MobaPlayerContract


@pytest.fixture
def team() -> MobaTeamBase:
    return MobaTeamBase(
        name="Test Team",
        nationality="Test",
        region="Test",
        description="Test",
        logo_path="test-logo.png",
    )


@pytest.fixture
def team_instance(team) -> MobaTeam:
    return MobaTeam(
        name=team.name,
        nationality=team.nationality,
        region=team.region,
        description=team.description,
        logo_path=team.logo_path,
    )


async def test_create_moba_team(team: MobaTeamBase):
    assert team.name == "Test Team"
    assert team.nationality == "Test"
    assert team.region == "Test"
    assert team.description == "Test"
    assert team.logo_path == "test-logo.png"


async def test_update_moba_team(team: MobaTeamBase):
    team.name = "Updated Team"
    assert team.name == "Updated Team"


async def test_moba_team_instance(team_instance: MobaTeam, session: AsyncSession):
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance)
    assert team_instance.id is not None
    assert team_instance.created_at is not None
    assert await session.get(MobaTeam, team_instance.id) == team_instance


async def test_moba_team_instance_add_player(team_instance: MobaTeam, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    contract = MobaPlayerContract(
        player_id=player.id,
        team_id=team_instance.id,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    team_instance.add_player(player, contract)
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance, ["contracts"])
    assert len(team_instance.contracts) == 1
    assert team_instance.contracts[0] == contract
    assert await session.get(MobaPlayer, player.id) == player


async def test_moba_team_instance_remove_player(team_instance: MobaTeam, session: AsyncSession):
    player = MobaPlayer(
        first_name="Test",
        last_name="Player",
        date_of_birth=date(2005, 1, 1),
        nationality="Test",
        role=MobaPlayerRole.TOP,
    )
    contract = MobaPlayerContract(
        player_id=player.id,
        team_id=team_instance.id,
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        salary=1000,
        is_active=True,
    )
    team_instance.add_player(player, contract)
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance, ["contracts"])
    assert len(team_instance.contracts) == 1
    assert team_instance.contracts[0] == contract
    assert await session.get(MobaPlayer, player.id) == player
    team_instance.remove_player(player)
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance, ["contracts"])
    assert len(team_instance.contracts) == 1
    assert await session.get(MobaPlayer, player.id) == player
    contract_check = await session.get(MobaPlayerContract, contract.id)
    assert contract_check == contract
    assert not contract_check.is_active


async def test_moba_team_add_more_than_one_active_contract(
    team_instance: MobaTeam, session: AsyncSession
):
    players = []
    contracts = []
    roles = list(MobaPlayerRole)
    for i in range(5):
        player = MobaPlayer(
            first_name="Test",
            last_name="Player",
            date_of_birth=date(2005, 1, 1),
            nationality="Test",
            role=roles[i],
        )
        contract = MobaPlayerContract(
            player_id=player.id,
            team_id=team_instance.id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            salary=1000,
            is_active=True,
        )
        players.append(player)
        contracts.append(contract)
        team_instance.add_player(player, contract)
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance, ["contracts"])
    assert len(team_instance.contracts) == 5
    assert team_instance.current_players == players


async def test_moba_team_remove_one_active_contract_from_team(
    team_instance: MobaTeam, session: AsyncSession
):
    players = []
    contracts = []
    roles = list(MobaPlayerRole)
    for i in range(5):
        player = MobaPlayer(
            first_name="Test",
            last_name="Player",
            date_of_birth=date(2005, 1, 1),
            nationality="Test",
            role=roles[i],
        )
        contract = MobaPlayerContract(
            player_id=player.id,
            team_id=team_instance.id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            salary=1000,
            is_active=True,
        )
        players.append(player)
        contracts.append(contract)
        team_instance.add_player(player, contract)
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance, ["contracts"])
    assert len(team_instance.contracts) == 5
    assert team_instance.current_players == players
    team_instance.remove_player(players[0])
    session.add(team_instance)
    await session.commit()
    await session.refresh(team_instance, ["contracts"])
    assert len(team_instance.contracts) == 5
    assert len(team_instance.current_players) == 4
