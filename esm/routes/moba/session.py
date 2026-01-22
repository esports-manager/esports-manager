# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.config import Config
from esm.db import get_session
from esm.models.moba import (
    MobaGameSession,
    MobaGameSessionCreate,
    MobaGameSessionPublic,
)
from esm.models.moba.team import MobaTeam
from esm.services.game_session import copy_base_database


session_routes = APIRouter(
    prefix="/sessions",
    tags=["moba_sessions"],
    responses={404: {"description": "Session not found"}},
)


def build_display_name(
    first_name: str, last_name: str, nickname: Optional[str]
) -> str:
    if nickname:
        return nickname
    parts = [first_name.strip(), last_name.strip()]
    return " ".join(part for part in parts if part)


def build_session_public(
    game_session: MobaGameSession, team: Optional[MobaTeam]
) -> MobaGameSessionPublic:
    data = game_session.model_dump()
    data["manager_display_name"] = build_display_name(
        game_session.manager_first_name,
        game_session.manager_last_name,
        game_session.manager_nickname,
    )
    if team:
        data["team_name"] = team.name
        if team.logo_path:
            filename = Path(team.logo_path).name
            data["team_logo_url"] = f"/api/moba/teams/images/{filename}"
        if team.banner_path:
            filename = Path(team.banner_path).name
            data["team_banner_url"] = f"/api/moba/teams/images/{filename}"
    return MobaGameSessionPublic.model_validate(data)


@session_routes.get("/", response_model=List[MobaGameSessionPublic])
async def list_sessions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(MobaGameSession).order_by(MobaGameSession.created_at.desc())
    )
    sessions = result.scalars().all()
    if not sessions:
        return []
    team_ids = {game_session.team_id for game_session in sessions}
    team_result = await session.execute(
        select(MobaTeam).where(MobaTeam.id.in_(team_ids))
    )
    teams = team_result.scalars().all()
    team_map = {team.id: team for team in teams}
    return [
        build_session_public(game_session, team_map.get(game_session.team_id))
        for game_session in sessions
    ]


@session_routes.get("/{session_id}", response_model=MobaGameSessionPublic)
async def get_session_by_id(
    session_id: int, session: AsyncSession = Depends(get_session)
):
    game_session = await session.get(MobaGameSession, session_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")
    team = await session.get(MobaTeam, game_session.team_id)
    return build_session_public(game_session, team)


@session_routes.post(
    "/", response_model=MobaGameSessionPublic, status_code=status.HTTP_201_CREATED
)
async def create_session(
    payload: MobaGameSessionCreate,
    session: AsyncSession = Depends(get_session),
):
    config = Config()
    config.load_config()
    base_database_url = payload.base_database_url or config.database_url

    if payload.team_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid team selection")

    team = await session.get(MobaTeam, payload.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    manager_first_name = payload.manager_first_name.strip()
    manager_last_name = payload.manager_last_name.strip()
    manager_nickname = (payload.manager_nickname or "").strip() or None
    manager_nationality = (payload.manager_nationality or "").strip() or None

    if not manager_first_name or not manager_last_name:
        raise HTTPException(
            status_code=400, detail="Manager first and last name are required"
        )

    display_name = build_display_name(
        manager_first_name, manager_last_name, manager_nickname
    )
    session_name = payload.name or f"{display_name}'s Career"

    try:
        session_db_url = await copy_base_database(base_database_url)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    seed = payload.seed if payload.seed is not None else 0

    game_session = MobaGameSession(
        name=session_name,
        manager_first_name=manager_first_name,
        manager_last_name=manager_last_name,
        manager_nickname=manager_nickname,
        manager_birthdate=payload.manager_birthdate,
        manager_nationality=manager_nationality,
        team_id=payload.team_id,
        base_database_url=base_database_url,
        session_database_url=session_db_url,
        current_day=1,
        seed=seed,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    session.add(game_session)
    await session.commit()
    await session.refresh(game_session)

    return build_session_public(game_session, team)


@session_routes.post(
    "/{session_id}/save", response_model=MobaGameSessionPublic
)
async def save_session(
    session_id: int, session: AsyncSession = Depends(get_session)
):
    game_session = await session.get(MobaGameSession, session_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")
    game_session.updated_at = datetime.now()
    session.add(game_session)
    await session.commit()
    await session.refresh(game_session)
    team = await session.get(MobaTeam, game_session.team_id)
    return build_session_public(game_session, team)
