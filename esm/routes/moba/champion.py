# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status
from typing import Optional
from esm.db import get_session
from esm.models.moba.champion import (
    MobaChampion,
    MobaChampionCreate,
    MobaChampionUpdate,
    MobaChampionPublic,
    MobaChampionRole,
    MobaChampionType,
    MobaChampionDifficulty,
    MobaChampionTier,
)
from sqlmodel import Session, select
from fastapi import Depends, HTTPException

champion_routes = APIRouter(
    prefix="/champions",
    tags=["moba_champions"],
    responses={404: {"description": "Champion not found"}},
)


@champion_routes.get("/", response_model=list[MobaChampionPublic])
def get_champions(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    role: Optional[MobaChampionRole] = None,
    type: Optional[MobaChampionType] = None,
    difficulty: Optional[MobaChampionDifficulty] = None,
    tier: Optional[MobaChampionTier] = None,
):
    query = select(MobaChampion)

    if role:
        query = query.where(MobaChampion.role == role)
    if type:
        query = query.where(MobaChampion.type == type)
    if difficulty:
        query = query.where(MobaChampion.difficulty == difficulty)
    if tier:
        query = query.where(MobaChampion.tier == tier)

    return session.exec(query.offset(skip).limit(limit)).all()


@champion_routes.post(
    "/", response_model=MobaChampionPublic, status_code=status.HTTP_201_CREATED
)
def create_champion(
    *,
    session: Session = Depends(get_session),
    champion: MobaChampionCreate,
):
    db_champion = MobaChampion.model_validate(champion)
    session.add(db_champion)
    session.commit()
    session.refresh(db_champion)
    return db_champion


@champion_routes.get("/{id}/tier", response_model=MobaChampionTier)
def get_champion_tier(*, session: Session = Depends(get_session), id: int):
    champion = session.get(MobaChampion, id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    return champion.get_champion_tier()


@champion_routes.get("/{id}", response_model=MobaChampionPublic)
def get_champion(*, session: Session = Depends(get_session), id: int):
    champion = session.get(MobaChampion, id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    return champion


@champion_routes.patch("/{id}", response_model=MobaChampionPublic)
def update_champion(
    *, session: Session = Depends(get_session), id: int, champion: MobaChampionUpdate
):
    db_champion = session.get(MobaChampion, id)
    if not db_champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    champion_data = champion.model_dump(exclude_unset=True)
    db_champion.sqlmodel_update(champion_data)
    session.add(db_champion)
    session.commit()
    session.refresh(db_champion)
    return db_champion


@champion_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_champion(*, session: Session = Depends(get_session), id: int):
    champion = session.get(MobaChampion, id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    session.delete(champion)
    session.commit()
    return None
