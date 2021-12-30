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

from esm.core.utils import find_file
from esm.definitions import RES_DIR
from esm.ui.gui_components import *


class GUI:
    """
    The GUI class creates the GUI window and stores references to each layout in the game. Here
    are all the implementation details from PySimpleGUI, and the code in each layout is also very
    specific to the GUI we are currently using.
    """

    def __init__(self, controller):
        self.icon = "esportsmanagertrophy.png"
        # Each layout is added to the list
        self.controller = controller
        self.layouts = self.get_layouts()

        self.window = self._create_window()

    def _encode_icon(self) -> bytes:
        """
        Encodes the icon used for the window title. This is the default icon for the window and the
        game on the desktop.
        """
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

    def get_layouts(self):
        """
        Gets GUI layouts from the controller classes.
        """
        return [controller.layout for controller in self.controller.controllers]

    def _get_cols(self) -> list:
        """
        Gets all the layouts and makes them all invisible, except for the main screen one.
        This function gets called in the beginning of the game's execution.
        :return:
        """
        cols = [layout.col for layout in self.layouts]

        return [[sg.Pane(cols, relief=sg.RELIEF_FLAT, show_handle=False)]]

    @staticmethod
    def error_message(e) -> None:
        tb = traceback.format_exc()
        sg.Print("The following error happened:", e, tb)
        sg.popup_error('The following error occurred:', e, tb)

    @staticmethod
    def information_window(*args, **kwargs):
        sg.popup_ok(*args, **kwargs)
        

def init_theme():
    create_look_and_feel()
    sg.theme("EsmTheme")
