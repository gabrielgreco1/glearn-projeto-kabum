# Observar · Aula 35 · Métricas do pipeline: RED, USE e o primeiro painel no Grafana

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/p05-02-metricas-do-pipeline-red-use-e

Cada execução manda ao Pushgateway quantos pedidos fez, com que status e em quanto tempo; o Prometheus guarda a série e o Grafana mostra o painel "Kabum · saúde". A loja de ensaio (`ensaio/`) deixa rodar o projeto quantas vezes quiser sem pedir nada à Kabum.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: carregar.py, coletar.py, compose.yaml, conferir.py, ensaio/loja.py, ensaio/rodada.py, fluxo.py, infra/grafana/paineis/kabum-saude.json, infra/grafana/provisioning/dashboards/paineis.yaml, infra/grafana/provisioning/datasources/prometheus.yaml, infra/prometheus.yml, observabilidade/metricas.py, pyproject.toml, runbook.md, testes/test_metricas.py, uv.lock.

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

Comandos da aula: `docker compose up -d --wait`, `uv run python ensaio/loja.py AAAA-MM-DD` (num terminal) e `uv run python ensaio/rodada.py`.
