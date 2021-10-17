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

import threading

from esm.core.esports.moba.match_tester import MatchTester
from esm.core.core import MobaModel
from esm.core.esports.moba.match_live import MatchLive

from esm.ui.view import View
from esm.ui.layouts.controllers import *
from esm.ui.gui import init_theme


class ESMMobaController:
    """
    The ESM class corresponds to a Controller on a traditional MVC model. Not a full controller yet.
    """
    def __init__(self, amount_players=50):
        self._amount_players = amount_players
        self._amount_test_matches = 1000
        self.is_match_running = False
        self.match_tester = None
        self.match_tester_thread = None
        self.current_match = None
        self.match_thread = None
        self.controllers = None
        self.modules = None
        init_theme()
        self.initialize_controllers()
        self.core = MobaModel(self.amount_players)
        self.view = View(self)
        self.manager = None
    
    @staticmethod
    def team_data(match_live=None):
        if match_live is None:
            return None
        players = [
            [player for player in team.list_players] for team in match_live.match.teams
        ]

        data = []
        for team in players:
            team_data = [
                [
                    player.lane.name,
                    player.nick_name,
                    player.kills,
                    player.deaths,
                    player.assists,
                    player.champion,
                    int(player.get_player_total_skill()),
                ]
                for player in team
            ]
            data.append(team_data)

        return data
    
    @property
    def amount_test_matches(self) -> int:
        return self._amount_test_matches

    @amount_test_matches.setter
    def amount_test_matches(self, amount) -> None:
        self._amount_test_matches = amount

    @property
    def amount_players(self) -> int:
        return self._amount_players

    @amount_players.setter
    def amount_players(self, amount):
        self.core.amount_players = amount
        self._amount_players = amount

    def initialize_controllers(self):
        debug_cont.DebugController(self)
        debugmatch_cont.DebugMatchController(self)
        debug_championship_controller.DebugChampionshipController(self)
        loadgame_cont.LoadGameController(self)
        mainscreen_cont.MainScreenController(self)
        match_tester_cont.MatchTesterController(self)
        newgame_cont.NewGameController(self)
        picksbans_cont.PicksBansController(self)
        pickteam_cont.PickTeamController(self)
        settings_cont.SettingsController(self)
        teamselect_cont.TeamSelectController(self)
    
    def get_layouts(self):
        return [controller.layout for controller in self.controllers]
    
    def start_match_sim(self) -> None:
        self.current_match.simulation()
        self.view.enable_debug_buttons()

    def generate_all_data(self) -> None:
        """
        Starts a thread to generate data and show a window progress bar.
        """
        self.reset_generators()
        self.core.generate_all()
        # try:
        #     generate_data_thread = threading.Thread(
        #         target=self.core.generate_all, daemon=True
        #     )
        #     generate_data_thread.start()
        #     # self.view.print_generate_data_window(
        #     #     self.core.players.players_dict,
        #     #     self.core.teams.teams_dict,
        #     #     self.core.champions.champions_list,
        #     # )
        #     generate_data_thread.join()
        # except RuntimeError as e:
        #     self.view.print_error(e)

    def check_files(self) -> None:
        try:
            self.core.check_files()
        except FileNotFoundError as e:
            self.generate_all_data()

    def reset_generators(self) -> None:
        """
        Resets all generators. This prevents memory allocation of unnecessary elements.
        """
        self.core.reset_generators()

    def reset_match(self, match) -> None:
        self.core.reset_team_values(match)
        self.core.reset_match(match)

    def update_amount(self, value):
        self.view.gui.window["settings_amount_input"].update(value=value)

    def update_debug_match_info(self, current_match, data):
        self.view.gui.update_debug_match_info(current_match, data)

    def update_match_tester_match_info(self, current_match, data):
        self.view.gui.update_match_tester_match_info(current_match, data)

    def initialize_random_debug_match(self, picksbans=True) -> MatchLive:
        self.core.initialize_random_debug_match()

        # Resetting
        self.reset_generators()

        self.core.get_player_default_lanes()

        if picksbans:
            self.core.match_live.picks_and_bans()

        self.current_match = self.core.match_live

        return self.core.match_live

    def reset_match_tester(self):
        if self.match_tester is not None:
            self.match_tester.reset_values()

    def start_match_tester(self, amount):
        self.match_tester = MatchTester(amount, self.current_match)
        self.match_tester.running_test = True
        self.match_tester.run_match_test()
        self.view.enable_match_tester_buttons()

    def start_match_tester_thread(self, amount):
        try:
            self.match_tester_thread = threading.Thread(
                target=self.start_match_tester, args=(int(amount),), daemon=True
            )
            self.match_tester_thread.start()
            self.view.disable_match_tester_buttons()
        except RuntimeError as e:
            self.view.print_error(e)

    def start_match_sim_thread(self) -> None:
        try:
            self.match_thread = threading.Thread(
                target=self.start_match_sim, daemon=True
            )
            self.match_thread.start()
            self.view.disable_debug_buttons()
        except RuntimeError as e:
            self.view.print_error(e)

    def app(self) -> None:
        self.view.start()
