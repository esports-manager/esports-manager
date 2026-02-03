# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any
from urllib.parse import parse_qs
from datetime import datetime
import json

from esm.db import get_session
from esm.config import FRONTEND_DIR
from esm.models.moba import (
    MobaMatch,
    MobaMatchLineup,
    MobaMatchLineupSlot,
    MobaMatchDraftSession,
    MobaMatchDraftAction,
    MobaMatchDraftSessionPublic,
    MobaMatchDraftActionPublic,
    DraftPhase,
    DraftTeamSide,
    DraftActionType,
    LineupStatus,
    MobaChampion,
    MobaChampionMastery,
    MobaTeam,
    MobaPlayer,
)
from frontend.sidebar import sidebar

draft_routes = APIRouter(
    prefix="/draft",
    tags=["moba_draft"],
    responses={404: {"description": "Draft not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


DRAFT_ORDER = {
    DraftPhase.BAN_1: [
        (DraftTeamSide.BLUE, DraftActionType.BAN),
        (DraftTeamSide.RED, DraftActionType.BAN),
        (DraftTeamSide.BLUE, DraftActionType.BAN),
        (DraftTeamSide.RED, DraftActionType.BAN),
        (DraftTeamSide.BLUE, DraftActionType.BAN),
        (DraftTeamSide.RED, DraftActionType.BAN),
    ],
    DraftPhase.PICK_1: [
        (DraftTeamSide.BLUE, DraftActionType.PICK),
        (DraftTeamSide.RED, DraftActionType.PICK),
        (DraftTeamSide.RED, DraftActionType.PICK),
        (DraftTeamSide.BLUE, DraftActionType.PICK),
        (DraftTeamSide.BLUE, DraftActionType.PICK),
        (DraftTeamSide.RED, DraftActionType.PICK),
    ],
    DraftPhase.BAN_2: [
        (DraftTeamSide.RED, DraftActionType.BAN),
        (DraftTeamSide.BLUE, DraftActionType.BAN),
        (DraftTeamSide.RED, DraftActionType.BAN),
        (DraftTeamSide.BLUE, DraftActionType.BAN),
    ],
    DraftPhase.PICK_2: [
        (DraftTeamSide.RED, DraftActionType.PICK),
        (DraftTeamSide.BLUE, DraftActionType.PICK),
        (DraftTeamSide.BLUE, DraftActionType.PICK),
        (DraftTeamSide.RED, DraftActionType.PICK),
    ],
}

ROLES = ["top", "jungle", "mid", "adc", "support"]


def get_current_turn_info(
    draft: MobaMatchDraftSession,
) -> tuple[DraftTeamSide, DraftActionType]:
    if draft.current_phase == DraftPhase.COMPLETED:
        return None, None

    phase_order = DRAFT_ORDER.get(draft.current_phase, [])
    if draft.turn_number < len(phase_order):
        return phase_order[draft.turn_number]

    return None, None


@draft_routes.post("/match/{match_id}/initialize")
async def initialize_draft(
    match_id: int,
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

    if (
        lineup.blue_team_status != LineupStatus.CONFIRMED
        or lineup.red_team_status != LineupStatus.CONFIRMED
    ):
        raise HTTPException(status_code=400, detail="Both lineups must be confirmed")

    existing = await session.execute(
        select(MobaMatchDraftSession).where(MobaMatchDraftSession.match_id == match_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Draft already initialized")

    draft = MobaMatchDraftSession(match_id=match_id)
    session.add(draft)
    await session.commit()
    await session.refresh(draft)

    return MobaMatchDraftSessionPublic.model_validate(draft)


@draft_routes.get("/match/{match_id}")
async def get_draft(
    match_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    match = await session.get(MobaMatch, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    draft_result = await session.execute(
        select(MobaMatchDraftSession).where(MobaMatchDraftSession.match_id == match_id)
    )
    draft = draft_result.scalars().first()

    if not draft:
        draft = await initialize_draft(match_id, session)

    actions_result = await session.execute(
        select(MobaMatchDraftAction)
        .where(MobaMatchDraftAction.draft_session_id == draft.id)
        .order_by(MobaMatchDraftAction.order_index)
    )
    actions = actions_result.scalars().all()

    blue_team = await session.get(MobaTeam, match.blue_team_id)
    red_team = await session.get(MobaTeam, match.red_team_id)

    slots_result = await session.execute(
        select(MobaMatchLineupSlot)
        .where(MobaMatchLineupSlot.match_id == match_id)
        .order_by(MobaMatchLineupSlot.team_id, MobaMatchLineupSlot.slot_order)
    )
    slots = slots_result.scalars().all()

    banned_actions = [a for a in actions if a.action_type == DraftActionType.BAN]
    pick_actions = [a for a in actions if a.action_type == DraftActionType.PICK]
    banned_champion_ids = [a.champion_id for a in banned_actions]
    picked_champion_ids = [a.champion_id for a in pick_actions]

    champions_result = await session.execute(select(MobaChampion))
    all_champions = champions_result.scalars().all()
    champion_by_id = {c.id: c for c in all_champions}

    available_champions = [
        c
        for c in all_champions
        if c.id not in banned_champion_ids and c.id not in picked_champion_ids
    ]
    available_champions = sorted(
        available_champions, key=lambda c: (c.strength, c.name), reverse=True
    )

    player_ids = [slot.player_id for slot in slots if slot.player_id]
    player_masteries: dict[int, dict[int, dict[str, Any]]] = {}
    if player_ids:
        mastery_result = await session.execute(
            select(MobaChampionMastery).where(
                MobaChampionMastery.player_id.in_(player_ids)
            )
        )
        masteries = mastery_result.scalars().all()
        for mastery in masteries:
            player_masteries.setdefault(mastery.player_id, {})[mastery.champion_id] = {
                "tier": mastery.tier.value,
                "points": mastery.points,
            }
    player_masteries_json = json.dumps(player_masteries)

    pick_map = {
        (a.team_side, (a.player_slot or "").lower()): {
            "team_side": a.team_side,
            "player_slot": a.player_slot,
            "champion_id": a.champion_id,
            "champion": champion_by_id.get(a.champion_id),
            "order_index": a.order_index,
        }
        for a in pick_actions
        if a.player_slot
    }
    unassigned_picks: dict[DraftTeamSide, list[dict[str, Any]]] = {
        DraftTeamSide.BLUE: [],
        DraftTeamSide.RED: [],
    }
    for action in pick_actions:
        if action.player_slot:
            continue
        unassigned_picks[action.team_side].append(
            {
                "team_side": action.team_side,
                "champion_id": action.champion_id,
                "champion": champion_by_id.get(action.champion_id),
                "order_index": action.order_index,
            }
        )
    for picks in unassigned_picks.values():
        picks.sort(key=lambda item: item["order_index"])

    async def build_slot_payload(slot: MobaMatchLineupSlot) -> dict[str, Any]:
        team_side = (
            DraftTeamSide.BLUE
            if slot.team_id == match.blue_team_id
            else DraftTeamSide.RED
        )
        player = None
        if slot.player_id:
            player_obj = await session.get(MobaPlayer, slot.player_id)
            if player_obj:
                player = {
                    "id": player_obj.id,
                    "nick_name": player_obj.nick_name,
                    "role": player_obj.role.value,
                    "overall": player_obj.overall,
                }
        slot_role = slot.slot_role
        return {
            "id": slot.id,
            "slot_role": slot_role,
            "assigned_role": slot.assigned_role or slot.slot_role,
            "player": player,
            "team_side": team_side,
            "pick": pick_map.get((team_side, slot_role.lower())),
        }

    blue_slots: list[dict[str, Any]] = []
    red_slots: list[dict[str, Any]] = []
    for slot in slots:
        slot_payload = await build_slot_payload(slot)
        if slot.team_id == match.blue_team_id:
            blue_slots.append(slot_payload)
        else:
            red_slots.append(slot_payload)
    blue_player_ids = [
        slot["player"]["id"] for slot in blue_slots if slot.get("player")
    ]
    red_player_ids = [slot["player"]["id"] for slot in red_slots if slot.get("player")]
    blue_player_ids_json = json.dumps(blue_player_ids)
    red_player_ids_json = json.dumps(red_player_ids)

    current_turn, current_action = get_current_turn_info(draft)
    current_team_slots: list[dict[str, Any]] = []
    if current_turn:
        team_slots = blue_slots if current_turn == DraftTeamSide.BLUE else red_slots
        current_team_slots = [slot for slot in team_slots if not slot.get("pick")]

    banned_champions = [
        {
            "team_side": a.team_side,
            "champion_id": a.champion_id,
            "champion": champion_by_id.get(a.champion_id),
        }
        for a in banned_actions
    ]
    blue_bans = [
        ban for ban in banned_champions if ban["team_side"] == DraftTeamSide.BLUE
    ]
    red_bans = [
        ban for ban in banned_champions if ban["team_side"] == DraftTeamSide.RED
    ]

    context = {
        "request": request,
        "match": match,
        "draft": draft,
        "session_id": session_id,
        "blue_team": blue_team,
        "red_team": red_team,
        "actions": actions,
        "blue_slots": blue_slots,
        "red_slots": red_slots,
        "available_champions": available_champions,
        "current_turn": current_turn,
        "current_action": current_action,
        "banned_champions": banned_champions,
        "blue_bans": blue_bans,
        "red_bans": red_bans,
        "player_masteries": player_masteries,
        "player_masteries_json": player_masteries_json,
        "blue_player_ids_json": blue_player_ids_json,
        "red_player_ids_json": red_player_ids_json,
        "blue_unassigned_picks": unassigned_picks[DraftTeamSide.BLUE],
        "red_unassigned_picks": unassigned_picks[DraftTeamSide.RED],
        "current_team_slots": current_team_slots,
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "pages/champion_select.html",
            context,
        )

    layout_context = {
        **context,
        "content": "pages/champion_select.html",
        "sidebar": sidebar,
        "current_page": "matches",
    }

    return templates.TemplateResponse(
        request,
        "layout.html",
        layout_context,
    )


@draft_routes.post("/session/{draft_id}/action")
async def submit_draft_action(
    draft_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    payload: Dict[str, Any] = {}
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        body = (await request.body()).decode("utf-8")
        if body:
            parsed = parse_qs(body, keep_blank_values=True)
            payload = {
                key: values[0] if len(values) == 1 else values
                for key, values in parsed.items()
            }

    draft = await session.get(MobaMatchDraftSession, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft session not found")

    champion_id = payload.get("champion_id")
    if champion_id is None:
        raise HTTPException(status_code=400, detail="champion_id required")
    try:
        champion_id = int(champion_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="champion_id required")

    champion = await session.get(MobaChampion, champion_id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")

    player_slot = payload.get("player_slot")
    if isinstance(player_slot, str):
        player_slot = player_slot.strip() or None

    existing_actions = await session.execute(
        select(MobaMatchDraftAction).where(
            MobaMatchDraftAction.draft_session_id == draft_id,
            MobaMatchDraftAction.champion_id == champion_id,
        )
    )
    existing_action = existing_actions.scalars().first()
    if existing_action:
        if existing_action.action_type != DraftActionType.PICK:
            raise HTTPException(
                status_code=400, detail="Champion already banned or picked"
            )
        if not player_slot:
            raise HTTPException(
                status_code=400, detail="player_slot required to assign pick"
            )
        if existing_action.player_slot:
            raise HTTPException(
                status_code=400, detail="Champion already assigned to slot"
            )
        player_slot = str(player_slot).lower()
        if player_slot not in ROLES:
            raise HTTPException(status_code=400, detail="Invalid player slot")

        match = await session.get(MobaMatch, draft.match_id)
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        team_id = (
            match.blue_team_id
            if existing_action.team_side == DraftTeamSide.BLUE
            else match.red_team_id
        )
        slot_result = await session.execute(
            select(MobaMatchLineupSlot).where(
                MobaMatchLineupSlot.match_id == draft.match_id,
                MobaMatchLineupSlot.team_id == team_id,
                MobaMatchLineupSlot.slot_role == player_slot,
            )
        )
        slot = slot_result.scalars().first()
        if not slot:
            raise HTTPException(status_code=400, detail="Invalid player slot")

        existing_slot_pick = await session.execute(
            select(MobaMatchDraftAction).where(
                MobaMatchDraftAction.draft_session_id == draft_id,
                MobaMatchDraftAction.action_type == DraftActionType.PICK,
                MobaMatchDraftAction.team_side == existing_action.team_side,
                MobaMatchDraftAction.player_slot == player_slot,
            )
        )
        if existing_slot_pick.scalars().first():
            raise HTTPException(status_code=400, detail="Player slot already picked")

        assigned_role = (slot.assigned_role or slot.slot_role).lower()
        champion_roles = {champion.primary_role.value}
        if champion.secondary_role:
            champion_roles.add(champion.secondary_role.value)
        if assigned_role not in champion_roles:
            raise HTTPException(
                status_code=400,
                detail="Champion role does not match assigned role",
            )

        existing_action.player_slot = player_slot
        draft.updated_at = datetime.now()
        session.add(existing_action)
        session.add(draft)
        await session.commit()
        await session.refresh(existing_action)

        if request.headers.get("HX-Request"):
            return await get_draft(draft.match_id, request, session)

        return MobaMatchDraftActionPublic.model_validate(existing_action)

    if draft.is_completed:
        raise HTTPException(status_code=400, detail="Draft already completed")

    current_turn, current_action = get_current_turn_info(draft)

    if not current_turn or not current_action:
        raise HTTPException(status_code=400, detail="No valid turn available")

    if current_action == DraftActionType.PICK:
        if player_slot:
            player_slot = str(player_slot).lower()
            if player_slot not in ROLES:
                raise HTTPException(status_code=400, detail="Invalid player slot")

            match = await session.get(MobaMatch, draft.match_id)
            if not match:
                raise HTTPException(status_code=404, detail="Match not found")
            team_id = (
                match.blue_team_id
                if current_turn == DraftTeamSide.BLUE
                else match.red_team_id
            )
            slot_result = await session.execute(
                select(MobaMatchLineupSlot).where(
                    MobaMatchLineupSlot.match_id == draft.match_id,
                    MobaMatchLineupSlot.team_id == team_id,
                    MobaMatchLineupSlot.slot_role == player_slot,
                )
            )
            slot = slot_result.scalars().first()
            if not slot:
                raise HTTPException(status_code=400, detail="Invalid player slot")

            existing_slot_pick = await session.execute(
                select(MobaMatchDraftAction).where(
                    MobaMatchDraftAction.draft_session_id == draft_id,
                    MobaMatchDraftAction.action_type == DraftActionType.PICK,
                    MobaMatchDraftAction.team_side == current_turn,
                    MobaMatchDraftAction.player_slot == player_slot,
                )
            )
            if existing_slot_pick.scalars().first():
                raise HTTPException(
                    status_code=400, detail="Player slot already picked"
                )

            assigned_role = (slot.assigned_role or slot.slot_role).lower()
            champion_roles = {champion.primary_role.value}
            if champion.secondary_role:
                champion_roles.add(champion.secondary_role.value)
            if assigned_role not in champion_roles:
                raise HTTPException(
                    status_code=400,
                    detail="Champion role does not match assigned role",
                )
        else:
            player_slot = None
    else:
        player_slot = None

    total_actions = await session.execute(
        select(MobaMatchDraftAction).where(
            MobaMatchDraftAction.draft_session_id == draft_id
        )
    )
    order_index = len(total_actions.scalars().all())

    action = MobaMatchDraftAction(
        draft_session_id=draft_id,
        action_type=current_action,
        team_side=current_turn,
        champion_id=champion_id,
        player_slot=player_slot,
        order_index=order_index,
    )

    session.add(action)

    draft.turn_number += 1

    phase_order = DRAFT_ORDER.get(draft.current_phase, [])
    if draft.turn_number >= len(phase_order):
        if draft.current_phase == DraftPhase.BAN_1:
            draft.current_phase = DraftPhase.PICK_1
        elif draft.current_phase == DraftPhase.PICK_1:
            draft.current_phase = DraftPhase.BAN_2
        elif draft.current_phase == DraftPhase.BAN_2:
            draft.current_phase = DraftPhase.PICK_2
        elif draft.current_phase == DraftPhase.PICK_2:
            draft.current_phase = DraftPhase.COMPLETED
            draft.is_completed = True

        draft.turn_number = 0

    next_turn, _ = get_current_turn_info(draft)
    if next_turn:
        draft.current_turn = next_turn

    draft.updated_at = datetime.now()
    session.add(draft)

    await session.commit()
    await session.refresh(action)

    if request.headers.get("HX-Request"):
        return await get_draft(draft.match_id, request, session)

    return MobaMatchDraftActionPublic.model_validate(action)


@draft_routes.get("/session/{draft_id}/composition")
async def get_draft_composition(
    draft_id: int,
    session: AsyncSession = Depends(get_session),
):
    draft = await session.get(MobaMatchDraftSession, draft_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft session not found")

    if not draft.is_completed:
        raise HTTPException(status_code=400, detail="Draft not completed yet")

    actions_result = await session.execute(
        select(MobaMatchDraftAction)
        .where(
            MobaMatchDraftAction.draft_session_id == draft_id,
            MobaMatchDraftAction.action_type == DraftActionType.PICK,
        )
        .order_by(MobaMatchDraftAction.order_index)
    )
    picks = actions_result.scalars().all()

    slots_result = await session.execute(
        select(MobaMatchLineupSlot)
        .where(MobaMatchLineupSlot.match_id == draft.match_id)
        .order_by(MobaMatchLineupSlot.team_id, MobaMatchLineupSlot.slot_order)
    )
    slots = slots_result.scalars().all()

    match = await session.get(MobaMatch, draft.match_id)

    composition = {
        "match_id": draft.match_id,
        "blue_team": [],
        "red_team": [],
    }

    for pick in picks:
        champion = await session.get(MobaChampion, pick.champion_id)

        slot = next(
            (
                s
                for s in slots
                if s.team_id
                == (
                    match.blue_team_id
                    if pick.team_side == DraftTeamSide.BLUE
                    else match.red_team_id
                )
                and (pick.player_slot is None or s.slot_role == pick.player_slot)
            ),
            None,
        )

        if not slot:
            continue

        pick_data = {
            "player_id": slot.player_id,
            "champion_id": champion.id,
            "role": slot.assigned_role or slot.slot_role,
        }

        if pick.team_side == DraftTeamSide.BLUE:
            composition["blue_team"].append(pick_data)
        else:
            composition["red_team"].append(pick_data)

    return composition
