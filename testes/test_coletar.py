"""O endereço de cada página leva sempre o mesmo tamanho. E, sem o contato do .env, como nos testes do GitHub,
importar o coletar.py funciona, e o pedido para com a mensagem que diz o que falta."""

import pytest

import coletar
from coletar import endereco


def test_endereco_usa_sempre_120_por_pagina():
    assert endereco(1).endswith("?page_number=1&page_size=120")
    assert endereco(4).endswith("?page_number=4&page_size=120")


def test_sem_contato_o_pedido_para_com_a_mensagem(monkeypatch):
    monkeypatch.delenv("KABUM_USER_AGENT", raising=False)  # tira o contato só durante este teste
    with pytest.raises(SystemExit, match="KABUM_USER_AGENT"):
        coletar.pedir(coletar.endereco(1))
