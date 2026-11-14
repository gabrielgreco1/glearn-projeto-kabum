# Aula 7 · Fechar o projeto: uma rodada, um comando

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pk-07-fechar-o-projeto-uma-rodada-um

O `rodar.py` faz a rodada do dia com um comando. O README diz como rodar, as regras e o que o projeto não faz.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: rodar.py, README.md.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python rodar.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
