"""Os 3 anúncios mais baratos de um modelo no último dia da silver: `uv run python barato.py "RTX 5070"`.
Lê só o parquet da silver: não pede nada à loja nem fala com o banco."""

import re
import sys
from pathlib import Path

import polars as pl

from silver import MODELO

SILVER = Path("dados/silver/precos.parquet")
QUANTOS = 3


def normalizar(texto):
    """O mesmo formato do modelo na silver: 'rtx5070 ti' vira 'RTX 5070 TI'. None quando o texto não tem modelo."""
    achado = re.search(MODELO, texto)
    if achado is None:
        return None
    familia, numero, sufixo = achado.groups()
    return " ".join(parte.upper() for parte in (familia, numero, sufixo) if parte)


def buscar(silver, texto):
    """Os anúncios mais baratos do modelo no último dia da silver, do mais barato para o mais caro. Vazio se não há."""
    modelo = normalizar(texto)
    if modelo is None:
        return silver.clear()
    ultimo = silver["dia"].max()
    return (silver.filter((pl.col("dia") == ultimo) & pl.col("e_placa") & (pl.col("modelo") == modelo))
            .drop_nulls("preco_final")
            .sort("preco_final", "id")
            .head(QUANTOS))


def reais(centavos):
    """213918 vira 'R$ 2.139,18'."""
    return f"R$ {centavos // 100:,}".replace(",", ".") + f",{centavos % 100:02d}"


def principal(argv, caminho=SILVER):
    """Imprime os anúncios e devolve o código de saída: 0 quando achou, 1 quando não há o modelo no dia ou não há silver."""
    if not argv:
        print('Uso: uv run python barato.py "RTX 5070"')
        return 1
    texto = " ".join(argv)
    if not caminho.exists():
        print(f"Não há silver em {caminho}: rode a etapa Transformar antes.")
        return 1
    silver = pl.read_parquet(caminho)
    achados = buscar(silver, texto)
    if achados.is_empty():
        print(f"Não há anúncio de {texto} no último dia da silver ({silver['dia'].max()}).")
        return 1
    print(f"Os {achados.height} anúncios mais baratos de {normalizar(texto)} em {silver['dia'].max()}:")
    for posicao, linha in enumerate(achados.iter_rows(named=True), start=1):
        print(f"{posicao}. {reais(linha['preco_final'])}  {linha['titulo']}")
        print(f"   {linha['link']}")
    return 0


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
