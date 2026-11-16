# Observar · Aula 38 · Observabilidade de dados: frescor, volume, esquema e linhagem

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/p05-05-observabilidade-de-dados-frescor-volume-esquema

Depois da carga, `medir.py` mede o dia publicado (linhas, vazios por coluna, campos da fonte) e manda junto com as métricas; três alertas de dado e o painel "Kabum · dados"; `linhagem.py` leva de um preço no banco à página da API de onde ele veio.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: ensaio/loja.py, fluxo.py, infra/alertmanager.yml, infra/grafana/paineis/kabum-dados.json, infra/regras/kabum.yml, infra/testes_alertas.yml, linhagem.py, medir.py, observabilidade/dados.py, testes/test_dados.py.

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

Comandos da aula: `uv run python ensaio/loja.py AAAA-MM-DD --sem-fabricante`, `uv run python ensaio/rodada.py` e `uv run python linhagem.py <id>`.
