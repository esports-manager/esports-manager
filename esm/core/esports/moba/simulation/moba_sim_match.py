#  eSports Manager - free and open source eSports Management game
#  Copyright (C) 2020-2024  Pedrenrique G. Guimarães
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from ..mobamatch import MobaMatch
from ..mobateam import MobaTeamSimulation
from .moba_sim_engine import MobaSimEngine


class NoChampionError(Exception):
    pass


class MobaSimMatch:
    def __init__(
        self,
        match: MobaMatch,
        team1: MobaTeamSimulation,
        team2: MobaTeamSimulation,
    ):
        self.team1 = team1
        self.team2 = team2
        self.match = match
        self.teams = [self.team1, self.team2]
        self.simulation_engine = MobaSimEngine(self.team1, self.team2)

    def run(self):
        for team in self.teams:
            for player in team.players:
                if player.champion is None:
                    raise NoChampionError

        self.simulation_engine.run()
