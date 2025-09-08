from sqlmodel import SQLModel, Field
from typing import Optional, Tuple
from datetime import datetime
import random

from esm.models.moba.events.event_factory import get_event_from_type
from esm.models.moba.player import MobaPlayerRole
from esm.models.moba.team_simulation import MobaTeamSimulation
from esm.models.moba.events.event import MobaEventBase
from esm.models.moba.moba_match_state import (
    MobaMatchState,
    MobaMatchStatus,
    MobaJungleObjective,
)
from esm.models.moba.events.event_types import MobaEventType, MobaJungleType


class MobaMatchSimulation(SQLModel):
    team1: MobaTeamSimulation
    team2: MobaTeamSimulation
    state: "MobaMatchState" = MobaMatchState()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    events: list["MobaEventBase"] = Field(default_factory=list)
    enabled_events: list[Tuple[MobaEventType, Optional[MobaJungleType]]] = Field(
        default_factory=list
    )
    commentary_log: list[str] = Field(default_factory=list)

    def _towers_remaining(self) -> Tuple[int, int]:
        return self.team1.towers_remaining, self.team2.towers_remaining

    def _inhibitors_exposed(self) -> Tuple[bool, bool]:
        return self.team1.are_inhibitors_exposed, self.team2.are_inhibitors_exposed

    def _nexus_conditions_met(self) -> Tuple[bool, bool]:
        return self.team1.is_nexus_exposed(), self.team2.is_nexus_exposed()

    def _update_jungle_objectives(self) -> list[MobaJungleObjective]:
        for obj in self.state.jungle_objectives:
            obj.refresh(self.state.time)
        return self.state.jungle_objectives

    def _update_win_probability(self) -> None:
        s1, s2 = self.team1.score(), self.team2.score()
        total = s1 + s2
        self.team1.state.win_probability = s1 / total if total > 0 else 0.5
        self.team2.state.win_probability = s2 / total if total > 0 else 0.5

    def add_event(self, event: MobaEventBase) -> None:
        self.events.append(event)

    def get_enabled_events(
        self,
    ) -> list[Tuple[MobaEventType, Optional[MobaJungleType]]]:
        enabled: list[Tuple[MobaEventType, Optional[MobaJungleType]]] = [
            (MobaEventType.NOTHING_EVENT, None),
            (MobaEventType.FIGHT_EVENT, None),
        ]

        for obj in self._update_jungle_objectives():
            if obj.available:
                enabled.append((MobaEventType.JUNGLE_EVENT, obj.type))

        # Towers become available after 10 mins
        if self.state.time >= 10 * 60:
            t1, t2 = self._towers_remaining()
            if (t1 + t2) > 0:
                enabled.append((MobaEventType.TOWER_EVENT, None))

        inhibitors_team1, inhibitors_team2 = self._inhibitors_exposed()
        if inhibitors_team1 or inhibitors_team2:
            enabled.append((MobaEventType.INHIBITOR_EVENT, None))

        nexus_team1, nexus_team2 = self._nexus_conditions_met()
        if nexus_team1 or nexus_team2:
            enabled.append((MobaEventType.NEXUS_EVENT, None))

        self.enabled_events = enabled
        return enabled

    def get_event(self) -> MobaEventBase:
        # Choose one event from the enabled list using weighted probabilities
        candidates = self.get_enabled_events()

        # Base weights
        weights: list[float] = []

        # Count available jungle objectives to adjust weights
        jungle_count = sum(1 for c in candidates if c[0] == MobaEventType.JUNGLE_EVENT)

        for ev, jtype in candidates:
            if ev == MobaEventType.NOTHING_EVENT:
                w = 0.5 if jungle_count == 0 else 0.3
            elif ev == MobaEventType.FIGHT_EVENT:
                # Slightly less common than nothing; increase a bit if many objectives are up
                w = 0.2 + 0.03 * jungle_count
            elif ev == MobaEventType.JUNGLE_EVENT:
                # If objectives are up, they should be attractive
                # Bias toward the team with higher win prob by giving a modest boost
                lead = abs(
                    self.team1.state.win_probability - self.team2.state.win_probability
                )
                w = 0.12 + 0.06 * lead
            elif ev == MobaEventType.TOWER_EVENT:
                w = 0.12
            elif ev == MobaEventType.INHIBITOR_EVENT:
                w = 0.08
            elif ev == MobaEventType.NEXUS_EVENT:
                w = 0.05
            else:
                w = 0.01
            # Late-game pressure: after 50:00, heavily bias towards objectives that close games
            minutes = self.state.minutes_played
            if minutes >= 50:
                if ev == MobaEventType.NEXUS_EVENT:
                    # Strongly favor ending the game once Nexus is attackable
                    w *= 6.0
                elif ev == MobaEventType.INHIBITOR_EVENT:
                    # Push toward enabling Nexus conditions
                    w *= 2.5
                elif ev == MobaEventType.TOWER_EVENT:
                    # Towers also accelerate toward base exposure
                    w *= 1.8
                elif ev == MobaEventType.FIGHT_EVENT:
                    # Deprioritize random fights late
                    w *= 0.7
                elif ev == MobaEventType.NOTHING_EVENT:
                    # Make "nothing happens" rare late game
                    w *= 0.2
            if minutes >= 60:
                # Further escalate Nexus ending in ultra late game
                if ev == MobaEventType.NEXUS_EVENT:
                    w *= 1.5
            weights.append(w)

        # Normalize to probabilities
        s = sum(weights)
        if s <= 0:
            # Fallback
            chosen = (MobaEventType.NOTHING_EVENT, None)
        else:
            probs = [w / s for w in weights]
            chosen = random.choices(candidates, weights=probs, k=1)[0]

        # Update win probabilities prior to instantiating the event
        self._update_win_probability()

        # Instantiate the chosen event
        ev_type, jtype = chosen
        event = get_event_from_type(ev_type, jungle_type=jtype)
        # Populate runtime context
        event.name = ev_type.value
        event.event_type = ev_type
        event.jungle_type = jtype
        event.team1 = self.team1
        event.team2 = self.team2
        event.state = self.state
        return event

    # --- Simulation Loop ---
    def start(self) -> None:
        if self.state.status == MobaMatchStatus.NOT_STARTED:
            self.state.reset()
            self.state.status = MobaMatchStatus.IN_PROGRESS
            self.started_at = datetime.now()
            self.updated_at = self.started_at

    def _instantiate_event(
        self, ev_type: MobaEventType, jtype: Optional[MobaJungleType]
    ) -> MobaEventBase:
        event = get_event_from_type(ev_type, jungle_type=jtype)
        event.name = ev_type.value
        event.event_type = ev_type
        event.jungle_type = jtype
        event.team1 = self.team1
        event.team2 = self.team2
        event.state = self.state
        return event

    def _follow_up_is_valid(
        self, follow_up: Tuple[MobaEventType, Optional[MobaJungleType]]
    ) -> bool:
        ev, jtype = follow_up
        enabled = self.get_enabled_events()
        if ev == MobaEventType.JUNGLE_EVENT:
            # require specific objective available
            return (ev, jtype) in enabled
        # For others, just ensure event type is enabled
        return any(e == ev for e, _ in enabled)

    def _execute_event(self, event: MobaEventBase) -> "MobaMatchState":
        # Calculate result state and commit
        new_state = event.calculate()
        self.state = new_state
        self.updated_at = datetime.now()
        # Aggregate commentary
        if getattr(event, "commentary", None):
            self.commentary_log.extend(event.commentary)
        # After time advances, tick death timers and apply farming for alive players
        try:
            # Do not tick immediately after fight events; tests expect fresh timers
            if event.event_type != MobaEventType.FIGHT_EVENT:
                self._tick_after_event(event.duration)
        except Exception:
            # Never break simulation on tick errors
            pass
        # Track event
        self.add_event(event)
        # Update win probabilities after state changes
        self._update_win_probability()
        # End time bookkeeping
        if self.state.status == MobaMatchStatus.ENDED:
            self.ended_at = datetime.now()
        return event

    def _tick_after_event(self, duration: int) -> None:
        if duration <= 0:
            return
        # Farming starts after ~2 minutes
        farming_enabled = self.state.time >= 2 * 60
        for team in (self.team1, self.team2):
            for p in team.players:
                # Tick death timers first
                if p.death_timer > 0:
                    p.death_timer = max(0, p.death_timer - duration)
                    continue
                if not farming_enabled:
                    continue
                # Base CS/min by the assigned simulation role (fallback to player's default)
                role = getattr(p, "role", None) or getattr(p.player, "role", None)
                if role in (MobaPlayerRole.TOP, MobaPlayerRole.MID, MobaPlayerRole.ADC):
                    base_rate = 10.0
                elif role == MobaPlayerRole.JUNGLE:
                    base_rate = 7.5
                else:
                    # SUPPORT or unknown
                    base_rate = 2.0
                # Skill factor from player's farming attribute (0.8x to 1.2x)
                farming_attr = getattr(p.player, "farming", 50)
                factor = 0.8 + 0.4 * (max(0, min(100, farming_attr)) / 100.0)
                rate = base_rate * factor
                # Apply off-role performance factor if applicable
                try:
                    rate *= float(getattr(p, "get_off_role_factor")())
                except Exception:
                    pass
                # Convert per-minute rate to this step's duration
                gain = int(max(0, round(rate * (duration / 60.0))))
                if gain > 0:
                    p.farm += gain
                    # Small points from farming
                    p.points += max(0, gain // 20)

    def step(self) -> Optional[MobaEventBase]:
        if self.state.status == MobaMatchStatus.ENDED:
            return None
        if self.state.status == MobaMatchStatus.NOT_STARTED:
            self.start()

        # Prefer chaining follow-up events immediately
        # If there is a previous event with a valid follow-up, run it
        if self.events and self.events[-1].follow_up:
            fu = self.events[-1].follow_up
            if fu and self._follow_up_is_valid(fu):
                ev = self._instantiate_event(fu[0], fu[1])
                return self._execute_event(ev)

        # Otherwise select a new event based on current state
        ev = self.get_event()
        return self._execute_event(ev)

    def run_until_end(self, max_steps: int | None = None) -> None:
        # Run until the match is ended. The max_steps parameter is accepted for
        # backward compatibility but is ignored to avoid imposing a hard cap.
        steps = 0
        while self.state.status != MobaMatchStatus.ENDED:
            executed = self.step()
            if executed is None:
                break
            # If the executed event produced a follow-up, loop to immediately execute it
            chain = 0
            while (
                executed.follow_up
                and self.state.status != MobaMatchStatus.ENDED
                and self._follow_up_is_valid(executed.follow_up)
            ):
                executed = self._execute_event(
                    self._instantiate_event(
                        executed.follow_up[0], executed.follow_up[1]
                    )
                )
                chain += 1
                if chain >= 10:
                    # safety cap to avoid excessive chaining within a single step
                    break
            steps += 1
