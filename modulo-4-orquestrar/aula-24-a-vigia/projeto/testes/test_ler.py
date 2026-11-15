"""Testes da leitura de uma página da API. A amostra foi escrita à mão, com a estrutura da resposta real."""

from pathlib import Path

from ler import ler_pagina

AMOSTRA = Path(__file__).parent / "amostra_pagina.json"


def test_um_dicionario_por_produto_com_os_campos_como_vieram():
    produtos = ler_pagina(AMOSTRA.read_bytes())
    assert len(produtos) == 2
    assert produtos[0]["id"] == 111
    assert produtos[0]["price_with_discount"] == 950.0
    assert produtos[0]["fabricante"] == "Fabricante A"


def test_o_preco_da_oferta_vem_do_bloco_offer():
    produtos = ler_pagina(AMOSTRA.read_bytes())
    assert produtos[0]["oferta_price_with_discount"] == 855.0
    assert produtos[0]["oferta_ends_at"] == 1795701540
    assert produtos[1]["oferta_price_with_discount"] is None


def test_produto_sem_fabricante_fica_com_o_campo_vazio():
    produtos = ler_pagina(AMOSTRA.read_bytes())
    assert produtos[1]["fabricante"] is None
    assert produtos[1]["available"] is False


def test_menu_e_vendedor_vem_do_bronze():
    produtos = ler_pagina(AMOSTRA.read_bytes())
    assert produtos[0]["menu"] == "Hardware/Placa de vídeo (VGA)/Placa de vídeo Nvidia"
    assert produtos[0]["is_marketplace"] is False
    assert produtos[0]["vendedor"] is None  # vendido pela própria Kabum: o bloco marketplace vem vazio
    assert produtos[1]["vendedor"] == "Loja inventada"
