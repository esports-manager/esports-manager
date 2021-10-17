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

import random
import uuid
from typing import Union, Any

from esm.core.esports.moba.player import MobaPlayer
from esm.core.esports.moba.team import Team
from esm.resources.utils import load_list_from_file


class MobaEvent:
    def __init__(
        self,
        event_id: int = uuid.uuid4(),
        event_name: str = None,
        priority: int = 0,
        points: int = 0,
        event_time: float = 0.0,
        show_commentary=True,
    ):
        self.event_name = event_name
        self.event_id = event_id
        self.priority = priority
        self.show_commentary = show_commentary
        self.commentary = None
        self.event_time = event_time
        self.factor = random.gauss(0, 1)
        self.points = points

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

        probs = []
        if lanes:
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
            player1.kills += 1
            if player1.is_player_on_killing_spree():
                self.points += 5
            if player1.is_player_godlike():
                self.points += 10
            if player1.is_player_legendary():
                self.points += 20
            if player2.is_player_on_killing_spree():
                self.points += 10
                player2.consecutive_kills = 0
            if player2.is_player_godlike():
                self.points += 20
                player2.consecutive_kills = 0
            if player2.is_player_legendary():
                self.points += 50
                player2.consecutive_kills = 0
            player1.points += self.points
            player1.consecutive_kills += 1
            player2.deaths += 1

        return killed

    def calculate_assists(self, team: list, killer: MobaPlayer, amount_kills: int):
        will_there_be_assists = random.randint(0, 1)
        if will_there_be_assists == 1:

            for i in range(amount_kills):
                # Get players to assign assists
                assists = random.choices(
                    team, [player.get_player_total_skill() for player in team]
                )

                for player in assists:
                    if player is not killer:
                        player.assists += 1
                        player.points += self.points / len(assists)

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

        # TODO: Currently, Assists are not awarded to members of the killer's team. This should be implemented
        # TODO: Before 0.1.0-alpha
        # The player enters in duel mode against other players, to decide who wins the fight
        for player in duel_players:
            killed = self.player_duel(killer, player)
            if killed == 0:
                duel_players.remove(player)

        amount_kills = len(duel_players)
        self.calculate_assists(team_killer, killer, amount_kills)
        killed_players = duel_players

        if killed_players:
            self.get_commentary(
                amount_kills, killer=killer, killed_names=killed_players
            )

    def calculate_jungle(self, team1: Team, team2: Team, jungle: str):
        """
        Calculates the outcome of a major jungle attempt (baron or dragon)
        """
        attack_team, def_team = self._get_probable_team(team1, team2)

        prevailing_team = random.choices(
            [attack_team, def_team], [attack_team.win_prob, def_team.win_prob]
        )[0]

        for player in prevailing_team.list_players:
            player.points += self.points / 5

        if prevailing_team == attack_team:
            self.get_commentary(atk_team_name=prevailing_team.name, jg_name=jungle)
        else:
            self.get_commentary(
                def_team_name=prevailing_team.name, jg_name=jungle, stole=True
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
        if self.event_name == "BARON":
            self.calculate_jungle(team1, team2, "Baron")
        if self.event_name == "DRAGON":
            self.calculate_jungle(team1, team2, "Dragon")
        if self.event_name == "TOWER ASSAULT":
            self.calculate_tower(team1, team2)
        if self.event_name == "INHIB ASSAULT":
            self.calculate_inhib(team1, team2)
        if self.event_name == "NEXUS ASSAULT":
            self.calculate_nexus(team1, team2, which_nexus)

    @staticmethod
    def list_names(players: list):
        names = ""
        for i, player in enumerate(players):
            if i == len(players) - 1:
                names = names + player.nick_name + "."
            else:
                names = names + player.nick_name + ", "

        return names

    def _get_kill_commentaries(
        self,
        killed_names,
        amount_kills,
        killer
    ):
        names = self.list_names(killed_names)
        if amount_kills == 2:
            self.commentary = killer.nick_name + " got a Double Kill!"
        elif amount_kills == 3:
            self.commentary = killer.nick_name + " got a Triple Kill!"
        elif amount_kills == 4:
            self.commentary = killer.nick_name + " got a QUADRA KILL!"
        elif amount_kills == 5:
            self.commentary = killer.nick_name + " got a PENTAKILL!"

        if amount_kills != 0:
            if self.commentary is not None:
                self.commentary = (
                    self.commentary + "\n" + killer.nick_name + " has slain: " + names
                )
            else:
                self.commentary = killer.nick_name + " has slain " + names

        if self.commentary is not None:
            if killer.is_player_godlike():
                self.commentary = (
                    self.commentary + "\n" + killer.nick_name + " is GODLIKE!"
                )
            if killer.is_player_on_killing_spree():
                self.commentary = (
                    self.commentary + "\n" + killer.nick_name + " is on a KILLING SPREE!"
                )
            if killer.is_player_legendary():
                self.commentary = (
                    self.commentary + "\n" + killer.nick_name + " is LEGENDARY!!"
                )
    
    def _get_jg_commentary(
        self,
        stole,
        def_team_name,
        atk_team_name,
        jg_name,
    ):
        if stole:
            self.commentary = def_team_name + " stole the " + jg_name
        else:
            self.commentary = atk_team_name + " has slain the " + jg_name

    def _get_inhib_commentary(
        self,
        defended,
        def_team_name,
        atk_team_name,
        lane,
    ):
        if defended:
            self.commentary = (
                def_team_name
                + " has defended the "
                + lane
                + " inhibitor successfully"
            )
        else:
            self.commentary = (
                atk_team_name + " has destroyed the " + lane + " inhibitor"
            )

    def _get_tower_commentary(
        self,
        defended,
        def_team_name,
        atk_team_name,
        lane
    ):
        if defended:
            self.commentary = (
                def_team_name + " has defended the " + lane + " tower successfully"
            )
        else:
            self.commentary = (
                atk_team_name + " has destroyed the " + lane + " tower"
            )
    
    def get_commentary(
        self,
        amount_kills: int = 0,
        atk_team_name: str = "",
        def_team_name: str = "",
        killer: MobaPlayer = None,
        defended: bool = False,
        killed_names: Union[list, str] = "",
        lane: str = "",
        jg_name: str = "",
        stole: bool = False,
        commentaries: list = None,
    ):
        """
        Chooses commentary based on a list of commentaries.

        For now this is a dummy implementation that does nothing, but it will load commentaries depending
        on the locale.
        """
        if self.event_name == "KILL" and killed_names is not None:
            self._get_kill_commentaries(killed_names, amount_kills, killer)

        if self.event_name in ["BARON", "DRAGON"]:
            self._get_jg_commentary(stole, def_team_name, atk_team_name, jg_name)

        if self.event_name == "INHIB ASSAULT":
            self._get_inhib_commentary(defended, def_team_name, atk_team_name, lane)

        elif self.event_name == "NEXUS ASSAULT":
            self.commentary = atk_team_name + " won the match!"

        elif self.event_name == "TOWER ASSAULT":
            self._get_tower_commentary(defended, def_team_name, atk_team_name, lane)
            
        if self.show_commentary:
            print(str(self.event_time) + " " + self.event_name)
            print(self.commentary)


class MobaEventHandler:
    def __init__(self):
        """
        Initializes the event handler.
        """
        self.events = load_list_from_file("mobaevents.json")
        self.commentaries = None
        self.event = MobaEvent()
        self.enabled_events = []
        self.event_history = []

    def get_game_state(
        self, game_time, which_nexus_exposed, is_any_inhib_open, towers_number
    ) -> None:
        if game_time == 0.0:
            self.get_enabled_events(["NOTHING", "KILL"])

        if game_time >= 10.0:
            self.get_enabled_events(["TOWER ASSAULT"])
        if towers_number == 0:
            self.remove_enabled_event("TOWER ASSAULT")

        self.check_jungle(game_time, "BARON")
        self.check_jungle(game_time, "DRAGON")

        # TODO: We need to add a Inhibitor Spawn time
        if is_any_inhib_open:
            self.get_enabled_events(["INHIB ASSAULT"])
        else:
            self.remove_enabled_event("INHIB ASSAULT")

        if which_nexus_exposed is not None:
            self.get_enabled_events(["NEXUS ASSAULT"])

    def check_jungle(self, game_time: float, jungle: str) -> None:
        """
        Checks if the jungle event is available
        """
        for event in self.events:
            if event["name"] == jungle:
                if self.event.event_name == jungle:
                    if event in self.enabled_events:
                        self.enabled_events.remove(event)
                    event["spawn_time"] += event["cooldown"]
                else:
                    if (
                        game_time >= event["spawn_time"]
                        and event not in self.enabled_events
                    ):
                        self.get_enabled_events([event["name"]])

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

    def generate_event(self, game_time: float, show_commentary: bool):
        """
        Generates events for the match based on their priorities and available events.
        """
        priorities = self.get_event_priorities()
        ev_chosen = random.choices(self.enabled_events, priorities)[0]
        self.event = MobaEvent(
            event_name=ev_chosen["name"],
            priority=ev_chosen["priority"],
            points=ev_chosen["points"],
            event_time=game_time,
            show_commentary=show_commentary,
        )
        self.event_history.append(self.event)
