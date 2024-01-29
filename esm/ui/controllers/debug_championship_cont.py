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
import threading
import uuid

from esm.core.esmcore import ESMCore
from esm.core.esports.moba.championship import Championship
from esm.ui.igamecontroller import IGameController
from esm.ui.layouts.debug_championship import DebugChampionshipLayout

from .controllerinterface import IController


class DebugChampionshipController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.core = core
        self.controller = controller
        self.layout = DebugChampionshipLayout()
        self.championship = None
        self.teams = None
        self.match_details = []
        self.championship_details = []
        self.championship_thread = None

    def initialize_random_championship(self):
        if self.teams is None:
            self.core.check_files()
        self.teams = self.core.db.load_moba_teams()
        self.championship = Championship("Debug", uuid.uuid4(), "Debug", self.teams)
        self.championship.schedule_matches()
        self.get_default_championship_details()
        self.get_default_match_details()
        self.update_data_in_matches_table()
        self.update_data_in_championship_table()

    def reset_details(self):
        self.championship_details = [
            ["TEAM1NAME12345678901213154879", "000", "00", "00", "000"]
        ]
        self.match_details = [
            ["TEAM1NAME12345678901213154879", "TEAM1NAME12345678901213154879", "None"]
        ]

    def get_default_championship_details(self):
        self.championship_details = [
            [team.name, team.get_team_overall(), 0, 0, 0] for team in self.teams
        ]

    def get_default_match_details(self):
        self.match_details = [
            [match.game.team1.name, match.game.team2.name, "None"]
            for match in self.championship.matches
        ]

    def assign_win_and_loss_in_championship_table(self, match):
        for detail in self.championship_details:
            if detail[0] in [match.game.team1.name, match.game.team2.name]:
                if detail[0] == match.game.victorious_team.name:
                    detail[2] += 1
                    detail[4] += 3
                else:
                    detail[3] += 1

    def get_winning_team(self, live_match):
        for detail in self.match_details:
            if (
                live_match.game.team1.name == detail[0]
                and live_match.game.team2.name == detail[1]
            ):
                if live_match.victorious_team.name == detail[0]:
                    detail[2] = detail[0]
                elif live_match.victorious_team.name == detail[1]:
                    detail[2] = detail[1]
                else:
                    detail[2] = "None"

    def play_championship(self):
        for live_match in self.championship.matches:
            for team in live_match.game.teams:
                team.get_players_default_lanes()
            live_match.picks_and_bans()
            live_match.simulation()
            self.get_winning_team(live_match)
            self.assign_win_and_loss_in_championship_table(live_match)

            for team in live_match.game.teams:
                team.reset_values()

    def reset_championship(self):
        self.championship.reset_championship()
        self.get_default_championship_details()
        self.get_default_match_details()

    def update_data_in_championship_table(self):
        self.championship_details.sort(key=lambda x: x[4], reverse=True)
        self.controller.update_element_on_screen(
            "debug_championship_table", values=self.championship_details
        )

    def update_data_in_matches_table(self):
        self.controller.update_element_on_screen(
            "debug_matches_table", values=self.match_details
        )

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("debug_championship_screen").visible is True:
            if self.championship is None:
                self.initialize_random_championship()

            self.update_data_in_championship_table()
            self.update_data_in_matches_table()

            if event == "debug_startchampionship_btn":
                self.reset_championship()
                try:
                    self.championship_thread = threading.Thread(
                        target=self.play_championship, daemon=True
                    )
                    self.championship_thread.start()
                    self.controller.update_element_on_screen(
                        "debug_startchampionship_btn", disabled=True
                    )
                except RuntimeError as e:
                    self.controller.print_error(e)

            if (
                self.championship_thread is not None
                and not self.championship_thread.is_alive()
            ):
                self.controller.update_element_on_screen(
                    "debug_startchampionship_btn", disabled=False
                )

            # Click the Cancel button
            if event == "debug_championshipcancel_btn":
                self.reset_details()
                make_screen("debug_championship_screen", "main_screen")
        else:
            self.championship = None
