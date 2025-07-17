# Import models here to make them available when importing from the models module
# Order is important to avoid circular imports
from .person import Person  # Base model (not a table)
from .champion import Champion
from .staff import (
    Staff,
    # Enums
    CoachType,
    CoachingStyle,
    Department,
    JobTitle,
    # Legacy constants may be defined in staff.py for backward compatibility
    # We're importing the enums now instead of individual constants
)
from .moba_team import MobaTeam, TeamRegion
from .champion_mastery import ChampionMastery
from .moba_player import (
    MobaPlayer,  # Inherits from Person
    PlayerRole,
    ContractStatus,
)
from .match import (
    Match,
    MatchResult,
    MatchStatus,
    MatchType,
    MatchFormat,
)
from .match_performance import (
    MatchPerformance,
    MatchPlayerStats,
    MapResult,
)
from .tournament import (
    Tournament,
    TournamentStage,
    Season,
    TournamentTeamLink,
    TournamentType,
    TournamentFormat,
    StageType,
)

__all__ = [
    "Person",
    "Champion",
    "ChampionMastery",
    "MobaTeam",
    "MobaPlayer",
    "Staff",
    "Match",
    "MatchResult",
    "MatchStatus",
    "MatchType",
    "MatchFormat",
    "MatchPerformance",
    "MatchPlayerStats",
    "MapResult",
    "Tournament",
    "TournamentStage",
    "Season",
    "TournamentTeamLink",
    "TournamentType",
    "TournamentFormat",
    "StageType",
    "PlayerRole",
    "TeamRegion",
    "CoachType",
    "CoachingStyle",
    "Department",
    "JobTitle",
    "ContractStatus",
]
