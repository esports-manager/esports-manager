#      eSports Manager - free and open source eSports Management game
#      Copyright (C) 2020-2024  Pedrenrique G. Guimarães
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
import pytest

from esm.core.esports.moba.generator import MobaTeamGenerator
from esm.core.esports.moba.simulation.picksbans import PBPhase, PickBanInput, PicksBans


def test_first_ban_phase(moba_picks_bans: PicksBans):
    assert moba_picks_bans.pb_phase == PBPhase.BAN_BLUE_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_RED_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_BLUE_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_RED_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_BLUE_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_RED_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.PICK_BLUE_SIDE
    assert moba_picks_bans.bans_count == 6


def test_second_ban_phase(moba_picks_bans: PicksBans):
    moba_picks_bans.bans_count = 6
    moba_picks_bans.picks_count = 6
    moba_picks_bans.pb_phase = PBPhase.BAN_RED_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_BLUE_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_RED_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.BAN_BLUE_SIDE
    moba_picks_bans.bans()
    assert moba_picks_bans.pb_phase == PBPhase.PICK_RED_SIDE
    assert moba_picks_bans.bans_count == 10


def test_first_pick_phase(moba_picks_bans: PicksBans):
    moba_picks_bans.bans_count = 6
    moba_picks_bans.pb_phase = PBPhase.PICK_BLUE_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 1
    assert moba_picks_bans.pb_phase == PBPhase.PICK_RED_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 3
    assert moba_picks_bans.pb_phase == PBPhase.PICK_BLUE_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 5
    assert moba_picks_bans.pb_phase == PBPhase.PICK_RED_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 6
    assert moba_picks_bans.pb_phase == PBPhase.BAN_RED_SIDE


def test_second_pick_phase(moba_picks_bans: PicksBans):
    moba_picks_bans.bans_count = 10
    moba_picks_bans.picks_count = 6
    moba_picks_bans.pb_phase = PBPhase.PICK_RED_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 7
    assert moba_picks_bans.pb_phase == PBPhase.PICK_BLUE_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 9
    assert moba_picks_bans.pb_phase == PBPhase.PICK_RED_SIDE
    moba_picks_bans.picks()
    assert moba_picks_bans.picks_count == 10
    assert moba_picks_bans.pb_phase == PBPhase.PB_DONE
    assert moba_picks_bans.is_over is True


def test_picks_and_bans_run(moba_picks_bans: PicksBans):
    moba_picks_bans.run()
    assert moba_picks_bans.is_over
    assert moba_picks_bans.bans_count == 10
    assert moba_picks_bans.picks_count == 10
    assert moba_picks_bans.pb_phase == PBPhase.PB_DONE
