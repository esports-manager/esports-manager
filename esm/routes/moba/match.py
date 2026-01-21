# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Dict, Any

from esm.db import get_session
from esm.config import FRONTEND_DIR
from esm.models.moba import (
    MobaMatch,
    MobaMatchCreate,
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


@match_routes.get("/list")
async def list_matches(
    session: AsyncSession = Depends(get_session),
):
    """Get all matches with team info."""
    result = await session.execute(
        select(MobaMatch).order_by(MobaMatch.id.desc())
    )
    matches = result.scalars().all()
    
    matches_data = []
    for match in matches:
        blue_team = await session.get(MobaTeam, match.blue_team_id)
        red_team = await session.get(MobaTeam, match.red_team_id)
        
        matches_data.append({
            "id": match.id,
            "status": match.status.value if match.status else MobaMatchStatus.NOT_STARTED.value,
            "blue_team": {
                "id": blue_team.id,
                "name": blue_team.name,
            } if blue_team else None,
            "red_team": {
                "id": red_team.id,
                "name": red_team.name,
            } if red_team else None,
            "created_at": match.created_at.isoformat() if match.created_at else None,
        })
    
    return matches_data


@match_routes.post("/create", response_model=MobaMatchPublic)
async def create_match(
    payload: Dict[str, Any],
    session: AsyncSession = Depends(get_session),
):
    """Create a new match between two teams."""
    blue_team_id = payload.get("blue_team_id")
    red_team_id = payload.get("red_team_id")
    
    if not blue_team_id or not red_team_id:
        raise HTTPException(status_code=400, detail="Both team IDs required")
    
    blue_team = await session.get(MobaTeam, blue_team_id)
    red_team = await session.get(MobaTeam, red_team_id)
    
    if not blue_team or not red_team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    print(payload)
    
    match = MobaMatch(
        blue_team_id=blue_team_id,
        red_team_id=red_team_id,
        status=MobaMatchStatus.NOT_STARTED,
    )
    
    session.add(match)
    await session.commit()
    await session.refresh(match)
    
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
        raise HTTPException(status_code=404, detail="Match not found")
    
    blue_team = await session.get(MobaTeam, match.blue_team_id)
    red_team = await session.get(MobaTeam, match.red_team_id)
    
    context = {
        "request": request,
        "match": match,
        "blue_team": blue_team,
        "red_team": red_team,
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
    match = await session.get(MobaMatch, match_id)
    if not match:
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
        ) if lineup else False,
        "draft_initialized": draft is not None,
        "draft_completed": draft.is_completed if draft else False,
        "ready_for_simulation": (
            draft is not None and draft.is_completed
        ),
    }
    
    return status
