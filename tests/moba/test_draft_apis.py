from datetime import date

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.models.moba import (
    DraftPhase,
    DraftTeamSide,
    LineupStatus,
    MobaMatch,
    MobaMatchDraftSession,
    MobaMatchLineup,
    MobaMatchLineupSlot,
    MobaTeam,
)
from esm.models.moba.champion import (
    MobaChampion,
    MobaChampionDifficulty,
    MobaChampionRole,
    MobaChampionType,
)

ROLES = ["top", "jungle", "mid", "adc", "support"]


async def _create_match_with_lineup(session: AsyncSession) -> MobaMatch:
    blue_team = MobaTeam(name="Blue")
    red_team = MobaTeam(name="Red")
    session.add(blue_team)
    session.add(red_team)
    await session.commit()
    await session.refresh(blue_team)
    await session.refresh(red_team)

    match = MobaMatch(blue_team_id=blue_team.id, red_team_id=red_team.id)
    session.add(match)
    await session.commit()
    await session.refresh(match)

    lineup = MobaMatchLineup(
        match_id=match.id,
        blue_team_status=LineupStatus.CONFIRMED,
        red_team_status=LineupStatus.CONFIRMED,
    )
    session.add(lineup)
    await session.flush()

    for team_id in [blue_team.id, red_team.id]:
        for idx, role in enumerate(ROLES):
            slot = MobaMatchLineupSlot(
                match_id=match.id,
                team_id=team_id,
                slot_role=role,
                assigned_role=role,
                slot_order=idx,
            )
            session.add(slot)

    await session.commit()
    await session.refresh(lineup)
    return match


async def _create_champion(
    session: AsyncSession, name: str, role: MobaChampionRole
) -> MobaChampion:
    champion = MobaChampion(
        name=name,
        release_date=date(2024, 1, 1),
        primary_role=role,
        champion_type1=MobaChampionType.MAGE,
        difficulty=MobaChampionDifficulty.MEDIUM,
        strength=55,
    )
    session.add(champion)
    await session.commit()
    await session.refresh(champion)
    return champion


async def _setup_draft(
    client: AsyncClient, session: AsyncSession, turn_number: int = 0
) -> tuple[MobaMatchDraftSession, dict[str, MobaChampion]]:
    match = await _create_match_with_lineup(session)
    top_one = await _create_champion(session, "TopOne", MobaChampionRole.TOP)
    top_two = await _create_champion(session, "TopTwo", MobaChampionRole.TOP)
    mid_one = await _create_champion(session, "MidOne", MobaChampionRole.MID)

    response = await client.post(f"/api/moba/draft/match/{match.id}/initialize")
    assert response.status_code == 200

    draft_result = await session.execute(
        select(MobaMatchDraftSession).where(MobaMatchDraftSession.match_id == match.id)
    )
    draft = draft_result.scalars().first()
    assert draft is not None

    draft.current_phase = DraftPhase.PICK_1
    draft.turn_number = turn_number
    draft.current_turn = DraftTeamSide.BLUE if turn_number == 0 else DraftTeamSide.RED
    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    return draft, {"top_one": top_one, "top_two": top_two, "mid_one": mid_one}


async def test_draft_pick_allows_unassigned_then_assign(
    client: AsyncClient, session: AsyncSession
) -> None:
    draft, champions = await _setup_draft(client, session, turn_number=0)

    response = await client.post(
        f"/api/moba/draft/session/{draft.id}/action",
        json={"champion_id": champions["top_one"].id},
    )

    assert response.status_code == 200
    assert response.json()["player_slot"] is None

    response = await client.post(
        f"/api/moba/draft/session/{draft.id}/action",
        json={"champion_id": champions["top_one"].id, "player_slot": "top"},
    )

    assert response.status_code == 200
    assert response.json()["player_slot"] == "top"


async def test_draft_pick_rejects_invalid_slot(
    client: AsyncClient, session: AsyncSession
) -> None:
    draft, champions = await _setup_draft(client, session, turn_number=0)

    response = await client.post(
        f"/api/moba/draft/session/{draft.id}/action",
        json={"champion_id": champions["top_one"].id, "player_slot": "coach"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid player slot"


async def test_draft_pick_rejects_role_mismatch(
    client: AsyncClient, session: AsyncSession
) -> None:
    draft, champions = await _setup_draft(client, session, turn_number=0)

    response = await client.post(
        f"/api/moba/draft/session/{draft.id}/action",
        json={"champion_id": champions["mid_one"].id, "player_slot": "top"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Champion role does not match assigned role"


async def test_draft_pick_rejects_duplicate_slot(
    client: AsyncClient, session: AsyncSession
) -> None:
    draft, champions = await _setup_draft(client, session, turn_number=1)

    response = await client.post(
        f"/api/moba/draft/session/{draft.id}/action",
        json={"champion_id": champions["top_one"].id, "player_slot": "top"},
    )
    assert response.status_code == 200

    response = await client.post(
        f"/api/moba/draft/session/{draft.id}/action",
        json={"champion_id": champions["top_two"].id, "player_slot": "top"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Player slot already picked"
