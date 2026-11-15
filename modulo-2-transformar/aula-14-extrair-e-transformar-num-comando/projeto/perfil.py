"""Mede o precos.csv antes de qualquer limpeza: o tamanho, os tipos, os vazios e as colunas que nunca mudam. Não altera nada."""

import polars as pl

from coletar import registro


def medir(caminho):
    """Lê o CSV e devolve as medidas num dicionário."""
    tabela = pl.read_csv(caminho)
    vazios = tabela.null_count().to_dicts()[0]  # uma linha só, com a contagem de cada coluna
    diferentes = tabela.select(pl.all().n_unique()).to_dicts()[0]
    return {
        "linhas": tabela.height,
        "colunas": tabela.width,
        "dias": sorted(tabela["dia"].unique().to_list()),
        "produtos": tabela["id"].n_unique(),
        "tipos": {coluna: str(tipo) for coluna, tipo in tabela.schema.items()},
        "vazios": {coluna: n for coluna, n in vazios.items() if n > 0},
        "um_valor_so": [coluna for coluna, n in diferentes.items() if n == 1],
        "menor_preco": tabela["price_with_discount"].min(),
        "maior_preco": tabela["price_with_discount"].max(),
    }


def main():
    medidas = medir("dados/precos.csv")
    registro.info("%s linhas e %s colunas, de %s dia(s): %s", medidas["linhas"], medidas["colunas"], len(medidas["dias"]), ", ".join(medidas["dias"]))
    registro.info("%s produtos diferentes", medidas["produtos"])
    registro.info("vazios: %s", medidas["vazios"] or "nenhum")
    registro.info("colunas com um valor só: %s", ", ".join(medidas["um_valor_so"]) or "nenhuma")
    registro.info("price_with_discount vai de %s a %s", medidas["menor_preco"], medidas["maior_preco"])


if __name__ == "__main__":
    main()
