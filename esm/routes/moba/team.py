# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter
from esm import get_session
from esm.models.moba.team import MobaTeam, MobaTeamCreate, MobaTeamUpdate, MobaPlayer
from sqlmodel import Session, select
from fastapi import Depends, HTTPException


team_routes = APIRouter(
    prefix="/teams",
    tags=["moba_teams"],
    responses={404: {"description": "Team not found"}},
)


@team_routes.get("/", response_model=list[MobaTeam])
def get_teams(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    query = select(MobaTeam)
    return session.exec(query.offset(skip).limit(limit)).all()


@team_routes.post("/", response_model=MobaTeam)
def create_team(*, session: Session = Depends(get_session), team: MobaTeamCreate):
    db_team = MobaTeam.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_routes.get("/{id}", response_model=MobaTeam)
def get_team(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@team_routes.patch("/{id}", response_model=MobaTeam)
def update_team(
    *, session: Session = Depends(get_session), id: int, team: MobaTeamUpdate
):
    db_team = session.get(MobaTeam, id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_routes.get("/{id}/players", response_model=list[MobaPlayer])
def get_team_players(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.players


@team_routes.delete("/{id}")
def delete_team(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"message": "Team deleted"}
