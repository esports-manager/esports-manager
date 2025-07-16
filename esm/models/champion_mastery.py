"""
Champion mastery model for the Esports Manager.

This module defines the relationship between MobaPlayers and Champions,
tracking their proficiency with specific champions.
"""

from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .moba_player import MobaPlayer
    from .champion import Champion


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
