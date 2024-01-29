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
from datetime import datetime
from uuid import uuid4

import pytest

from ..core.esports.moba.mobamatch import InvalidTeamId, MatchType, MobaMatch


@pytest.fixture
def moba_match() -> MobaMatch:
    return MobaMatch(
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        MatchType.FRIENDLY,
        datetime.strptime("2020-01-01, 10:00", "%Y-%m-%d, %H:%M"),
        None,
    )


def test_moba_match_serialize(moba_match: MobaMatch):
    team1 = moba_match.team1.hex
    team2 = moba_match.team2.hex
    serialized = moba_match.serialize()
    assert serialized["team1"] == team1
    assert serialized["team2"] == team2
    assert serialized["victorious_team"] is None
    assert MatchType(serialized["match_type"]) == MatchType.FRIENDLY


def test_moba_match_raises_error_for_invalid_victorious_team(moba_match):
    moba_match.victorious_team = uuid4()
    with pytest.raises(InvalidTeamId):
        moba_match.serialize()


def test_moba_match_raises_error_loading_invalid_victorious_team(moba_match):
    serialized = moba_match.serialize()
    serialized["victorious_team"] = uuid4().hex
    with pytest.raises(InvalidTeamId):
        MobaMatch.get_from_dict(serialized)
