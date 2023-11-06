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
import random
import uuid
from abc import ABC, abstractmethod
from datetime import timedelta
from queue import Queue
from typing import Union

from esm.core.esports.moba.simulation.commentaries import Commentaries
from esm.core.esports.moba.team import Team

logger = logging.getLogger(__name__)


class EventCreator(ABC):
    @abstractmethod
    def factory_method(
        self, event_chosen: dict, game_time: float, show_commentary: bool, queue: Queue
    ):
        pass


class MobaEvent(ABC):
    def __init__(
        self,
        event_id: int = uuid.uuid4(),
        event_name: str = None,
        priority: int = 0,
        points: int = 0,
        event_time: float = 0.0,
        show_commentary: bool = True,
        queue: Queue = None,
    ):
        self.event_name = event_name
        self.event_id = event_id
        self.priority = priority
        self.show_commentary = show_commentary
        self.commentary = None
        self.event_time = event_time
        self.factor = random.gauss(0, 1)
        self.points = points
        self.queue = queue

    @classmethod
    def get_from_dict(
        cls, event_chosen: dict, game_time: float, show_commentary: bool, queue: Queue
    ):
        return cls(
            event_name=event_chosen["name"],
            priority=event_chosen["priority"],
            points=event_chosen["points"],
            event_time=game_time,
            show_commentary=show_commentary,
            queue=queue,
        )

    @staticmethod
    def _get_probable_team(team1: Team, team2: Team):
        """
        Gets the team with a higher probability to attack the other team
        """
        attack_team = random.choices([team1, team2], [team1.win_prob, team2.win_prob])[
            0
        ]
        def_team = team2 if team1 == attack_team else team1
        return attack_team, def_team

    @staticmethod
    def _get_team_players(team1, team2) -> list:
        """
        Gets all the players from each team
        """
        return [team1.list_players, team2.list_players]

    def get_commentary(
        self,
        kill_dict_event: list = None,
        atk_team_name: str = "",
        def_team_name: str = "",
        defended: bool = False,
        lane: str = "",
        jg_name: str = "",
        stole: bool = False,
        commentaries: list = None,
    ):
        """
        Chooses commentary based on a list of commentaries.
        """
        self.commentary = Commentaries(
            self.event_name,
            kill_dict_event,
            atk_team_name,
            def_team_name,
            defended,
            lane,
            jg_name,
            stole,
            commentaries,
        )

        if self.show_commentary and self.queue:
            logger.debug(self.event_name + str(self.event_time))
            self.commentary = (
                f"{str(timedelta(minutes=self.event_time))} - {self.commentary.commentary}"
                + "\n"
            )
            self.queue.put(self.commentary, block=False)

    @abstractmethod
    def calculate_event(self, *args, **kwargs):
        pass


class NothingEvent(MobaEvent):
    def calculate_event(self, team1: Team, team2: Team, which_nexus: Union[Team, None]):
        pass

    def get_commentary(self, *args, **kwargs):
        pass
