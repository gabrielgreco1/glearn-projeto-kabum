"""O perfil de um precos.csv escrito à mão: três linhas, dois dias, dois produtos."""

from pathlib import Path

from perfil import medir

AMOSTRA = Path(__file__).parent / "amostra_precos.csv"


def test_medir_conta_linhas_dias_e_produtos():
    medidas = medir(AMOSTRA)
    assert medidas["linhas"] == 3
    assert medidas["dias"] == ["2026-11-14", "2026-11-15"]
    assert medidas["produtos"] == 2


def test_vazios_e_colunas_que_nao_mudam():
    medidas = medir(AMOSTRA)
    assert medidas["vazios"] == {"oferta_price": 2, "oferta_price_with_discount": 2, "oferta_ends_at": 2, "fabricante": 1, "vendedor": 2}
    assert medidas["um_valor_so"] == ["old_price", "available"]
    assert medidas["tipos"]["available"] == "Boolean"
