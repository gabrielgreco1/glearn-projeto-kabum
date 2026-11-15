# Transformar · Aula 14 · Extrair e transformar num comando só

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-07-extrair-e-transformar-num-comando-so

O `qualidade.py` grava o relatório de cada rodada e decide se publica; o `transformar.py` roda a etapa inteira, e o `rodar.py` faz extrair e transformar com um comando.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: qualidade.py, transformar.py, rodar.py, validar.py, testes/test_qualidade.py, README.md.

## Como rodar esta pasta

```
cd projeto
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu (um e-mail ou o endereço do seu repositório). Depois:

```
uv sync
uv run python rodar.py
```

O `rodar.py` faz a coleta do dia e a etapa Transformar inteira. Com um dia só, o histórico tem um dia: as mudanças de preço aparecem a partir do segundo dia de coleta.

Comandos da aula, nesta ordem: `uv run python rodar.py`, `uv run pytest`.
