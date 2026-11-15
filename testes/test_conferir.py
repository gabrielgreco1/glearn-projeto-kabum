"""Testes da conferência, com uma página da loja escrita à mão. Não fazem pedido nenhum."""

from pathlib import Path

import conferir
from conferir import anotar, barrar, total_da_pagina

AMOSTRA = Path(__file__).parent / "amostra_loja.html"


def test_total_vem_do_json_guardado_dentro_do_texto():
    assert total_da_pagina(AMOSTRA.read_text(encoding="utf-8")) == 123


def test_pagina_sem_o_bloco_devolve_none():
    assert total_da_pagina("<html><body>sem o bloco</body></html>") is None


def test_conferir_de_novo_o_mesmo_dia_troca_a_linha(tmp_path):
    destino = tmp_path / "conferencia.csv"
    dia_14 = {"dia": "2026-11-14", "lidos": 472, "diferentes": 451, "repetidos": 21, "declarado": 472, "loja": 473, "cobertura": "0.956"}
    dia_15 = {"dia": "2026-11-15", "lidos": 474, "diferentes": 474, "repetidos": 0, "declarado": 474, "loja": 474, "cobertura": "1.000"}
    anotar(dia_14, destino)
    anotar(dia_15, destino)
    anotar(dia_14, destino)  # o dia 14 conferido de novo: a linha dele é trocada, não repetida
    assert destino.read_text(encoding="utf-8").splitlines() == [
        "dia,lidos,diferentes,repetidos,declarado,loja,cobertura",
        "2026-11-14,472,451,21,472,473,0.956",
        "2026-11-15,474,474,0,474,474,1.000",
    ]


def test_barrar_tira_a_pasta_do_bronze(tmp_path, monkeypatch):
    monkeypatch.setattr(conferir, "BARRADOS", tmp_path / "barrados")
    pasta = tmp_path / "bronze/2026-11-15"
    pasta.mkdir(parents=True)
    (pasta / "pagina-001.json").write_text("{}", encoding="utf-8")
    destino = barrar(pasta)
    assert not pasta.exists()  # a próxima rodada do dia coleta tudo de novo
    assert destino.parent == tmp_path / "barrados" and destino.name.startswith("2026-11-15-")
    assert (destino / "pagina-001.json").exists()  # a coleta barrada fica guardada, para você ler
