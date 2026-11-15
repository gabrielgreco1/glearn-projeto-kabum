"""Carrega o histórico de preços no Postgres, um dia por vez: o dia é apagado no banco e gravado de novo, inteiro,
numa transação própria. Sem dia pedido, vão só os dias depois da marca d'água. Carregar de novo deixa o banco igual."""

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


def marca_dagua(conexao):
    """O dia mais novo que já foi carregado, lido da tabela cargas. None quando o banco ainda não recebeu nenhum dia."""
    return conexao.execute("SELECT max(dia) FROM cargas").fetchone()[0]


def depois_da_marca(dias, marca):
    """Os dias que vêm depois da marca. Sem marca, todos."""
    return [dia for dia in dias if marca is None or dia > marca]


def conferir(silver, banco):
    """A conta do dia: o banco tem de ter as mesmas linhas e a mesma soma dos preços finais que a silver. Se não
    fecha, para com erro, e o with da conexão desfaz o dia inteiro."""
    if silver != banco:
        raise ValueError(f"o dia não fecha: a silver tem (linhas, soma) = {silver} e o banco tem {banco}")


def main(pedidos=()):
    tabela = ler_silver()
    with conectar() as conexao:
        criar_tabelas(conexao)
        marca = marca_dagua(conexao)
    if pedidos:
        fila = sorted(date.fromisoformat(texto) for texto in pedidos)
        registro.info("dias pedidos: %s", ", ".join(map(str, fila)))
    else:
        fila = depois_da_marca(dias_da_silver(tabela), marca)
        registro.info("marca d'água: %s; dias a carregar: %s", marca, ", ".join(map(str, fila)) or "nenhum")
    for dia in fila:
        parte = do_dia(tabela, dia)
        silver = (parte.height, int(parte["preco_final"].sum()))
        with conectar() as conexao:  # uma conexão por dia: o with confirma o dia inteiro, ou desfaz o dia inteiro
            apagadas = carregar_dia(conexao, parte)
            banco = conexao.execute("SELECT count(*), sum(preco_final)::bigint FROM precos WHERE dia = %s", [dia]).fetchone()
            conferir(silver, banco)
            conexao.execute("INSERT INTO cargas (dia, apagadas, inseridas, soma_final) VALUES (%s, %s, %s, %s)",
                            [dia, apagadas, parte.height, silver[1]])
        registro.info("%s: apaguei %s linhas e gravei %s; conferido: %s linhas e soma %s", dia, apagadas, parte.height, *silver)


if __name__ == "__main__":
    main(sys.argv[1:])
