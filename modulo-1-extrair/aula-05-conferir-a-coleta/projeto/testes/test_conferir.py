"""Testes da conferência, com uma página da loja escrita à mão. Não fazem pedido nenhum."""

from pathlib import Path

from conferir import total_da_pagina

AMOSTRA = Path(__file__).parent / "amostra_loja.html"


def test_total_vem_do_json_guardado_dentro_do_texto():
    assert total_da_pagina(AMOSTRA.read_text(encoding="utf-8")) == 123


def test_pagina_sem_o_bloco_devolve_none():
    assert total_da_pagina("<html><body>sem o bloco</body></html>") is None
