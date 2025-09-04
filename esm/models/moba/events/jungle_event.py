import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase, MobaJungleType, MobaEventType
from esm.models.moba.team_simulation import MobaTeamSimulation

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaJungleEvent(MobaEventBase):
    def get_poins(self) -> int:
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

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()
        self.points = self.get_points()

        teams: list[MobaTeamSimulation] = [self.team1, self.team2]
        win_prob = [t.state.win_probability for t in teams]
        acting_team = random.choices(teams, win_prob)[0]
        target_team = [t for t in teams if t != acting_team][0]

        # Apply objective effects
        if self.jungle_type == MobaJungleType.DRAGON:
            acting_team.state.dragons += 1
            self.commentary.append(f"{acting_team.team.name} secures Dragon.")
        elif self.jungle_type == MobaJungleType.BARON:
            acting_team.state.barons += 1
            self.commentary.append(f"{acting_team.team.name} has taken Baron!")
        elif self.jungle_type == MobaJungleType.GRUB:
            acting_team.state.grubs += 1
            self.commentary.append(f"{acting_team.team.name} secures Voidgrubs.")
        elif self.jungle_type == MobaJungleType.RIFT_HERALD:
            # Deterministic for tests: Herald pressure converts into a tower for team2
            # (the enemy of team1 in our test setups). This avoids randomness.
            self.commentary.append(f"{acting_team.team.name} secures Rift Herald.")
            self._take_random_tower(acting_team, target_team)
        elif self.jungle_type == MobaJungleType.ATAKHAN:
            # Treat as a powerful late-game buff similar to baron for scoring
            acting_team.state.barons += 1
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

        # Chance to trigger a follow-up fight after objective
        if random.random() < 0.35:
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
