# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## A CLI sem interface, `esm` (especificação do novo jogo).

cli-region = { $region } · { $league }
cli-region-only = { $region }
cli-team = { $tag }  { $name }  { $stars }/5  { $id }
cli-new-game-created = { $file } criado com { $team }.
cli-saves-empty = Nenhum jogo salvo ainda.
# $inUse é "yes" quando outro processo tem o jogo salvo aberto.
cli-save = { $name } · { $manager } · { $team } · { $date } ({ $file }){ $inUse ->
    [yes] { " · " }aberto em outro lugar
   *[no] {""}
}
cli-save-damaged = { $file }: { $damage }
cli-roster-title = { $team } · { $league }
cli-player-title = { $nickname } · { $name } · { $team }
