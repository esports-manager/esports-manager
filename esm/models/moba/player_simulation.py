from sqlmodel import SQLModel
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from esm.models.moba.champion_mastery import (
        MobaChampionMastery,
        MobaChampionMasteryTier,
    )
    from esm.models.moba.player import MobaPlayer
    from esm.models.moba.champion import MobaChampion


class MobaPlayerSimulation(SQLModel):
    player: "MobaPlayer"
    champion: "MobaChampion"
    mastery: Optional["MobaChampionMastery"] = None
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    farm: int = 0
    points: int = 0
    death_timer: int = 0

    @property
    def kda(self) -> float:
        if self.deaths == 0:
            return self.kills + self.assists
        return (self.kills + self.assists) / self.deaths

    def get_cs_per_minute(self, minutes: int) -> float:
        return self.farm / minutes

    def get_mastery_tier(self) -> MobaChampionMasteryTier:
        return self.mastery.tier if self.mastery else MobaChampionMasteryTier.BRONZE
