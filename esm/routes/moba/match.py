# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any
from sqlalchemy.orm import selectinload

from esm.db import get_session
from esm.config import FRONTEND_DIR
from esm.models.moba import (
    MobaMatch,
    MobaMatchPublic,
    MobaMatchStatus,
    MobaTeam,
)
from frontend.sidebar import sidebar

match_routes = APIRouter(
    prefix="/match",
    tags=["moba_match"],
    responses={404: {"description": "Match not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)

logger = logging.getLogger("esm.routes.moba.match")


async def _build_match_status(
    match_id: int,
    session: AsyncSession,
) -> Dict[str, Any]:
    match = await session.get(MobaMatch, match_id)
    if not match:
        logger.warning("Match not found match_id=%s", match_id)
        raise HTTPException(status_code=404, detail="Match not found")

    from esm.models.moba import MobaMatchLineup, MobaMatchDraftSession

    lineup_result = await session.execute(
        select(MobaMatchLineup).where(MobaMatchLineup.match_id == match_id)
    )
    lineup = lineup_result.scalars().first()

    draft_result = await session.execute(
        select(MobaMatchDraftSession).where(MobaMatchDraftSession.match_id == match_id)
    )
    draft = draft_result.scalars().first()

    status = {
        "match_id": match_id,
        "lineup_initialized": lineup is not None,
        "lineup_confirmed": (
            lineup.blue_team_status.value == "confirmed"
            and lineup.red_team_status.value == "confirmed"
        )
        if lineup
        else False,
        "draft_initialized": draft is not None,
        "draft_id": draft.id if draft else None,
        "draft_completed": draft.is_completed if draft else False,
        "ready_for_simulation": (draft is not None and draft.is_completed),
    }

    logger.debug("Match status built match_id=%s status=%s", match_id, status)
    return status


@match_routes.get("/list")
async def list_matches(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Get all matches with team info."""
    session_id = request.query_params.get("session_id")
    logger.debug("Listing matches session_id=%s", session_id)
    result = await session.execute(
        select(MobaMatch)
        .options(
            selectinload(MobaMatch.blue_team),
            selectinload(MobaMatch.red_team),
        )
        .order_by(MobaMatch.id.desc())
    )
    matches = result.scalars().all()

    matches_data = []
    for match in matches:
        blue_team = match.blue_team
        red_team = match.red_team

        matches_data.append(
            {
                "id": match.id,
                "status": match.status.value
                if match.status
                else MobaMatchStatus.NOT_STARTED.value,
                "blue_team": {
                    "id": blue_team.id,
                    "name": blue_team.name,
                }
                if blue_team
                else None,
                "red_team": {
                    "id": red_team.id,
                    "name": red_team.name,
                }
                if red_team
                else None,
                "created_at": match.created_at.isoformat()
                if match.created_at
                else None,
            }
        )

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/matches/matches_list.html",
            {
                "request": request,
                "matches": matches_data,
                "session_id": session_id,
            },
        )

    return matches_data


@match_routes.post("/create", response_model=MobaMatchPublic)
async def create_match(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Create a new match between two teams."""
    is_htmx = bool(request.headers.get("HX-Request"))
    session_id = request.query_params.get("session_id")
    payload: Dict[str, Any] = {}
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form = await request.form()
        payload = dict(form)

    def parse_team_id(value: Any) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return 0

    blue_team_id = parse_team_id(payload.get("blue_team_id"))
    red_team_id = parse_team_id(payload.get("red_team_id"))

    if not blue_team_id or not red_team_id:
        detail = "Both team IDs required"
        logger.warning(
            "Match creation failed missing team ids blue_team_id=%s red_team_id=%s",
            blue_team_id,
            red_team_id,
        )
        if is_htmx:
            return HTMLResponse(content=detail, status_code=200)
        raise HTTPException(status_code=400, detail=detail)

    blue_team = await session.get(MobaTeam, blue_team_id)
    red_team = await session.get(MobaTeam, red_team_id)

    if not blue_team or not red_team:
        detail = "Team not found"
        logger.warning(
            "Match creation failed team not found blue_team_id=%s red_team_id=%s",
            blue_team_id,
            red_team_id,
        )
        if is_htmx:
            return HTMLResponse(content=detail, status_code=200)
        raise HTTPException(status_code=404, detail=detail)

    match = MobaMatch(
        blue_team_id=blue_team_id,
        red_team_id=red_team_id,
        status=MobaMatchStatus.NOT_STARTED,
    )

    session.add(match)
    await session.commit()
    await session.refresh(match)

    logger.info(
        "Match created match_id=%s blue_team_id=%s red_team_id=%s",
        match.id,
        blue_team_id,
        red_team_id,
    )

    if is_htmx:
        redirect_url = f"/api/moba/match/{match.id}"
        if session_id:
            redirect_url = f"{redirect_url}?session_id={session_id}"
        return HTMLResponse(
            content="",
            status_code=201,
            headers={"HX-Redirect": redirect_url},
        )

    return MobaMatchPublic.model_validate(match)


@match_routes.get("/{match_id}")
async def get_match(
    match_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Get match details and redirect to appropriate phase."""
    match = await session.get(MobaMatch, match_id)
    if not match:
        logger.warning("Match not found match_id=%s", match_id)
        raise HTTPException(status_code=404, detail="Match not found")

    blue_team = await session.get(MobaTeam, match.blue_team_id)
    red_team = await session.get(MobaTeam, match.red_team_id)
    session_id = request.query_params.get("session_id")

    match_status = await _build_match_status(match_id, session)
    logger.debug("Loaded match overview match_id=%s", match_id)
    context = {
        "request": request,
        "match": match,
        "blue_team": blue_team,
        "red_team": red_team,
        "session_id": session_id,
        "status": match_status,
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "pages/match_overview.html",
            context,
        )

    layout_context = {
        **context,
        "content": "pages/match_overview.html",
        "sidebar": sidebar,
        "current_page": "matches",
    }

    return templates.TemplateResponse(
        request,
        "layout.html",
        layout_context,
    )


@match_routes.get("/{match_id}/status")
async def get_match_status(
    match_id: int,
    session: AsyncSession = Depends(get_session),
):
    """Get current phase status for a match."""
    return await _build_match_status(match_id, session)
