# Orquestrar · Aula 21 · O projeto Kabum no Prefect

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pko-01-o-projeto-kabum-no-prefect

O padrão da PWO, de uma vez: o projeto vira um flow do Prefect, com uma task por etapa, novas tentativas na coleta, o registro no painel, o aviso de falha em avisos.log e o runbook.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: fluxo.py, prefect.toml, runbook.md, coletar.py, .gitignore, pyproject.toml, uv.lock.

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

Comandos da aula: `uv run python fluxo.py` (sem rede, com o banco desligado e normal) e `uv run pytest`.
