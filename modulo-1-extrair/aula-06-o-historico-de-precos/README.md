# Aula 6 · O histórico de preços

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pk-06-o-historico-de-precos

O `tabela.py` monta `dados/precos.csv`, uma linha por produto por dia de coleta.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: tabela.py, testes/test_tabela.py.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python coletar.py`, `uv run python tabela.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
