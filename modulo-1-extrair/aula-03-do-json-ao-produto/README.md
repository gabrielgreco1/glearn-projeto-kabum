# Aula 3 · Do JSON ao produto

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pk-03-do-json-ao-produto

O `ler.py` transforma cada produto da página guardada num dicionário, com os campos como vieram, incluindo o preço da oferta.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: ler.py, testes/test_ler.py, testes/amostra_pagina.json, pyproject.toml, uv.lock.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python ler.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
