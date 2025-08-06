# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates
from esm.config import FRONTEND_DIR, ESM_DIR
from esm.db import get_session
from esm.services import serve_image
from pathlib import Path
from esm.models.moba.team import MobaTeam, MobaTeamPublic
from esm.models.moba.player import (
    MobaPlayer,
    MobaPlayerPublic,
    MobaPlayerCreate,
    MobaPlayerUpdate,
)
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
from typing import Optional

player_routes = APIRouter(
    prefix="/players",
    tags=["moba_players"],
    responses={404: {"description": "Player not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


class MobaPlayerWithTeam(MobaPlayerPublic):
    team: Optional["MobaTeamPublic"] = None


@player_routes.get("/", response_model=list[MobaPlayerPublic])
async def get_players(
    request: Request,
    session: Session = Depends(get_session),
):
    query = select(MobaPlayer)
    count_query = select(MobaPlayer)

    page = 1
    per_page = 20
    current_page = request.query_params.get("page", 1)
    per_page = request.query_params.get("per_page", 20)

    if current_page:
        page = max(1, int(current_page))
    if per_page:
        per_page = min(100, max(1, int(per_page)))

    skip = (page - 1) * per_page

    is_active = request.query_params.get("is_active")
    first_name = request.query_params.get("first_name")
    last_name = request.query_params.get("last_name")
    nick_name = request.query_params.get("nick_name")
    date_of_birth = request.query_params.get("date_of_birth")
    role = request.query_params.get("role")
    nationality = request.query_params.get("nationality")
    search = request.query_params.get("search")
    sort = request.query_params.get("sort")
    sort_direction = request.query_params.get("direction", "asc")
    sort_map = {
        "name": MobaPlayer.nick_name,
        "role": MobaPlayer.role,
        "nationality": MobaPlayer.nationality,
    }
    search = request.query_params.get("search")

    if is_active:
        query = query.where(MobaPlayer.is_active == bool(is_active))
        count_query = count_query.where(MobaPlayer.is_active == bool(is_active))
    if first_name:
        query = query.where(MobaPlayer.first_name == first_name)
        count_query = count_query.where(MobaPlayer.first_name == first_name)
    if last_name:
        query = query.where(MobaPlayer.last_name == last_name)
        count_query = count_query.where(MobaPlayer.last_name == last_name)
    if nick_name:
        query = query.where(MobaPlayer.nick_name == nick_name)
        count_query = count_query.where(MobaPlayer.nick_name == nick_name)
    if date_of_birth:
        query = query.where(MobaPlayer.date_of_birth == date_of_birth)
        count_query = count_query.where(MobaPlayer.date_of_birth == date_of_birth)
    if role:
        query = query.where(MobaPlayer.role == role)
        count_query = count_query.where(MobaPlayer.role == role)
    if nationality:
        query = query.where(MobaPlayer.nationality == nationality)
        count_query = count_query.where(MobaPlayer.nationality == nationality)
    if search:
        query = query.where(MobaPlayer.nick_name.icontains(search))
        count_query = count_query.where(MobaPlayer.nick_name.icontains(search))
    if date_of_birth:
        query = query.where(MobaPlayer.date_of_birth == date_of_birth)
        count_query = count_query.where(MobaPlayer.date_of_birth == date_of_birth)
    if role:
        query = query.where(MobaPlayer.role == role)
        count_query = count_query.where(MobaPlayer.role == role)
    if nationality:
        query = query.where(MobaPlayer.nationality == nationality)
        count_query = count_query.where(MobaPlayer.nationality == nationality)
    if search:
        query = query.where(MobaPlayer.nick_name.icontains(search))
        count_query = count_query.where(MobaPlayer.nick_name.icontains(search))
    if sort and sort_direction:
        sort_map = {
            "name": MobaPlayer.nick_name,
            "role": MobaPlayer.role,
            "nationality": MobaPlayer.nationality,
        }
        if sort in sort_map:
            sort_field = sort_map[sort]
            if sort_direction == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    total_players = len(session.exec(count_query).all())
    total_pages = (total_players + per_page - 1) // per_page

    players = session.exec(query.offset(skip).limit(per_page)).all()

    result = []
    for player in players:
        team_data = None
        player_data = player.model_dump()
        if player.current_contract and player.current_contract.team_id:
            team_data = session.get(MobaTeam, player.current_contract.team_id)
            player_data["team"] = MobaTeamPublic.model_validate(team_data).model_dump()
        player_with_team = MobaPlayerWithTeam.model_validate(player_data)

        result.append(player_with_team)

    pagination = {
        "page": page,
        "per_page": per_page,
        "total_players": total_players,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "showing_start": min(skip + 1, total_players) if total_players > 0 else 0,
        "showing_end": min(skip + per_page, total_players),
    }

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/players_list.html",
            {
                "request": request,
                "players": result,
                "pagination": pagination,
                "current_filters": {
                    "role": request.query_params.get("role", ""),
                    "nationality": request.query_params.get("nationality", ""),
                    "search": request.query_params.get("search", ""),
                    "sort": sort,
                    "direction": sort_direction,
                },
            },
        )

    return result


@player_routes.post(
    "/", response_model=MobaPlayerPublic, status_code=status.HTTP_201_CREATED
)
async def create_player(
    *, session: Session = Depends(get_session), player: MobaPlayerCreate
):
    db_player = MobaPlayer.model_validate(player)
    session.add(db_player)
    session.commit()
    session.refresh(db_player)
    return db_player


@player_routes.get("/{id}")
async def get_player(*, session: Session = Depends(get_session), request: Request):
    id = int(request.path_params.get("id"))
    player = session.get(MobaPlayer, id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player_data = player.model_dump()
    team_data = None
    if player.current_contract and player.current_contract.team_id:
        team_data = session.get(MobaTeam, player.current_contract.team_id)
        player_data["team"] = MobaTeamPublic.model_validate(team_data.model_dump())
    player_with_team = MobaPlayerWithTeam.model_validate(player_data)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/player_info.html",
            {
                "request": request,
                "player": player_with_team,
            },
        )

    return player_with_team


@player_routes.patch("/{id}", response_model=MobaPlayerPublic)
async def update_player(
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
async def delete_player(*, session: Session = Depends(get_session), id: int):
    player = session.get(MobaPlayer, id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    session.delete(player)
    session.commit()
    return {"message": "Player deleted"}


@player_routes.get("/images/{filename}")
async def get_player_image(filename: str):
    """Serve player images from the res/img/players directory"""
    image_path = Path(ESM_DIR) / "res" / "img" / "players" / filename
    return serve_image(
        image_path, Path(ESM_DIR) / "res" / "img" / "players" / "default_player.webp"
    )
