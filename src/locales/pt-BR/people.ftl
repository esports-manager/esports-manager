# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## Pessoas, o elenco e o perfil do jogador.

# $order é "given-first" ou "family-first", conforme a nacionalidade.
person-full-name = { $order ->
    [family-first] { $family } { $given }
   *[given-first] { $given } { $family }
}
roster-starters = Titulares
roster-subs = Reservas
roster-column-role = Função
roster-column-nickname = Apelido
roster-column-name = Nome
roster-column-nationality = Nac.
roster-column-age = Idade
roster-column-overall = Geral
profile-overall = Geral { $overall }
profile-born = Data de nascimento: { $date }
profile-skills = Habilidades
profile-traits = Traços
profile-hidden = Ocultos
profile-unknown = ?
# What screen readers say for profile-unknown.
profile-unknown-label = desconhecido
attribute-mechanics = Mecânica
attribute-laning = Fase de rotas
attribute-game-sense = Leitura de Jogo
attribute-awareness = Percepção
attribute-positioning = Posicionamento
attribute-champion-pool-breadth = Variedade de Campeões
attribute-shotcalling = Liderança em Jogo
attribute-teamwork = Trabalho em Equipe
attribute-aggression = Agressividade
attribute-composure = Compostura
attribute-work-ethic = Dedicação
attribute-consistency = Consistência
attribute-potential = Potencial
