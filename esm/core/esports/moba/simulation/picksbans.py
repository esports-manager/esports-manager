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
from queue import Queue

from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.mobaplayer import MobaPlayerSimulation
from esm.core.esports.moba.mobateam import MobaTeamSimulation

"""
PICKS AND BANS REWORK:

    - Picks are not specific to a player
    - Maybe assign picks to a lane
    - Give the player the option to reshuffle their picks

"""


class PicksBans:
    def __init__(
        self,
        champions: list[Champion],
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
    ):
        self.champions = champions
        self.team1 = team1
        self.team2 = team2
        self.team1_bans: list[Champion] = []
        self.team2_bans: list[Champion] = []
        self.team1_picks: list[Champion] = []
        self.team2_picks: list[Champion] = []
        self.turns = 0
        self.is_banning_phase = True

    def bans(self):
        pass

    def picks(self):
        pass

    def picks_bans(self):
        self.bans()
        self.picks()
