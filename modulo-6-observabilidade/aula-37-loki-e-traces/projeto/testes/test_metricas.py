"""O pedido medido conta pelo status, ou como erro_rede quando não houve resposta. Nenhum teste fala com a loja."""

import httpx
import pytest

from observabilidade import logs, metricas


def contagem(status, etapa="coletar"):
    return metricas.REGISTRO.get_sample_value("glearn_pedidos_total", {"servico": "kabum", "etapa": etapa, "status": status}) or 0


def test_o_pedido_conta_pelo_status(monkeypatch):
    monkeypatch.setattr(metricas.cliente, "get", lambda url, **opcoes: httpx.Response(429))
    antes = contagem("429")
    with logs.na_etapa("id-de-teste", "coletar"):
        metricas.pedir("http://loja/pagina")
    assert contagem("429") == antes + 1


def test_sem_resposta_conta_como_erro_de_rede_e_o_erro_sobe(monkeypatch):
    def cair(url, **opcoes):
        raise httpx.ConnectError("sem rede")

    monkeypatch.setattr(metricas.cliente, "get", cair)
    antes = contagem("erro_rede")
    with pytest.raises(httpx.ConnectError), logs.na_etapa("id-de-teste", "coletar"):
        metricas.pedir("http://loja/pagina")
    assert contagem("erro_rede") == antes + 1
