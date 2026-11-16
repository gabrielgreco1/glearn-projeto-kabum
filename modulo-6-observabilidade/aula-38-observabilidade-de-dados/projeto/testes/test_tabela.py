"""O histórico com dois dias de coleta, montado a partir da amostra. Não faz pedido nenhum."""

import shutil
from pathlib import Path

from conferir import SELO
from tabela import montar

AMOSTRA = Path(__file__).parent / "amostra_pagina.json"


def test_uma_linha_por_produto_por_dia(tmp_path):
    for dia in ["2026-11-14", "2026-11-15"]:
        pasta = tmp_path / "bronze" / dia
        pasta.mkdir(parents=True)
        shutil.copy(AMOSTRA, pasta / "pagina-001.json")
        shutil.copy(AMOSTRA, pasta / "pagina-002.json")  # a mesma página duas vezes: os mesmos produtos repetidos
        (pasta / SELO).write_text("1.000\n", encoding="utf-8")
    linhas = montar(tmp_path / "bronze")
    assert len(linhas) == 4  # 2 produtos x 2 dias; os repetidos do mesmo dia entram uma vez
    assert [(linha["dia"], linha["id"]) for linha in linhas] == [
        ("2026-11-14", 111), ("2026-11-14", 222), ("2026-11-15", 111), ("2026-11-15", 222)]


def test_dia_sem_selo_fica_fora(tmp_path):
    for dia in ["2026-11-14", "2026-11-15"]:
        pasta = tmp_path / "bronze" / dia
        pasta.mkdir(parents=True)
        shutil.copy(AMOSTRA, pasta / "pagina-001.json")
    (tmp_path / "bronze/2026-11-14" / SELO).write_text("1.000\n", encoding="utf-8")  # o dia 15 parou no meio da coleta
    assert {linha["dia"] for linha in montar(tmp_path / "bronze")} == {"2026-11-14"}
