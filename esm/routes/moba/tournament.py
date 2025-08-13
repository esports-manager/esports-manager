# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session, select

from esm.db import get_session
from esm.models.moba.tournament import (
    MobaTournament,
    MobaTournamentCreate,
    MobaTournamentUpdate,
    MobaTournamentPublic,
)
from esm.models.moba.tournament_participant import MobaTournamentParticipant
from esm.models.moba.team import MobaTeam, MobaTeamPublic


tournament_routes = APIRouter(
    prefix="/tournaments",
    tags=["moba_tournaments"],
    responses={404: {"description": "Tournament not found"}},
)


@tournament_routes.get("/", response_model=list[MobaTournamentPublic])
async def get_tournaments(
    request: Request,
    session: Session = Depends(get_session),
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

    tournaments = session.exec(query.offset(skip).limit(per_page)).all()
    return tournaments


@tournament_routes.post(
    "/", response_model=MobaTournamentPublic, status_code=status.HTTP_201_CREATED
)
async def create_tournament(
    *,
    session: Session = Depends(get_session),
    tournament: MobaTournamentCreate,
):
    db_tournament = MobaTournament.model_validate(tournament)
    session.add(db_tournament)
    session.commit()
    session.refresh(db_tournament)
    return db_tournament


@tournament_routes.get("/{id}", response_model=MobaTournamentPublic)
async def get_tournament(*, session: Session = Depends(get_session), id: int):
    tournament = session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@tournament_routes.get("/{id}/teams", response_model=list[MobaTeamPublic])
async def get_tournament_teams(*, session: Session = Depends(get_session), id: int):
    # Ensure tournament exists
    tournament = session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    team_ids = [
        tp.team_id
        for tp in session.exec(
            select(MobaTournamentParticipant).where(
                MobaTournamentParticipant.tournament_id == id
            )
        ).all()
    ]
    if not team_ids:
        return []
    teams = session.exec(select(MobaTeam).where(MobaTeam.id.in_(team_ids))).all()
    return [MobaTeamPublic.model_validate(t.model_dump()) for t in teams]


class TournamentTeamLink(BaseModel):
    team_id: int


@tournament_routes.post("/{id}/teams", status_code=status.HTTP_204_NO_CONTENT)
async def add_tournament_team(
    *, session: Session = Depends(get_session), id: int, link: TournamentTeamLink
):
    tournament = session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    team = session.get(MobaTeam, link.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    # avoid duplicates
    existing = session.exec(
        select(MobaTournamentParticipant).where(
            (MobaTournamentParticipant.tournament_id == id)
            & (MobaTournamentParticipant.team_id == link.team_id)
        )
    ).first()
    if existing:
        return None
    assoc = MobaTournamentParticipant(tournament_id=id, team_id=link.team_id)
    session.add(assoc)
    session.commit()
    return None


@tournament_routes.delete(
    "/{id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_tournament_team(
    *, session: Session = Depends(get_session), id: int, team_id: int
):
    assoc = session.exec(
        select(MobaTournamentParticipant).where(
            (MobaTournamentParticipant.tournament_id == id)
            & (MobaTournamentParticipant.team_id == team_id)
        )
    ).first()
    if not assoc:
        return None
    session.delete(assoc)
    session.commit()
    return None


@tournament_routes.patch("/{id}", response_model=MobaTournamentPublic)
async def update_tournament(
    *,
    session: Session = Depends(get_session),
    id: int,
    tournament: MobaTournamentUpdate,
):
    db_tournament = session.get(MobaTournament, id)
    if not db_tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    tournament_data = tournament.model_dump(exclude_unset=True)
    db_tournament.sqlmodel_update(tournament_data)
    session.add(db_tournament)
    session.commit()
    session.refresh(db_tournament)
    return db_tournament


@tournament_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(*, session: Session = Depends(get_session), id: int):
    tournament = session.get(MobaTournament, id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    session.delete(tournament)
    session.commit()
    return None
