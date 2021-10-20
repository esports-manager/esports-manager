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
from ..debug import DebugLayout


class DebugController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = DebugLayout(self)
    
    def update(self, event, values, make_screen):
        if event == "debug_pickteam_btn":
            make_screen("debug_game_mode_screen", "debug_pickteam_screen")

        elif event == "debug_cancelmain_btn":
            make_screen("debug_game_mode_screen", "main_screen")

        elif event == "debug_championship_btn":
            make_screen("debug_game_mode_screen", "debug_championship_screen")

        elif event == "debug_picksbans_btn":
            make_screen("debug_game_mode_screen", "debug_picks_bans_screen")

        elif event == "debug_match_btn":
            team_data = self.controller.team_data
            update_debug_match_info = self.controller.update_debug_match_info

            self.controller.check_files()
            match_live = self.controller.initialize_random_debug_match()

            data = team_data(match_live=match_live)
            update_debug_match_info(match_live, data)
            make_screen("debug_game_mode_screen", "debug_match_screen")

        elif event == "debug_matchtester_btn":
            team_data = self.controller.team_data
            update_match_tester_match_info = (
                self.controller.update_match_tester_match_info
            )

            self.controller.check_files()
            if not self.controller.current_match:
                match_live = self.controller.initialize_random_debug_match()
            else:
                match_live = self.controller.current_match

            match_live.simulate = False
            match_live.show_commentary = False
            data = team_data(match_live=match_live)
            update_match_tester_match_info(match_live, data)
            make_screen("debug_game_mode_screen", "match_tester_screen")
