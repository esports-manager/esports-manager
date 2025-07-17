"""
Champions model for the Esports Manager.

This module defines the Champion model for representing playable characters in MOBAs.
"""

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Enum as SQLAlchemyEnum
from typing import Optional, Dict, Any, List, TYPE_CHECKING
import json
from datetime import date
from .moba_player import PlayerRole

if TYPE_CHECKING:
    from .champion_mastery import ChampionMastery


# Valid roles are now defined in the PlayerRole enum in moba_player.py


class Champion(SQLModel, table=True):
    """
    Model representing a MOBA champion/character.

    Attributes:
        id: Unique identifier
        name: Champion's name
        title: Champion's title or epithet
        primary_role: Main role/position
        secondary_role: Secondary role/position (optional)
        difficulty: Difficulty rating from 1-10
        release_date: When the champion was added to the game
        rework_date: Latest major rework (optional)
        abilities: JSON string storing abilities data
        stats: JSON string storing base and scaling stats
        description: Lore or gameplay description
        image_path: Local path to champion splash art image file
    """

    __tablename__ = "champion"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    title: str
    primary_role: PlayerRole = Field(
        sa_column=Column(SQLAlchemyEnum(PlayerRole), index=True)
    )
    secondary_role: Optional[PlayerRole] = Field(
        sa_column=Column(SQLAlchemyEnum(PlayerRole), nullable=True), default=None
    )
    difficulty: int = Field(ge=1, le=10)
    release_date: date
    rework_date: Optional[date] = Field(default=None)

    # Store abilities and stats as JSON strings
    abilities: Optional[str] = Field(default=None)
    stats: Optional[str] = Field(default=None)

    # Additional fields
    description: Optional[str] = Field(default=None)
    image_path: Optional[str] = Field(default=None)  # Path to local image file

    # Relationships
    player_masteries: List["ChampionMastery"] = Relationship(back_populates="champion")

    def get_abilities(self) -> Dict[str, Any]:
        """
        Get champion abilities as a dictionary.

        Returns:
            Dict containing ability data or empty dict if no data is set
        """
        if not self.abilities:
            return {}
        return json.loads(self.abilities)

    def set_abilities(self, abilities_dict: Dict[str, Any]) -> None:
        """
        Set champion abilities from a dictionary.

        Args:
            abilities_dict: Dictionary containing ability data
        """
        self.abilities = json.dumps(abilities_dict)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get champion stats as a dictionary.

        Returns:
            Dict containing stat data or empty dict if no data is set
        """
        if not self.stats:
            return {}
        return json.loads(self.stats)

    def set_stats(self, stats_dict: Dict[str, Any]) -> None:
        """
        Set champion stats from a dictionary.

        Args:
            stats_dict: Dictionary containing stat data
        """
        self.stats = json.dumps(stats_dict)

    def years_since_release(self) -> int:
        """
        Calculate years since champion release.

        Returns:
            Number of years since champion was released
        """
        today = date.today()
        years = today.year - self.release_date.year

        # Adjust if birthday hasn't occurred yet this year
        if (today.month, today.day) < (self.release_date.month, self.release_date.day):
            years -= 1

        return years

    def __repr__(self) -> str:
        """
        Return string representation of the Champion.

        Returns:
            String containing champion name, title, and primary role
        """
        return f"<Champion: {self.name} ({self.title}, {self.primary_role.value})>"
