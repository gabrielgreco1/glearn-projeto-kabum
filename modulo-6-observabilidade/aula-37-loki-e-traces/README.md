# Observar · Aula 37 · Logs centralizados no Loki e traces com OpenTelemetry

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/p05-04-logs-centralizados-no-loki-e-traces

O OpenTelemetry Collector lê `logs/kabum.jsonl` e manda ao Loki, e recebe os spans do projeto (os do Prefect, um por task, e os dos pedidos e do banco) e manda ao Tempo; no Grafana, do log ao trace com um clique.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: .gitignore, carregar.py, compose.yaml, fluxo.py, infra/grafana/provisioning/datasources/fontes.yaml, infra/grafana/provisioning/datasources/prometheus.yaml, infra/loki.yaml, infra/otel-collector.yaml, infra/tempo.yaml, logs/.gitkeep, observabilidade/logs.py, observabilidade/metricas.py, observabilidade/traces.py, pyproject.toml, runbook.md, testes/test_metricas.py, uv.lock.

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

Comandos da aula: `docker compose up -d --wait`, `uv run python ensaio/rodada.py` e, no Grafana, Explore com Loki e Tempo.
