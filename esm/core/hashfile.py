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
import cbor2
import os
import hashlib
from esm.definitions import HASH_FILE
from dataclasses import dataclass, field


@dataclass
class HashFile:
    """
    The Hash file is a file that stores data related to load and save games.

    It is used to make it more difficult to tamper with Save game files.
    Every time a game is saved, the filename is stored to the HashFile, which
    also stores the save file hash.

    When the game is loaded, the LoadGame module compares the loaded save file with
    the hash stored in the Hash file. If the hash is different, then the file might
    be corrupted or has been tampered with.

    The HashFile is a binary file, just like the save game files. It's an additional
    method to protect save game files, but may not be enough for that.
    """
    filename: str = HASH_FILE
    hash_data: dict = field(default_factory=dict)

    def write_hash_file(self):
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'wb') as fp:
            cbor2.dump(self.hash_data, fp)

    def read_hash_file(self):
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        with open(self.filename, 'rb') as fp:
            self.hash_data = cbor2.load(fp)

    def hash_file(self, filename):
        """
        Creates a SHA256 hash of the savegame file.

        Solution for hashing:
        https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
        """
        h = hashlib.sha256()
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                h.update(byte_block)

        return h.hexdigest()

    def write_to_hash_file(self, filename):
        try:
            self.read_hash_file()
        except FileNotFoundError:
            pass
        self.hash_data[filename] = self.hash_file(filename)
        self.write_hash_file()
