# Carregar · Aula 17 · A marca d'água: só os dias novos

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkc-03-a-marca-d-agua-so-os

A tabela `cargas` guarda cada dia carregado e a conta dele. Sem dia pedido, a carga vai só com os dias depois do último carregado, e retoma do dia que caiu.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: carregar.py, schema.sql, testes/test_carregar.py.

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
uv run python rodar.py
```

O `rodar.py` faz a coleta do dia e a etapa Transformar, e cria a pasta `dados/`; a carga é o `carregar.py`. Numa pasta nova, a silver tem um dia só, o de hoje: é esse o dia que o `carregar.py` recebe (por exemplo, `uv run python carregar.py 2026-11-15`).

Se o banco não estiver de pé (depois de desligar o computador, por exemplo), suba de novo com `docker compose up -d --wait`. O banco desta pasta usa a porta 5434: se outra pasta do projeto estiver com o banco ligado, desligue aquela com `docker compose down` antes.

Comandos da aula: `uv run python carregar.py` (duas vezes) e `uv run pytest`.
