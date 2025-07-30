# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter
from typing import Optional
from esm.db import get_session
from esm.models.moba.player import (
    MobaPlayer,
    MobaPlayerCreate,
    MobaPlayerUpdate,
    MobaPlayerPublic,
    MobaPlayerRole,
)
from sqlmodel import Session, select
from fastapi import Depends, HTTPException

player_routes = APIRouter(
    prefix="/players",
    tags=["moba_players"],
    responses={404: {"description": "Player not found"}},
)


@player_routes.get("/", response_model=list[MobaPlayerPublic])
def get_players(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    role: Optional[MobaPlayerRole] = None,
    nationality: Optional[str] = None,
):
    query = select(MobaPlayer)

    if role:
        query = query.where(MobaPlayer.role == role)
    if nationality:
        query = query.where(MobaPlayer.nationality == nationality)

    return session.exec(query.offset(skip).limit(limit)).all()


@player_routes.post("/", response_model=MobaPlayerPublic)
def create_player(*, session: Session = Depends(get_session), player: MobaPlayerCreate):
    db_player = MobaPlayer.model_validate(player)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player


@player_routes.get("/{id}", response_model=MobaPlayerPublic)
def get_player(*, session: Session = Depends(get_session), id: int):
    player = session.get(MobaPlayer, id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@player_routes.patch("/{id}", response_model=MobaPlayerPublic)
def update_player(
    *, session: Session = Depends(get_session), id: int, player: MobaPlayerUpdate
):
    db_player = session.get(MobaPlayer, id)
    if not db_player:
        raise HTTPException(status_code=404, detail="Player not found")
    player_data = player.model_dump(exclude_unset=True)
    db_player.sqlmodel_update(player_data)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player


@player_routes.delete("/{id}")
def delete_player(*, session: Session = Depends(get_session), id: int):
    player = session.get(MobaPlayer, id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player)
    session.commit()
    return {"message": "Player deleted"}
