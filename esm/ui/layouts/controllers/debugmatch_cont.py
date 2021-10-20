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
from queue import Queue

from .controllerinterface import IController
from ..debugmatch import DebugMatchLayout


class DebugMatchController(IController):
    def __init__(self, controller):
        super().__init__(controller)
        self.layout = DebugMatchLayout(self)
        self.queue = Queue()

    def get_queue_messages_and_update(self):
        if not self.queue.empty():
            message = self.queue.get(block=False)
            self.controller.update_gui_element("debug_match_output", value=message, append=True)

    def update(self, event, values, make_screen):
        team_data = self.controller.team_data
        update_debug_match_info = self.controller.update_debug_match_info

        self.get_queue_messages_and_update()

        # Click the Start Match button
        if event == "debug_startmatch_btn":
            self.controller.update_gui_element("debug_match_output", value="", append=False)
            self.controller.is_match_running = True
            self.controller.reset_match(self.controller.current_match, self.queue)
            self.controller.current_match.is_match_over = False
            self.controller.start_match_sim_thread()

        # Click the Cancel button
        if event == "debug_cancel_btn":
            if self.controller.is_match_running:
                self.controller.current_match.is_match_over = True
                self.controller.current_match = None
            make_screen("debug_match_screen", "main_screen")

        # Click the New Teams button
        elif event == "debug_newteams_btn":
            self.controller.check_files()
            self.controller.initialize_random_debug_match()
            data = team_data(match_live=self.controller.current_match)
            update_debug_match_info(self.controller.current_match, data)

        # Click the Reset Match button
        elif event == "debug_resetmatch_btn":
            self.controller.reset_match(self.controller.current_match)
            data = team_data(match_live=self.controller.current_match)
            update_debug_match_info(self.controller.current_match, data)

        # Check if the match is running to update values on the fly
        if self.controller.is_match_running:
            if (
                self.controller.current_match is not None
                and self.controller.current_match.is_match_over
                and not self.controller.match_thread.is_alive()
            ):
                self.controller.is_match_running = False

            if self.controller.current_match is not None:
                self.controller.current_match.simulate = bool(
                    values["debug_simulate_checkbox"]
                )
                data = team_data(self.controller.current_match)
                update_debug_match_info(self.controller.current_match, data)
