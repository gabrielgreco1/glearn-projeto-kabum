"""As regras da vigia, com números escritos à mão. Não falam com o banco."""

from datetime import date

from vigiar import avisos_do_dia, dias_faltando


def test_dia_que_faltou_no_meio():
    dias = [date(2026, 11, 14), date(2026, 11, 15), date(2026, 11, 17)]
    assert dias_faltando(dias) == [date(2026, 11, 16)]
    assert dias_faltando(dias[:2]) == []


def test_dia_como_sempre_nao_avisa():
    assert avisos_do_dia(date(2026, 11, 15), 0.996, 2, date(2026, 11, 14), 477, 2) == []


def test_cobertura_perto_do_minimo_e_sumico_da_paginacao():
    avisos = avisos_do_dia(date(2026, 11, 15), 0.942, 28, date(2026, 11, 14), 477, 28)
    assert len(avisos) == 2
    assert avisos[0].startswith("a cobertura de 2026-11-15 ficou em 94.2%")
    assert "pode ser só ela" in avisos[1]


def test_sumico_maior_que_a_paginacao_aponta_a_loja():
    avisos = avisos_do_dia(date(2026, 11, 15), 1.0, 0, date(2026, 11, 14), 477, 240)
    assert avisos == ["sumiram 240 dos 477 produtos de 2026-11-14 para 2026-11-15 (50.3%); mais do que a paginação perdeu: "
                      "a loja tirou produtos ou a categoria mudou. Abra a página da categoria no navegador."]
