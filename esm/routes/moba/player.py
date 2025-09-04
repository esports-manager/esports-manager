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
from esm.models.moba.player_contract import MobaPlayerContract
from esm.models.moba.player import (
    MobaPlayer,
    MobaPlayerPublic,
    MobaPlayerCreate,
    MobaPlayerUpdate,
    MobaPlayerRole,
)
from esm.models.moba.champion import MobaChampion
from esm.models.moba.champion_mastery import (
    MobaChampionMasteryPublic,
    MobaChampionMastery,
    MobaChampionMasteryTier,
    MobaChampionMasteryUpdate,
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
    # Base queries
    query = (
        select(MobaPlayer)
        .join(
            MobaPlayerContract,
            MobaPlayerContract.player_id == MobaPlayer.id,
            isouter=True,
        )
        .join(MobaTeam, MobaTeam.id == MobaPlayerContract.team_id, isouter=True)
    )
    count_query = (
        select(MobaPlayer)
        .join(
            MobaPlayerContract,
            MobaPlayerContract.player_id == MobaPlayer.id,
            isouter=True,
        )
        .join(MobaTeam, MobaTeam.id == MobaPlayerContract.team_id, isouter=True)
    )

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
    role = request.query_params.get("role")
    nationality = request.query_params.get("nationality")
    region = request.query_params.get("region")
    team_id = request.query_params.get("team_id")
    status = request.query_params.get("status")
    search = request.query_params.get("search")
    sort = request.query_params.get("sort")
    sort_direction = request.query_params.get("direction", "asc")
    sort_map = {
        "name": MobaPlayer.nick_name,
        "role": MobaPlayer.role,
        "nationality": MobaPlayer.nationality,
    }
    search = request.query_params.get("search")

    if is_active is not None:
        # Accept 'true'/'false' strings
        active = str(is_active).lower() in ["1", "true", "yes"]
        query = query.where(MobaPlayer.is_active == active)
        count_query = count_query.where(MobaPlayer.is_active == active)
    if role:
        # Coerce to enum if possible
        try:
            role_enum = MobaPlayerRole(role)
        except Exception:
            role_enum = None
        if role_enum is not None:
            query = query.where(MobaPlayer.role == role_enum)
            count_query = count_query.where(MobaPlayer.role == role_enum)
    if nationality:
        query = query.where(MobaPlayer.nationality == nationality)
        count_query = count_query.where(MobaPlayer.nationality == nationality)
    if region:
        # Filter by the region of the player's current team (if any)
        query = query.where(MobaTeam.region == region)
        count_query = count_query.where(MobaTeam.region == region)
    if team_id:
        try:
            tid = int(team_id)
            query = query.where(
                MobaPlayerContract.is_active is True, MobaPlayerContract.team_id == tid
            )
            count_query = count_query.where(
                MobaPlayerContract.is_active is True, MobaPlayerContract.team_id == tid
            )
        except ValueError:
            pass
    if search:
        query = query.where(MobaPlayer.nick_name.icontains(search))
        count_query = count_query.where(MobaPlayer.nick_name.icontains(search))
    if status:
        status_lc = status.lower()
        if status_lc == "signed":
            query = query.where(MobaPlayerContract.is_active is True)
            count_query = count_query.where(MobaPlayerContract.is_active is True)
        elif status_lc == "free":
            # No active contract
            query = query.where(
                (MobaPlayerContract.id is None)
                | (MobaPlayerContract.is_active is False)
            )
            count_query = count_query.where(
                (MobaPlayerContract.id is None)
                | (MobaPlayerContract.is_active is False)
            )
    if sort and sort_direction:
        sort_map = {
            "name": MobaPlayer.nick_name,
            "role": MobaPlayer.role,
            "nationality": MobaPlayer.nationality,
            "overall": MobaPlayer.overall,
            "value": MobaPlayer.value,
        }
        if sort in sort_map:
            sort_field = sort_map[sort]
            if sort_direction == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

    # Avoid duplicates due to joins
    query = query.distinct(MobaPlayer.id)
    count_query = count_query.distinct(MobaPlayer.id)

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
            request,
            "components/players/players_list.html",
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


@player_routes.get("/{id}", response_model=MobaPlayerWithTeam)
async def get_player(
    *, session: Session = Depends(get_session), id: int, request: Request
):
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
            request,
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


@player_routes.delete("/{id}", response_model=dict[str, str])
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
    default_image = Path(ESM_DIR) / "res" / "img" / "players" / "default_player.webp"

    return serve_image(image_path, default_image)


@player_routes.get(
    "/{player_id}/champion_pool", response_model=list[MobaChampionMasteryPublic]
)
async def get_player_champion_pool(
    *, session: Session = Depends(get_session), player_id: int
):
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    champions = []
    for champion in player.champion_pool:
        champions.append(MobaChampionMasteryPublic.model_validate(champion))

    champions = sorted(champions, key=lambda x: (x.tier.value, x.points), reverse=True)

    return champions


@player_routes.get(
    "/{player_id}/champion_pool/{champion_id}", response_model=MobaChampionMasteryPublic
)
async def get_champion_pool(
    *, session: Session = Depends(get_session), player_id: int, champion_id: int
):
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    champion = session.get(MobaChampion, champion_id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    for champion_mastery in player.champion_pool:
        if champion_mastery.champion_id == champion_id:
            champion_mastery_data = champion_mastery.model_dump()
            champion_mastery_public = MobaChampionMasteryPublic.model_validate(
                champion_mastery_data
            )
            return champion_mastery_public
    raise HTTPException(status_code=404, detail="Champion not found in pool")


@player_routes.post(
    "/{player_id}/champion_pool/{champion_id}", response_model=MobaChampionMasteryPublic
)
async def add_champion_to_player_pool(
    *,
    request: Request,
    session: Session = Depends(get_session),
    player_id: int,
    champion_id: int,
):
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    champion = session.get(MobaChampion, champion_id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")

    for champion_mastery in player.champion_pool:
        if champion_mastery.champion_id == champion_id:
            raise HTTPException(status_code=400, detail="Champion already in pool")

    if request.query_params.get("tier"):
        tier = request.query_params.get("tier")
    else:
        tier = MobaChampionMasteryTier.BRONZE

    if request.query_params.get("points"):
        points = request.query_params.get("points")
    else:
        points = 0

    champion_mastery_data = {
        "player_id": player_id,
        "champion_id": champion_id,
        "tier": tier,
        "points": points,
    }

    champion_mastery = MobaChampionMastery.model_validate(champion_mastery_data)
    session.add(champion_mastery)
    session.commit()
    session.refresh(champion_mastery)
    return champion_mastery


@player_routes.delete(
    "/{player_id}/champion_pool/{champion_id}", response_model=dict[str, str]
)
async def remove_champion_from_player_pool(
    *, session: Session = Depends(get_session), player_id: int, champion_id: int
):
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    champion = session.get(MobaChampion, champion_id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    for champion_mastery in player.champion_pool:
        if champion_mastery.champion_id == champion_id:
            session.delete(champion_mastery)
            session.commit()
            return {"message": "Champion removed from pool"}

    raise HTTPException(status_code=404, detail="Champion not found in pool")


@player_routes.patch(
    "/{player_id}/champion_pool/{champion_id}", response_model=MobaChampionMasteryUpdate
)
async def update_champion_in_player_pool(
    *,
    session: Session = Depends(get_session),
    player_id: int,
    champion_id: int,
    champion_mastery: MobaChampionMasteryUpdate,
):
    player = session.get(MobaPlayer, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    champion = session.get(MobaChampion, champion_id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    for champion_mastery in player.champion_pool:
        if champion_mastery.champion_id == champion_id:
            champion_mastery_data = champion_mastery.model_dump(exclude_unset=True)
            champion_mastery_update = MobaChampionMasteryUpdate.model_validate(
                champion_mastery_data
            )
            champion_mastery.sqlmodel_update(
                champion_mastery_update.model_dump(exclude_unset=True)
            )
            session.add(champion_mastery)
            session.commit()
            session.refresh(champion_mastery)
            return champion_mastery

    raise HTTPException(status_code=404, detail="Champion not found in pool")
