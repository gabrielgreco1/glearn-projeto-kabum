"""Confere a silver contra regras escritas e grava as duas saídas: a silver em Parquet e os rejeitados em CSV.

Uma linha que falha numa regra de erro sai da silver e vai para os rejeitados, com o motivo. Uma linha que falha num
aviso fica na silver, com o nome do aviso na coluna avisos."""

from pathlib import Path

import polars as pl

import silver
from coletar import registro

SILVER = Path("dados/silver/precos.parquet")
REJEITADOS = Path("dados/silver/rejeitados.csv")
MAXIMO = 500_000_00  # R$ 500 mil em centavos; a placa mais cara de 15/11/2026 custava R$ 117.647,06 no cartão

REGRAS = [
    {"id": "id_dia_unico", "tipo": "unicidade", "severidade": "erro", "coluna": "id",
     "descricao": "um produto aparece uma vez por dia",
     "expr": pl.struct("id", "dia").is_first_distinct()},
    {"id": "titulo_obrigatorio", "tipo": "obrigatoriedade", "severidade": "erro", "coluna": "titulo",
     "descricao": "título preenchido",
     "expr": pl.col("titulo").is_not_null()},
    {"id": "preco_faixa", "tipo": "faixa", "severidade": "erro", "coluna": "preco_cartao",
     "descricao": "preço no cartão entre R$ 1 e R$ 500 mil",
     "expr": pl.col("preco_cartao").is_between(100, MAXIMO)},
    {"id": "pix_menor", "tipo": "consistência", "severidade": "erro", "coluna": "preco_pix",
     "descricao": "preço no Pix menor ou igual ao do cartão",
     "expr": pl.col("preco_pix") <= pl.col("preco_cartao")},
    {"id": "desconto_confere", "tipo": "consistência", "severidade": "erro", "coluna": "desconto_pix",
     "descricao": "o desconto do Pix bate com os dois preços",
     "expr": ((pl.col("preco_cartao") - pl.col("preco_pix")) * 100 / pl.col("preco_cartao")).round() == pl.col("desconto_pix")},
    {"id": "oferta_menor", "tipo": "consistência", "severidade": "aviso", "coluna": "preco_oferta",
     "descricao": "a oferta é mais barata que o Pix",
     "expr": pl.col("preco_oferta") < pl.col("preco_pix")},
    {"id": "placa_com_modelo", "tipo": "referência", "severidade": "aviso", "coluna": "titulo",
     "descricao": "toda placa tem um modelo reconhecido no título",
     "expr": ~pl.col("e_placa") | pl.col("modelo").is_not_null()},
    {"id": "preco_mediana", "tipo": "faixa", "severidade": "aviso", "coluna": "preco_final",
     "descricao": "preço final até 3 vezes a mediana do mesmo modelo no mesmo dia",
     "expr": pl.col("modelo").is_null() | (pl.col("preco_final") <= 3 * pl.col("preco_final").median().over("modelo", "dia"))},
]


def aplicar(tabela, regras):
    """Uma coluna booleana por regra: True passou, False falhou. Nulo conta como passou."""
    return tabela.with_columns([r["expr"].fill_null(True).alias(r["id"]) for r in regras])


def separar(tabela, regras=REGRAS):
    """Devolve a silver válida (com a coluna avisos), os rejeitados (uma linha por falha de erro) e as falhas por regra."""
    marcado = aplicar(tabela.with_row_index("linha", offset=1), regras)
    erros = [r["id"] for r in regras if r["severidade"] == "erro"]
    avisos = pl.concat_str([pl.when(~pl.col(r["id"])).then(pl.lit(r["id"])) for r in regras if r["severidade"] == "aviso"],
                           separator=",", ignore_nulls=True)
    validos = marcado.filter(pl.all_horizontal(erros)).with_columns(
        pl.when(avisos != "").then(avisos).alias("avisos")  # sem aviso nenhum, a coluna fica vazia
    ).drop("linha", *[r["id"] for r in regras])
    partes = []
    for r in regras:
        if r["severidade"] != "erro":
            continue
        partes.append(marcado.filter(~pl.col(r["id"])).select(
            "linha", "dia", "id", "titulo",
            pl.lit(r["id"]).alias("regra_id"),
            pl.lit(r["descricao"]).alias("motivo"),
            pl.col(r["coluna"]).cast(pl.String).alias("valor"),
        ))
    rejeitados = pl.concat(partes)
    if marcado.height != validos.height + rejeitados["linha"].n_unique():
        raise RuntimeError("a conta não fechou: lidos != válidos + rejeitados")
    falhas = {r["id"]: marcado.filter(~pl.col(r["id"])).height for r in regras}
    return validos, rejeitados, falhas


def main():
    tabela = silver.montar()
    validos, rejeitados, falhas = separar(tabela)
    SILVER.parent.mkdir(parents=True, exist_ok=True)
    validos.write_parquet(SILVER)
    rejeitados.write_csv(REJEITADOS)
    registro.info("lidos %s = válidos %s + rejeitados %s", tabela.height, validos.height, rejeitados["linha"].n_unique())
    for r in REGRAS:
        registro.info("%-18s %-6s %s falhas", r["id"], r["severidade"], falhas[r["id"]])
    registro.info("gravei %s e %s", SILVER, REJEITADOS)


if __name__ == "__main__":
    main()
