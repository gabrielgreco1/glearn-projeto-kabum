"""O relatório de qualidade e a decisão de publicar, com a amostra e com rodadas inventadas. Não faz pedido nenhum."""

from pathlib import Path

import polars as pl

from qualidade import cobertura_do_dia, decidir, relatorio
from silver import montar
from validar import separar

AMOSTRA = Path(__file__).parent / "amostra_precos.csv"


def test_relatorio_da_amostra_publica():
    tabela = montar(AMOSTRA)
    rel = relatorio(tabela, *separar(tabela))
    assert (rel["dia"], rel["lidos"], rel["validos"], rel["rejeitados"]) == ("2026-11-15", 3, 3, 0)
    assert rel["publicado"] is True


def test_regra_de_erro_acima_de_2_por_cento_segura_a_publicacao():
    rel = {"lidos": 478, "validos": 466, "rejeitados_por_regra": {"pix_menor": 12, "preco_faixa": 0}}
    assert decidir(rel) == (False, "pix_menor: 2.5% das linhas rejeitadas, acima de 2%")
    rel["rejeitados_por_regra"]["pix_menor"] = 9  # 1,9%: um produto com o preço errado, não a fonte inteira
    assert decidir(rel)[0] is True


def test_sem_linha_valida_nao_publica():
    assert decidir({"lidos": 0, "validos": 0, "rejeitados_por_regra": {}}) == (False, "nenhuma linha válida")


def test_cobertura_vem_da_conferencia_do_mesmo_dia(tmp_path):
    conferencia = tmp_path / "conferencia.csv"
    pl.DataFrame({"dia": ["2026-11-14", "2026-11-15"], "cobertura": [0.998, 0.996]}).write_csv(conferencia)
    assert cobertura_do_dia("2026-11-15", conferencia) == 0.996
    assert cobertura_do_dia("2026-11-16", conferencia) is None
    assert cobertura_do_dia("2026-11-15", tmp_path / "nao-existe.csv") is None
