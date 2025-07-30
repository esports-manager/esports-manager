# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status
from sqlmodel import SQLModel
from esm.db import get_session
from esm.models.moba.team import (
    MobaTeam,
    MobaTeamCreate,
    MobaTeamUpdate,
    MobaTeamPublic,
)
from esm.models.moba.player import MobaPlayer, MobaPlayerPublic
from esm.models.moba.player_contract import MobaPlayerContract, MobaPlayerContractCreate
from sqlmodel import Session, select
from fastapi import Depends, HTTPException


team_routes = APIRouter(
    prefix="/teams",
    tags=["moba_teams"],
    responses={404: {"description": "Team not found"}},
)


@team_routes.get("/", response_model=list[MobaTeamPublic])
def get_teams(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    query = select(MobaTeam)
    return session.exec(query.offset(skip).limit(limit)).all()


@team_routes.post(
    "/", response_model=MobaTeamPublic, status_code=status.HTTP_201_CREATED
)
def create_team(*, session: Session = Depends(get_session), team: MobaTeamCreate):
    db_team = MobaTeam.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_routes.get("/{id}", response_model=MobaTeamPublic)
def get_team(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@team_routes.patch("/{id}", response_model=MobaTeamPublic)
def update_team(
    *, session: Session = Depends(get_session), id: int, team: MobaTeamUpdate
):
    db_team = session.get(MobaTeam, id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_routes.get("/{id}/players", response_model=list[MobaPlayerPublic])
def get_team_players(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team.current_players


@team_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    session.delete(team)
    session.commit()
    return None


class AddPlayerToTeamRequest(SQLModel):
    contract: MobaPlayerContractCreate


@team_routes.post(
    "/add-player/", response_model=MobaTeamPublic, status_code=status.HTTP_201_CREATED
)
def add_player_to_team(
    *,
    session: Session = Depends(get_session),
    request: AddPlayerToTeamRequest,
):
    team = session.get(MobaTeam, request.contract.team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    player = session.get(MobaPlayer, request.contract.player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    contract = MobaPlayerContract.model_validate(request.contract)
    session.add(contract)
    session.commit()
    session.refresh(contract)
    team.add_player(player, contract)
    session.refresh(team)
    session.refresh(player)
    return team
