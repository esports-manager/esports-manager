# SPDX-FileCopyrightText: 2025 Pedrenrique G. Guimarães <admin@esportsmanager.net>
# SPDX-License-Identifier: GPL-3.0-or-later
# License-Filename: LICENSES/GPL-3.0-or-later
"""Teams registered for a BGMI tournament.

The project does not have a game agnostic team entity yet, so BGMI events
reuse the existing team registry (``moba_teams``). When a generic team model
lands this foreign key should move to it.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel

# Imported for its side effect: SQLAlchemy needs the referenced table in the
# metadata registry when this foreign key is resolved.
from esm.models.moba.team import MobaTeam  # noqa: F401


class BgmiTournamentParticipant(SQLModel, table=True):
    __tablename__ = "bgmi_tournament_participants"

    id: Optional[int] = Field(default=None, primary_key=True)
    tournament_id: int = Field(foreign_key="bgmi_tournaments.id", index=True)
    team_id: int = Field(foreign_key="moba_teams.id", index=True)

    created_at: datetime = Field(
        default_factory=datetime.now, sa_column=Column(DateTime)
    )
    updated_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime))
