"""A gold montada a partir de uma silver de três dias escrita à mão, numa pasta temporária. Não faz pedido nenhum."""

from datetime import date

import duckdb
import polars as pl

from historico import MODELOS, MUDANCAS, SUMIRAM

D14, D15, D16 = date(2026, 11, 14), date(2026, 11, 15), date(2026, 11, 16)


def preparar(pasta):
    """dados/silver/precos.parquet e dados/conferencia.csv dentro da pasta temporária."""
    (pasta / "dados/silver").mkdir(parents=True)
    pl.DataFrame({
        "dia": [D14, D14, D15, D15, D16, D16],
        "id": [1, 2, 1, 3, 1, 2],
        "titulo": ["Placa A", "Placa B", "Placa A", "Placa C", "Placa A", "Placa B"],
        "e_placa": [True] * 6,
        "modelo": ["RTX 5060", "RTX 5060", "RTX 5060", "RTX 5060", "RTX 5060", "RTX 5060"],
        "preco_final": [100000, 50000, 90000, 70000, 90000, 50000],
        "em_oferta": [False, False, False, False, True, False],
    }).write_parquet(pasta / "dados/silver/precos.parquet")
    (pasta / "dados/conferencia.csv").write_text("dia,cobertura\n2026-11-15,1.000\n2026-11-16,0.950\n", encoding="utf-8")


def test_mudanca_de_preco_e_de_oferta(tmp_path, monkeypatch):
    preparar(tmp_path)
    monkeypatch.chdir(tmp_path)  # as consultas leem dados/ a partir da pasta onde o programa roda
    linhas = duckdb.sql(MUDANCAS).fetchall()
    assert [(dia, i, antes, depois, pct) for dia, i, _, _, antes, depois, _, pct, _, _ in linhas] == [
        (D15, 1, 100000, 90000, -10.0),  # caiu 10%
        (D16, 1, 90000, 90000, 0.0),  # mesmo preço, mas entrou em oferta
    ]


def test_o_que_sumiu_vem_com_a_cobertura_do_dia(tmp_path, monkeypatch):
    preparar(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert duckdb.sql(SUMIRAM).fetchall() == [
        (D15, 2, "Placa B", 50000, 1.0),  # a coleta do dia 15 estava completa: o produto saiu mesmo
        (D16, 3, "Placa C", 70000, 0.95),  # no dia 16 faltaram 5%: pode ter sido a paginação
    ]


def test_menor_preco_de_cada_modelo_por_dia(tmp_path, monkeypatch):
    preparar(tmp_path)
    monkeypatch.chdir(tmp_path)
    assert duckdb.sql(MODELOS).fetchall() == [
        (D14, "RTX 5060", 2, 50000, 75000.0, 2),
        (D15, "RTX 5060", 2, 70000, 80000.0, 3),
        (D16, "RTX 5060", 2, 50000, 70000.0, 2),
    ]
