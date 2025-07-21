#      eSports Manager - A free and open source eSports management simulation game
#      Copyright (C) 2020-2025  Pedrenrique G. Guimarães
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .moba_player import MobaPlayer
    from .champion import Champion


class ChampionMasteryBase(SQLModel):
    player_id: int
    champion_id: int
    mastery_level: int = 0
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    kda_ratio: float = 0.0
    is_comfort_pick: bool = False
    notes: Optional[str] = None


class ChampionMasteryCreate(ChampionMasteryBase):
    pass


class ChampionMasteryRead(ChampionMasteryBase):
    id: int
    win_rate: float


class ChampionMasteryUpdate(SQLModel):
    mastery_level: Optional[int] = None
    games_played: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    kda_ratio: Optional[float] = None
    is_comfort_pick: Optional[bool] = None
    notes: Optional[str] = None


class ChampionMastery(SQLModel, table=True):
    """
    Model representing a player's mastery of a specific champion.

    This is a many-to-many relationship table between MobaPlayer and Champion
    with additional attributes to track mastery level and performance.

    Attributes:
        id: Unique identifier
        player_id: Foreign key to MobaPlayer
        champion_id: Foreign key to Champion
        mastery_level: Numeric rating of player's skill with this champion (0-100)
        games_played: Total games played with this champion
        wins: Total wins with this champion
        losses: Total losses with this champion
        kda_ratio: Kill/Death/Assist ratio with this champion
        is_comfort_pick: Whether this is a comfort pick for the player
        notes: Additional notes about the player's performance with this champion
    """

    __tablename__ = "champion_mastery"

    id: Optional[int] = Field(default=None, primary_key=True)
    player_id: int = Field(foreign_key="moba_player.id")
    champion_id: int = Field(foreign_key="champion.id")

    # Mastery metrics
    mastery_level: int = Field(default=0, ge=0, le=100)
    games_played: int = Field(default=0)
    wins: int = Field(default=0)
    losses: int = Field(default=0)
    kda_ratio: float = Field(default=0.0)
    is_comfort_pick: bool = Field(default=False)
    notes: Optional[str] = Field(default=None)

    # Relationships
    player: "MobaPlayer" = Relationship(back_populates="champion_masteries")
    champion: "Champion" = Relationship(back_populates="player_masteries")

    @property
    def win_rate(self) -> float:
        """
        Calculate win rate percentage for this champion.

        Returns:
            Float representing win rate percentage (0-100) or 0 if no games played
        """
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100.0

    def __repr__(self) -> str:
        """
        Return string representation of the ChampionMastery.

        Returns:
            String showing player-champion relationship and mastery level
        """
        return f"<ChampionMastery: Player {self.player_id} - {self.champion_id}, Level: {self.mastery_level}>"
