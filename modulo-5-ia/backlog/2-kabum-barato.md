# Kabum: o menor preço de um modelo, num comando

Quem acompanha uma placa quer saber, sem abrir o banco: qual é o anúncio mais barato de hoje de um modelo?

Pronto quando:
- `uv run python barato.py "RTX 5070"` imprime, do último dia da silver (`dados/silver/precos.parquet`), os 3 anúncios mais baratos desse modelo: preço final em reais, título e link.
- Modelo que não existe no dia: uma linha dizendo isso, e o programa sai com código 1.
- Um teste novo em `testes/`, com uma tabela escrita à mão, sem internet e sem banco.
- `uv run pytest` passa.
