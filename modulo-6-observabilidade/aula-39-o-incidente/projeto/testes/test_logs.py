"""O formato dos logs: uma linha de JSON com os campos fixos e o id da execução, e nada de segredo ou e-mail nela."""

import json
import logging

import pytest

from observabilidade import logs


def linha(mensagem, *args, **extra):
    """Formata um registro como o arquivo logs/kabum.jsonl o grava e devolve o dicionário."""
    registro = logging.LogRecord("kabum", logging.INFO, "x.py", 1, mensagem, args, None)
    for chave, valor in extra.items():
        setattr(registro, chave, valor)
    return json.loads(logs.FormatoJson().format(registro))


def test_toda_linha_tem_os_campos_fixos_e_o_id_da_etapa():
    with logs.na_etapa("11111111-2222-3333-4444-555555555555", "coletar", 2):
        dado = linha("baixei a página %s", 3, pagina=3)
    assert dado["execucao_id"] == "11111111-2222-3333-4444-555555555555"
    assert dado["etapa"] == "coletar"
    assert dado["tentativa"] == 2
    assert dado["msg"] == "baixei a página 3"
    assert dado["pagina"] == 3
    assert {"ts", "nivel", "servico"} <= set(dado)


def test_fora_da_etapa_o_id_fica_vazio():
    assert linha("sem etapa")["execucao_id"] is None


def test_senha_do_banco_nao_vai_para_o_log():
    dado = linha("conectando em %s", "postgresql://postgres:treino@localhost:5434/postgres")
    assert "treino" not in json.dumps(dado)
    assert dado["msg"] == "conectando em postgresql://postgres:***@localhost:5434/postgres"


def test_cabecalhos_e_email_nao_vao_para_o_log():
    cabecalhos = {"User-Agent": "projeto-de-estudo/0.1 (aluna@exemplo.com.br)", "Authorization": "Bearer abc123", "Cookie": "sessao=xyz"}
    texto = json.dumps(linha("a loja recusou; cabeçalhos: %s", cabecalhos))
    for segredo in ("aluna@exemplo.com.br", "abc123", "xyz"):
        assert segredo not in texto


def test_parada_de_proposito_fica_no_log_como_erro_com_a_mensagem(caplog):
    with pytest.raises(SystemExit), logs.na_etapa("id-de-teste", "carregar"):
        raise SystemExit("O banco recusou a senha do DATABASE_URL (.env).")
    assert caplog.records[-1].levelname == "ERROR"
    assert "a etapa carregar parou: O banco recusou a senha" in caplog.records[-1].getMessage()
