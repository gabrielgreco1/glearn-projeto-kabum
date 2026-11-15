# Transformar · Aula 11 · O que é placa, quem fez e qual modelo

Aula na plataforma: https://learn.gabrielgreco.com/learn/trilha/pkt-04-o-que-e-placa-quem-fez

O `silver.py` separa placa de acessório pelo menu da loja, tira o modelo do título com uma expressão regular e troca o fabricante pela marca com a tabela `fabricantes.csv`.

A pasta `projeto/` mostra como a sua pasta `projeto-kabum/` deve estar no fim desta aula. Arquivos novos ou alterados nesta aula: silver.py, fabricantes.csv, testes/test_silver.py, testes/amostra_precos.csv.

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
