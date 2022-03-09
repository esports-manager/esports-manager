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

import logging
import random
import uuid
from datetime import timedelta
from queue import Queue
from typing import Union

from esm.core.esports.moba.commentaries import Commentaries
from esm.core.esports.moba.player import MobaPlayer
from esm.core.esports.moba.team import Team
from esm.core.esports.moba.moba_events_details import get_moba_events

logger = logging.getLogger(__name__)


class MobaEvent:
    def __init__(
            self,
            event_id: int = uuid.uuid4(),
            event_name: str = None,
            event_type: str = None,
            priority: int = 0,
            points: int = 0,
            event_time: float = 0.0,
            show_commentary: bool = True,
            queue: Queue = None,
    ):
        self.event_name = event_name
        self.event_type = event_type
        self.event_id = event_id
        self.priority = priority
        self.show_commentary = show_commentary
        self.commentary = None
        self.event_time = event_time
        self.factor = random.gauss(0, 1)
        self.points = points
        self.queue = queue

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

    def _get_tower_attributes(self, team1: Team, team2: Team):
        """
        Checks which towers are up, and if they can be attacked. If it is a Base tower,
        there is a higher chance to focus on it
        """
        if team1.are_all_towers_down():
            attack_team = team1
            def_team = team2
        elif team2.are_all_towers_down():
            attack_team = team2
            def_team = team1
        else:
            attack_team, def_team = self._get_probable_team(team1, team2)

        lanes = [lanes for lanes, value in def_team.towers.items() if value != 0]

        # You cannot attack a base tower unless it is exposed
        if not def_team.are_base_towers_exposed():
            lanes.remove("base")

        if lanes:
            probs = []
            for lane, value in def_team.towers.items():
                if lane in lanes:
                    if value == 1:
                        probs.append(0.5)
                    elif value == 2:
                        probs.append(0.3)
                    else:
                        probs.append(0.2)

            chosen_lane = random.choices(lanes, weights=probs)[0]
        else:
            chosen_lane = None

        return attack_team, def_team, chosen_lane

    def choose_duel_players(self, killer: MobaPlayer, team: list, amount: int):
        """
        Chooses players to duel. The killer is decided in self.calculate_kill()
        """
        duel_players = []
        random.shuffle(team)

        for player in team:
            if killer.get_player_total_skill() >= player.get_player_total_skill():
                # 68% chance of happening
                if -1.0 <= self.factor <= 1.0:
                    duel_players.append(player)
                    amount -= 1
            elif self.factor >= 1.0 or self.factor <= -1.0:
                duel_players.append(player)
                amount -= 1

            if amount == 0:
                break

        if amount > 0:
            if duel_players:
                amount = len(duel_players)
            else:
                duel_players.append(random.choice(team))

        # sort teams back to normal
        team.sort(key=lambda x: x.lane.value)

        return amount, duel_players

    def player_duel(self, player1: MobaPlayer, player2: MobaPlayer):
        killed = 0
        total_prob = player1.get_player_total_skill() + player2.get_player_total_skill()

        player1_prob = player1.get_player_total_skill() / total_prob
        player2_prob = 1 - player1_prob

        diff_probs = abs(player1_prob - player2_prob)

        if player1_prob > player2_prob and (
                -1.0 <= self.factor <= 1.0 or diff_probs >= 0.3
        ):
            killed = 1
        elif diff_probs <= 0.15 and -0.5 <= self.factor <= 0.5:
            killed = 1

        if killed == 1:

            # Player gets more points for killing more players consecutively
            if player1.is_player_on_killing_spree():
                self.points += 2
            if player1.is_player_godlike():
                self.points += 4
            if player1.is_player_legendary():
                self.points += 6

            # Shutdown gives more gold to enemy team and ends the player streak
            if player2.is_player_on_killing_spree():
                self.points += 4
            if player2.is_player_godlike():
                self.points += 6
            if player2.is_player_legendary():
                self.points += 8

            # Awards points to the player that killed
            player1.points += self.points
            player1.consecutive_kills += 1
            player1.kills += 1

            player2.deaths += 1
            player2.consecutive_kills = 0

            return player2

        return None

    def calculate_assists(self, team: list, killer: MobaPlayer):
        # 50% chance to get assists
        will_there_be_assists = random.randint(0, 1)
        assistance_players = []

        if will_there_be_assists == 1:
            # Higher level players are more likely to get assists
            assists = random.choices(
                team, [player.get_player_total_skill() for player in team]
            )

            for player in assists:
                if player is not killer:
                    player.assists += 1
                    player.points += self.points / len(assists)
                    assistance_players.append(player)

        return assistance_players

    def get_kill_dict(self, killer: MobaPlayer, killed_players: list, team: list):
        return [
            {
                "killer": killer,
                "killed_player": killed_player,
                "assists": self.calculate_assists(team, killer)
            }
            for killed_player in killed_players
        ]

    def calculate_kill(self, team1: Team, team2: Team):
        """
        This will calculate the kill event
        """
        teams = self._get_team_players(team1, team2)

        # Chooses the team from which the killer will come from, most likely the team with the highest win probability
        team_killer = random.choices(teams, [team1.win_prob, team2.win_prob])[0]

        # Chooses the killer player, most probably the highest skill player
        killer = random.choices(
            team_killer, [player.get_player_total_skill() for player in team_killer]
        )[0]

        # A player is less likely to get a pentakill in a match
        # TODO: we should in the future try to weight this up with the current player total skill lvl
        # TODO: If a player is on a very good form, a pentakill should occur more often
        weight = [0.5, 0.3, 0.1, 0.08, 0.02]

        # Randomly chooses the amount of kills that the player is going to attempt
        amount_kills = random.choices([i + 1 for i in range(5)], weight)[0]

        if killer in teams[0]:
            amount_kills, duel_players = self.choose_duel_players(
                killer, teams[1], amount_kills
            )
        else:
            amount_kills, duel_players = self.choose_duel_players(
                killer, teams[0], amount_kills
            )

        # The player enters in duel mode against other players, to decide who wins the fight
        killed_players = []
        for player in duel_players:
            result = self.player_duel(killer, player)
            if result is not None:
                killed_players.append(player)

        logger.debug("Killer: {0} killed {1}".format(killer.nick_name, len(killed_players)))

        if killed_players:
            kill_dict = self.get_kill_dict(killer, killed_players, team_killer)
            logger.debug(kill_dict)
            self.get_commentary(
                kill_dict_event=kill_dict
            )

    def calculate_jungle(self, team1: Team, team2: Team):
        """
        Calculates the outcome of a major jungle attempt (baron, dragon or herald)
        """
        attack_team, def_team = self._get_probable_team(team1, team2)

        prevailing_team = random.choices(
            [attack_team, def_team], [attack_team.win_prob, def_team.win_prob]
        )[0]

        for player in prevailing_team.list_players:
            player.points += self.points / 5

        if prevailing_team == attack_team:
            self.get_commentary(atk_team_name=prevailing_team.name, jg_name=self.event_type)
        else:
            self.get_commentary(
                def_team_name=prevailing_team.name, jg_name=self.event_type, stole=True
            )

    def calculate_tower(self, team1: Team, team2: Team):
        """
        This method calculates the tower assault outcome
        """
        attack_team, def_team, lane = self._get_tower_attributes(team1, team2)

        if lane is not None:
            # Chooses which team prevails over the tower assault
            prevailing = random.choices(
                [attack_team, def_team], [attack_team.win_prob, def_team.win_prob]
            )[0]
            # If the prevailing team destroys the tower
            if prevailing == attack_team:
                self._destroy_tower(
                    prevailing, attack_team, def_team, lane
                )

            else:
                self.get_commentary(
                    def_team_name=def_team.name, defended=True, lane=lane
                )

                for player in def_team.list_players:
                    player.points += self.points / 5
        else:
            self.event_name = "NOTHING"

        logger.debug("Calculate tower method done!")

    def _destroy_tower(self, prevailing, attack_team, def_team, lane):
        # Decides the player that destroys the tower
        skills = [
            player.get_player_total_skill()
            for player in prevailing.list_players
        ]
        player = random.choices(attack_team.list_players, skills)[0]

        # player gets full points for destroying the tower
        player.points += self.points

        # Other players are awarded points as well, but reduced number of points
        for other_player in prevailing.list_players:
            if other_player != player:
                other_player.points += self.points / 4

        def_team.towers[lane] -= 1
        self.get_commentary(atk_team_name=prevailing.name, lane=lane)

        logger.debug("Team {0} destroyed the {1} tower".format(prevailing.name, lane))

    def calculate_inhib(self, team1: Team, team2: Team):
        if team1.get_exposed_inhibs():
            attack_team = team2
            def_team = team1
        elif team2.get_exposed_inhibs():
            attack_team = team1
            def_team = team2
        else:
            attack_team, def_team = self._get_probable_team(team1, team2)

        exposed = random.choice(def_team.get_exposed_inhibs())

        prevailing = random.choices(
            [attack_team, def_team], [attack_team.win_prob, def_team.win_prob]
        )[0]

        for player in prevailing.list_players:
            player.points += self.points / 5

        if prevailing == attack_team:
            def_team.inhibitors[exposed] -= 1
            self.get_commentary(atk_team_name=prevailing.name, lane=exposed)
        else:
            self.get_commentary(
                def_team_name=prevailing.name, defended=True, lane=exposed
            )

    def calculate_nexus(self, team1: Team, team2: Team, which_nexus: Union[Team, None]):
        if which_nexus is not None:
            if which_nexus == team1:
                atk_team = team2
                def_team = team1
            elif which_nexus == team2:
                atk_team = team1
                def_team = team2
            else:
                # gets which team is more likely to attack due to the skill lvl
                atk_team, def_team = self._get_probable_team(team1, team2)

            prevailing = random.choices(
                [atk_team, def_team], [atk_team.total_skill, def_team.total_skill]
            )[0]

            if prevailing == atk_team:
                def_team.nexus = 0
                self.get_commentary(atk_team_name=prevailing.name)

    def calculate_event(self, team1: Team, team2: Team, which_nexus: Union[Team, None]):
        """
        Takes the event to the appropriate function that calculates its outcome.
        """
        if self.event_name == "KILL":
            self.calculate_kill(team1, team2)
        if self.event_name == "JUNGLE":
            self.calculate_jungle(team1, team2)
        if self.event_name == "TOWER ASSAULT":
            self.calculate_tower(team1, team2)
        if self.event_name == "INHIB ASSAULT":
            self.calculate_inhib(team1, team2)
        if self.event_name == "NEXUS ASSAULT":
            self.calculate_nexus(team1, team2, which_nexus)

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
            commentaries
        )

        if self.show_commentary and self.queue:
            self.commentary = (str(timedelta(minutes=self.event_time)) + " - " + self.commentary.commentary + "\n")
            self.queue.put(self.commentary, block=False)


class MobaEventHandler:
    def __init__(self, show_commentary: bool = False, queue: Queue = None):
        """
        Initializes the event handler.
        """
        self.events = get_moba_events()
        self.commentaries = None
        self.event = MobaEvent()
        self.enabled_events = []
        self.event_history = []
        self.show_commentary = show_commentary
        self.queue = queue if self.show_commentary else None

    def get_game_state(
            self, game_time, which_nexus_exposed, is_any_inhib_open, towers_number
    ) -> None:
        if game_time == 0.0:
            self.get_enabled_events(["NOTHING", "KILL"])

        if game_time >= 10.0:
            self.get_enabled_events(["TOWER ASSAULT"])
        if towers_number == 0:
            self.remove_enabled_event("TOWER ASSAULT")

        self.check_jungle(game_time)

        # TODO: We need to add a Inhibitor Spawn time
        if is_any_inhib_open:
            self.get_enabled_events(["INHIB ASSAULT"])
        else:
            self.remove_enabled_event("INHIB ASSAULT")

        if which_nexus_exposed is not None:
            self.get_enabled_events(["NEXUS ASSAULT"])

    def check_jungle(self, game_time: float) -> None:
        """
        Checks if the jungle event is available
        """
        jungle_names = [event for event in self.events if event["name"] == "JUNGLE"]

        for event in jungle_names:
            if self.event.event_type == event["jg_name"]:
                if event in self.enabled_events:
                    self.enabled_events.remove(event)
                event["spawn_time"] += event["cooldown"]
            elif (
                    game_time >= event["spawn_time"]
                    and event not in self.enabled_events
            ):
                self.enabled_events.append(event)
            if 0.0 < event["end_time"] <= game_time and event in self.enabled_events:
                self.enabled_events.remove(event)

    def remove_enabled_event(self, name):
        """
        Removes no longer available event from the list of enabled events
        """
        for event in self.enabled_events:
            if event["name"] == name:
                self.enabled_events.remove(event)

    def get_enabled_events(self, names):
        """
        Adds events to the list of enabled events
        """
        for event in self.events:
            for name in names:
                if event["name"] == name and event not in self.enabled_events:
                    self.enabled_events.append(event)

    def load_commentaries_file(self):
        """
        Load commentaries file
        """
        pass

    def get_event_priorities(self):
        """
        Gets the priority of events
        """
        return [event["priority"] for event in self.enabled_events]

    def generate_event(self, game_time: float):
        """
        Generates events for the match based on their priorities and available events.
        """
        priorities = self.get_event_priorities()
        ev_chosen = random.choices(self.enabled_events, priorities)[0]
        if ev_chosen["name"] != "JUNGLE":
            self.event = MobaEvent(
                event_name=ev_chosen["name"],
                priority=ev_chosen["priority"],
                points=ev_chosen["points"],
                event_time=game_time,
                show_commentary=self.show_commentary,
                queue=self.queue,
            )
        else:
            self.event = MobaEvent(
                event_name=ev_chosen["name"],
                event_type=ev_chosen["jg_name"],
                priority=ev_chosen["priority"],
                points=ev_chosen["points"],
                event_time=game_time,
                show_commentary=self.show_commentary,
                queue=self.queue,
            )
        self.event_history.append(self.event)
