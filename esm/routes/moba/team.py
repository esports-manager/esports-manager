# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import logging

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

logger = logging.getLogger("esm.routes.moba.team")


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
    session_id = request.query_params.get("session_id")
    logger.debug("Listing teams session_id=%s", session_id)
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

    region_aliases = {
        "europe": "LEC",
        "north america": "LCS",
        "north_america": "LCS",
        "korea": "LCK",
        "china": "LPL",
        "southeast asia": "PCS",
        "southeast_asia": "PCS",
    }
    league_codes = {"lec", "lcs", "lck", "lpl", "pcs"}

    def normalize_region(value: str) -> str:
        region_key = value.strip().lower()
        if region_key in region_aliases:
            return region_aliases[region_key]
        if region_key in league_codes:
            return region_key.upper()
        return value

    if region:
        mapped_region = normalize_region(region)
        query = query.where(MobaTeam.region == mapped_region)
        count_query = count_query.where(MobaTeam.region == mapped_region)

    if search:
        query = query.where(MobaTeam.name.icontains(search))
        count_query = count_query.where(MobaTeam.name.icontains(search))

    if league:
        mapped_league = normalize_region(league)
        query = query.where(MobaTeam.region == mapped_league)
        count_query = count_query.where(MobaTeam.region == mapped_league)

    sort_by = request.query_params.get("sort")
    sort_direction = request.query_params.get("direction", "asc")
    sort_map = {
        "name": MobaTeam.name,
        "region": MobaTeam.region,
    }

    tier_key = None
    if tier_param:
        tier_key = tier_param.strip().lower()
        if tier_key == "s+":
            tier_key = "sp"
        if tier_key not in {"sp", "s", "a", "b", "c", "d", "f"}:
            tier_key = None

    if sort_by in sort_map and tier_key is None:
        sort_field = sort_map[sort_by]
        if sort_direction == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    if tier_key:
        result_query = await session.execute(query)
        teams = result_query.scalars().all()

        def team_overall(team: MobaTeam) -> int:
            players = team.current_players
            if not players:
                return 0
            return sum(player.overall for player in players) // len(players)

        def team_tier(overall: int) -> str:
            if overall >= 95:
                return "sp"
            if overall >= 90:
                return "s"
            if overall >= 85:
                return "a"
            if overall >= 80:
                return "b"
            if overall >= 75:
                return "c"
            if overall >= 70:
                return "d"
            return "f"

        teams = [
            team
            for team in teams
            if team_tier(team_overall(team)) == tier_key
        ]

        if sort_by in sort_map:
            reverse = sort_direction == "desc"
            if sort_by == "name":
                teams.sort(key=lambda team: team.name or "", reverse=reverse)
            elif sort_by == "region":
                teams.sort(key=lambda team: team.region or "", reverse=reverse)

        total_teams = len(teams)
        total_pages = (total_teams + per_page - 1) // per_page
        teams = teams[skip : skip + per_page]
    else:
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

    logger.debug("Teams fetched count=%s page=%s", len(result), page)

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
                "session_id": session_id,
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
async def get_team_options(
    request: Request, session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(MobaTeam).order_by(MobaTeam.name))
    teams = result.scalars().all()
    logger.debug("Team options loaded count=%s", len(teams))
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/teams/team_options.html",
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
async def create_team(
    *, session: AsyncSession = Depends(get_session), team: MobaTeamCreate
):
    db_team = MobaTeam.model_validate(team)
    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    logger.info("Team created team_id=%s name=%s", db_team.id, db_team.name)
    return db_team


@team_routes.get("/{id}", response_model=MobaTeamPublic)
async def get_team(
    *, request: Request, session: AsyncSession = Depends(get_session), id: int
):
    session_id = request.query_params.get("session_id")
    team = await session.get(MobaTeam, id)
    if not team:
        logger.warning("Team not found team_id=%s", id)
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
                "session_id": session_id,
            },
        )
    logger.debug("Fetched team team_id=%s", id)
    return team_public


@team_routes.patch("/{id}", response_model=MobaTeam)
async def update_team(
    *, session: AsyncSession = Depends(get_session), id: int, team: MobaTeamUpdate
):
    db_team = await session.get(MobaTeam, id)
    if not db_team:
        logger.warning("Team not found team_id=%s", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    team_data = team.model_dump(exclude_unset=True)
    db_team.sqlmodel_update(team_data)
    session.add(db_team)
    await session.commit()
    await session.refresh(db_team)
    logger.info("Team updated team_id=%s", id)
    return db_team


@team_routes.get("/{id}/players", response_model=list[MobaPlayerPublic])
async def get_team_players(
    *, request: Request, session: AsyncSession = Depends(get_session), id: int
):
    session_id = request.query_params.get("session_id")
    result = await session.execute(
        select(MobaTeam)
        .where(MobaTeam.id == id)
        .options(
            selectinload(MobaTeam.contracts).selectinload(MobaPlayerContract.player)
        )
    )
    team = result.scalars().first()
    if not team:
        logger.warning("Team not found team_id=%s", id)
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
                "session_id": session_id,
            },
        )
    logger.debug("Team players loaded team_id=%s count=%s", id, len(players))
    return players


@team_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_team(*, session: AsyncSession = Depends(get_session), id: int):
    team = await session.get(MobaTeam, id)
    if not team:
        logger.warning("Team not found team_id=%s", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    await session.delete(team)
    await session.commit()
    logger.info("Team deleted team_id=%s", id)
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
        select(MobaTeam)
        .where(MobaTeam.id == request.contract.team_id)
        .options(
            selectinload(MobaTeam.contracts).selectinload(MobaPlayerContract.player)
        )
    )
    team = result.scalars().first()
    if not team:
        logger.warning("Team not found team_id=%s", request.contract.team_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )
    player_result = await session.execute(
        select(MobaPlayer)
        .where(MobaPlayer.id == request.contract.player_id)
        .options(selectinload(MobaPlayer.contracts))
    )
    player = player_result.scalars().first()
    if not player:
        logger.warning("Player not found player_id=%s", request.contract.player_id)
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
    logger.info(
        "Player added to team team_id=%s player_id=%s",
        request.contract.team_id,
        request.contract.player_id,
    )
    return team


@team_routes.get("/images/{filename}")
async def get_team_image(filename: str):
    image_path = Path(ESM_DIR) / "res" / "img" / "teams" / filename
    default_image = Path(ESM_DIR) / "res" / "img" / "teams" / "default_team.webp"
    return await serve_image_async(image_path, default_image)
