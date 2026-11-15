# Transformar · Aula 13 · O que mudou de um dia para o outro

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-06-o-que-mudou-de-um-dia

O DuckDB entra no projeto e o `historico.py` monta a camada gold em SQL: as mudanças de preço, os produtos que sumiram e o menor preço de cada modelo por dia.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: historico.py, testes/test_historico.py, pyproject.toml, uv.lock.

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

Comandos da aula, nesta ordem: `uv run python validar.py`, `uv run python historico.py`, `uv run pytest`.
