from sqlmodel import SQLModel
from typing import Optional, Any

from esm.models.moba.champion_mastery import (
    MobaChampionMastery,
    MobaChampionMasteryTier,
)
from esm.models.moba.player import MobaPlayer, MobaPlayerRole
from esm.models.moba.champion import MobaChampion


class MobaPlayerSimulation(SQLModel):
    player: MobaPlayer
    champion: MobaChampion
    role: Optional[MobaPlayerRole] = None
    mastery: Optional[MobaChampionMastery] = None
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

    def model_post_init(self, __context: Any) -> None:  # pydantic v2 hook
        if self.role is None and self.player is not None:
            self.role = self.player.role

    def get_strength(self) -> int:
        champion_strength = self.champion.strength
        mastery_tier = self.get_mastery_tier()
        if mastery_tier == MobaChampionMasteryTier.SILVER:
            champion_strength *= 1.015
        elif mastery_tier == MobaChampionMasteryTier.GOLD:
            champion_strength *= 1.03
        elif mastery_tier == MobaChampionMasteryTier.PLATINUM:
            champion_strength *= 1.05
        elif mastery_tier == MobaChampionMasteryTier.DIAMOND:
            champion_strength *= 1.08
        elif mastery_tier == MobaChampionMasteryTier.MASTER:
            champion_strength *= 1.10
        elif mastery_tier == MobaChampionMasteryTier.GRANDMASTER:
            champion_strength *= 1.15
        elif mastery_tier == MobaChampionMasteryTier.CHALLENGER:
            champion_strength *= 1.20

        strength = champion_strength + self.player.overall
        return int(strength)

    def get_score(self) -> int:
        return self.get_strength() + self.points
