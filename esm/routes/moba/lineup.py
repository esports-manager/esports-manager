# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any
from datetime import datetime

from esm.db import get_session
from esm.config import FRONTEND_DIR
from esm.models.moba import (
    MobaMatch,
    MobaMatchLineup,
    MobaMatchLineupSlot,
    MobaMatchLineupPublic,
    MobaMatchLineupSlotPublic,
    LineupStatus,
    MobaTeam,
    MobaPlayer,
    MobaPlayerContract,
)
from frontend.sidebar import sidebar

lineup_routes = APIRouter(
    prefix="/lineup",
    tags=["moba_lineup"],
    responses={404: {"description": "Lineup not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)

ROLES = ["top", "jungle", "mid", "adc", "support"]


async def _auto_assign_empty_slots(
    match: MobaMatch,
    lineup: MobaMatchLineup,
    slots: list[MobaMatchLineupSlot],
    blue_roster: list[MobaPlayer],
    red_roster: list[MobaPlayer],
    session: AsyncSession,
) -> None:
    roster_by_team = {
        match.blue_team_id: sorted(blue_roster, key=lambda p: p.overall, reverse=True),
        match.red_team_id: sorted(red_roster, key=lambda p: p.overall, reverse=True),
    }
    status_by_team = {
        match.blue_team_id: lineup.blue_team_status,
        match.red_team_id: lineup.red_team_status,
    }
    assigned_by_team = {
        match.blue_team_id: {
            slot.player_id
            for slot in slots
            if slot.team_id == match.blue_team_id and slot.player_id
        },
        match.red_team_id: {
            slot.player_id
            for slot in slots
            if slot.team_id == match.red_team_id and slot.player_id
        },
    }
    eligible_team_ids = {
        team_id for team_id, assigned in assigned_by_team.items() if not assigned
    }
    changed = False

    for slot in slots:
        if slot.team_id not in eligible_team_ids:
            continue
        if slot.player_id:
            continue
        if status_by_team.get(slot.team_id) != LineupStatus.DRAFT:
            continue
        roster = roster_by_team.get(slot.team_id, [])
        assigned_ids = assigned_by_team.get(slot.team_id, set())
        preferred = next(
            (
                player
                for player in roster
                if player.role.value == slot.slot_role and player.id not in assigned_ids
            ),
            None,
        )
        if preferred:
            slot.player_id = preferred.id
            slot.assigned_role = slot.slot_role
            slot.updated_at = datetime.now()
            session.add(slot)
            assigned_ids.add(preferred.id)
            changed = True

    if changed:
        await session.commit()


def _summarize_team_slots(
    team_slots: list[dict[str, Any]],
    team_status: LineupStatus,
) -> dict[str, Any]:
    total_slots = len(team_slots)
    assigned_slots = [slot for slot in team_slots if slot["player"]]
    assigned_count = len(assigned_slots)
    missing_roles = [slot["slot_role"] for slot in team_slots if not slot["player"]]
    off_role_slots = [
        slot
        for slot in assigned_slots
        if slot["player"]["role"] != slot["assigned_role"]
    ]
    assigned_ids = [slot["player"]["id"] for slot in assigned_slots]
    duplicate_players = len(assigned_ids) != len(set(assigned_ids))
    can_confirm = (
        team_status == LineupStatus.DRAFT
        and assigned_count == total_slots
        and not duplicate_players
    )

    return {
        "assigned_count": assigned_count,
        "total_slots": total_slots,
        "missing_roles": missing_roles,
        "missing_count": len(missing_roles),
        "off_role_count": len(off_role_slots),
        "on_role_count": assigned_count - len(off_role_slots),
        "duplicate_players": duplicate_players,
        "can_confirm": can_confirm,
    }


async def _build_lineup_context(
    match_id: int, session: AsyncSession, request: Request
) -> Dict[str, Any]:
    match = await session.get(MobaMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    lineup_result = await session.execute(
        select(MobaMatchLineup).where(MobaMatchLineup.match_id == match_id)
    )
    lineup = lineup_result.scalars().first()

    if not lineup:
        lineup = await initialize_lineup(match_id, session)

    blue_roster_result = await session.execute(
        select(MobaPlayer)
        .join(MobaPlayerContract, MobaPlayerContract.player_id == MobaPlayer.id)
        .where(
            MobaPlayerContract.team_id == match.blue_team_id,
            MobaPlayerContract.is_active == True,
        )
    )
    blue_roster = blue_roster_result.scalars().all()

    red_roster_result = await session.execute(
        select(MobaPlayer)
        .join(MobaPlayerContract, MobaPlayerContract.player_id == MobaPlayer.id)
        .where(
            MobaPlayerContract.team_id == match.red_team_id,
            MobaPlayerContract.is_active == True,
        )
    )
    red_roster = red_roster_result.scalars().all()

    slots_result = await session.execute(
        select(MobaMatchLineupSlot)
        .where(MobaMatchLineupSlot.match_id == match_id)
        .order_by(MobaMatchLineupSlot.team_id, MobaMatchLineupSlot.slot_order)
    )
    slots = slots_result.scalars().all()

    await _auto_assign_empty_slots(match, lineup, slots, blue_roster, red_roster, session)

    blue_team = await session.get(MobaTeam, match.blue_team_id)
    red_team = await session.get(MobaTeam, match.red_team_id)

    blue_slots = []
    red_slots = []

    for slot in slots:
        slot_data = {
            "id": slot.id,
            "slot_role": slot.slot_role,
            "assigned_role": slot.assigned_role or slot.slot_role,
            "player": None,
        }

        if slot.player_id:
            player = await session.get(MobaPlayer, slot.player_id)
            if player:
                slot_data["player"] = {
                    "id": player.id,
                    "nick_name": player.nick_name,
                    "role": player.role.value,
                    "overall": player.overall,
                }

        if slot.team_id == match.blue_team_id:
            blue_slots.append(slot_data)
        else:
            red_slots.append(slot_data)

    blue_assigned_ids = [
        slot["player"]["id"] for slot in blue_slots if slot["player"]
    ]
    red_assigned_ids = [
        slot["player"]["id"] for slot in red_slots if slot["player"]
    ]

    blue_summary = _summarize_team_slots(blue_slots, lineup.blue_team_status)
    red_summary = _summarize_team_slots(red_slots, lineup.red_team_status)

    return {
        "request": request,
        "match": match,
        "lineup": lineup,
        "blue_team": blue_team,
        "red_team": red_team,
        "blue_slots": blue_slots,
        "red_slots": red_slots,
        "blue_roster": blue_roster,
        "red_roster": red_roster,
        "blue_assigned_ids": blue_assigned_ids,
        "red_assigned_ids": red_assigned_ids,
        "roles": ROLES,
        "blue_summary": blue_summary,
        "red_summary": red_summary,
    }


@lineup_routes.post("/match/{match_id}/initialize")
async def initialize_lineup(
    match_id: int,
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(MobaMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    existing = await session.execute(
        select(MobaMatchLineup).where(MobaMatchLineup.match_id == match_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Lineup already initialized")
    
    lineup = MobaMatchLineup(match_id=match_id)
    session.add(lineup)
    await session.flush()
    
    for team_id in [match.blue_team_id, match.red_team_id]:
        for idx, role in enumerate(ROLES):
            slot = MobaMatchLineupSlot(
                match_id=match_id,
                team_id=team_id,
                slot_role=role,
                assigned_role=role,
                slot_order=idx,
            )
            session.add(slot)
    
    await session.commit()
    await session.refresh(lineup)
    return MobaMatchLineupPublic.model_validate(lineup)


@lineup_routes.get("/match/{match_id}")
async def get_lineup(
    match_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    context = await _build_lineup_context(match_id, session, request)
    
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "pages/lineup_setup.html",
            context,
        )

    layout_context = {
        **context,
        "content": "pages/lineup_setup.html",
        "sidebar": sidebar,
        "current_page": "matches",
    }

    return templates.TemplateResponse(
        request,
        "layout.html",
        layout_context,
    )


@lineup_routes.post("/slot/{slot_id}/assign")
async def assign_player_to_slot(
    slot_id: int,
    request: Request,
    payload: Dict[str, Any] | None = Body(default=None),
    session: AsyncSession = Depends(get_session),
):
    slot = await session.get(MobaMatchLineupSlot, slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    lineup_result = await session.execute(
        select(MobaMatchLineup).where(MobaMatchLineup.match_id == slot.match_id)
    )
    lineup = lineup_result.scalars().first()
    
    if not lineup:
        raise HTTPException(status_code=404, detail="Lineup not found")
    
    match = await session.get(MobaMatch, slot.match_id)
    team_status = (
        lineup.blue_team_status
        if slot.team_id == match.blue_team_id
        else lineup.red_team_status
    )
    
    if team_status == LineupStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Lineup already confirmed")
    
    data = payload or await request.form()
    player_id = data.get("player_id")
    assigned_role = data.get("assigned_role") or slot.slot_role
    assigned_role = str(assigned_role).lower()
    from_slot_id = data.get("from_slot_id")

    if from_slot_id in (None, "", 0, "0"):
        from_slot_id = None
    else:
        try:
            from_slot_id = int(from_slot_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid source slot")

    if assigned_role not in ROLES:
        raise HTTPException(status_code=400, detail="Invalid role assignment")

    if player_id in (None, "", 0, "0"):
        player_id = None
    else:
        try:
            player_id = int(player_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid player")

    from_slot = None
    if from_slot_id and player_id:
        from_slot = await session.get(MobaMatchLineupSlot, from_slot_id)
        if not from_slot or from_slot.match_id != slot.match_id:
            raise HTTPException(status_code=400, detail="Invalid source slot")
        if from_slot.team_id != slot.team_id:
            raise HTTPException(status_code=400, detail="Cannot move across teams")
        if from_slot.player_id != player_id:
            raise HTTPException(status_code=400, detail="Source slot mismatch")
    
    if player_id:
        player = await session.get(MobaPlayer, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")

        duplicate_query = select(MobaMatchLineupSlot).where(
            MobaMatchLineupSlot.match_id == slot.match_id,
            MobaMatchLineupSlot.team_id == slot.team_id,
            MobaMatchLineupSlot.player_id == player_id,
            MobaMatchLineupSlot.id != slot_id,
        )
        if from_slot_id:
            duplicate_query = duplicate_query.where(
                MobaMatchLineupSlot.id != from_slot_id
            )
        existing_result = await session.execute(duplicate_query)
        if existing_result.scalars().first():
            raise HTTPException(
                status_code=400, detail="Player already assigned to another slot"
            )

        contract_result = await session.execute(
            select(MobaPlayerContract).where(
                MobaPlayerContract.player_id == player_id,
                MobaPlayerContract.team_id == slot.team_id,
                MobaPlayerContract.is_active == True,
            )
        )
        if not contract_result.scalars().first():
            raise HTTPException(
                status_code=400, detail="Player does not belong to this team"
            )
    
    if from_slot and from_slot.id != slot.id:
        from_slot.player_id = None
        from_slot.updated_at = datetime.now()
        session.add(from_slot)

    slot.player_id = player_id
    slot.assigned_role = assigned_role
    slot.updated_at = datetime.now()
    
    session.add(slot)
    await session.commit()
    await session.refresh(slot)
    
    if request.headers.get("HX-Request"):
        context = await _build_lineup_context(slot.match_id, session, request)
        return templates.TemplateResponse(
            request,
            "pages/lineup_setup.html",
            context,
        )

    return MobaMatchLineupSlotPublic.model_validate(slot)


@lineup_routes.post("/match/{match_id}/team/{team_id}/confirm")
async def confirm_lineup(
    match_id: int,
    team_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(MobaMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    lineup_result = await session.execute(
        select(MobaMatchLineup).where(MobaMatchLineup.match_id == match_id)
    )
    lineup = lineup_result.scalars().first()
    
    if not lineup:
        raise HTTPException(status_code=404, detail="Lineup not initialized")
    
    slots_result = await session.execute(
        select(MobaMatchLineupSlot).where(
            MobaMatchLineupSlot.match_id == match_id,
            MobaMatchLineupSlot.team_id == team_id,
        )
    )
    slots = slots_result.scalars().all()
    
    if len(slots) != 5:
        raise HTTPException(status_code=400, detail="Must have exactly 5 slots")
    
    player_ids = set()
    assigned_roles = []
    for slot in slots:
        if not slot.player_id:
            raise HTTPException(
                status_code=400, detail=f"Slot {slot.slot_role} has no player assigned"
            )
        if slot.player_id in player_ids:
            raise HTTPException(
                status_code=400, detail="Duplicate player assignments detected"
            )
        player_ids.add(slot.player_id)

        role = (slot.assigned_role or slot.slot_role).lower()
        if role not in ROLES:
            raise HTTPException(status_code=400, detail="Invalid role assignment")
        assigned_roles.append(role)

    if len(set(assigned_roles)) != len(assigned_roles):
        raise HTTPException(
            status_code=400, detail="Duplicate role assignments detected"
        )
    
    if team_id == match.blue_team_id:
        lineup.blue_team_status = LineupStatus.CONFIRMED
    elif team_id == match.red_team_id:
        lineup.red_team_status = LineupStatus.CONFIRMED
    else:
        raise HTTPException(status_code=400, detail="Invalid team for this match")
    
    lineup.updated_at = datetime.now()
    session.add(lineup)
    await session.commit()
    await session.refresh(lineup)

    if request.headers.get("HX-Request"):
        context = await _build_lineup_context(match_id, session, request)
        return templates.TemplateResponse(
            request,
            "pages/lineup_setup.html",
            context,
        )

    return MobaMatchLineupPublic.model_validate(lineup)


@lineup_routes.post("/match/{match_id}/team/{team_id}/unlock")
async def unlock_lineup(
    match_id: int,
    team_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(MobaMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    lineup_result = await session.execute(
        select(MobaMatchLineup).where(MobaMatchLineup.match_id == match_id)
    )
    lineup = lineup_result.scalars().first()
    
    if not lineup:
        raise HTTPException(status_code=404, detail="Lineup not initialized")
    
    if team_id == match.blue_team_id:
        lineup.blue_team_status = LineupStatus.DRAFT
    elif team_id == match.red_team_id:
        lineup.red_team_status = LineupStatus.DRAFT
    else:
        raise HTTPException(status_code=400, detail="Invalid team for this match")
    
    lineup.updated_at = datetime.now()
    session.add(lineup)
    await session.commit()
    await session.refresh(lineup)

    if request.headers.get("HX-Request"):
        context = await _build_lineup_context(match_id, session, request)
        return templates.TemplateResponse(
            request,
            "pages/lineup_setup.html",
            context,
        )
    
    return MobaMatchLineupPublic.model_validate(lineup)
