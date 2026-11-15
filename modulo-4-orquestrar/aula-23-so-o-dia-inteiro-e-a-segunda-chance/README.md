# Orquestrar · Aula 23 · Só o dia inteiro, e a segunda chance

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pko-03-so-o-dia-inteiro-e-a

A conferência deixa um selo na pasta do dia, e só um dia com selo entra no histórico. O fluxo.py agendar roda o projeto às 6h e às 18h, no horário de Brasília.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: conferir.py, tabela.py, fluxo.py, runbook.md, testes/test_tabela.py.

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

Comandos da aula: `uv run python fluxo.py` (com Ctrl+C no meio da coleta, e de novo), `uv run python conferir.py 2026-11-14`, `uv run python fluxo.py agendar` e `uv run prefect deployment run projeto-kabum/duas-vezes-por-dia`.
