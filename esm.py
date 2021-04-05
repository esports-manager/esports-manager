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

import threading

from src.core.core import Core
from src.ui.gui import View


class ESM:
    def __init__(self):
        self.core = Core()
        self.view = View(self)

    def start_match_sim(self, window):
        self.core.match_simulation.simulation()
        window.write_event_value('MATCH SIMULATED', 'DONE')

    def start_match_sim_thread(self, window):
        try:
            thread = threading.Thread(target=self.start_match_sim, args=(window))
            thread.start()
        except Exception as e:
            print('Error starting thread.')

    def app(self):
        self.view.start()


esm = ESM()
esm.app()
