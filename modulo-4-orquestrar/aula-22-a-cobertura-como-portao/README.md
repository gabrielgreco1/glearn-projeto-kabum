# Orquestrar · Aula 22 · A cobertura como portão

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pko-02-a-cobertura-como-portao

Abaixo de 90% de cobertura, nada é publicado: a coleta do dia vai para dados/barrados/, a execução termina em Failed com o motivo no painel, e a rodada seguinte coleta o dia de novo.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: conferir.py, runbook.md, testes/test_conferir.py.

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

Num terminal só dele, deixe o servidor do Prefect ligado: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api`. O painel fica em http://127.0.0.1:4200.

O banco desta pasta usa a porta 5434: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes. No Windows, os comandos são os mesmos no PowerShell.

Comandos da aula: `uv run python fluxo.py` (com uma página repetida de propósito, e de novo) e `uv run pytest`.
