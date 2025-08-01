# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
from fastapi import APIRouter, status, Request
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
from esm.db import get_session
from esm.config import FRONTEND_DIR
from esm.models.moba.champion import (
    MobaChampion,
    MobaChampionCreate,
    MobaChampionUpdate,
    MobaChampionPublic,
    MobaChampionRole,
    MobaChampionTier,
)
from sqlmodel import Session, select
from fastapi import Depends, HTTPException
import random

champion_routes = APIRouter(
    prefix="/champions",
    tags=["moba_champions"],
    responses={404: {"description": "Champion not found"}},
)

templates_dir = FRONTEND_DIR / "templates"
templates = Jinja2Templates(directory=templates_dir)


@champion_routes.get("/", response_model=list[MobaChampionPublic])
async def get_champions(
    request: Request,
    session: Session = Depends(get_session),
):
    query = select(MobaChampion)
    count_query = select(MobaChampion)

    # Handle pagination
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

    # Apply filters
    if request.query_params.get("role"):
        query = query.where(
            MobaChampion.primary_role == request.query_params.get("role")
        )
        count_query = count_query.where(
            MobaChampion.primary_role == request.query_params.get("role")
        )
    if request.query_params.get("type"):
        query = query.where(
            MobaChampion.champion_type1 == request.query_params.get("type")
        )
        count_query = count_query.where(
            MobaChampion.champion_type1 == request.query_params.get("type")
        )
    if request.query_params.get("difficulty"):
        query = query.where(
            MobaChampion.difficulty == request.query_params.get("difficulty")
        )
        count_query = count_query.where(
            MobaChampion.difficulty == request.query_params.get("difficulty")
        )
    # Handle tier filtering based on strength ranges
    if request.query_params.get("tier"):
        query = query.where(
            MobaChampion.champion_tier == request.query_params.get("tier")
        )
        count_query = count_query.where(
            MobaChampion.champion_tier == request.query_params.get("tier")
        )
    if request.query_params.get("search"):
        query = query.where(
            MobaChampion.name.icontains(request.query_params.get("search"))
        )
        count_query = count_query.where(
            MobaChampion.name.icontains(request.query_params.get("search"))
        )

    # Handle sorting
    sort_by = request.query_params.get("sort", "name")
    sort_direction = request.query_params.get("direction", "asc")

    # Map frontend sort fields to model attributes
    sort_map = {
        "name": MobaChampion.name,
        "winrate": MobaChampion.win_rate,
        "pickrate": MobaChampion.pick_rate,
        "banrate": MobaChampion.ban_rate,
    }

    # Apply sorting if the field exists in our mapping
    if sort_by in sort_map:
        sort_field = sort_map[sort_by]
        if sort_direction == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    # Count total champions matching filters
    total_champions = len(session.exec(count_query).all())
    total_pages = (total_champions + per_page - 1) // per_page  # Ceiling division

    # Execute query with pagination
    champions = session.exec(query.offset(skip).limit(per_page)).all()

    # Calculate pagination metadata
    pagination = {
        "page": page,
        "per_page": per_page,
        "total_champions": total_champions,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "showing_start": min(skip + 1, total_champions) if total_champions > 0 else 0,
        "showing_end": min(skip + per_page, total_champions),
    }

    # Return HTMX response or regular API response
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            "components/champions_list.html",
            {
                "request": request,
                "champions": champions,
                "pagination": pagination,
                "current_filters": {
                    "role": request.query_params.get("role", ""),
                    "difficulty": request.query_params.get("difficulty", ""),
                    "tier": request.query_params.get("tier", ""),
                    "search": request.query_params.get("search", ""),
                    "sort": sort_by,
                    "direction": sort_direction,
                },
            },
        )

    return champions


@champion_routes.post(
    "/", response_model=MobaChampionPublic, status_code=status.HTTP_201_CREATED
)
async def create_champion(
    *,
    session: Session = Depends(get_session),
    champion: MobaChampionCreate,
):
    db_champion = MobaChampion.model_validate(champion)
    session.add(db_champion)
    session.commit()
    session.refresh(db_champion)
    return db_champion


@champion_routes.get("/{id}/tier", response_model=MobaChampionTier)
async def get_champion_tier(*, session: Session = Depends(get_session), id: int):
    champion = session.get(MobaChampion, id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    return champion.champion_tier


@champion_routes.get("/{id}", response_model=MobaChampionPublic)
async def get_champion(*, session: Session = Depends(get_session), id: int):
    champion = session.get(MobaChampion, id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    return champion


@champion_routes.patch("/{id}", response_model=MobaChampionPublic)
async def update_champion(
    *, session: Session = Depends(get_session), id: int, champion: MobaChampionUpdate
):
    db_champion = session.get(MobaChampion, id)
    if not db_champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    champion_data = champion.model_dump(exclude_unset=True)
    db_champion.sqlmodel_update(champion_data)
    session.add(db_champion)
    session.commit()
    session.refresh(db_champion)
    return db_champion


@champion_routes.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_champion(*, session: Session = Depends(get_session), id: int):
    champion = session.get(MobaChampion, id)
    if not champion:
        raise HTTPException(status_code=404, detail="Champion not found")
    session.delete(champion)
    session.commit()
    return None


@champion_routes.get("/meta", response_model=Dict[str, Any])
async def get_champion_meta(
    request: Request,
    role: Optional[str] = None,
    session: Session = Depends(get_session),
):
    """
    Get meta statistics and information for champions.
    If role is specified, return meta data for that specific role.
    Otherwise, return overview meta data.
    """
    # Current patch information - simulated for now
    current_patch = {
        "version": "13.5",
        "name": "Midseason Update",
        "date": "2025-07-15",
        "major_changes": [
            "Baron and Dragon buff adjustments",
            "Jungle experience rebalancing",
            "Tower resistance changes",
        ],
    }

    # Basic meta statistics - would be calculated from match data in a real implementation
    meta_stats = {
        "avg_game_time": "28:47",
        "game_time_change": "+1:23",
        "first_baron_win_rate": 78.3,
        "baron_win_rate_change": +4.7,
        "avg_kills_per_game": 26.5,
        "kills_change": +3.2,
        "blue_side_win_rate": 51.4,
        "blue_side_change": -0.8,
    }

    # Fetch top champions by win rate
    query = select(MobaChampion).order_by(MobaChampion.win_rate.desc())
    if role:
        query = query.where(MobaChampion.primary_role == role)
    top_meta_champions = session.exec(query.limit(5)).all()

    # Get most banned champions
    query_banned = select(MobaChampion).order_by(MobaChampion.ban_rate.desc())
    most_banned_champions = session.exec(query_banned.limit(5)).all()

    # Get champion with highest pick rate
    query_picked = select(MobaChampion).order_by(MobaChampion.pick_rate.desc())
    most_picked_champions = session.exec(query_picked.limit(5)).all()

    # Get top champions by role
    role_champions = {}
    for role_type in MobaChampionRole:
        query_role = (
            select(MobaChampion)
            .where(MobaChampion.primary_role == role_type.value)
            .order_by(MobaChampion.win_rate.desc())
        )
        role_champions[role_type.value] = session.exec(query_role.limit(3)).all()

    # Get meta changes (champions rising/falling in meta)
    # In a real implementation, this would compare to previous patch data
    # Here we'll simulate with random data
    all_champions = session.exec(select(MobaChampion)).all()
    rising_champions = random.sample(all_champions, min(3, len(all_champions)))
    falling_champions = random.sample(
        [c for c in all_champions if c not in rising_champions],
        min(3, len(all_champions)),
    )

    meta_changes = {
        "rising": [
            {"id": champ.id, "name": champ.name, "change": random.randint(5, 15)}
            for champ in rising_champions
        ],
        "falling": [
            {"id": champ.id, "name": champ.name, "change": -random.randint(5, 12)}
            for champ in falling_champions
        ],
    }

    # Get strongest champion type in the current meta
    champion_types_count = {}
    for champ in top_meta_champions:
        if champ.champion_type1.value in champion_types_count:
            champion_types_count[champ.champion_type1.value] += 1
        else:
            champion_types_count[champ.champion_type1.value] = 1

        if champ.champion_type2 and champ.champion_type2.value in champion_types_count:
            champion_types_count[champ.champion_type2.value] += 0.5
        elif champ.champion_type2:
            champion_types_count[champ.champion_type2.value] = 0.5

    strongest_class = max(
        champion_types_count.items(), key=lambda x: x[1], default=("unknown", 0)
    )

    # Role-specific meta information
    role_meta = {
        "top": {
            "description": "The current top lane meta favors tanks and fighters who can absorb pressure and scale into late game.",
            "preferred_playstyle": "Split-pushing and flanking",
        },
        "jungle": {
            "description": "Early game pressure junglers with high mobility dominate the current meta.",
            "preferred_playstyle": "Aggressive invades and early objective control",
        },
        "mid": {
            "description": "Burst mages and mobile assassins are thriving in the current meta with roaming potential.",
            "preferred_playstyle": "Roaming and skirmishing",
        },
        "bot": {
            "description": "Hypercarry marksmen with strong late game potential are favored in the current meta.",
            "preferred_playstyle": "Scaling and team fighting",
        },
        "support": {
            "description": "Engage and peel supports are equally viable, with preference for those with strong early lane presence.",
            "preferred_playstyle": "Roaming and vision control",
        },
    }

    # Compile all the data
    meta_data = {
        "current_patch": current_patch,
        "meta_stats": meta_stats,
        "top_champions": [champion for champion in top_meta_champions],
        "most_banned": [champion for champion in most_banned_champions],
        "most_picked": [champion for champion in most_picked_champions],
        "role_champions": role_champions,
        "meta_changes": meta_changes,
        "strongest_class": strongest_class[0] if strongest_class else "unknown",
        "role_meta": role_meta,
    }

    # Return HTMX response or regular API response
    if request.headers.get("HX-Request"):
        selected_role = role if role else "overview"
        return templates.TemplateResponse(
            "components/champions_meta.html",
            {
                "request": request,
                "meta_data": meta_data,
                "selected_role": selected_role,
            },
        )

    return meta_data
