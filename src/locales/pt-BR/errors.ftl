# SPDX-FileCopyrightText: 2026 Pedrenrique G. Guimarães <admin@esportsmanager.net>
#
# SPDX-License-Identifier: GPL-3.0-or-later

## Erros do Novo Jogo, dos jogos salvos e das consultas.

error-manager-name-empty = Digite o nome do treinador.
error-manager-name-long = O nome do treinador pode ter no máximo { $max } caracteres.
error-save-name-empty = Digite o nome do jogo salvo.
error-save-name-long = O nome do jogo salvo pode ter no máximo { $max } caracteres.
# $field é "manager" ou "save".
error-control-characters = { $field ->
    [manager] O nome do treinador
   *[save] O nome do jogo salvo
} não pode ter caracteres de controle.
error-unknown-team = Não existe o time "{ $team }".
error-unknown-player = Não existe o jogador "{ $player }".
error-no-save-open = Abra ou comece um jogo primeiro.
error-invalid-seed = "{ $seed }" não é uma semente: use um número inteiro.
error-generation = Não foi possível gerar o mundo a partir deste pacote.
error-save-name-taken = Já existe um jogo salvo chamado "{ $name }".
error-save-ambiguous = Vários jogos salvos se chamam "{ $name }"; use o nome do arquivo.
error-save-not-found = Não existe o jogo salvo "{ $file }".
error-save-not-a-save = Este arquivo não é um jogo salvo.
error-save-newer = Este jogo salvo foi criado por uma versão mais nova.
error-save-in-use = Este jogo salvo está aberto em outro lugar.
error-output = Não foi possível escrever a saída: { $detail }
error-entropy = O sistema não forneceu uma semente aleatória: { $detail }
error-storage = Não foi possível ler ou gravar o jogo salvo: { $detail }
