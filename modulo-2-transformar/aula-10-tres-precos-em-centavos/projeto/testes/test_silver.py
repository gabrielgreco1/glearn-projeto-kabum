"""A silver montada a partir de um precos.csv escrito à mão. Não faz pedido nenhum."""

from datetime import date
from pathlib import Path

import polars as pl

from silver import centavos, montar, precos

AMOSTRA = Path(__file__).parent / "amostra_precos.csv"


def test_centavos_arredonda_antes_de_virar_inteiro():
    tabela = pl.DataFrame({"price": [2139.18, 4444.43, 19.9]})
    assert tabela.select(centavos("price"))["price"].to_list() == [213918, 444443, 1990]


def test_oferta_que_vale_no_dia_vira_o_preco_final():
    silver = montar(AMOSTRA)
    primeira = silver.drop("oferta_termina").row(0, named=True)
    assert primeira["dia"] == date(2026, 11, 14)
    assert primeira["em_oferta"] is True
    assert primeira["preco_final"] == 85500  # o preço da oferta, no Pix


def test_fim_da_oferta_no_horario_de_brasilia():
    silver = montar(AMOSTRA)
    texto = silver.select(pl.col("oferta_termina").dt.strftime("%d/%m/%Y %H:%M %z"))["oferta_termina"].to_list()
    assert texto == ["26/11/2026 10:59 -0300", None, None]  # 1795701540 segundos: 13h59 em UTC


def test_sem_oferta_o_preco_final_e_o_pix():
    silver = montar(AMOSTRA)
    assert silver["em_oferta"].to_list() == [True, False, False]
    assert silver["preco_final"].to_list() == [85500, 50000, 90000]


def test_oferta_vencida_nao_conta():
    tabela = pl.read_csv(AMOSTRA).with_columns(pl.lit("2026-11-27").alias("dia"))  # um dia depois do fim da oferta
    assert precos(tabela)["em_oferta"].to_list() == [False, False, False]
