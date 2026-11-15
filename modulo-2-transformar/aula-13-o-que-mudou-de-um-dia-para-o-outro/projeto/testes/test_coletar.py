"""O endereço de cada página leva sempre o mesmo tamanho."""

from coletar import endereco


def test_endereco_usa_sempre_120_por_pagina():
    assert endereco(1).endswith("?page_number=1&page_size=120")
    assert endereco(4).endswith("?page_number=4&page_size=120")
