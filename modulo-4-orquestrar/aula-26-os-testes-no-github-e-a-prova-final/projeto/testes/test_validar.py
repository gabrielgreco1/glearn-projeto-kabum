"""As regras da silver, cada uma quebrada de propósito numa cópia da amostra. Não faz pedido nenhum."""

from pathlib import Path

import polars as pl

from silver import montar
from validar import REGRAS, separar

AMOSTRA = Path(__file__).parent / "amostra_precos.csv"


def test_a_amostra_passa_em_todas_as_regras_de_erro():
    validos, rejeitados, falhas = separar(montar(AMOSTRA))
    assert validos.height == 3
    assert rejeitados.height == 0
    assert all(falhas[r["id"]] == 0 for r in REGRAS if r["severidade"] == "erro")


def test_pix_acima_do_cartao_vai_para_os_rejeitados_com_o_motivo():
    tabela = montar(AMOSTRA).with_columns(pl.when(pl.col("id") == 222).then(60000).otherwise(pl.col("preco_pix")).alias("preco_pix"))
    validos, rejeitados, falhas = separar(tabela)
    assert validos["id"].to_list() == [111, 111]
    assert rejeitados["regra_id"].to_list() == ["pix_menor", "desconto_confere"]  # uma linha, duas regras quebradas
    assert rejeitados["valor"].to_list() == ["60000", "0"]
    assert falhas["pix_menor"] == 1


def test_o_mesmo_produto_duas_vezes_no_dia_entra_uma_vez():
    tabela = montar(AMOSTRA)
    validos, rejeitados, _ = separar(pl.concat([tabela, tabela.head(1)]))
    assert validos.height == 3
    assert rejeitados["regra_id"].to_list() == ["id_dia_unico"]


def test_aviso_fica_na_silver_com_o_nome_da_regra():
    tabela = montar(AMOSTRA).with_columns(pl.lit(None, dtype=pl.String).alias("modelo"))  # nenhuma placa com modelo
    validos, rejeitados, falhas = separar(tabela)
    assert rejeitados.height == 0
    assert validos["avisos"].to_list() == ["placa_com_modelo", None, "placa_com_modelo"]  # o suporte não é placa
    assert falhas["placa_com_modelo"] == 2
