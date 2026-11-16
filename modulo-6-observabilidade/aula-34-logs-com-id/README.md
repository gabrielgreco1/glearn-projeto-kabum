# Observar · Aula 34 · Um id que segue a execução: logs estruturados no Kabum

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/p05-01-um-id-que-segue-a-execucao

Todo log do Kabum vira uma linha de JSON com o id da execução (o mesmo do flow run no Prefect), a etapa e a tentativa, sem senha nem e-mail; o mesmo id fica em cada linha que a carga grava no banco.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: .gitignore, carregar.py, coletar.py, conferir.py, fluxo.py, observabilidade/__init__.py, observabilidade/logs.py, rodar.py, runbook.md, schema.sql, testes/test_logs.py.

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

Comandos da aula: `uv run python fluxo.py`, `jq` em `logs/kabum.jsonl` (no PowerShell, `Get-Content … | ConvertFrom-Json`) e `uv run pytest`.
