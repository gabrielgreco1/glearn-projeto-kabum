# Orquestrar · Aula 24 · A vigia: o que o portão deixa passar

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pko-04-a-vigia-o-que-o-portao

Depois da carga, o vigiar.py lê o banco e avisa a cobertura perto do mínimo, os produtos que somem em massa e os dias que faltam, sem parar o projeto.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: vigiar.py, fluxo.py, runbook.md, testes/test_vigiar.py.

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

Comandos da aula: `uv run python vigiar.py`, `uv run python fluxo.py` e `uv run pytest`.
