#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2021  Pedrenrique G. Guimarães
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

from .controllerinterface import IController
from ..match_tester import MatchTesterLayout


class MatchTesterController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = MatchTesterLayout(self)
    
    def initialize_random_debug_match(self, picksbans=True):
        self.controller.initialize_random_debug_match(picksbans)
    
    def start_match_tester_thread(self, amount):
        self.controller.start_match_tester_thread(amount)
    
    def start_match_tester(self, amount):
        self.controller.start_match_tester(amount)
    
    def reset_match_tester(self):
        self.controller.reset_match_tester()
    
    def update(self, event, values, make_screen):
        update_match_tester_match_info = self.controller.update_match_tester_match_info

        # Click the Start Match button
        if event == "match_tester_startmatch_btn":
            self.reset_match_tester()
            self.start_match_tester_thread(values['match_tester_amount_of_matches'])

        # Click the Cancel button
        if event == "match_tester_cancel_btn":
            if (
                self.controller.match_tester is not None
                and self.controller.match_tester.running_test
            ):
                self.controller.match_tester.running_test = False
            make_screen("match_tester_screen", "main_screen")

        elif event == "match_tester_newteams_btn":
            self.controller.check_files()
            self.controller.initialize_random_debug_match()
            data = self.controller.team_data(match_live=self.controller.current_match)
            update_match_tester_match_info(self.controller.current_match, data)
