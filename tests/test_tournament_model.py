# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
import pytest
from sqlmodel import Session
from datetime import datetime

from esm.models.tournament import (
    TournamentBase,
    Tournament,
    TournamentType,
    TournamentFormat,
    TournamentTier,
)


@pytest.fixture
def tournament_base() -> TournamentBase:
    return TournamentBase(
        name="League of Legends World Championship 2025",
        abbreviation="Worlds 2025",
        type=TournamentType.INTERNATIONAL,
        format=TournamentFormat.SWISS,
        tier=TournamentTier.PREMIER,
        start_date=datetime(2025, 8, 1),
        end_date=datetime(2025, 8, 10),
        location="Europe",
        description="League of Legends - The most prestigious tournament of the year, featuring the best players from around the world. The most anticipated event of the year.",
        banner_path=None,
        default_color="#FFAA00",
        logo_path="/assets/tournaments/worlds.png",
    )


@pytest.fixture
def tournament_instance(tournament_base: TournamentBase) -> Tournament:
    return Tournament(
        name=tournament_base.name,
        type=tournament_base.type,
        format=tournament_base.format,
        tier=tournament_base.tier,
        start_date=tournament_base.start_date,
        end_date=tournament_base.end_date,
        location=tournament_base.location,
        description=tournament_base.description,
        banner_path=tournament_base.banner_path,
        default_color=tournament_base.default_color,
        logo_path=tournament_base.logo_path,
    )


def test_create_tournament_base(tournament_base: TournamentBase):
    assert tournament_base.name == "League of Legends World Championship 2025"
    assert tournament_base.abbreviation == "Worlds 2025"
    assert tournament_base.type == TournamentType.INTERNATIONAL
    assert tournament_base.format == TournamentFormat.SWISS
    assert tournament_base.tier == TournamentTier.PREMIER
    assert tournament_base.location == "Europe"
    assert tournament_base.description.startswith("League of Legends")
    assert tournament_base.banner_path is None
    assert tournament_base.default_color == "#FFAA00"
    assert tournament_base.logo_path == "/assets/tournaments/worlds.png"
    assert tournament_base.start_date == datetime(2025, 8, 1)
    assert tournament_base.end_date == datetime(2025, 8, 10)


def test_tournament_enums_assignment(tournament_base: TournamentBase):
    # Type enum
    for t in list(TournamentType):
        tournament_base.type = t
        assert tournament_base.type == t
    # Format enum
    for f in list(TournamentFormat):
        tournament_base.format = f
        assert tournament_base.format == f
    # Tier enum
    for tr in list(TournamentTier):
        tournament_base.tier = tr
        assert tournament_base.tier == tr


def test_tournament_instance_persistence(
    session: Session, tournament_instance: Tournament
):
    session.add(tournament_instance)
    session.commit()
    session.refresh(tournament_instance)

    assert tournament_instance.id is not None
    assert tournament_instance.created_at is not None
    assert isinstance(tournament_instance.created_at, datetime)

    fetched = session.get(Tournament, tournament_instance.id)
    assert fetched == tournament_instance
