#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2022  Pedrenrique G. Guimarães
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

from esm.core.core import MobaModel
from esm.core.esports.moba.match_live import MatchLive
from esm.core.game_manager import GameManager
from esm.core.settings import Settings
from esm.definitions import DEBUG
from esm.ui.gui import init_theme
from esm.ui.layouts.controllers import *
from esm.ui.layouts.controllers.game import *
from esm.ui.view import View


class ESMMobaController:
    """
    This class is a general class for MOBA-related control activities. It initializes all controllers
    and layouts, and also communicates with the View and MobaModel modules. It is the bread and butter
    for all other layout controllers.
    """

    def __init__(self):
        init_theme()
        self.controllers = None
        self.game_manager = None
        self.settings = Settings()
        self.settings.load_config_file()
        self.initialize_controllers()
        self.core = MobaModel()
        self.view = View(self)

    @property
    def amount_players(self):
        return self.core.amount_players

    @amount_players.setter
    def amount_players(self, value):
        self.core.amount_players = value

    def initialize_controllers(self):
        loadgame_cont.LoadGameController(self)
        mainscreen_cont.MainScreenController(self)
        newgame_cont.NewGameController(self)
        settings_cont.SettingsController(self)
        game_dashboard_cont.GameDashboardController(self)

        # Debug controllers
        if DEBUG:
            debug_cont.DebugController(self)
            debugmatch_cont.DebugMatchController(self)
            debug_championship_cont.DebugChampionshipController(self)
            teamselect_cont.TeamSelectController(self)
            picksbans_cont.PicksBansController(self)
            pickteam_cont.PickTeamController(self)
            match_tester_cont.MatchTesterController(self)

    def write_event_values(self, first_message: str, second_message: str):
        self.view.write_event_value(first_message, second_message)

    def create_game_manager(self, manager, filename, esport, season, game_name):
        self.game_manager = GameManager(manager, filename, esport, season, game_name, self.settings)

    def print_error(self, e):
        self.view.print_error(e)

    def generate_all_data(self) -> None:
        """
        Resets generators and generates data in the background.
        """
        self.reset_generators()
        try:
            self.core.check_player_amount()
        except ValueError as e:
            self.get_gui_information_window(
                e,
                'Number of players not supported!'
            )
            self.core.amount_players = 50
        finally:
            self.core.generate_all()

    def check_files(self) -> None:
        """
        Check if game files exist. If they don't, it creates them.
        """
        try:
            self.core.check_files()
        except FileNotFoundError:
            self.generate_all_data()

    def reset_generators(self) -> None:
        """
        Resets all generators. This prevents memory allocation of unnecessary elements.
        """
        self.core.reset_generators()

    def initialize_random_debug_match(self, picksbans=True, queue=None, picks_bans_queue=None) -> MatchLive:
        """
        Initializes a random debug match. Just works when debugging is enabled.
        """
        return self.core.initialize_random_debug_match(
            queue=queue,
            picksbans=picksbans,
            picks_bans_queue=picks_bans_queue,
        )

    def update_gui_element(self, element, **kwargs):
        """
        Wrapper for calling the View to update a GUI element with keyword arguments
        """
        self.view.update_element_on_screen(element, **kwargs)

    def update_progress_bar(self, key, value):
        self.view.update_progress_bar(key, value)

    def get_gui_element(self, element):
        """
        Wrapper for calling the View to return the given GUI element
        """
        return self.view.get_screen_element(element)

    def get_gui_information_window(self, information, title):
        self.view.information_window(information, title=title)

    def app(self) -> None:
        self.view.start()
