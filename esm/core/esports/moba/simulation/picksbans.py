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
from enum import Enum, auto
from queue import Queue
from typing import Optional

from esm.core.esports.moba.champion import Champion
from esm.core.esports.moba.mobaplayer import Lanes
from esm.core.esports.moba.mobateam import MobaTeamSimulation

"""
PICKS AND BANS REWORK:

    - Picks are not specific to a player
    - Maybe assign picks to a lane
    - Give the player the option to reshuffle their picks
    - Pick and Bans AI should take into account the player's lanes
      and ban according to the opponent team's strongest picks
"""
from abc import ABC, abstractmethod


class PBPhase(Enum):
    PICK_BLUE_SIDE = auto()
    BAN_BLUE_SIDE = auto()
    PICK_RED_SIDE = auto()
    BAN_RED_SIDE = auto()
    PB_DONE = auto()


class PickBanInput(ABC):
    @abstractmethod
    def pick(self):
        pass

    @abstractmethod
    def ban(self):
        pass


class PicksBans:
    def __init__(
        self,
        champions: list[Champion],
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
        team1_input: Optional[PickBanInput] = None,
        team2_input: Optional[PickBanInput] = None,
    ):
        self.champions = champions
        self.team1 = team1
        self.team2 = team2
        self.team1_bans: list[Champion] = []
        self.team2_bans: list[Champion] = []
        self.team1_picks: list[Champion] = []
        self.team2_picks: list[Champion] = []
        if team1_input is None:
            self.team1_input: Optional[PickBanInput] = PicksBansAI(team1, champions)
        else:
            self.team1_input = team1_input
        if team2_input is None:
            self.team2_input: Optional[PickBanInput] = PicksBansAI(team2, champions)
        else:
            self.team2_input: Optional[PickBanInput] = team2_input
        self.is_over = False
        self.pb_phase = PBPhase.BAN_BLUE_SIDE
        self.bans_count = 0
        self.picks_count = 0
        self.max_bans = 10
        self.queue = Queue()

    def bans(self):
        if self.pb_phase == PBPhase.BAN_BLUE_SIDE:
            self.team1_input.ban()
            self.bans_count += 1
            if self.bans_count == self.max_bans:
                self.pb_phase = PBPhase.PICK_RED_SIDE
            else:
                self.pb_phase = PBPhase.BAN_RED_SIDE
        elif self.pb_phase == PBPhase.BAN_RED_SIDE:
            self.team2_input.ban()
            self.bans_count += 1
            if self.bans_count == 6 and self.picks_count == 0:
                self.pb_phase = PBPhase.PICK_BLUE_SIDE
            else:
                self.pb_phase = PBPhase.BAN_BLUE_SIDE

    def picks(self):
        if self.pb_phase == PBPhase.PICK_BLUE_SIDE:
            if self.picks_count == 0:
                self.team1_input.pick()
            else:
                self.team1_input.pick()
                self.team1_input.pick()
                self.picks_count += 1

            self.picks_count += 1
            self.pb_phase = PBPhase.PICK_RED_SIDE
        elif self.pb_phase == PBPhase.PICK_RED_SIDE:
            if self.picks_count == 5 or self.picks_count == 6 or self.picks_count == 9:
                self.team2_input.pick()
            else:
                self.team2_input.pick()
                self.team2_input.pick()
                self.picks_count += 1

            self.picks_count += 1
            self.pb_phase = PBPhase.PICK_BLUE_SIDE

            if self.picks_count == 6 and self.bans_count == 6:
                self.pb_phase = PBPhase.BAN_RED_SIDE
            elif self.picks_count == 10:
                self.is_over = True
                self.pb_phase = PBPhase.PB_DONE
            else:
                self.pb_phase = PBPhase.PICK_BLUE_SIDE

    def run(self):
        while not self.is_over:
            self.bans()
            self.picks()


class PicksBansAI(PickBanInput):
    def __init__(self, team: MobaTeamSimulation, champions: list[Champion]):
        self.team = team
        self.champions = champions
        self.picks_prio = list(Lanes)

    def pick(self):
        pass

    def ban(self):
        pass
