#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
import random
from dataclasses import dataclass
from enum import Enum, auto
from queue import Queue
from typing import Optional

from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.mobaplayer import Lanes, MobaPlayerSimulation
from esm.core.esports.moba.mobateam import MobaTeamSimulation

"""
PICKS AND BANS REWORK:

    - Picks are not specific to a player
    - Maybe assign picks to a lane
    - Give the player the option to reshuffle their picks
    - Pick and Bans AI should take into account the player's lanes
      and ban according to the opponent team's strongest picks
"""


class PBPhase(Enum):
    PICK = auto()
    BAN = auto()


@dataclass
class ChampionPB:
    champion: Champion
    available: bool = True


class PicksBans:
    def __init__(
        self,
        champions: list[Champion],
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
    ):
        self.champions = [ChampionPB(c) for c in champions]
        self.team1 = team1
        self.team2 = team2
        self.team1_bans: list[Champion] = []
        self.team2_bans: list[Champion] = []
        self.team1_picks: list[Champion] = []
        self.team2_picks: list[Champion] = []
        self.team1_ai: Optional[PicksBansAI] = None
        self.team2_ai: Optional[PicksBansAI] = None
        self.is_over = False
        self.pb_phase = PBPhase.PICK
        self.bans_count = 0
        self.picks_count = 0
        self.team_turn = False
        self.is_banning_phase = True
        self.max_bans = 5
        self.queue = Queue()


class PicksBansAI:
    def __init__(self, team: MobaTeamSimulation, champions: list[ChampionPB]):
        self.team = team
        self.champions = champions

    def pick(self):
        pass

    def ban(self):
        pass
