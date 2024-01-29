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
from typing import Union

from esm.core.esmcore import ESMCore
from esm.core.esports.moba.match_tester import MatchTester
from esm.core.esports.moba.modules.match_manager import MatchLive, MatchManager
from esm.ui.controllers.controllerinterface import IController
from esm.ui.igamecontroller import IGameController
from esm.ui.layouts.match_tester import MatchTesterLayout


class MatchTesterController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.controller = controller
        self.core = core
        self.layout = MatchTesterLayout()
        self.game_initializer = MatchManager()
        self._amount_test_matches = 1000
        self.match_tester = None
        self.match_tester_thread = None

    @property
    def current_match(self) -> MatchLive:
        return self.game_initializer.current_live_game

    @current_match.setter
    def current_match(self, game: MatchLive):
        self.game_initializer.current_game = game.game
        self.game_initializer.current_live_game = MatchLive

    @property
    def amount_test_matches(self) -> int:
        return self._amount_test_matches

    @amount_test_matches.setter
    def amount_test_matches(self, amount) -> None:
        self._amount_test_matches = amount

    def initialize_random_debug_game(self, picksbans=True):
        self.core.check_files()
        teams = self.core.db.load_moba_teams()
        self.game_initializer.initialize_random_debug_game(teams, picksbans=picksbans)

    def start_match_tester_thread(self):
        """
        Starts a thread to run the match tester task.
        """
        try:
            self.match_tester_thread = threading.Thread(
                target=self.start_match_tester, daemon=True
            )
            self.match_tester_thread.start()
            self.disable_match_tester_buttons()
        except RuntimeError as e:
            self.controller.print_error(e)

    def reset_match_tester(self):
        """
        Reset the match tester function
        """
        if self.match_tester is not None:
            self.match_tester.reset_values()

    def start_match_tester(self):
        """
        Starts running the match tester task.
        """
        self.match_tester = MatchTester(self.amount_test_matches, self.current_match)
        self.match_tester.running_test = True
        self.match_tester.run_match_test()
        self.enable_match_tester_buttons()

    def enable_match_tester_buttons(self):
        """
        Tells the GUI we are done with match testing, and we can enable the layout buttons again
        """
        self.controller.write_event_value("MATCH TESTER", "MATCH TESTER DONE")
        self.controller.update_element_on_screen(
            "match_tester_startmatch_btn", disabled=False
        )
        self.controller.update_element_on_screen(
            "match_tester_newteams_btn", disabled=False
        )

    def disable_match_tester_buttons(self):
        """
        Tells the GUI match tester has started, and we should disable the layout buttons
        """
        self.controller.update_element_on_screen(
            "match_tester_startmatch_btn", disabled=True
        )
        self.controller.update_element_on_screen(
            "match_tester_newteams_btn", disabled=True
        )

    def get_team_data(self) -> Union[list, None]:
        if self.current_match is None:
            return None

        players = [list(team.roster) for team in self.current_match.game.teams]

        data = []
        for team in players:
            team_data = [
                [
                    player.lane.name,
                    player.nick_name,
                    player.champion_id,
                    int(player.get_player_total_skill()),
                ]
                for player in team
            ]
            data.append(team_data)

        return data

    def update_match_tester_match_info(self, data):
        self.controller.update_element_on_screen(
            "match_tester_team1table", values=data[0]
        )
        self.controller.update_element_on_screen(
            "match_tester_team2table", values=data[1]
        )
        self.controller.update_element_on_screen(
            "match_tester_team1skill", value=self.current_match.game.team1.total_skill
        )
        self.controller.update_element_on_screen(
            "match_tester_team2skill", value=self.current_match.game.team2.total_skill
        )
        self.controller.update_element_on_screen(
            "match_tester_team1name", value=self.current_match.game.team1.name
        )
        self.controller.update_element_on_screen(
            "match_tester_team2name", value=self.current_match.game.team2.name
        )

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("match_tester_screen").visible:
            if not self.game_initializer.current_live_game:
                self.initialize_random_debug_game()
                self.game_initializer.current_live_game.simulate = False
                self.game_initializer.current_live_game.show_commentary = False
                self.update_match_tester_match_info(self.get_team_data())

            # Click the Start Match button
            if event == "match_tester_startmatch_btn":
                self.amount_test_matches = int(values["match_tester_amount_of_matches"])
                self.reset_match_tester()
                self.start_match_tester_thread()

            # Click the Cancel button
            if event == "match_tester_cancel_btn":
                if self.match_tester is not None and self.match_tester.running_test:
                    self.match_tester.running_test = False
                make_screen("match_tester_screen", "main_screen")

            elif event == "match_tester_newteams_btn":
                self.initialize_random_debug_game()
                self.update_match_tester_match_info(self.get_team_data())
        else:
            self.match_tester = None
            self.match_tester_thread = None
