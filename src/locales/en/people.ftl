# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## People, the roster and the player profile.

# $order is "given-first" or "family-first", from the player's nationality.
person-full-name = { $order ->
    [family-first] { $family } { $given }
   *[given-first] { $given } { $family }
}
roster-starters = Starters
roster-subs = Subs
roster-column-role = Role
roster-column-nickname = Nickname
roster-column-name = Name
roster-column-nationality = Nat.
roster-column-age = Age
roster-column-overall = Overall
profile-overall = Overall { $overall }
profile-born = Born { $date }
profile-skills = Skills
profile-traits = Traits
profile-hidden = Hidden
profile-unknown = ?
# What screen readers say for profile-unknown.
profile-unknown-label = unknown
attribute-mechanics = Mechanics
attribute-laning = Laning
attribute-game-sense = Game Sense
attribute-awareness = Awareness
attribute-positioning = Positioning
attribute-champion-pool-breadth = Champion Pool Breadth
attribute-shotcalling = Shotcalling
attribute-teamwork = Teamwork
attribute-aggression = Aggression
attribute-composure = Composure
attribute-work-ethic = Work Ethic
attribute-consistency = Consistency
attribute-potential = Potential
