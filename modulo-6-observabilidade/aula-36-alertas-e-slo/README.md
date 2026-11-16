# Observar · Aula 36 · Alertas, SLOs e orçamento de erro para dados

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/p05-03-alertas-slos-e-orcamento-de-erro

O combinado do dado fresco (`docs/slo.md`), as regras de alerta do Prometheus, o Alertmanager agrupando e calando o sintoma quando a causa já disparou, o receptor que escreve em `avisos.log` e o painel "Kabum · SLO".

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: alertas/receptor.py, compose.yaml, docs/slo.md, infra/alertmanager.yml, infra/grafana/paineis/kabum-slo.json, infra/prometheus.yml, infra/regras/kabum.yml, infra/testes_alertas.yml, runbook.md.

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

Comandos da aula: `uv run python alertas/receptor.py` (num terminal), `uv run python ensaio/loja.py AAAA-MM-DD --recusar-depois 2` e o teste das regras com o `promtool`.
