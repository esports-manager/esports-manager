#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2023  Pedrenrique G. Guimarães
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

from esm.core.esports.moba.match_tester import MatchTester
from esm.ui.layouts.controllers.controllerinterface import IController
from esm.ui.layouts.match_tester import MatchTesterLayout
from esm.core.esports.moba.modules.init_game import GameInitializer


class MatchTesterController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = MatchTesterLayout(self)
        self.game_initializer = GameInitializer()
        self._amount_test_matches = 1000
        self.current_match = None
        self.match_tester = None
        self.match_tester_thread = None

    @property
    def amount_test_matches(self) -> int:
        return self._amount_test_matches

    @amount_test_matches.setter
    def amount_test_matches(self, amount) -> None:
        self._amount_test_matches = amount

    def initialize_random_debug_match(self, picksbans=True):
        self.current_match = self.game_initializer.initialize_random_debug_game(picksbans=picksbans)

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
        self.controller.write_event_values("MATCH TESTER", "MATCH TESTER DONE")
        self.controller.update_gui_element('match_tester_startmatch_btn', disabled=False)
        self.controller.update_gui_element('match_tester_newteams_btn', disabled=False)

    def disable_match_tester_buttons(self):
        """
        Tells the GUI match tester has started, and we should disable the layout buttons
        """
        self.controller.update_gui_element('match_tester_startmatch_btn', disabled=True)
        self.controller.update_gui_element('match_tester_newteams_btn', disabled=True)

    def get_team_data(self) -> Union[list, None]:
        if self.current_match is None:
            return None

        players = [
            [player for player in team.list_players] for team in self.current_match.match.teams
        ]

        data = []
        for team in players:
            team_data = [
                [
                    player.lane.name,
                    player.nick_name,
                    player.champion,
                    int(player.get_player_total_skill())
                ]
                for player in team
            ]
            data.append(team_data)

        return data

    def update_match_tester_match_info(self, data):
        self.controller.update_gui_element('match_tester_team1table', values=data[0])
        self.controller.update_gui_element('match_tester_team2table', values=data[1])
        self.controller.update_gui_element('match_tester_team1skill', value=self.current_match.match.team1.total_skill)
        self.controller.update_gui_element('match_tester_team2skill', value=self.current_match.match.team2.total_skill)
        self.controller.update_gui_element('match_tester_team1name', value=self.current_match.match.team1.name)
        self.controller.update_gui_element('match_tester_team2name', value=self.current_match.match.team2.name)

    def update(self, event, values, make_screen):
        if self.controller.get_gui_element("match_tester_screen").visible:
            if not self.current_match:
                self.controller.check_files()
                self.current_match = self.controller.initialize_random_debug_match()
                self.current_match.simulate = False
                self.current_match.show_commentary = False
                data = self.get_team_data()
                self.update_match_tester_match_info(data)

            # Click the Start Match button
            if event == "match_tester_startmatch_btn":
                self.amount_test_matches = int(values['match_tester_amount_of_matches'])
                self.reset_match_tester()
                self.start_match_tester_thread()

            # Click the Cancel button
            if event == "match_tester_cancel_btn":
                if (
                        self.match_tester is not None
                        and self.match_tester.running_test
                ):
                    self.match_tester.running_test = False
                make_screen("match_tester_screen", "main_screen")

            elif event == "match_tester_newteams_btn":
                self.controller.check_files()
                self.current_match = self.controller.initialize_random_debug_match()
                data = self.get_team_data()
                self.update_match_tester_match_info(data)

        else:
            self.current_match = None
            self.match_tester = None
            self.match_tester_thread = None
