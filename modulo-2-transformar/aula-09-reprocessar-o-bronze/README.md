# Transformar · Aula 9 · Reprocessar o bronze: os campos que faltavam

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-02-reprocessar-o-bronze-os-campos-que

O `ler.py` passa a ler mais três campos (menu, is_marketplace e vendedor) e o `tabela.py`, rodado de novo, refaz o `precos.csv` de todos os dias a partir do bronze, sem nenhum pedido.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: ler.py, testes/test_ler.py, testes/amostra_pagina.json, testes/amostra_precos.csv, testes/test_perfil.py.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
uv run python rodar.py
```

O `rodar.py` faz a coleta do dia e cria a pasta `dados/` com o bronze, o `conferencia.csv` e o `precos.csv`. Com um dia só, o histórico tem um dia: as mudanças de preço aparecem a partir do segundo dia de coleta.

Comandos da aula, nesta ordem: `uv run python tabela.py`, `uv run python perfil.py`, `uv run pytest`.
