"""Monta a silver do histórico a partir do precos.csv: tipos certos, preços em centavos e o preço que vale em cada dia."""

import polars as pl

from coletar import registro

FUSO = "America/Sao_Paulo"  # a API manda o fim da oferta em segundos desde 1970, em UTC; a loja fala no horário de Brasília
NOMES = {"title": "titulo", "discount_percentage": "desconto_pix", "stock": "estoque", "product_link": "link"}
COLUNAS = ["dia", "id", "titulo", "preco_cartao", "preco_pix", "desconto_pix", "preco_oferta", "oferta_termina",
           "em_oferta", "preco_final", "estoque", "fabricante", "menu", "is_marketplace", "vendedor", "link"]


def centavos(coluna):
    """R$ 2139.18 vira 213918. O round vem antes do cast: no float, 2139.18 * 100 dá 213917.99999999997."""
    return (pl.col(coluna) * 100).round().cast(pl.Int64)


def precos(tabela):
    """Os três preços em centavos, o fim da oferta no fuso de São Paulo e o preço final de cada dia."""
    tabela = tabela.with_columns(
        pl.col("dia").str.to_date(),
        centavos("price").alias("preco_cartao"),
        centavos("price_with_discount").alias("preco_pix"),
        centavos("oferta_price_with_discount").alias("preco_oferta"),
        pl.from_epoch("oferta_ends_at", time_unit="s").dt.replace_time_zone("UTC").dt.convert_time_zone(FUSO).alias("oferta_termina"),
    )
    em_oferta = pl.col("preco_oferta").is_not_null() & (pl.col("oferta_termina").dt.date() >= pl.col("dia"))
    return tabela.with_columns(
        em_oferta.alias("em_oferta"),
        pl.when(em_oferta).then(pl.col("preco_oferta")).otherwise(pl.col("preco_pix")).alias("preco_final"),
    )


def montar(caminho="dados/precos.csv"):
    """Lê o precos.csv e devolve a silver, com nomes em português e só as colunas que servem."""
    return precos(pl.read_csv(caminho)).rename(NOMES).select(COLUNAS)


def main():
    silver = montar()
    registro.info("silver: %s linhas e %s colunas", silver.height, silver.width)
    oferta = silver.filter(pl.col("em_oferta"))
    registro.info("em oferta: %s linhas; nelas, o preço final é o da oferta", oferta.height)
    fins = sorted(oferta["oferta_termina"].unique().dt.strftime("%d/%m %H:%M").to_list())
    registro.info("as ofertas terminam em: %s (horário de Brasília)", ", ".join(fins))
    menor = silver.filter(pl.col("preco_final") < pl.col("preco_pix")).height
    registro.info("preço final abaixo do Pix: %s linhas; igual ao Pix: %s", menor, silver.height - menor)


if __name__ == "__main__":
    main()
