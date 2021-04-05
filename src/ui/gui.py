#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020  Pedrenrique G. Guimarães
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
import PySimpleGUI as sg

from src.core.esports.moba.match_live import MatchLive
from src.resources import RES_DIR
from src.resources.utils import find_file
from src.ui.gui_components import *


class View:
    def __init__(self, controller):
        self.gui = GUI()
        self.controller = controller

    def start(self):
        while True:
            event, values = self.gui.window.read(timeout=100)

            if event in [sg.WINDOW_CLOSED, 'exit_main']:
                break


class GUI:
    def __init__(self):
        self.icon = 'esportsmanagertrophy.png'
        self.layouts = self._get_layouts()
        self.window = self._create_window()

    def _encode_icon(self) -> bytes:
        with open(find_file(self.icon, folder=RES_DIR), 'rb') as fp:
            encoded_icon = base64.b64encode(fp.read())

        return encoded_icon

    def _create_window(self) -> sg.Window:
        """
        Creates the main Window using PySimpleGUI, and assigns the eSM icon to it.
        It uses the _get_layouts() function to get a list of layouts used in this software.
        :return: the window PySimpleGUI object
        """

        encoded_icon = self._encode_icon()
        create_look_and_feel()
        sg.theme('EsmTheme')
        return sg.Window(
            'eSports Manager',
            element_justification='center',
            layout=self.layouts,
            # size=(900, 800),
            icon=encoded_icon,
            resizable=True,
        )

    def _get_layouts(self) -> list:
        """
        Gets all the layouts and makes them all invisible, except for the main screen one.
        This function gets called in the beginning of the game's execution.
        :return:
        """
        col_main_screen = sg.Column(self.main_screen(),
                                    key='main_screen',
                                    element_justification="center"
                                    )

        col_create_manager = sg.Column(self.create_manager_layout(),
                                       key='create_manager',
                                       visible=False,
                                       element_justification="center"
                                       )

        col_load_game = sg.Column(self.load_game_layout(),
                                  key='load_game',
                                  visible=False,
                                  element_justification="center"
                                  )

        return [
            [sg.Pane([col_main_screen,
                      col_create_manager,
                      col_load_game],
                     relief=sg.RELIEF_FLAT, show_handle=False)]
        ]


