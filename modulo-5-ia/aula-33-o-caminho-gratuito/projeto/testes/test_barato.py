"""O barato.py sobre uma silver escrita à mão. Não faz pedido nenhum e não usa o banco."""

from datetime import date

import polars as pl

from barato import aviso, buscar, normalizar, principal, reais

SILVER = pl.DataFrame({
    "dia": [date(2026, 11, 14), date(2026, 11, 15), date(2026, 11, 15), date(2026, 11, 15),
            date(2026, 11, 15), date(2026, 11, 15), date(2026, 11, 15)],
    "id": [1, 2, 3, 4, 5, 6, 7],
    "titulo": ["RTX 5070 velha", "RTX 5070 Caro", "RTX 5070 Barata", "RTX 5070 Media",
               "RTX 5070 Ti Gamer", "Suporte RTX 5070", "RTX 5060 Barata"],
    "e_placa": [True, True, True, True, True, False, True],
    "modelo": ["RTX 5070", "RTX 5070", "RTX 5070", "RTX 5070", "RTX 5070 TI", "RTX 5070", "RTX 5060"],
    "preco_final": [100000, 399990, 289900, 309000, 450000, 1000, 250000],
    "link": ["https://x/1", "https://x/2", "https://x/3", "https://x/4", "https://x/5", "https://x/6", "https://x/7"],
})


def test_os_tres_mais_baratos_do_ultimo_dia():
    achados = buscar(SILVER, "RTX 5070")
    assert achados["id"].to_list() == [3, 4, 2]  # sem o dia 14, sem o suporte, sem a Ti nem a 5060
    assert achados["preco_final"].to_list() == [289900, 309000, 399990]


def test_modelo_escrito_de_varios_jeitos_acha_o_mesmo():
    assert normalizar("rtx5070") == "RTX 5070"
    assert normalizar("  rtx  5070 ") == "RTX 5070"
    assert normalizar("RTX 5070 ti") == "RTX 5070 TI"
    assert normalizar("5070") is None


def test_modelo_que_nao_existe_no_dia_vem_vazio():
    assert buscar(SILVER, "RTX 4090").is_empty()
    assert buscar(SILVER, "sem modelo").is_empty()


def test_preco_em_reais():
    assert reais(213918) == "R$ 2.139,18"
    assert reais(1990) == "R$ 19,90"
    assert reais(100000) == "R$ 1.000,00"


def test_imprime_os_anuncios_e_sai_com_zero(tmp_path, capsys):
    caminho = tmp_path / "precos.parquet"
    SILVER.write_parquet(caminho)
    assert principal(["RTX", "5070"], caminho) == 0
    saida = capsys.readouterr().out
    assert "1. R$ 2.899,00  RTX 5070 Barata" in saida
    assert "   https://x/3" in saida
    assert "2. R$ 3.090,00  RTX 5070 Media" in saida
    assert "3. R$ 3.999,90  RTX 5070 Caro" in saida
    assert "RTX 5070 velha" not in saida


def test_modelo_fora_do_dia_diz_isso_e_sai_com_um(tmp_path, capsys):
    caminho = tmp_path / "precos.parquet"
    SILVER.write_parquet(caminho)
    assert principal(["RTX 4090"], caminho) == 1
    assert "Não há anúncio de RTX 4090" in capsys.readouterr().out


def test_sem_silver_diz_isso_e_sai_com_um(tmp_path, capsys):
    assert principal(["RTX 5070"], tmp_path / "nada.parquet") == 1
    assert "Não há silver" in capsys.readouterr().out


def anuncios(*precos):
    return pl.DataFrame({"id": list(range(1, len(precos) + 1)), "preco_final": list(precos)})


def test_avisa_quando_o_mais_barato_custa_menos_da_metade_do_segundo():
    texto = aviso(anuncios(199900, 599999, 605999))
    assert texto is not None
    assert "ATENÇÃO" in texto
    assert "R$ 1.999,00" in texto and "R$ 5.999,99" in texto


def test_nao_avisa_quando_o_preco_e_normal():
    assert aviso(anuncios(599999, 605999)) is None
    assert aviso(anuncios(300000, 600000)) is None  # exatamente a metade não é menos da metade
    assert aviso(anuncios(299999, 600000)) is not None


def test_nao_avisa_sem_dois_anuncios():
    assert aviso(anuncios(100)) is None
    assert aviso(anuncios()) is None


def test_imprime_o_aviso_junto_dos_anuncios(tmp_path, capsys):
    caminho = tmp_path / "precos.parquet"
    pl.DataFrame({
        "dia": [date(2026, 11, 15)] * 2,
        "id": [1, 2],
        "titulo": ["RTX 5070 Suspeita", "RTX 5070 Normal"],
        "e_placa": [True, True],
        "modelo": ["RTX 5070", "RTX 5070"],
        "preco_final": [100000, 300000],
        "link": ["https://x/1", "https://x/2"],
    }).write_parquet(caminho)
    assert principal(["RTX 5070"], caminho) == 0
    assert "ATENÇÃO" in capsys.readouterr().out
