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
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from tempfile import mkstemp
from typing import Union
from datetime import timezone

import cbor2

from esm.core.gamestate import GameState
from esm.definitions import SAVE_FILE_DIR


class SaveGame:
    def __init__(
            self,
            gamestate: GameState,
            filename: Union[str, Path],
            save_directory: str = None,
            autosave_enabled: bool = True
    ):
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
        """
        Converts GameState to a dictionary, and adds the saved date to the key-value pair.
        """
        data = asdict(self.gamestate)
        save_date = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S:%f")
        data['save_date'] = save_date
        return data

    def save_temporary_file(self):
        """
        Creates the temporary file that is used by the game to retrieve game information.

        Temporary files are used to store data currently in use. They can be retrieved by the current game session.

        This file is written to the user's "temp" folder, and is lost as soon as the computer is rebooted.
        We might add additional info to the tempfile, to make it act like a sort of a cache for anything that the game needs.
        """
        # TODO: perhaps add more info to the temporary file to make it act like a cache for the game, if needed.
        if self.temporary_file is None:
            _, self.temporary_file = mkstemp()
        self.write_save_file(self.temporary_file)

    def save_autosave(self):
        """
        Creates an autosave file.

        Autosave files are a backup file that gets created and can be deactivated by the user.

        Autosave can run after matches or important decisions, whereas the temporary file is always updated.
        """
        self.save_temporary_file()
        # TODO: We perhaps can have a list of autosave files and we might identify a list of autosaves, if needed.
        autosave = self.filename + '.bkp'
        self.autosave = os.path.join(self.save_directory, autosave)
        self.write_save_file(self.autosave)

    def save_game(self):
        """
        Saves the game to the file defined in filename.

        This overwrites the previous file and also saves to the temporary file again.
        """
        self.save_temporary_file()
        save_file_path = os.path.join(self.save_directory, self.filename)

        # Write save file and prevent tampering with data
        self.write_save_file(save_file_path, protect=True)
        self.delete_autosave()

    def delete_autosave(self):
        """
        Deletes the autosave file.

        Once the savegame file is effectively written, the autosave is no longer required.
        """
        if self.autosave is not None and os.path.exists(self.autosave):
            os.remove(self.autosave)

    def check_if_savedir_exists(self):
        """
        Checks if the save directory exists. If it does not, it creates the save dir.
        """
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)

    def write_save_file(self, filename: Union[str, Path], protect: bool = False):
        """
        Writes the desired save file.

        It can write the temporary_file, the auto_save or even the save_file.

        The "protect" argument will be used to prevent tampering with the save file.

        This will be used by the LoadGame module to check for corrupted save files.
        """
        # TODO: add the protect file function and features
        data = self.setup_data_file()
        with open(filename, 'wb') as fp:
            cbor2.dump(data, fp, timezone=timezone.utc)
