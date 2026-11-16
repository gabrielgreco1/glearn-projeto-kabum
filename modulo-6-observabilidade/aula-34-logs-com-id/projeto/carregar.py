"""Carrega o histórico de preços no Postgres, um dia por vez: o dia é apagado no banco e gravado de novo, inteiro,
numa transação própria. Sem dia pedido, vão os dias novos e os que mudaram na silver, pelo hash de cada dia.
Carregar de novo deixa o banco igual."""

import hashlib
import sys
from datetime import date
from pathlib import Path

import polars as pl

from banco import conectar, criar_tabelas
from coletar import registro
from conferir import REGISTRO as CONFERENCIA
from observabilidade import logs
from silver import COLUNAS as COLUNAS_SILVER

SILVER = Path("dados/silver/precos.parquet")
COLUNAS = [*COLUNAS_SILVER, "avisos"]  # as colunas da silver, na ordem da tabela precos
UPSERT_COLETA = """
INSERT INTO coletas (dia, diferentes, declarado, loja, cobertura) VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (dia) DO UPDATE
    SET diferentes = EXCLUDED.diferentes, declarado = EXCLUDED.declarado, loja = EXCLUDED.loja, cobertura = EXCLUDED.cobertura
"""


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


def carregar_dia(conexao, parte, execucao_id):
    """Apaga o dia no banco e grava as linhas dele com COPY, cada uma com o id da execução que a gravou. Devolve quantas
    linhas o DELETE tirou."""
    apagadas = conexao.execute("DELETE FROM precos WHERE dia = %s", [parte["dia"][0]]).rowcount
    with conexao.cursor() as cursor, cursor.copy(f"COPY precos ({', '.join(COLUNAS)}, execucao_id) FROM STDIN") as copia:
        for linha in linhas(parte):
            copia.write_row((*linha, execucao_id))
    return apagadas


def hash_dia(parte):
    """O sha256 do dia inteiro: as linhas em ordem de id, escritas em CSV. Mesmos valores, mesmo hash, em qualquer rodada."""
    return hashlib.sha256(parte.select(COLUNAS).sort("id").write_csv().encode("utf-8")).hexdigest()


def hashes_carregados(conexao):
    """O hash da última carga de cada dia, lido da tabela cargas: {dia: hash}."""
    return dict(conexao.execute("SELECT DISTINCT ON (dia) dia, hash_dia FROM cargas ORDER BY dia, id DESC").fetchall())


def a_carregar(hashes, carregados):
    """Os dias cujo hash na silver é diferente do hash da última carga: os novos, que não têm carga, e os que mudaram."""
    return [dia for dia, valor in sorted(hashes.items()) if carregados.get(dia) != valor]


def ler_conferencia(caminho=CONFERENCIA):
    """As linhas do conferencia.csv que vão para a tabela coletas, com o dia como data."""
    conferencia = pl.read_csv(caminho, try_parse_dates=True)
    return conferencia.select("dia", "diferentes", "declarado", "loja", "cobertura").rows()


def gravar_coletas(conexao):
    """A conferência de cada dia vai para a tabela coletas, com upsert pelo dia. Devolve quantos dias."""
    conferencia = ler_conferencia()
    with conexao.cursor() as cursor:
        cursor.executemany(UPSERT_COLETA, conferencia)
    return len(conferencia)


def conferir(silver, banco):
    """A conta do dia: o banco tem de ter as mesmas linhas e a mesma soma dos preços finais que a silver. Se não
    fecha, para com erro, e o with da conexão desfaz o dia inteiro."""
    if silver != banco:
        raise ValueError(f"o dia não fecha: a silver tem (linhas, soma) = {silver} e o banco tem {banco}")


def main(pedidos=(), execucao_id=None):
    execucao_id = execucao_id or logs.novo_id()  # sem o Prefect, um id novo para esta carga
    tabela = ler_silver()
    hashes = {dia: hash_dia(do_dia(tabela, dia)) for dia in dias_da_silver(tabela)}
    with conectar() as conexao:
        criar_tabelas(conexao)
        coletas = gravar_coletas(conexao)
        carregados = hashes_carregados(conexao)
    registro.info("coletas: %s dias conferidos, do %s", coletas, CONFERENCIA)
    if pedidos:
        fila = sorted(date.fromisoformat(texto) for texto in pedidos)
        registro.info("dias pedidos: %s", ", ".join(map(str, fila)))
    else:
        fila = a_carregar(hashes, carregados)
        novos = [dia for dia in fila if dia not in carregados]
        registro.info("dias na silver: %s; a carregar: %s novos e %s que mudaram", len(hashes), len(novos), len(fila) - len(novos))
    for dia in fila:
        parte = do_dia(tabela, dia)
        silver = (parte.height, int(parte["preco_final"].sum()))
        with conectar() as conexao:  # uma conexão por dia: o with confirma o dia inteiro, ou desfaz o dia inteiro
            apagadas = carregar_dia(conexao, parte, execucao_id)
            banco = conexao.execute("SELECT count(*), sum(preco_final)::bigint FROM precos WHERE dia = %s", [dia]).fetchone()
            conferir(silver, banco)
            conexao.execute("INSERT INTO cargas (dia, apagadas, inseridas, soma_final, hash_dia, execucao_id)"
                            " VALUES (%s, %s, %s, %s, %s, %s)", [dia, apagadas, parte.height, silver[1], hashes[dia], execucao_id])
        registro.info("%s: apaguei %s linhas e gravei %s; conferido: %s linhas e soma %s", dia, apagadas, parte.height, *silver)


if __name__ == "__main__":
    main(sys.argv[1:])
