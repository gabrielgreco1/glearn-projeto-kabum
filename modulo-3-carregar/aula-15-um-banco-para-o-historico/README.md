# Carregar · Aula 15 · Um banco para o histórico

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkc-01-um-banco-para-o-historico

O Postgres do projeto sobe no Docker, com o `compose.yaml` na porta 5434, o `banco.py` conecta e o `schema.sql` cria a tabela `precos`, com a chave (dia, id).

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: compose.yaml, .env.example, banco.py, schema.sql, pyproject.toml, uv.lock.

## Como rodar esta pasta

Você precisa do Docker instalado e aberto (no Windows e no Mac, o Docker Desktop).

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
docker compose up -d --wait
uv sync
uv run python rodar.py
```

O `rodar.py` faz a coleta do dia e a etapa Transformar, e cria a pasta `dados/`. Esta aula ainda não carrega nada: o `banco.py` só cria a tabela.

Se o banco não estiver de pé (depois de desligar o computador, por exemplo), suba de novo com `docker compose up -d --wait`. O banco desta pasta usa a porta 5434: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes.

Comandos da aula: `docker compose up -d --wait`, `uv run python banco.py` e `uv run pytest`.
