import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase
from esm.models.moba.team_simulation import MobaTeamSimulation
from esm.models.moba.events.event_types import MobaEventType, MobaJungleType

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaJungleEvent(MobaEventBase):
    def get_points(self) -> int:
        if self.jungle_type == MobaJungleType.DRAGON:
            return 15
        elif self.jungle_type == MobaJungleType.GRUB:
            return 5
        elif self.jungle_type == MobaJungleType.RIFT_HERALD:
            return 10
        elif self.jungle_type == MobaJungleType.ATAKHAN:
            return 18
        elif self.jungle_type == MobaJungleType.BARON:
            return 25
        return 0

    def get_duration(self) -> int:
        # Capturing an objective takes some time
        return random.randint(20, 60)

    def get_team_to_win_objective(
        self,
    ) -> tuple[MobaTeamSimulation, MobaTeamSimulation, bool]:
        """
        Calculates which team will win the objective and which will lose it

        Returns:
            tuple[MobaTeamSimulation, MobaTeamSimulation, bool]: The team that will win the objective, the team that will lose it,
                and whether it was stolen.
        """
        teams: list[MobaTeamSimulation] = [self.team1, self.team2]
        win_prob = [t.state.win_probability for t in teams]
        acting_team = random.choices(teams, win_prob)[0]
        defending_team = [t for t in teams if t != acting_team][0]

        acting_team_stats = sum(
            [
                (
                    player.player.communication
                    + player.player.leadership
                    + player.player.teamwork
                    + player.player.decisions
                    + player.points
                )
                for player in acting_team.players
            ]
        )

        defending_team_stats = sum(
            [
                (
                    player.player.communication
                    + player.player.leadership
                    + player.player.teamwork
                    + player.player.decisions
                    + player.points
                )
                for player in defending_team.players
            ]
        )

        steal_chance = defending_team_stats / (acting_team_stats + defending_team_stats)
        steal = random.random() > steal_chance

        if steal:
            return defending_team, acting_team
        return acting_team, defending_team

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()
        self.points = self.get_points()

        acting_team, defending_team, steal = self.get_team_to_win_objective()

        # Apply objective effects
        if self.jungle_type == MobaJungleType.DRAGON:
            if steal:
                defending_team.state.dragons += 1
                self.commentary.append(f"{defending_team.team.name} stole the! Dragon.")
            else:
                acting_team.state.dragons += 1
                self.commentary.append(f"{acting_team.team.name} secures Dragon.")
        elif self.jungle_type == MobaJungleType.BARON:
            if steal:
                defending_team.state.barons += 1
                self.commentary.append(f"{defending_team.team.name} stole the! Baron.")
            else:
                acting_team.state.barons += 1
                self.commentary.append(f"{acting_team.team.name} secures Baron.")
        elif self.jungle_type == MobaJungleType.GRUB:
            if steal:
                defending_team.state.grubs += 1
                self.commentary.append(
                    f"{defending_team.team.name} stole the! Voidgrubs."
                )
            else:
                acting_team.state.grubs += 1
                self.commentary.append(f"{acting_team.team.name} secures Voidgrubs.")
        elif self.jungle_type == MobaJungleType.RIFT_HERALD:
            if steal:
                self.commentary.append(
                    f"{defending_team.team.name} stole the! Rift Herald."
                )
                self._take_random_tower(defending_team, acting_team)
            else:
                self.commentary.append(f"{acting_team.team.name} secures Rift Herald.")
                self._take_random_tower(acting_team, defending_team)
        elif self.jungle_type == MobaJungleType.ATAKHAN:
            if steal:
                self.commentary.append(
                    f"{defending_team.team.name} stole the! Atakhan."
                )
            else:
                self.commentary.append(f"{acting_team.team.name} secures Atakhan!")

        for player in acting_team.players:
            player.points += self.points

        end_time = state.time + self.duration
        for obj in self.state.jungle_objectives:
            if obj.type == self.jungle_type:
                obj.taken(end_time)
                break

        # Advance clock
        state.time = end_time

        acting_team_aggression = sum(
            [player.player.aggression + player.points for player in acting_team.players]
        )
        defending_team_aggression = sum(
            [
                player.player.aggression + player.points
                for player in defending_team.players
            ]
        )

        acting_team_fight_chance = acting_team_aggression / (
            acting_team_aggression + defending_team_aggression
        )
        if random.random() < acting_team_fight_chance:
            self.follow_up = (MobaEventType.FIGHT_EVENT, None)

        return state

    def _take_random_tower(
        self, acting_team: MobaTeamSimulation, target_team: MobaTeamSimulation
    ) -> None:
        # Reduce one tower from the enemy, prioritizing outer lanes then base
        lanes = ["top", "mid", "bot"]
        random.shuffle(lanes)
        for lane in lanes:
            count = getattr(target_team.state.towers, lane)
            if count > 0:
                setattr(target_team.state.towers, lane, count - 1)
                return
        # If all lane towers are down, try base towers
        if target_team.state.towers.base > 0:
            target_team.state.towers.base -= 1

        # If there are no towers, try to take the inhibitor
        elif target_team.are_inhibitors_exposed():
            exposed_inhibitors = target_team.get_exposed_inhibitors()
            if len(exposed_inhibitors) > 1:
                inhibitor = random.choice(exposed_inhibitors)
            else:
                inhibitor = exposed_inhibitors[0]

            target_team.take_inhibitor(inhibitor)
            self.commentary.append(
                f"{acting_team.team.name} secures inhibitor {inhibitor}."
            )
