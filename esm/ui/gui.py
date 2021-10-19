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

import base64
import traceback

from esm.definitions import RES_DIR
from esm.resources.utils import find_file
from esm.ui.gui_components import *
from esm.ui.layouts import *


class GUI:
    def __init__(self, controller):
        self.icon = "esportsmanagertrophy.png"
        # Each layout is added to the list
        self.layouts = controller.get_layouts()
        
        self.window = self._create_window()
    
    def _encode_icon(self) -> bytes:

        with open(find_file(self.icon, folder=RES_DIR), "rb") as fp:
            encoded_icon = base64.b64encode(fp.read())

        return encoded_icon

    def _create_window(self) -> sg.Window:
        """
        Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
        It uses the _get_layouts() function to get a list of layouts used in this software.
        :return: the window PySimpleGUI object
        """

        encoded_icon = self._encode_icon()

        return sg.Window(
            "eSports Manager",
            element_justification="center",
            layout=self._get_cols(),
            size=(1280, 720),
            icon=encoded_icon,
            resizable=True,
            finalize=True,
        )

    def _get_cols(self) -> list:
        """
        Gets all the layouts and makes them all invisible, except for the main screen one.
        This function gets called in the beginning of the game's execution.
        :return:
        """

        cols = [layout.col for layout in self.layouts]

        return [[sg.Pane(cols, relief=sg.RELIEF_FLAT, show_handle=False)]]

    @staticmethod
    def generate_data_window(players, teams, champions) -> None:
        for i, _ in enumerate(champions):
            sg.one_line_progress_meter(
                "Generating Champions", i + 1, len(champions), "generate_champ"
            )

        for i, _ in enumerate(players):
            sg.one_line_progress_meter(
                "Generating players", i + 1, len(players), "generate_players"
            )

        for i, _ in enumerate(teams):
            sg.one_line_progress_meter(
                "Generating teams", i + 1, len(teams), "generate_teams"
            )

    def update_debug_match_info(self, match, data) -> None:
        win_prob = match.match.team1.win_prob * 100
        window = self.window
        window["debug_team1table"].update(values=data[0])
        window["debug_team2table"].update(values=data[1])
        window["debug_team1skill"].update(value=match.match.team1.total_skill)
        window["debug_team2skill"].update(value=match.match.team2.total_skill)
        window["debug_team1winprob"].update(value=match.match.team1.win_prob)
        window["debug_team2winprob"].update(value=match.match.team2.win_prob)
        window["debug_winprob"].update_bar(win_prob)
        window["debug_match_current_time"].update(value=match.game_time)
        window["debug_team1towers"].Update(value=match.match.team1.towers)
        window["debug_team2towers"].Update(value=match.match.team2.towers)
        window["debug_team1inhibs"].Update(value=match.match.team1.inhibitors)
        window["debug_team2inhibs"].Update(value=match.match.team2.inhibitors)
        window["debug_team1name"].Update(value=match.match.team1.name)
        window["debug_team2name"].Update(value=match.match.team2.name)
        window.refresh()

    def update_match_tester_match_info(self, match, data) -> None:
        window = self.window
        window["match_tester_team1table"].update(values=data[0])
        window["match_tester_team2table"].update(values=data[1])
        window["match_tester_team1skill"].update(value=match.match.team1.total_skill)
        window["match_tester_team2skill"].update(value=match.match.team2.total_skill)
        window["match_tester_team1name"].Update(value=match.match.team1.name)
        window["match_tester_team2name"].Update(value=match.match.team2.name)
        window.refresh()

    @staticmethod
    def error_message(e) -> None:
        tb = traceback.format_exc()
        sg.Print("The following error happened:", e, tb)
        sg.popup_error(f"The following error occurred:", e, tb)


def init_theme():
    create_look_and_feel()
    sg.theme("EsmTheme")
