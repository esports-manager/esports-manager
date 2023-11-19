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
from .controllers import *
from .gui import GUI, init_theme
from .gui_components import sg
from .igamecontroller import IGameController
from ..core.esmcore import ESMCore
from ..definitions import DEBUG


class GUIController(IGameController):
    """
    This class is an abstraction layer over the GUI. It should provide functions that interact
    with the GUI, but do not expose any details about the GUI itself.
    """

    def __init__(self, core: ESMCore):
        init_theme()
        self.controllers = []
        self.__initialize_controllers(core)
        self.gui = GUI(self.controllers)

    def __initialize_controllers(self, core: ESMCore):
        self.controllers = [
            MainScreenController(),
            NewGameController(self, core),
            LoadGameController(self, core),
            SettingsController(self, core),
            GameDashboardController(self, core),
        ]

        # Debug controllers
        if DEBUG:
            self.controllers.append(DebugController())
            self.controllers.append(DebugMatchController(self, core))
            self.controllers.append(DebugChampionshipController(self, core))
            self.controllers.append(TeamSelectController(self, core))
            self.controllers.append(PicksBansController(self, core))
            self.controllers.append(PickTeamController())
            self.controllers.append(MatchTesterController(self, core))

    def print_error(self, e):
        self.gui.error_message(e)

    def make_screen_visible(self, inv_screen, vis_screen):
        self.gui.window[inv_screen].update(visible=False)
        self.gui.window[vis_screen].update(visible=True)

    def update_element_on_screen(self, element, **kwargs):
        self.gui.window[element].update(**kwargs)

    def get_gui_element(self, element):
        return self.gui.window[element]

    def write_event_value(self, first_message, second_message):
        self.gui.window.write_event_value(first_message, second_message)

    def update_progress_bar(self, key, value):
        self.gui.window[key].update_bar(value)

    def get_gui_information_window(self, *args, **kwargs):
        self.gui.information_window(*args, **kwargs)

    def get_gui_confirmation_window(self, *args, **kwargs):
        return self.gui.confirmation_window(*args, **kwargs)

    def update(self, *args, **kwargs) -> None:
        """
        Event handling for each layout
        """
        for controller in self.controllers:
            controller.update(*args, **kwargs)

    def start(self):
        """
        App loop
        """
        while True:
            event, values = self.gui.window.read(timeout=500)

            if event in [sg.WINDOW_CLOSED, "main_exit_btn"]:
                break

            # Goes through each layout and runs their update method (event handling)
            self.update(
                event,
                values,
                self.make_screen_visible,
            )
