"""Carrega o histórico de preços no Postgres, um dia por vez: o dia é apagado no banco e gravado de novo, inteiro,
numa transação própria. Carregar o mesmo dia duas vezes deixa o banco igual."""

import sys
from datetime import date
from pathlib import Path

import polars as pl

from banco import conectar, criar_tabelas
from coletar import registro
from silver import COLUNAS as COLUNAS_SILVER

SILVER = Path("dados/silver/precos.parquet")
COLUNAS = [*COLUNAS_SILVER, "avisos"]  # as colunas da silver, na ordem da tabela precos


def ler_silver():
    """A silver validada, com todos os dias guardados."""
    return pl.read_parquet(SILVER)


def linhas(tabela):
    """Cada linha vira uma tupla, na ordem das colunas. O vazio do Polars chega como None, que o Postgres grava como NULL."""
    return tabela.select(COLUNAS).rows()


def dias_da_silver(tabela):
    """Os dias que a silver tem, do mais antigo ao mais novo."""
    return tabela["dia"].unique().sort().to_list()


def do_dia(tabela, dia):
    """As linhas da silver de um dia. Para com uma mensagem se a silver não tem esse dia."""
    parte = tabela.filter(pl.col("dia") == dia)
    if parte.is_empty():
        raise SystemExit(f"A silver não tem o dia {dia}. Os dias que ela tem: {', '.join(map(str, dias_da_silver(tabela)))}")
    return parte


def carregar_dia(conexao, parte):
    """Apaga o dia no banco e grava as linhas dele com COPY. Devolve quantas linhas o DELETE tirou."""
    apagadas = conexao.execute("DELETE FROM precos WHERE dia = %s", [parte["dia"][0]]).rowcount
    with conexao.cursor() as cursor, cursor.copy(f"COPY precos ({', '.join(COLUNAS)}) FROM STDIN") as copia:
        for linha in linhas(parte):
            copia.write_row(linha)
    return apagadas


def main(pedidos=()):
    tabela = ler_silver()
    if not pedidos:
        raise SystemExit("Diga o dia: uv run python carregar.py 2026-11-14")
    with conectar() as conexao:
        criar_tabelas(conexao)
    for dia in sorted(date.fromisoformat(texto) for texto in pedidos):
        parte = do_dia(tabela, dia)
        with conectar() as conexao:  # uma conexão por dia: o with confirma o dia inteiro, ou desfaz o dia inteiro
            apagadas = carregar_dia(conexao, parte)
        registro.info("%s: apaguei %s linhas e gravei %s", dia, apagadas, parte.height)


if __name__ == "__main__":
    main(sys.argv[1:])
