# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import SQLModel
from typing import Optional
from esm.config import FRONTEND_DIR, ESM_DIR
from esm.db import get_session
from esm.services import serve_image
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

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


class MobaTeamWithPlayers(MobaTeamPublic):
    players: list[MobaPlayerPublic] = []
    image_url: Optional[str] = None
    image_banner: Optional[str] = None


@team_routes.get("/", response_model=list[MobaTeamPublic])
async def get_teams(request: Request, session: Session = Depends(get_session)):
    query = select(MobaTeam)
    count_query = select(MobaTeam)

    page = 1
    per_page = 20

    if request.query_params.get("page") and request.query_params.get("page").isdigit():
        page = max(1, int(request.query_params.get("page")))
    if (
        request.query_params.get("per_page")
        and request.query_params.get("per_page").isdigit()
    ):
        per_page = min(100, max(1, int(request.query_params.get("per_page"))))
    skip = (page - 1) * per_page

    if request.query_params.get("region"):
        query = query.where(MobaTeam.region == request.query_params.get("region"))
    if request.query_params.get("search"):
        query = query.where(MobaTeam.name.icontains(request.query_params.get("search")))

    sort_by = request.query_params.get("sort")
    sort_direction = request.query_params.get("direction", "asc")
    sort_map = {
        "name": MobaTeam.name,
        "region": MobaTeam.region,
    }

    if sort_by in sort_map:
        sort_field = sort_map[sort_by]
        if sort_direction == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    total_teams = len(session.exec(count_query).all())
    total_pages = (total_teams + per_page - 1) // per_page

    teams = session.exec(query.offset(skip).limit(per_page)).all()

    result = []
    for team in teams:
        team_data = team.model_dump()
        if team.current_players:
            team_data["players"] = [
                MobaPlayerPublic.model_validate(player.model_dump())
                for player in team.current_players
            ]
        if team.logo_path:
            filename = Path(team.logo_path).name
            team_data["image_url"] = f"/api/moba/teams/images/{filename}"

        result.append(MobaTeamPublic.model_validate(team_data))

    pagination = {
        "page": page,
        "per_page": per_page,
        "total_teams": total_teams,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "showing_start": min(skip + 1, total_teams) if total_teams > 0 else 0,
        "showing_end": min(skip + per_page, total_teams),
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/teams_list.html",
            {
                "request": request,
                "teams": result,
                "pagination": pagination,
                "current_filters": {
                    "region": request.query_params.get("region", ""),
                    "league": request.query_params.get("league", ""),
                    "tier": request.query_params.get("tier", ""),
                    "search": request.query_params.get("search", ""),
                    "sort": sort_by,
                    "direction": sort_direction,
                },
            },
        )

    return result


@team_routes.post(
    "/", response_model=MobaTeamPublic, status_code=status.HTTP_201_CREATED
)
async def create_team(*, session: Session = Depends(get_session), team: MobaTeamCreate):
    db_team = MobaTeam.model_validate(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@team_routes.get("/{id}", response_model=MobaTeamPublic)
async def get_team(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team


@team_routes.patch("/{id}", response_model=MobaTeamPublic)
async def update_team(
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
async def get_team_players(*, session: Session = Depends(get_session), id: int):
    team = session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    return team.current_players


@team_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(*, session: Session = Depends(get_session), id: int):
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
async def add_player_to_team(
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


@team_routes.get("/images/{filename}")
async def get_team_image(filename: str):
    image_path = Path(ESM_DIR) / "res" / "img" / "teams" / filename
    return serve_image(image_path)
