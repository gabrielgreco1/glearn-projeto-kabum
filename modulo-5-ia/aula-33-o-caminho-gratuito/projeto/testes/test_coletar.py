"""O endereço de cada página leva sempre o mesmo tamanho. E, sem o contato do .env, como nos testes do GitHub,
importar o coletar.py funciona, e o pedido para com a mensagem que diz o que falta."""

import json

import httpx
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


def _fingir_loja(monkeypatch, paginas_por_categoria):
    """Troca o pedido à loja por respostas escritas à mão: sem internet e sem pausa. Devolve a lista de caminhos pedidos."""
    pedidos = []

    def pedir_falso(caminho):
        pedidos.append(caminho)
        total = next(n for trecho, n in paginas_por_categoria.items() if trecho in caminho)
        return json.dumps({"meta": {"total_pages_count": total}, "data": []}).encode()

    monkeypatch.setattr(coletar, "pedir", pedir_falso)
    return pedidos


NOVEMBRO = {"placa-de-video-vga": 5, "ssd-2-5": 9, "memoria-ram": 12, "processadores": 6}  # 32 páginas, como em 15/11/2026


def test_coleta_as_quatro_categorias_cada_uma_na_sua_pasta(tmp_path, monkeypatch):
    pedidos = _fingir_loja(monkeypatch, NOVEMBRO)
    assert coletar.coletar(tmp_path) == 32
    assert len(pedidos) == 32
    assert len(list(tmp_path.glob("pagina-*.json"))) == 5  # as placas ficam na raiz da pasta do dia
    assert len(list((tmp_path / "ssd").glob("pagina-*.json"))) == 9
    assert len(list((tmp_path / "memoria").glob("pagina-*.json"))) == 12
    assert len(list((tmp_path / "processador").glob("pagina-*.json"))) == 6


def test_os_caminhos_pedidos_sao_os_da_issue_e_sem_sort(tmp_path, monkeypatch):
    pedidos = _fingir_loja(monkeypatch, NOVEMBRO)
    coletar.coletar(tmp_path)
    for categoria in ("hardware/placa-de-video-vga", "hardware/ssd-2-5", "hardware/memoria-ram", "hardware/processadores"):
        assert any(f"/products-by-category/{categoria}?page_number=1&page_size=120" in p for p in pedidos)
    assert not any("sort" in p for p in pedidos)
    assert all(p.endswith("&page_size=120") for p in pedidos)


def test_o_teto_vale_para_a_soma_e_para_antes_das_outras_paginas(tmp_path, monkeypatch):
    pedidos = _fingir_loja(monkeypatch, dict(NOVEMBRO, **{"memoria-ram": 22}))  # 5 + 9 + 22 + 6 = 42, acima de 40
    with pytest.raises(SystemExit, match="teto de 40"):
        coletar.coletar(tmp_path)
    assert len(pedidos) == 4  # só a página 1 de cada categoria
    assert not list(tmp_path.glob("pagina-002.json"))


def test_no_teto_exato_a_coleta_segue(tmp_path, monkeypatch):
    pedidos = _fingir_loja(monkeypatch, dict(NOVEMBRO, **{"memoria-ram": 20}))  # 5 + 9 + 20 + 6 = 40
    assert coletar.coletar(tmp_path) == 40
    assert len(pedidos) == 40


def test_o_teto_e_de_40_paginas():
    assert coletar.LIMITE_PAGINAS == 40


def test_rodar_de_novo_no_mesmo_dia_nao_pede_nada(tmp_path, monkeypatch):
    pedidos = _fingir_loja(monkeypatch, NOVEMBRO)
    coletar.coletar(tmp_path)
    pedidos.clear()
    coletar.coletar(tmp_path)
    assert pedidos == []


def test_cada_pedido_e_seguido_da_pausa(monkeypatch):
    esperas = []
    monkeypatch.setenv("KABUM_USER_AGENT", "teste")
    resposta = httpx.Response(200, headers={"content-type": "application/json"}, content=b"{}")
    monkeypatch.setattr(coletar.httpx, "get", lambda *args, **kwargs: resposta)
    monkeypatch.setattr(coletar.time, "sleep", esperas.append)
    coletar.pedir("/x")
    coletar.pedir("/y")
    assert esperas == [coletar.PAUSA, coletar.PAUSA]
    assert coletar.PAUSA == 3.0
