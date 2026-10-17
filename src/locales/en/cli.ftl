# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## The headless CLI, `esm` (new game spec).

cli-region = { $region } · { $league }
cli-region-only = { $region }
cli-team = { $tag }  { $name }  { $stars }/5  { $id }
cli-new-game-created = Created { $file } with { $team }.
cli-saves-empty = No saves yet.
# $inUse is "yes" when another process has the save open.
cli-save = { $name } · { $manager } · { $team } · { $date } ({ $file }){ $inUse ->
    [yes] { " · " }open somewhere else
   *[no] {""}
}
cli-save-damaged = { $file }: { $damage }
cli-roster-title = { $team } · { $league }
cli-player-title = { $nickname } · { $name } · { $team }
