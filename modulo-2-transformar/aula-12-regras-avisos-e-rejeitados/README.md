# Transformar · Aula 12 · Regras, avisos e rejeitados

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-05-regras-avisos-e-rejeitados

O `validar.py` confere a silver contra oito regras escritas, grava a silver em Parquet e guarda os rejeitados com o motivo.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: validar.py, testes/test_validar.py.

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

O `rodar.py` faz a coleta do dia e cria a pasta `dados/` com o bronze, o `conferencia.csv` e o `precos.csv`. Com um dia só, o histórico tem um dia: as mudanças de preço aparecem a partir do segundo dia de coleta.

Comandos da aula, nesta ordem: `uv run python validar.py`, `uv run pytest`.
