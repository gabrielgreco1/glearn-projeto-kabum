"""Depois da carga: mede o dia que acabou de ser publicado e põe as medidas nas métricas da execução. As checagens
da transformação param a rodada quando algo passa do limite; estas medidas não param nada, deixam o histórico para o
Prometheus comparar com a semana passada."""

import json
from pathlib import Path

import polars as pl

from carregar import SILVER
from coletar import registro
from observabilidade import dados

VIGIADAS = ["preco_oferta", "fabricante", "chip", "modelo", "estoque"]  # colunas que podem vir vazias, e quanto importa


def campos_da_fonte(pasta):
    """Todos os nomes de campo que a API mandou nos produtos do dia, somando as páginas."""
    campos = set()
    for arquivo in sorted(Path(pasta).glob("pagina-*.json")):
        for item in json.loads(arquivo.read_text(encoding="utf-8"))["data"]:
            campos |= set(item["attributes"])
    return campos


def medir(pasta):
    silver = pl.read_parquet(SILVER)
    dia = silver["dia"].max()
    do_dia = silver.filter(pl.col("dia") == dia)
    fracoes = {coluna: do_dia[coluna].null_count() / do_dia.height for coluna in VIGIADAS}
    campos = campos_da_fonte(pasta)
    dados.volume("precos", do_dia.height)
    dados.nulos("precos", fracoes)
    dados.esquema("api", campos)
    dados.dia_mais_novo("precos", dia)
    registro.info("medidas de %s: %s linhas, %s campos na fonte, vazios: %s", dia, do_dia.height, len(campos),
                  ", ".join(f"{coluna} {fracao:.1%}" for coluna, fracao in fracoes.items()))
