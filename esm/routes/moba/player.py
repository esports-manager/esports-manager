# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates
from esm.config import FRONTEND_DIR
from esm.db import get_session
from esm.models.moba.player import (
    MobaPlayer,
    MobaPlayerCreate,
    MobaPlayerUpdate,
    MobaPlayerPublic,
)
from sqlmodel import Session, select
from fastapi import Depends, HTTPException

player_routes = APIRouter(
    prefix="/players",
    tags=["moba_players"],
    responses={404: {"description": "Player not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


@player_routes.get("/", response_model=list[MobaPlayerPublic])
async def get_players(
    request: Request,
    session: Session = Depends(get_session),
):
    query = select(MobaPlayer)
    count_query = select(MobaPlayer)

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

    if request.query_params.get("role"):
        query = query.where(MobaPlayer.role == request.query_params.get("role"))
        count_query = count_query.where(
            MobaPlayer.role == request.query_params.get("role")
        )
    if request.query_params.get("nationality"):
        query = query.where(
            MobaPlayer.nationality == request.query_params.get("nationality")
        )
        count_query = count_query.where(
            MobaPlayer.nationality == request.query_params.get("nationality")
        )
    if request.query_params.get("search"):
        query = query.where(
            MobaPlayer.nick_name.icontains(request.query_params.get("search"))
        )
        count_query = count_query.where(
            MobaPlayer.nick_name.icontains(request.query_params.get("search"))
        )

    sort_by = request.query_params.get("sort")
    sort_direction = request.query_params.get("direction", "asc")
    sort_map = {
        "name": MobaPlayer.nick_name,
        "role": MobaPlayer.role,
        "nationality": MobaPlayer.nationality,
    }

    if sort_by in sort_map:
        sort_field = sort_map[sort_by]
        if sort_direction == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    total_players = len(session.exec(count_query).all())
    total_pages = (total_players + per_page - 1) // per_page

    players = session.exec(query.offset(skip).limit(per_page)).all()

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
                "players": players,
                "pagination": pagination,
                "current_filters": {
                    "role": request.query_params.get("role", ""),
                    "nationality": request.query_params.get("nationality", ""),
                    "search": request.query_params.get("search", ""),
                    "sort": sort_by,
                    "direction": sort_direction,
                },
            },
        )

    return players


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


@player_routes.get("/{id}", response_model=MobaPlayerPublic)
async def get_player(*, session: Session = Depends(get_session), id: int):
    player = session.get(MobaPlayer, id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


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
