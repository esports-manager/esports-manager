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
import os
import cbor2
from tempfile import NamedTemporaryFile

from esm.definitions import SAVE_FILE_DIR
from esm.core.gamestate import GameState


class SaveGame:
    def __init__(self, gamestate: GameState, filename: str, save_directory: str = None, autosave_enabled: bool = True):
        self.gamestate = gamestate
        self.filename = filename
        self.save_directory = save_directory

        if self.save_directory is None:
            self.save_directory = SAVE_FILE_DIR
        self.check_if_savedir_exists()

        self.autosave_enabled = autosave_enabled

        self.temporary_file = None
        self.autosave = None

    def setup_data_file(self):
        return self.gamestate.get_data()

    def save_temporary_file(self):
        """
        Creates the temporary file that is used by the game to retrieve game information.

        Temporary files are used to store data currently in use. They can be retrieved by the current game session.
        """
        if self.temporary_file is None:
            self.temporary_file = NamedTemporaryFile()
        self.write_save_file(self.temporary_file)

    def save_autosave(self):
        """
        Creates an autosave file

        Autosave files are a backup file that gets created and can be deactivated by the user.

        Autosave can run after matches or important decisions, whereas the temporary file is always updated.
        """
        autosave = self.filename + '.bkp'
        self.autosave = os.path.join(self.save_directory, autosave)
        self.write_save_file(self.autosave)

    def save_game(self):
        """
        Saves the game
        """
        self.save_temporary_file()
        save_file_path = os.path.join(self.save_directory, self.filename)
        self.write_save_file(save_file_path)
        self.delete_autosave()

    def delete_autosave(self):
        """
        Deletes the autosave file
        """
        if self.autosave is not None and os.path.exists(self.autosave):
            os.remove(self.autosave)

    def check_if_savedir_exists(self):
        """
        Checks if the save directory exists. If it does not, it creates the save dir.
        """
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def write_save_file(self, filename):
        with open(filename, 'w') as fp:
            cbor2.dump(self.gamestate.get_data(), fp)
