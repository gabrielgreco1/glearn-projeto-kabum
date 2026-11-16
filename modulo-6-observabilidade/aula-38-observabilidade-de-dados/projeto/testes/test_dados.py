"""A impressão digital do esquema: a ordem dos campos não muda o número; um campo a mais muda."""

from observabilidade.dados import impressao


def test_mesma_lista_em_outra_ordem_da_o_mesmo_numero():
    assert impressao(["price", "title", "id"]) == impressao(["id", "price", "title"])


def test_um_campo_a_mais_muda_o_numero():
    assert impressao(["id", "price", "title"]) != impressao(["id", "price", "title", "selo_black"])


def test_o_numero_cabe_em_oito_digitos_hexadecimais():
    assert 0 <= impressao(["id"]) < 16**8
