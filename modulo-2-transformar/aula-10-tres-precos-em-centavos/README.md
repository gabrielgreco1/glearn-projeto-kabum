# Transformar · Aula 10 · Três preços, em centavos

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-03-tres-precos-em-centavos

O `silver.py` lê o `precos.csv` e guarda os preços em centavos, o fim da oferta no horário de Brasília e o preço final de cada dia.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: silver.py, testes/test_silver.py.

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

Comandos da aula, nesta ordem: `uv run python silver.py`, `uv run pytest`.
