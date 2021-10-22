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

from .gui_components import sg
from .gui import GUI, init_theme


class View:
    """
    The View class corresponds to a View on a traditional MVC model. It interacts with the GUI.
    """
    def __init__(self, controller):
        self.gui = GUI(controller)
    
    def print_error(self, e):
        self.gui.error_message(e)

    def print_generate_data_window(self, players, teams, champions):
        self.gui.generate_data_window(players, teams, champions)

    def make_screen_visible(self, inv_screen, vis_screen):
        self.gui.window[inv_screen].update(visible=False)
        self.gui.window[vis_screen].update(visible=True)

    def disable_debug_buttons(self):
        self.gui.window.Element("debug_startmatch_btn").Update(disabled=True)
        self.gui.window.Element("debug_newteams_btn").Update(disabled=True)
        self.gui.window.Element("debug_resetmatch_btn").Update(disabled=True)

    def disable_match_tester_buttons(self):
        self.gui.window['match_tester_startmatch_btn'].update(disabled=True)
        self.gui.window['match_tester_newteams_btn'].update(disabled=True)
        self.gui.window['match_tester_startmatch_btn'].update(disabled=True)

    def enable_debug_buttons(self):
        self.gui.window.write_event_value("MATCH SIMULATED", "DONE")
        self.gui.window.Element("debug_startmatch_btn").Update(disabled=False)
        self.gui.window.Element("debug_newteams_btn").Update(disabled=False)
        self.gui.window.Element("debug_resetmatch_btn").Update(disabled=False)

    def enable_match_tester_buttons(self):
        self.gui.window.write_event_value("MATCH TESTER", "MATCH TESTER DONE")
        self.gui.window['match_tester_startmatch_btn'].update(disabled=False)
        self.gui.window['match_tester_newteams_btn'].update(disabled=False)

    def update(self, *args, **kwargs) -> None:
        """
        Event handling for each layout
        """
        for layout in self.gui.layouts:
            layout.update(*args, **kwargs)

    def update_element_on_screen(self, element, **kwargs):
        self.gui.window[element].update(**kwargs)

    def get_screen_element(self, element):
        return self.gui.window[element]

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
