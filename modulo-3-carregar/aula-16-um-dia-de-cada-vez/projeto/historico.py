"""Monta a camada gold a partir da silver, em SQL: o que mudou de preço, o que sumiu de um dia para o outro e o
menor preço de cada modelo em cada dia. Os preços continuam em centavos."""

from pathlib import Path

import duckdb

from coletar import registro

SILVER = "dados/silver/precos.parquet"
GOLD = Path("dados/gold")

MUDANCAS = f"""
WITH serie AS (
    SELECT dia, id, titulo, preco_final, em_oferta,
           lag(dia) OVER (PARTITION BY id ORDER BY dia) AS dia_anterior,
           lag(preco_final) OVER (PARTITION BY id ORDER BY dia) AS preco_anterior,
           lag(em_oferta) OVER (PARTITION BY id ORDER BY dia) AS oferta_anterior
    FROM '{SILVER}'
)
SELECT dia, id, titulo, dia_anterior, preco_anterior, preco_final,
       preco_final - preco_anterior AS variacao,
       round(100 * (preco_final - preco_anterior) / preco_anterior, 1) AS variacao_pct,
       oferta_anterior, em_oferta
FROM serie
WHERE preco_final <> preco_anterior OR em_oferta <> oferta_anterior
ORDER BY dia, variacao_pct
"""

SUMIRAM = f"""
WITH dias AS (
    SELECT dia, lag(dia) OVER (ORDER BY dia) AS anterior
    FROM (SELECT DISTINCT dia FROM '{SILVER}')
)
SELECT d.dia, ontem.id, ontem.titulo, ontem.preco_final AS ultimo_preco, c.cobertura
FROM dias d
JOIN '{SILVER}' ontem ON ontem.dia = d.anterior
LEFT JOIN '{SILVER}' hoje ON hoje.dia = d.dia AND hoje.id = ontem.id
LEFT JOIN read_csv('dados/conferencia.csv') c ON c.dia = d.dia
WHERE hoje.id IS NULL
ORDER BY d.dia, ontem.id
"""

MODELOS = f"""
SELECT dia, modelo, count(*) AS anuncios, min(preco_final) AS menor_preco,
       median(preco_final) AS mediana, arg_min(id, preco_final) AS id_mais_barato
FROM '{SILVER}'
WHERE e_placa AND modelo IS NOT NULL
GROUP BY dia, modelo
ORDER BY modelo, dia
"""


def gravar(consulta, nome):
    """Roda a consulta, grava o resultado em dados/gold/<nome>.parquet e devolve quantas linhas saíram."""
    destino = GOLD / f"{nome}.parquet"
    duckdb.sql(consulta).write_parquet(str(destino))
    return duckdb.sql(f"SELECT count(*) FROM '{destino}'").fetchall()[0][0]


def main():
    GOLD.mkdir(parents=True, exist_ok=True)
    linhas = {nome: gravar(consulta, nome) for nome, consulta in [("mudancas", MUDANCAS), ("sumiram", SUMIRAM), ("modelos", MODELOS)]}
    duckdb.sql("SELECT dia, id, preco_anterior / 100 AS antes, preco_final / 100 AS depois, variacao_pct "
               "FROM 'dados/gold/mudancas.parquet'").show()
    duckdb.sql("SELECT dia, id, ultimo_preco / 100 AS ultimo_preco, cobertura FROM 'dados/gold/sumiram.parquet'").show()
    registro.info("gold: %s mudanças, %s sumiços e %s linhas na tabela dos modelos, em %s",
                  linhas["mudancas"], linhas["sumiram"], linhas["modelos"], GOLD)


if __name__ == "__main__":
    main()
