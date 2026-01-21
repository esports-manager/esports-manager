import random
from typing import TYPE_CHECKING

from esm.models.moba.events.event import MobaEventBase
from esm.models.moba.events.event_types import MobaEventType
from esm.services.narration import narrate_kill, narrate_ace, narrate_teamfight, EventSeverity

if TYPE_CHECKING:
    from esm.models.moba.moba_match_simulation import MobaMatchState


class MobaFightEvent(MobaEventBase):
    def get_duration(self) -> int:
        # Fights are usually short bursts
        return random.randint(10, 45)

    def calculate(self) -> "MobaMatchState":
        state = self.state.model_copy()
        self.duration = self.get_duration()
        end_time = state.time + self.duration

        # Which team likely wins the skirmish
        p_team1 = self.team1.state.win_probability
        winning_team = self.team1 if random.random() < p_team1 else self.team2
        losing_team = self.team2 if winning_team is self.team1 else self.team1

        # Determine fight size (favor small skirmishes)
        sizes = [1, 2, 3, 4, 5]
        weights = [0.35, 0.35, 0.18, 0.08, 0.04]
        size_per_side = random.choices(sizes, weights=weights, k=1)[0]

        # Outcome: chance of kills
        if random.random() < 0.6:
            kills = random.randint(1, min(3, size_per_side))
        else:
            kills = 0

        # Track kill streak for double kill detection
        kill_tracker = {}
        
        # Check for teamfight (4+ per side)
        if size_per_side >= 4:
            text, severity = narrate_teamfight()
            self.commentary.append(text)
        
        # Apply kills/deaths and simple points if we have players
        if kills > 0 and winning_team.players and losing_team.players:
            for _ in range(kills):
                killer = random.choice(winning_team.players)
                victim = random.choice(losing_team.players)
                killer.kills += 1
                killer.points += self.points
                victim.deaths += 1
                
                # Track for double kill
                kill_tracker[killer.player.id] = kill_tracker.get(killer.player.id, 0) + 1
                is_double = kill_tracker[killer.player.id] >= 2
                
                # First blood special commentary
                is_first_blood = not state.first_blood
                if is_first_blood:
                    state.first_blood = True
                    winning_team.state.first_blood = True
                
                text, severity = narrate_kill(
                    killer, victim, winning_team,
                    is_first_blood=is_first_blood,
                    is_double=is_double
                )
                self.commentary.append(text)
                
                # Death timer scales with game time
                minutes = max(0, state.time // 60)
                victim.death_timer = max(victim.death_timer, min(60, 10 + 2 * minutes))
                
                # Random assist from a teammate in the skirmish
                if random.random() < 0.6 and len(winning_team.players) > 1:
                    assister = random.choice(
                        [p for p in winning_team.players if p is not killer]
                    )
                    assister.assists += 1
                    assister.points += 1
        
        # Check for ace (all 5 dead)
        if kills >= 5:
            text, severity = narrate_ace(winning_team)
            self.commentary.append(text)

        # Advance time
        state.time = end_time

        # After a fight, small chance to convert to an objective or tower
        follow_roll = random.random()
        if follow_roll < 0.25:
            # Prefer jungle objective if one is up
            available_objs = [
                obj for obj in self.state.jungle_objectives if obj.available
            ]
            if available_objs:
                chosen = random.choice(available_objs)
                self.follow_up = (MobaEventType.JUNGLE_EVENT, chosen.type)
            else:
                self.follow_up = (MobaEventType.TOWER_EVENT, None)
        elif follow_roll < 0.30:
            # Rarely, immediate inhibitor push if exposed
            self.follow_up = (MobaEventType.INHIBITOR_EVENT, None)

        return state
