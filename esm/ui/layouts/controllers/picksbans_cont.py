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
import gc
import threading
from queue import Queue

from esm.core.esmcore import ESMCore
from esm.core.esports.moba.modules.match_factory import MatchFactory
from .controllerinterface import IController
from ..picksbans import PicksBansLayout
from ...igamecontroller import IGameController


class PicksBansController(IController):
    def __init__(self, controller: IGameController, core: ESMCore):
        self.controller = controller
        self.core = core
        self.game_initializer = MatchFactory()
        self.layout = PicksBansLayout()
        self.queue = Queue()
        self.current_match = None
        self.pick_ban_thread = None
        self.team1 = None
        self.team2 = None
        self.ch_list = None
        self.champion_table_data = None
        self.team1_bans = None
        self.team2_bans = None

    @staticmethod
    def get_players(team):
        return [
            [
                player.lane.name,
                player.nick_name,
                player.skill,
                player.champion,
                int(player.get_player_total_skill())
            ] for player in team
        ]

    def get_champions(self):
        player = None
        picks_bans = self.current_match.picks_bans

        if picks_bans.bans_turn == -1:
            if self.current_match.picks_bans.picks_order:
                player = picks_bans.picks_order[0]

            self.champion_table_data = [
                [
                    champion,
                    champion.skill,
                    int(player.get_projected_champion_skill(champion)) if player is not None else 0,
                    champion.status
                ]
                for champion in self.ch_list
            ]
        else:
            self.champion_table_data = [
                [
                    champion,
                    champion.skill,
                    champion.skill,
                    champion.status
                ]
                for champion in self.ch_list
            ]

        self.champion_table_data.sort(key=lambda x: x[2], reverse=True)
        return self.champion_table_data

    @staticmethod
    def get_bans(bans):
        return [
            ban.name
            for ban in bans
        ]

    def update_elements(self):
        pick_ban = self.current_match.picks_bans
        self.controller.update_element_on_screen("pickban_team1_label", value=self.team1.name)
        self.controller.update_element_on_screen("pickban_team2_label", value=self.team2.name)
        self.controller.update_element_on_screen("pickban_team1_table", values=self.get_players(self.team1.list_players))
        self.controller.update_element_on_screen("pickban_team2_table", values=self.get_players(self.team2.list_players))
        self.controller.update_element_on_screen("pickban_team1_bans", value=self.get_bans(self.team1_bans))
        self.controller.update_element_on_screen("pickban_team2_bans", value=self.get_bans(self.team2_bans))
        self.controller.update_element_on_screen("pickban_champion_table", values=self.get_champions())
        if pick_ban.bans_turn != -1:
            self.controller.update_element_on_screen("pickban_pick_btn", text="Ban")
        else:
            self.controller.update_element_on_screen("pickban_pick_btn", text="Pick")

    def get_elements(self):
        self.team1 = self.current_match.match.team1
        self.team2 = self.current_match.match.team2
        self.ch_list = self.current_match.picks_bans.champion_list
        self.team1_bans = self.current_match.match.team1.bans
        self.team2_bans = self.current_match.match.team2.bans

    def update(self, event, values, make_screen):
        if not self.controller.get_gui_element("debug_picks_bans_screen").visible:
            return

        if self.current_match is None:
            self.core.check_files()
            teams = self.core.db.load_moba_teams()
            self.current_match = self.game_initializer.initialize_random_debug_game(teams, picks_bans_queue=self.queue)
            self.current_match.match.team1.is_players_team = True
            try:
                self.pick_ban_thread = threading.Thread(target=self.current_match.picks_and_bans, daemon=True)
                self.pick_ban_thread.start()
            except RuntimeError as e:
                self.controller.print_error(e)
            self.get_elements()
            self.update_elements()

        if event == "pickban_cancel_btn":
            # This will terminate the pick_ban_thread
            self.current_match.picks_bans.num_picks = 10
            self.current_match = None
            self.pick_ban_thread = None
            self.queue = Queue()

            # Get rid of the rest of the objects that are not being used
            gc.collect()
            make_screen("debug_picks_bans_screen", "debug_game_mode_screen")

        if event == "pickban_pick_btn":
            if values["pickban_champion_table"]:
                champion = self.champion_table_data[values["pickban_champion_table"][0]][0]
                if champion.status == "Not picked":
                    self.queue.put(champion)

            self.update_elements()

        if self.pick_ban_thread is not None and not self.pick_ban_thread.is_alive():
            self.update_elements()
            self.pick_ban_thread = None
