# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## The main menu, New Game, Load Game and the roster screens (new game and
## roster specs).

menu-new-game = New Game
menu-load-game = Load Game
menu-quit = Quit
nav-back = Back
nav-next = Next

new-game-title = New Game
# $step is 1, 2 or 3.
new-game-progress = Step { $step } of 3
new-game-step-manager = Your name
new-game-step-team = Choose your team
new-game-step-confirm = Name your save
new-game-manager-label = Manager name
new-game-region-tabs = Regions
new-game-chosen-team = Team: { $team }
new-game-save-label = Save name
new-game-advanced = Advanced
new-game-seed-label = World seed (optional)
new-game-seed-hint = The same seed builds the same world.
new-game-start = Start
new-game-starting = Building the world…
new-game-failed = The game couldn't be started:
# $stars is from 1 to 5.
team-strength = { $stars } of 5 stars

load-game-title = Load Game
load-game-empty = No saves yet.
load-game-column-name = Save
load-game-column-manager = Manager
load-game-column-team = Team
load-game-column-date = Date
load-game-column-played = Last played
# $damage is why the save can't be opened.
load-game-damaged = Can't open: { $damage }
load-game-failed = The save couldn't be opened:
load-game-list-failed = The saves couldn't be listed:
load-game-opening = Opening the save…

roster-view-player = { $nickname }, view profile
profile-back = Back to roster
# $age is in whole years.
profile-age = { $age } years old
profile-nationality = { $country } ({ $code })
