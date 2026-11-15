"""Testa a preparação das linhas para o COPY, sem banco: uma amostra com os vazios de verdade da silver."""

from datetime import date

import polars as pl
import pytest

from carregar import COLUNAS, conferir, depois_da_marca, dias_da_silver, do_dia, linhas

# Duas linhas com ids da silver de 14 e 15/11/2026: uma placa com modelo e um suporte sem modelo. O resto fica vazio.
AMOSTRA = pl.DataFrame({coluna: [None, None] for coluna in COLUNAS}).with_columns(
    pl.Series("dia", [date(2026, 11, 15), date(2026, 11, 14)]),
    pl.Series("id", [907752, 952540]),
    pl.Series("modelo", ["RTX 5070", None]),
    pl.Series("preco_final", [1162161, 2379]),
)


def test_vazio_vira_none():
    placa, suporte = linhas(AMOSTRA)
    assert len(placa) == len(COLUNAS)
    assert placa[COLUNAS.index("modelo")] == "RTX 5070"
    assert suporte[COLUNAS.index("modelo")] is None


def test_dias_em_ordem():
    assert dias_da_silver(AMOSTRA) == [date(2026, 11, 14), date(2026, 11, 15)]


def test_dia_que_a_silver_nao_tem():
    with pytest.raises(SystemExit, match="não tem o dia 2026-11-13"):
        do_dia(AMOSTRA, date(2026, 11, 13))


def test_so_os_dias_depois_da_marca():
    dias = [date(2026, 11, 14), date(2026, 11, 15)]
    assert depois_da_marca(dias, None) == dias
    assert depois_da_marca(dias, date(2026, 11, 14)) == [date(2026, 11, 15)]
    assert depois_da_marca(dias, date(2026, 11, 15)) == []


def test_conferir_para_quando_a_conta_nao_fecha():
    conferir((477, 217122953), (477, 217122953))
    with pytest.raises(ValueError, match="não fecha"):
        conferir((477, 217122953), (478, 217125332))
