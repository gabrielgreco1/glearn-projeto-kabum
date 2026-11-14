# Aula 5 · Conferir a coleta: o que faltou

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pk-05-conferir-a-coleta-o-que-faltou

O `conferir.py` mede a cobertura contra o total da API, olha o total da página da loja, lista os repetidos e anota cada conferência em `dados/conferencia.csv`.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: conferir.py, testes/test_conferir.py, testes/amostra_loja.html.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python coletar.py`, `uv run python conferir.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
