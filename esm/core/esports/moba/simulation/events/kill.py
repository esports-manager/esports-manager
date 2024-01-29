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
from queue import Queue
from typing import Union

from esm.core.esports.moba.player import MobaPlayer
from esm.core.esports.moba.team import Team
from .general import MobaEvent, EventCreator

logger = logging.getLogger(__name__)


class KillEventEventCreator(EventCreator):
    def factory_method(
        self, event_chosen: dict, game_time: float, show_commentary: bool, queue: Queue
    ):
        return KillEvent(
            event_name=event_chosen["name"],
            priority=event_chosen["priority"],
            points=event_chosen["points"],
            event_time=game_time,
            show_commentary=show_commentary,
            queue=queue,
        )


class KillEvent(MobaEvent):
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
                self.points *= 1.20
            if player1.is_player_godlike():
                self.points *= 1.25
            if player1.is_player_legendary():
                self.points *= 1.30

            # Shutdown gives more gold to enemy team and ends the player streak
            if player2.is_player_on_killing_spree():
                self.points *= 1.10
            if player2.is_player_godlike():
                self.points *= 1.15
            if player2.is_player_legendary():
                self.points *= 1.20

            # Awards points to the player that killed
            player1.points += int(self.points)
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
                "assists": self.calculate_assists(team, killer),
            }
            for killed_player in killed_players
        ]

    def calculate_event(self, team1: Team, team2: Team, which_nexus: Union[Team, None]):
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

        logger.debug(
            "Killer: {0} killed {1}".format(killer.nick_name, len(killed_players))
        )

        if killed_players:
            kill_dict = self.get_kill_dict(killer, killed_players, team_killer)
            logger.debug(kill_dict)
            self.get_commentary(kill_dict_event=kill_dict)
