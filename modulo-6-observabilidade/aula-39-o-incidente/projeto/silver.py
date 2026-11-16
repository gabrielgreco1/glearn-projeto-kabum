"""Monta a silver do histórico a partir do precos.csv: tipos certos, preços em centavos, o preço que vale em cada dia
e, para cada produto, se é placa, o chip, o modelo e a marca."""

import polars as pl

from coletar import registro

FUSO = "America/Sao_Paulo"  # a API manda o fim da oferta em segundos desde 1970, em UTC; a loja fala no horário de Brasília
NOMES = {"title": "titulo", "discount_percentage": "desconto_pix", "stock": "estoque", "product_link": "link"}
COLUNAS = ["dia", "id", "titulo", "e_placa", "chip", "modelo", "marca", "fabricante", "preco_cartao", "preco_pix",
           "desconto_pix", "preco_oferta", "oferta_termina", "em_oferta", "preco_final", "estoque", "is_marketplace",
           "vendedor", "link"]
MAPA = "fabricantes.csv"  # de fabricante, como a loja escreve, para marca; vazio quando a loja não diz quem fez
MODELO = r"(?i)\b(RTX|GTX|GT|RX)\s*(\d{3,4})\s*(Ti|XT|Super|GRE)?\b"  # RTX 5060 Ti, Rtx5060, RX 580, GT 730, RTX  5090


def centavos(coluna):
    """R$ 2139.18 vira 213918. O round vem antes do cast: no float, 2139.18 * 100 dá 213917.99999999997.
    Um preço que não é número (a API mandando "R$ 1.299,90") vira vazio, e a regra preco_obrigatorio o rejeita."""
    return (pl.col(coluna).cast(pl.Float64, strict=False) * 100).round().cast(pl.Int64)


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


def classificar(tabela, mapa):
    """Placa ou acessório e o chip, pelo menu da loja; o modelo, pelo título; a marca, pela tabela de fabricantes."""
    familia = pl.col("title").str.extract(MODELO, 1)
    modelo = pl.concat_str(familia.str.to_uppercase(), pl.col("title").str.extract(MODELO, 2),
                           pl.col("title").str.extract(MODELO, 3).str.to_uppercase(), separator=" ", ignore_nulls=True)
    return tabela.join(mapa.select("fabricante", "marca"), on="fabricante", how="left").with_columns(
        (~pl.col("menu").str.ends_with("/Acessórios")).alias("e_placa"),
        pl.col("menu").str.extract(r"/Placa de vídeo (Nvidia|AMD|Intel)$", 1).alias("chip"),
        pl.when(familia.is_not_null()).then(modelo).alias("modelo"),
    )


def montar(caminho="dados/precos.csv", mapa=MAPA):
    """Lê o precos.csv e devolve a silver, com nomes em português, só as colunas que servem e em ordem de dia e id."""
    tabela = classificar(precos(pl.read_csv(caminho)), pl.read_csv(mapa))
    return tabela.rename(NOMES).select(COLUNAS).sort("dia", "id")


def sem_mapa(caminho="dados/precos.csv", mapa=MAPA):
    """Os fabricantes que aparecem no precos.csv e ainda não estão na tabela: cada um precisa de uma linha nova."""
    conhecidos = pl.read_csv(mapa)["fabricante"]
    fabricantes = pl.read_csv(caminho)["fabricante"].drop_nulls().unique()
    return sorted(fabricantes.filter(~fabricantes.is_in(conhecidos.to_list())).to_list())


def main():
    silver = montar()
    registro.info("silver: %s linhas e %s colunas", silver.height, silver.width)
    placas = silver.filter(pl.col("e_placa"))
    registro.info("placas: %s linhas; acessórios: %s", placas.height, silver.height - placas.height)
    chips = placas.group_by("chip").len().sort("len", "chip", descending=[True, False], nulls_last=True)
    registro.info("chip das placas: %s", ", ".join(f"{chip or 'sem chip'} {n}" for chip, n in chips.iter_rows()))
    registro.info("placas com modelo: %s; sem modelo: %s; modelos diferentes: %s", placas["modelo"].count(),
                  placas["modelo"].null_count(), placas["modelo"].drop_nulls().n_unique())
    registro.info("linhas sem marca: %s; marcas diferentes: %s", silver["marca"].null_count(), silver["marca"].drop_nulls().n_unique())
    novos = sem_mapa()
    if novos:
        registro.warning("fabricantes fora do %s: %s. Acrescente uma linha para cada um.", MAPA, ", ".join(novos))


if __name__ == "__main__":
    main()
