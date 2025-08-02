# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates
from esm.config import FRONTEND_DIR, ESM_DIR
from esm.db import get_session
from esm.services import serve_image
from esm.models.moba import MobaPlayer, MobaTeam
from pathlib import Path
from esm.models.moba.player import (
    MobaPlayerPublic,
    MobaPlayerCreate,
    MobaPlayerUpdate,
)
from esm.models.moba.team import MobaTeamPublic
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
    image_url: Optional[str] = None


@player_routes.get("/")
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

    result = []
    for player in players:
        team_data = None
        player_data = player.model_dump()
        if player.current_contract and player.current_contract.team_id:
            team_data = session.get(MobaTeam, player.current_contract.team_id)
        player_with_team = MobaPlayerWithTeam.model_validate(player_data)

        # Set the team data
        player_with_team.team = team_data

        # Generate image URL for the player
        if player.image_path:
            # If image_path is a URL, use it directly
            if player.image_path.startswith("http"):
                player_with_team.image_url = player.image_path
            else:
                # If it's a local path, extract the filename and create a URL to our endpoint
                filename = Path(player.image_path).name
                player_with_team.image_url = f"/api/moba/players/images/{filename}"
        else:
            # Use default image if no image path specified
            player_with_team.image_url = "/static/img/default_player.png"

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
                    "sort": sort_by,
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


@player_routes.get("/images/{filename}")
async def get_player_image(filename: str):
    """Serve player images from the res/img/players directory"""
    image_path = Path(ESM_DIR) / "res" / "img" / "players" / filename
    return serve_image(image_path)
