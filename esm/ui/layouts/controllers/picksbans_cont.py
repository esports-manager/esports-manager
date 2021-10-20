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

from queue import Queue

from .controllerinterface import IController
from ..picksbans import PicksBansLayout


class PicksBansController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = PicksBansLayout(self)
        self.queue = Queue()

    @staticmethod
    def get_players(team):
        return [
            [
                player.lane.name,
                player.nick_name,
                player.skill,
                player.champion
            ]
            for player in team
        ]

    @staticmethod
    def get_champions(ch_list):
        return [
            [
                champion.name,
                champion.skill,
            ]
            for champion in ch_list
        ]

    def update(self, event, values, make_screen):
        if self.controller.current_match is None:
            self.controller.initialize_random_debug_match(False)
            self.controller.current_match.match.team1.is_players_team = True

        if self.controller.current_match is not None:
            team1 = self.controller.current_match.match.team1
            team2 = self.controller.current_match.match.team2
            ch_list = self.controller.current_match.picks_bans.champion_list
            self.controller.update_gui_element("pickban_team1_label", value=team1.name)
            self.controller.update_gui_element("pickban_team2_label", value=team2.name)
            self.controller.update_gui_element("pickban_team1_table", values=self.get_players(team1.list_players))
            self.controller.update_gui_element("pickban_team2_table", values=self.get_players(team2.list_players))
            self.controller.update_gui_element("pickban_champion_table", values=self.get_champions(ch_list))

        if event == "pickban_cancel_btn":
            make_screen("debug_picks_bans_screen", "debug_game_mode_screen")
            self.controller.current_match = None
