# Orquestrar · Aula 25 · Uma execução por vez

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pko-05-uma-execucao-por-vez

Um limite de concorrência do Prefect, projeto-kabum, deixa uma execução por vez: a segunda espera a primeira terminar e não pede nada de novo à loja.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: fluxo.py, runbook.md.

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
```

Num terminal só dele, deixe o servidor do Prefect ligado: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`. A partir desta aula, também uma vez: `uv run prefect gcl create projeto-kabum --limit 1`. O painel fica em http://127.0.0.1:4200.

O banco desta pasta usa a porta 5434: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes. No Windows, os comandos são os mesmos no PowerShell.

Comandos da aula: `uv run prefect gcl create projeto-kabum --limit 1`, duas vezes `uv run python fluxo.py` ao mesmo tempo, em dois terminais, e `uv run pytest`.
