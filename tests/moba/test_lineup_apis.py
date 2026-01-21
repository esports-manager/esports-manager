from datetime import date

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.models.moba import MobaMatch, MobaMatchLineupSlot, MobaTeam
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.player_contract import MobaPlayerContract


async def _create_team_with_players(
    session: AsyncSession, name: str, roles: list[MobaPlayerRole]
) -> tuple[MobaTeam, list[MobaPlayer]]:
    team = MobaTeam(name=name)
    session.add(team)
    await session.commit()
    await session.refresh(team)

    players: list[MobaPlayer] = []
    for idx, role in enumerate(roles):
        player = MobaPlayer(
            first_name=f"{name}{idx}",
            last_name="Player",
            nick_name=f"{name}{idx}",
            date_of_birth=date(2000, 1, 1),
            nationality="Test",
            role=role,
        )
        session.add(player)
        await session.flush()
        contract = MobaPlayerContract(
            team_id=team.id,
            player_id=player.id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 12, 31),
            salary=1000,
            is_active=True,
        )
        session.add(contract)
        players.append(player)

    await session.commit()
    for player in players:
        await session.refresh(player)

    return team, players


async def _initialize_match(
    session: AsyncSession,
) -> tuple[MobaMatch, MobaTeam, MobaTeam, list[MobaPlayer], list[MobaPlayer]]:
    roles = [
        MobaPlayerRole.TOP,
        MobaPlayerRole.JUNGLE,
        MobaPlayerRole.MID,
        MobaPlayerRole.ADC,
        MobaPlayerRole.SUPPORT,
    ]
    blue_team, blue_players = await _create_team_with_players(session, "Blue", roles)
    red_team, red_players = await _create_team_with_players(session, "Red", roles)

    match = MobaMatch(blue_team_id=blue_team.id, red_team_id=red_team.id)
    session.add(match)
    await session.commit()
    await session.refresh(match)

    return match, blue_team, red_team, blue_players, red_players


async def _get_team_slots(
    session: AsyncSession, match_id: int, team_id: int
) -> list[MobaMatchLineupSlot]:
    result = await session.execute(
        select(MobaMatchLineupSlot)
        .where(
            MobaMatchLineupSlot.match_id == match_id,
            MobaMatchLineupSlot.team_id == team_id,
        )
        .order_by(MobaMatchLineupSlot.slot_order)
    )
    return result.scalars().all()


async def test_assign_lineup_rejects_wrong_team(
    client: AsyncClient, session: AsyncSession
) -> None:
    match, blue_team, _, _, red_players = await _initialize_match(session)

    response = await client.post(
        f"/api/moba/lineup/match/{match.id}/initialize"
    )
    assert response.status_code == 200

    blue_slots = await _get_team_slots(session, match.id, blue_team.id)
    slot = blue_slots[0]

    response = await client.post(
        f"/api/moba/lineup/slot/{slot.id}/assign",
        json={"player_id": red_players[0].id, "assigned_role": "top"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Player does not belong to this team"


async def test_confirm_lineup_rejects_duplicate_roles(
    client: AsyncClient, session: AsyncSession
) -> None:
    match, blue_team, _, blue_players, _ = await _initialize_match(session)

    response = await client.post(
        f"/api/moba/lineup/match/{match.id}/initialize"
    )
    assert response.status_code == 200

    blue_slots = await _get_team_slots(session, match.id, blue_team.id)
    for idx, slot in enumerate(blue_slots):
        assigned_role = "mid" if idx < 2 else slot.slot_role
        response = await client.post(
            f"/api/moba/lineup/slot/{slot.id}/assign",
            json={
                "player_id": blue_players[idx].id,
                "assigned_role": assigned_role,
            },
        )
        assert response.status_code == 200

    response = await client.post(
        f"/api/moba/lineup/match/{match.id}/team/{blue_team.id}/confirm"
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Duplicate role assignments detected"


async def test_confirm_lineup_success(
    client: AsyncClient, session: AsyncSession
) -> None:
    match, blue_team, _, blue_players, _ = await _initialize_match(session)

    response = await client.post(
        f"/api/moba/lineup/match/{match.id}/initialize"
    )
    assert response.status_code == 200

    blue_slots = await _get_team_slots(session, match.id, blue_team.id)
    for slot, player in zip(blue_slots, blue_players):
        response = await client.post(
            f"/api/moba/lineup/slot/{slot.id}/assign",
            json={
                "player_id": player.id,
                "assigned_role": slot.slot_role,
            },
        )
        assert response.status_code == 200

    response = await client.post(
        f"/api/moba/lineup/match/{match.id}/team/{blue_team.id}/confirm"
    )
    assert response.status_code == 200

    lineup_slots = await _get_team_slots(session, match.id, blue_team.id)
    assert all(slot.player_id for slot in lineup_slots)
