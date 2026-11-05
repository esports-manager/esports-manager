# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Game agnostic tournament listing.

MOBA and BGMI tournaments live in their own tables because their rules
differ, but listings and search need a single view over all of them. The
helpers here normalise both models into :class:`TournamentSummary` objects
and provide the filtering, sorting and pagination used by the API.
"""

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from esm.models.bgmi.tournament import BgmiGameMode, BgmiTournament
from esm.models.game import (
    BGMI_SLUG,
    LEAGUE_OF_LEGENDS_SLUG,
    Game,
    TournamentSystem,
)
from esm.models.moba.tournament import MobaTournament
from esm.models.tournament import (
    TournamentFormat,
    TournamentStatus,
    TournamentSummary,
    TournamentTier,
    TournamentType,
)

MOBA_TOURNAMENT_PATH = "/tournaments/{id}"
BGMI_TOURNAMENT_PATH = "/tournaments/bgmi/{id}"
MOBA_TOURNAMENT_IMAGES = "/api/moba/tournaments/images/"
BGMI_TOURNAMENT_IMAGES = "/api/bgmi/tournaments/images/"

SORT_FIELDS = ("name", "start_date", "end_date", "tier")

_TIER_ORDER = {tier: index for index, tier in enumerate(TournamentTier)}


async def load_games(session: AsyncSession) -> dict[int, Game]:
    result = await session.execute(select(Game))
    return {game.id: game for game in result.scalars().all()}


def _game_identity(game: Optional[Game], fallback_slug: str, fallback_name: str):
    if game is None:
        return fallback_slug, fallback_name
    return game.slug, game.name


def summary_from_moba(
    tournament: MobaTournament, game: Optional[Game] = None
) -> TournamentSummary:
    game_slug, game_name = _game_identity(
        game, LEAGUE_OF_LEGENDS_SLUG, "League of Legends"
    )
    return TournamentSummary(
        id=tournament.id,
        name=tournament.name,
        abbreviation=tournament.abbreviation,
        type=tournament.type,
        format=tournament.format,
        tier=tournament.tier,
        status=tournament.status,
        start_date=tournament.start_date,
        end_date=tournament.end_date,
        location=tournament.location,
        description=tournament.description,
        banner_path=getattr(tournament, "banner_path", None),
        default_color=tournament.default_color,
        logo_path=tournament.logo_path,
        game_id=tournament.game_id,
        game_slug=game_slug,
        game_name=game_name,
        system=TournamentSystem.MOBA.value,
        url=MOBA_TOURNAMENT_PATH.format(id=tournament.id),
        images_url=MOBA_TOURNAMENT_IMAGES,
    )


def summary_from_bgmi(
    tournament: BgmiTournament, game: Optional[Game] = None
) -> TournamentSummary:
    game_slug, game_name = _game_identity(game, BGMI_SLUG, "BGMI")
    return TournamentSummary(
        id=tournament.id,
        name=tournament.name,
        abbreviation=tournament.abbreviation,
        type=tournament.type,
        format=tournament.format,
        tier=tournament.tier,
        status=tournament.status,
        start_date=tournament.start_date,
        end_date=tournament.end_date,
        location=tournament.location,
        description=tournament.description,
        banner_path=tournament.banner_path,
        default_color=tournament.default_color,
        logo_path=tournament.logo_path,
        game_id=tournament.game_id,
        game_slug=game_slug,
        game_name=game_name,
        system=TournamentSystem.BGMI.value,
        url=BGMI_TOURNAMENT_PATH.format(id=tournament.id),
        images_url=BGMI_TOURNAMENT_IMAGES,
    )


def apply_filters(
    query: Any,
    model: Any,
    *,
    search: Optional[str] = None,
    tier: Optional[TournamentTier] = None,
    type_: Optional[TournamentType] = None,
    format_: Optional[TournamentFormat] = None,
    status: Optional[TournamentStatus] = None,
    location: Optional[str] = None,
    game_mode: Optional[BgmiGameMode] = None,
) -> Any:
    """Apply the filters shared by every tournament table."""
    if search:
        query = query.where(model.name.icontains(search))
    if tier is not None:
        query = query.where(model.tier == tier)
    if type_ is not None:
        query = query.where(model.type == type_)
    if format_ is not None:
        query = query.where(model.format == format_)
    if status is not None:
        query = query.where(model.status == status)
    if location:
        query = query.where(model.location == location)
    if game_mode is not None and model is BgmiTournament:
        query = query.where(model.game_mode == game_mode)
    return query


def _sort_key(sort_by: str):
    if sort_by == "name":
        return lambda summary: summary.name.lower()
    if sort_by == "end_date":
        return lambda summary: summary.end_date
    if sort_by == "tier":
        return lambda summary: _TIER_ORDER.get(summary.tier, len(_TIER_ORDER))
    return lambda summary: summary.start_date


def sort_summaries(
    tournaments: list[TournamentSummary], sort_by: str, direction: str
) -> list[TournamentSummary]:
    """Sort summaries, keeping tournaments without the sort value last."""
    key = _sort_key(sort_by if sort_by in SORT_FIELDS else "start_date")
    present = [t for t in tournaments if key(t) is not None]
    missing = [t for t in tournaments if key(t) is None]
    present.sort(key=key, reverse=direction == "desc")
    return present + missing


def pagination_meta(total: int, page: int, per_page: int) -> dict[str, int | bool]:
    total_pages = (total + per_page - 1) // per_page
    skip = (page - 1) * per_page
    return {
        "page": page,
        "per_page": per_page,
        "total_tournaments": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "showing_start": min(skip + 1, total) if total > 0 else 0,
        "showing_end": min(skip + per_page, total),
    }


async def list_tournament_summaries(
    session: AsyncSession,
    *,
    system: Optional[TournamentSystem] = None,
    search: Optional[str] = None,
    tier: Optional[TournamentTier] = None,
    type_: Optional[TournamentType] = None,
    format_: Optional[TournamentFormat] = None,
    status: Optional[TournamentStatus] = None,
    location: Optional[str] = None,
    game_mode: Optional[BgmiGameMode] = None,
    sort_by: str = "start_date",
    direction: str = "desc",
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[TournamentSummary], dict[str, int | bool]]:
    """List tournaments of every system (or a single one) in one list.

    Tournaments are a small, bounded dataset, so filtering, sorting and
    pagination happen in Python after both tables are read. That keeps the
    merged listing consistent without a union query per backend.
    """
    games = await load_games(session)
    filters = {
        "search": search,
        "tier": tier,
        "type_": type_,
        "format_": format_,
        "status": status,
        "location": location,
        "game_mode": game_mode,
    }

    summaries: list[TournamentSummary] = []

    if system in (None, TournamentSystem.MOBA):
        query = apply_filters(select(MobaTournament), MobaTournament, **filters)
        rows = (await session.execute(query)).scalars().all()
        summaries.extend(summary_from_moba(row, games.get(row.game_id)) for row in rows)

    if system in (None, TournamentSystem.BGMI):
        query = apply_filters(select(BgmiTournament), BgmiTournament, **filters)
        rows = (await session.execute(query)).scalars().all()
        summaries.extend(summary_from_bgmi(row, games.get(row.game_id)) for row in rows)

    ordered = sort_summaries(summaries, sort_by, direction)

    total = len(ordered)
    skip = (page - 1) * per_page
    page_rows = ordered[skip : skip + per_page]
    return page_rows, pagination_meta(total, page, per_page)


class InvalidFilterError(ValueError):
    """Raised when a query string filter cannot be parsed."""


def parse_enum(enum_class: Any, value: str, field: str) -> Any:
    """Parse ``value`` as ``enum_class`` accepting values or member names."""
    normalized = value.strip()
    for member in enum_class:
        if member.value == normalized.lower() or member.name == normalized.upper():
            return member
    options = ", ".join(member.value for member in enum_class)
    raise InvalidFilterError(f"Invalid {field} '{value}'. Expected one of: {options}")


def pagination_from_query(page: Optional[str], per_page: Optional[str]):
    page_number = int(page) if page and page.isdigit() else 1
    page_size = int(per_page) if per_page and per_page.isdigit() else 20
    return max(1, page_number), min(100, max(1, page_size))


def filters_from_query(query_params: Any) -> dict[str, Any]:
    """Parse the tournament filters shared by the listing endpoints."""

    def _get(name: str) -> Optional[str]:
        raw = query_params.get(name)
        return raw.strip() if raw and raw.strip() else None

    filters: dict[str, Any] = {
        "search": _get("search"),
        "location": _get("location"),
    }
    for param, enum_class, key in (
        ("tier", TournamentTier, "tier"),
        ("type", TournamentType, "type_"),
        ("format", TournamentFormat, "format_"),
        ("status", TournamentStatus, "status"),
        ("game_mode", BgmiGameMode, "game_mode"),
    ):
        raw = _get(param)
        if raw:
            filters[key] = parse_enum(enum_class, raw, param)
    return filters


def sort_from_query(query_params: Any) -> tuple[str, str]:
    sort_by = (query_params.get("sort") or "start_date").lower()
    direction = (query_params.get("direction") or "desc").lower()
    if sort_by not in SORT_FIELDS:
        sort_by = "start_date"
    if direction not in ("asc", "desc"):
        direction = "desc"
    return sort_by, direction
