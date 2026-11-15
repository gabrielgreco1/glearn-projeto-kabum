# Carregar · Aula 18 · Um dia que passou

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkc-04-um-dia-que-passou

Refazer um dia antigo não muda o banco. O hash de cada dia, gravado na tabela `cargas`, acha o dia antigo que a transformação mudou e que a marca d'água deixava passar.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: carregar.py, schema.sql, testes/test_carregar.py.

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

O `rodar.py` faz a coleta do dia e a etapa Transformar, e cria a pasta `dados/`; a carga é o `carregar.py`. Numa pasta nova, a silver tem um dia só, o de hoje: é esse o dia que o `carregar.py` recebe (por exemplo, `uv run python carregar.py 2026-11-15`).

Se o banco não estiver de pé (depois de desligar o computador, por exemplo), suba de novo com `docker compose up -d --wait`. O banco desta pasta usa a porta 5434: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes.

Comandos da aula: `uv run python carregar.py`, `uv run python carregar.py AAAA-MM-DD` e `uv run pytest`.
