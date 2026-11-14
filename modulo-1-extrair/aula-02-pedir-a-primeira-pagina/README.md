# Aula 2 · O pedido da página, em Python

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pk-02-o-pedido-da-pagina-em-python

O `coletar.py` pede a página 1 da API com 120 produtos, guarda a resposta como veio em `dados/bronze/<dia>/` e, na segunda rodada do mesmo dia, não pede de novo.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: coletar.py, pyproject.toml, uv.lock, .python-version, .env.example, .gitignore.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python coletar.py`, `uv run python coletar.py`. Cada programa lê o que o anterior gravou em `dados/`.
