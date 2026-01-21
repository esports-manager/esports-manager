# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from datetime import datetime
from typing import List

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


@session_routes.get("/", response_model=List[MobaGameSessionPublic])
async def list_sessions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(MobaGameSession).order_by(MobaGameSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [MobaGameSessionPublic.model_validate(s.model_dump()) for s in sessions]


@session_routes.get("/{session_id}", response_model=MobaGameSessionPublic)
async def get_session_by_id(
    session_id: int, session: AsyncSession = Depends(get_session)
):
    game_session = await session.get(MobaGameSession, session_id)
    if not game_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return MobaGameSessionPublic.model_validate(game_session.model_dump())


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

    manager_name = payload.manager_name.strip()
    if not manager_name:
        raise HTTPException(status_code=400, detail="Manager name is required")

    session_name = payload.name or f"{manager_name}'s Career"

    try:
        session_db_url = await copy_base_database(base_database_url)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    seed = payload.seed if payload.seed is not None else 0

    game_session = MobaGameSession(
        name=session_name,
        manager_name=manager_name,
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

    return MobaGameSessionPublic.model_validate(game_session.model_dump())
