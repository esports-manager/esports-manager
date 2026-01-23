# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from esm.config import ESM_DIR, FRONTEND_DIR
from esm.db import get_session
from esm.services import serve_image
from esm.models.moba.tournament import (
    MobaTournament,
    MobaTournamentCreate,
    MobaTournamentUpdate,
    MobaTournamentPublic,
)
from esm.models.tournament import TournamentType
from esm.models.moba.tournament_participant import MobaTournamentParticipant
from esm.models.moba.team import MobaTeam, MobaTeamPublic


tournament_routes = APIRouter(
    prefix="/tournaments",
    tags=["moba_tournaments"],
    responses={404: {"description": "Tournament not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


@tournament_routes.get("/", response_model=list[MobaTournamentPublic])
async def get_tournaments(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    query = select(MobaTournament)
    count_query = select(MobaTournament)

    # Filtering
    if request.query_params.get("tier"):
        query = query.where(MobaTournament.tier == request.query_params.get("tier"))
        count_query = count_query.where(
            MobaTournament.tier == request.query_params.get("tier")
        )
    if request.query_params.get("type"):
        query = query.where(MobaTournament.type == request.query_params.get("type"))
        count_query = count_query.where(
            MobaTournament.type == request.query_params.get("type")
        )
    if request.query_params.get("format"):
        query = query.where(MobaTournament.format == request.query_params.get("format"))
        count_query = count_query.where(
            MobaTournament.format == request.query_params.get("format")
        )
    # Optional location filter (maps from frontend region/location controls)
    location_param = request.query_params.get("location")
    if location_param:
        location_key = location_param.strip().lower()
        if location_key == "international":
            query = query.where(MobaTournament.type == TournamentType.INTERNATIONAL)
            count_query = count_query.where(
                MobaTournament.type == TournamentType.INTERNATIONAL
            )
        else:
            location_map = {
                "korea": ["South Korea", "Korea"],
                "china": ["China"],
                "europe": ["Europe"],
                "north_america": ["United States", "Canada"],
            }
            locations = location_map.get(location_key, [location_param])
            if len(locations) == 1:
                query = query.where(MobaTournament.location == locations[0])
                count_query = count_query.where(MobaTournament.location == locations[0])
            else:
                query = query.where(MobaTournament.location.in_(locations))
                count_query = count_query.where(MobaTournament.location.in_(locations))
    if request.query_params.get("search"):
        search = request.query_params.get("search")
        query = query.where(MobaTournament.name.icontains(search))
        count_query = count_query.where(MobaTournament.name.icontains(search))

    # Sorting
    sort_by = (request.query_params.get("sort", "start_date") or "start_date").lower()
    sort_direction = (request.query_params.get("direction", "desc") or "desc").lower()

    sort_map = {
        "name": MobaTournament.name,
        "start_date": MobaTournament.start_date,
        "end_date": MobaTournament.end_date,
        "tier": MobaTournament.tier,
    }

    if sort_by in sort_map:
        sort_field = sort_map[sort_by]
        if sort_direction == "desc":
            query = query.order_by(sort_field.desc(), MobaTournament.id.desc())
        else:
            query = query.order_by(sort_field.asc(), MobaTournament.id.asc())

    # Pagination
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

    result_query = await session.execute(query.offset(skip).limit(per_page))
    tournaments = result_query.scalars().all()

    # Pagination metadata
    count_result = await session.execute(count_query)
    total_tournaments = len(count_result.scalars().all())
    total_pages = (total_tournaments + per_page - 1) // per_page
    pagination = {
        "page": page,
        "per_page": per_page,
        "total_tournaments": total_tournaments,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "showing_start": min(skip + 1, total_tournaments)
        if total_tournaments > 0
        else 0,
        "showing_end": min(skip + per_page, total_tournaments),
    }

    # HTMX partial rendering support
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request,
            "components/tournaments/tournaments_list.html",
            {
                "request": request,
                "tournaments": tournaments,
                "pagination": pagination,
                "current_filters": {
                    "tier": request.query_params.get("tier", ""),
                    "type": request.query_params.get("type", ""),
                    "format": request.query_params.get("format", ""),
                    "location": request.query_params.get("location", ""),
                    "search": request.query_params.get("search", ""),
                    "sort": sort_by,
                    "direction": sort_direction,
                },
            },
        )

    return tournaments


@tournament_routes.post(
    "/", response_model=MobaTournament, status_code=status.HTTP_201_CREATED
)
async def create_tournament(
    *,
    session: AsyncSession = Depends(get_session),
    tournament: MobaTournamentCreate,
):
    db_tournament = MobaTournament.model_validate(tournament)
    session.add(db_tournament)
    await session.commit()
    await session.refresh(db_tournament)
    return db_tournament


@tournament_routes.get("/{id}", response_model=MobaTournamentPublic)
async def get_tournament(*, session: AsyncSession = Depends(get_session), id: int):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament = MobaTournamentPublic.model_validate(tournament.model_dump())
    return tournament


@tournament_routes.get("/{id}/teams", response_model=list[MobaTeamPublic])
async def get_tournament_teams(
    *, session: AsyncSession = Depends(get_session), id: int
):
    # Ensure tournament exists
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    result = await session.execute(
        select(MobaTournamentParticipant).where(
            MobaTournamentParticipant.tournament_id == id
        )
    )
    team_ids = [tp.team_id for tp in result.scalars().all()]
    if not team_ids:
        return []
    teams_result = await session.execute(
        select(MobaTeam).where(MobaTeam.id.in_(team_ids))
    )
    teams = teams_result.scalars().all()
    return [MobaTeamPublic.model_validate(t.model_dump()) for t in teams]


class TournamentTeamLink(BaseModel):
    team_id: int


@tournament_routes.post("/{id}/teams", status_code=status.HTTP_204_NO_CONTENT)
async def add_tournament_team(
    *, session: AsyncSession = Depends(get_session), id: int, link: TournamentTeamLink
):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    team = await session.get(MobaTeam, link.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # avoid duplicates
    result = await session.execute(
        select(MobaTournamentParticipant).where(
            (MobaTournamentParticipant.tournament_id == id)
            & (MobaTournamentParticipant.team_id == link.team_id)
        )
    )
    existing = result.scalars().first()
    if existing:
        return None
    assoc = MobaTournamentParticipant(tournament_id=id, team_id=link.team_id)
    session.add(assoc)
    await session.commit()
    return None


@tournament_routes.delete(
    "/{id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_tournament_team(
    *, session: AsyncSession = Depends(get_session), id: int, team_id: int
):
    result = await session.execute(
        select(MobaTournamentParticipant).where(
            (MobaTournamentParticipant.tournament_id == id)
            & (MobaTournamentParticipant.team_id == team_id)
        )
    )
    assoc = result.scalars().first()
    if not assoc:
        return None
    await session.delete(assoc)
    await session.commit()
    return None


@tournament_routes.patch("/{id}", response_model=MobaTournament)
async def update_tournament(
    *,
    session: AsyncSession = Depends(get_session),
    id: int,
    tournament: MobaTournamentUpdate,
):
    db_tournament = await session.get(MobaTournament, id)
    if not db_tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament.model_dump(exclude_unset=True)
    db_tournament.sqlmodel_update(tournament_data)
    session.add(db_tournament)
    await session.commit()
    await session.refresh(db_tournament)
    return db_tournament


@tournament_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(*, session: AsyncSession = Depends(get_session), id: int):
    tournament = await session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    await session.delete(tournament)
    await session.commit()
    return None


@tournament_routes.get("/images/{filename}")
async def get_tournament_image(filename: str):
    image_path = Path(ESM_DIR) / "res" / "img" / "tournaments" / filename
    return serve_image(
        image_path,
        Path(ESM_DIR) / "res" / "img" / "tournaments" / "default_tournament.webp",
    )
