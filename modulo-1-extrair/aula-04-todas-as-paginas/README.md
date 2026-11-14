# Aula 4 · Todas as páginas, sem seguir o links.next

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pk-04-todas-as-paginas-sem-seguir-o

O `coletar.py` lê o total de páginas na página 1 e pede as outras com o mesmo tamanho, sem seguir o `links.next`.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: coletar.py, testes/test_coletar.py.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
```

Comandos da aula, nesta ordem: `uv run python coletar.py`, `uv run pytest`. Cada programa lê o que o anterior gravou em `dados/`.
