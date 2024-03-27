#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
import logging
import os

from ..definitions import DEBUG
from .db import DB
from .game_session import GameSession
from .settings import Settings


class AmountPlayersError(Exception):
    pass


class ESMCore:
    """
    Core module deals with core functions of the game
    """

    def __init__(self):
        self.settings = Settings()
        self.settings.load_config_file()
        self.logger = self.initialize_logging()
        self.db = DB(self.settings)
        self.game_session = GameSession(self.settings, self.db)

    def initialize_logging(self):
        os.makedirs(self.settings.logs_dir, exist_ok=True)
        logs_file = self.settings.logs_dir / "esm.log"
        logging.basicConfig(
            filename=logs_file,
            encoding="utf-8",
            format="%(levelname)s %(asctime)s: %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p ",
        )

        if DEBUG:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.ERROR)

        return logging.getLogger(__name__)
