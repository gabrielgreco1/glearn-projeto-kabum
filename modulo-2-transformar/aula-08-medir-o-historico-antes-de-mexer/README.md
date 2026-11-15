# Transformar · Aula 8 · Medir o histórico antes de mexer

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-01-medir-o-historico-antes-de-mexer

O Polars entra no projeto e o `perfil.py` mede o `precos.csv`: tamanho, tipos, vazios e as colunas que nunca mudam.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: perfil.py, testes/test_perfil.py, testes/amostra_precos.csv, pyproject.toml, uv.lock.

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

Comandos da aula, nesta ordem: `uv run python perfil.py`, `uv run pytest`.
