# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import SQLModel, Field
from esm.config import FRONTEND_DIR, ESM_DIR
from esm.db import get_session
from esm.services import serve_image_async
from esm.models.moba.team import (
    MobaTeam,
    MobaTeamCreate,
    MobaTeamUpdate,
    MobaTeamPublic,
    MobaTeamTier,
)
from esm.models.moba.player import MobaPlayer, MobaPlayerPublic
from esm.models.moba.player_contract import MobaPlayerContract, MobaPlayerContractCreate
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import Depends, HTTPException


team_routes = APIRouter(
    prefix="/teams",
    tags=["moba_teams"],
    responses={404: {"description": "Team not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


class MobaTeamWithPlayers(MobaTeamPublic):
    players: list[MobaPlayerPublic] = Field(default_factory=list)

    @property
    def overall(self) -> int:
        if not self.players:
            return 0
        return sum(player.overall for player in self.players) // len(self.players)

    @property
    def tier(self) -> MobaTeamTier:
        if self.overall >= 95:
            return MobaTeamTier.SP
        elif self.overall >= 90:
            return MobaTeamTier.S
        elif self.overall >= 85:
            return MobaTeamTier.A
        elif self.overall >= 80:
            return MobaTeamTier.B
        elif self.overall >= 75:
            return MobaTeamTier.C
        elif self.overall >= 70:
            return MobaTeamTier.D

        return MobaTeamTier.F


@team_routes.get("/", response_model=list[MobaTeamWithPlayers])
async def get_teams(request: Request, session: AsyncSession = Depends(get_session)):
    query = select(MobaTeam).options(
        selectinload(MobaTeam.contracts).selectinload(MobaPlayerContract.player)
    )
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

    # Filters
    region = request.query_params.get("region")
    search = request.query_params.get("search")
    league = request.query_params.get("league")
    tier_param = request.query_params.get("tier")

    if region:
        query = query.where(MobaTeam.region == region)
        count_query = count_query.where(MobaTeam.region == region)

    if search:
        query = query.where(MobaTeam.name.icontains(search))
        count_query = count_query.where(MobaTeam.name.icontains(search))

    if league:
        query = query.where(MobaTeam.league == league)
        count_query = count_query.where(MobaTeam.league == league)

    # Tier filter based on overall thresholds mirroring MobaTeamWithPlayers.tier logic
    if tier_param:
        tier_param = tier_param.lower()
        lower_bound = None
        if tier_param == "sp":
            lower_bound = 95
        elif tier_param == "s":
            lower_bound = 90
        elif tier_param == "a":
            lower_bound = 85
        elif tier_param == "b":
            lower_bound = 80
        elif tier_param == "c":
            lower_bound = 75
        elif tier_param == "d":
            lower_bound = 70

        if lower_bound is not None:
            # Approximate using stored overall if present; if overall is not a stored column,
            # we fall back to name-only filters and leave tier as UI-only. Here we assume
            # teams have a numeric 'overall' field; if not, remove this or replace with a join/aggregate.
            try:
                query = query.where(MobaTeam.overall >= lower_bound)
                count_query = count_query.where(MobaTeam.overall >= lower_bound)
            except AttributeError:
                pass

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

    count_result = await session.execute(count_query)
    total_teams = len(count_result.scalars().all())
    total_pages = (total_teams + per_page - 1) // per_page

    result_query = await session.execute(query.offset(skip).limit(per_page))
    teams = result_query.scalars().all()

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
        if team.banner_path:
            filename = Path(team.banner_path).name
            team_data["image_banner"] = f"/api/moba/teams/images/{filename}"

        result.append(MobaTeamWithPlayers.model_validate(team_data))

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
            request,
            "components/teams/teams_list.html",
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


@team_routes.get("/options")
async def get_team_options(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(MobaTeam).order_by(MobaTeam.name))
    teams = result.scalars().all()
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/team_options.html",
            {
                "request": request,
                "teams": teams,
            },
        )
    # Fallback JSON
    return [{"id": t.id, "name": t.name} for t in teams]


@team_routes.post(
    "/", response_model=MobaTeamPublic, status_code=status.HTTP_201_CREATED
)
async def create_team(*, session: AsyncSession = Depends(get_session), team: MobaTeamCreate):
    db_team = MobaTeam.model_validate(team)
    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    return db_team


@team_routes.get("/{id}", response_model=MobaTeamPublic)
async def get_team(
    *, request: Request, session: AsyncSession = Depends(get_session), id: int
):
    team = await session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump()
    team_public = MobaTeamPublic.model_validate(team_data)

    if request.headers.get("HX-Request"):
        if team.current_players:
            team_data["players"] = [
                MobaPlayerPublic.model_validate(player.model_dump())
                for player in team.current_players
            ]
        if team.logo_path:
            filename = Path(team.logo_path).name
            team_data["image_url"] = f"/api/moba/teams/images/{filename}"
        if team.banner_path:
            filename = Path(team.banner_path).name
            team_data["image_banner"] = f"/api/moba/teams/images/{filename}"
        team_public = MobaTeamWithPlayers.model_validate(team_data)
        return templates.TemplateResponse(
            request,
            "components/team_info.html",
            {
                "request": request,
                "team": team_public,
            },
        )

    return team_public


@team_routes.patch("/{id}", response_model=MobaTeam)
async def update_team(
    *, session: AsyncSession = Depends(get_session), id: int, team: MobaTeamUpdate
):
    db_team = await session.get(MobaTeam, id)
    if not db_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    return db_team


@team_routes.get("/{id}/players", response_model=list[MobaPlayerPublic])
async def get_team_players(
    *, request: Request, session: AsyncSession = Depends(get_session), id: int
):
    result = await session.execute(
        select(MobaTeam).where(MobaTeam.id == id).options(
            selectinload(MobaTeam.contracts).selectinload(MobaPlayerContract.player)
        )
    )
    team = result.scalars().first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    players = []
    for player in team.current_players:
        player_data = player.model_dump()
        players.append(MobaPlayerPublic.model_validate(player_data))

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/team_players.html",
            {
                "request": request,
                "players": players,
                "team": team,
            },
        )
    return players


@team_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(*, session: AsyncSession = Depends(get_session), id: int):
    team = await session.get(MobaTeam, id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    await session.delete(team)
    await session.commit()
    return None


class AddPlayerToTeamRequest(SQLModel):
    contract: MobaPlayerContractCreate


@team_routes.post(
    "/add-player/", response_model=MobaTeamPublic, status_code=status.HTTP_201_CREATED
)
async def add_player_to_team(
    *,
    session: AsyncSession = Depends(get_session),
    request: AddPlayerToTeamRequest,
):
    result = await session.execute(
        select(MobaTeam).where(MobaTeam.id == request.contract.team_id).options(
            selectinload(MobaTeam.contracts).selectinload(MobaPlayerContract.player)
        )
    )
    team = result.scalars().first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    player_result = await session.execute(
        select(MobaPlayer).where(MobaPlayer.id == request.contract.player_id).options(selectinload(MobaPlayer.contracts))
    )
    player = player_result.scalars().first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Player not found"
        )
    contract = MobaPlayerContract.model_validate(request.contract)
    session.add(contract)
    await session.commit()
    await session.refresh(contract)
    team.add_player(player, contract)
    await session.refresh(team, ["contracts"])
    await session.refresh(player)
    return team


@team_routes.get("/images/{filename}")
async def get_team_image(filename: str):
    image_path = Path(ESM_DIR) / "res" / "img" / "teams" / filename
    default_image = Path(ESM_DIR) / "res" / "img" / "teams" / "default_team.webp"
    return await serve_image_async(image_path, default_image)
