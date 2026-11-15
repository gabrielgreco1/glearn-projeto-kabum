"""A silver montada a partir de um precos.csv escrito à mão. Não faz pedido nenhum."""

from datetime import date
from pathlib import Path

import polars as pl

from silver import centavos, classificar, montar, precos, sem_mapa

AMOSTRA = Path(__file__).parent / "amostra_precos.csv"
MAPA = pl.DataFrame({"fabricante": ["PALIT", "Outros"], "marca": ["Palit", None]})


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


def modelos(*titulos):
    tabela = pl.DataFrame({"title": list(titulos), "menu": "Hardware/Placa de vídeo (VGA)/Placa de vídeo Nvidia", "fabricante": "PALIT"})
    return classificar(tabela, MAPA)["modelo"].to_list()


def test_modelo_sai_do_titulo_escrito_de_varios_jeitos():
    # títulos copiados do bronze de 15/11/2026
    assert modelos("Placa De Vídeo MSI Geforce Rtx5060 8gb Gdrr7 Ventus Oc Edition",
                   "Gpu Inno3d Geforce RTX  5090 X3 Oc 32gb 512-bit Gddr7",
                   "Placa de Vídeo Nvidia Gainward RTX 5060TI 8GB GHOST OC GDDR7",
                   "Placa De Video Nvidia Geforce Gt210/1g 1") == ["RTX 5060", "RTX 5090", "RTX 5060 TI", "GT 210"]


def test_sem_familia_conhecida_o_modelo_fica_vazio():
    assert modelos("Placa Mãe B85 LGA  1150 Intel i3 i5 i7 4ª Geração Ddr3 16gb",
                   "Placa De Vídeo Gamer Nvidia Geforce Gtx1660s, Gddr6 6gb") == [None, None]


def test_placa_chip_e_marca():
    silver = montar(AMOSTRA)
    assert silver["e_placa"].to_list() == [True, False, True]
    assert silver["chip"].to_list() == ["Nvidia", None, "Nvidia"]
    assert silver["modelo"].to_list() == ["RTX 5060 TI", None, "RTX 5060 TI"]
    assert silver["marca"].to_list() == ["Palit", None, "Palit"]  # PALIT, como a loja escreve, vira Palit


def test_marcador_da_loja_vira_vazio_e_fabricante_novo_aparece(tmp_path):
    tabela = pl.DataFrame({"title": ["a", "b"], "menu": "x/Acessórios", "fabricante": ["Outros", "Marca Nova"]})
    assert classificar(tabela, MAPA)["marca"].to_list() == [None, None]
    mapa = tmp_path / "fabricantes.csv"
    MAPA.write_csv(mapa)
    precos_csv = tmp_path / "precos.csv"
    tabela.write_csv(precos_csv)
    assert sem_mapa(precos_csv, mapa) == ["Marca Nova"]  # Outros está na tabela, com a marca vazia de propósito
