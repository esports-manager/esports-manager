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

import logging

from esm.definitions import DEBUG, ROOT_DIR
from esm.core.esm import ESMMobaController


logging.basicConfig(
    filename="esm.log",
    encoding="utf-8",
    format="%(levelname)s %(asctime)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p ",
)
logger = logging.getLogger(__name__)

if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.ERROR)


logging.debug(ROOT_DIR)
esm = ESMMobaController()
esm.app()
