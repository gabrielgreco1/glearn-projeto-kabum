# Observar · Aula 39 · Incidente: quebrar o Kabum e investigar só com sinais

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/p05-06-incidente-quebrar-o-kabum-e-investigar

Uma de três falhas sorteada (`incidente/provocar.py`), investigada só pelo Grafana; as correções que o incidente mostrou (a parada no log, a senha recusada, o preço em texto rejeitado) e o postmortem sem culpados em `docs/`.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: .gitignore, README.md, banco.py, docs/postmortem-2026-11-16.md, docs/postmortem-modelo.md, incidente/desfazer.py, incidente/provocar.py, observabilidade/logs.py, silver.py, testes/test_logs.py, testes/test_silver.py, testes/test_validar.py, validar.py.

## Como rodar esta pasta

Você precisa do Docker instalado e aberto (no Windows e no Mac, o Docker Desktop).

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu. Depois:

```
docker compose up -d --wait
uv sync
```

Num terminal só dele, deixe o servidor do Prefect ligado: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api` e `uv run prefect gcl create projeto-kabum --limit 1`.

Se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes. No Windows, os comandos são os mesmos no PowerShell.

Comandos da aula: `uv run python incidente/provocar.py`, `uv run python incidente/desfazer.py` e `uv run pytest`.
