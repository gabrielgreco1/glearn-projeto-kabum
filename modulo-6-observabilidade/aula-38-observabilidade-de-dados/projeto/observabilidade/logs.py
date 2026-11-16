"""Logs em JSON, uma linha por evento, com o id da execução em todas as linhas.

Cada linha leva campos fixos (ts, nivel, servico, execucao_id, etapa, tentativa, msg), o trace_id e o span_id quando
a linha nasce dentro de um span (traces.py), e os campos extras que quem
registrou passou (pagina, status, duracao_ms...). O id e a etapa ficam em contextvars: a task diz uma vez em que
execução e etapa está, e toda linha registrada dali para baixo, no mesmo fio de execução, sai com eles.
Antes de ir para o arquivo, o texto passa pela máscara: senha, cabeçalho de autorização, cookie e e-mail viram ***."""

import contextvars
import json
import logging
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from opentelemetry import trace

SERVICO = "kabum"
ARQUIVO = Path("logs/kabum.jsonl")

execucao_id = contextvars.ContextVar("execucao_id", default=None)
etapa = contextvars.ContextVar("etapa", default=None)
tentativa = contextvars.ContextVar("tentativa", default=None)

# O que nunca vai para o log, nesta ordem: a senha dentro de um endereço de banco, o valor de um cabeçalho de
# autorização ou de cookie, e qualquer e-mail (o contato do User-Agent é dado pessoal).
MASCARAS = [
    (re.compile(r"(\w+://[^:/@\s]+:)[^@\s]+@"), r"\1***@"),
    (re.compile(r"(?i)\b(authorization|proxy-authorization|cookie|set-cookie)(['\"]?\s*[:=]\s*['\"]?)[^'\"\n,}]+"), r"\1\2***"),
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "***@***"),
]
# Os atributos que todo LogRecord tem. O que não está aqui veio pelo extra= de quem registrou e vai para a linha.
PADRAO = set(vars(logging.LogRecord("", 0, "", 0, "", None, None))) | {"message", "asctime", "taskName"}


def mascarar(texto):
    for padrao, troca in MASCARAS:
        texto = padrao.sub(troca, texto)
    return texto


class FormatoJson(logging.Formatter):
    """Uma linha de JSON por registro."""

    def format(self, registro):
        linha = {
            "ts": datetime.fromtimestamp(registro.created, timezone.utc).isoformat(timespec="milliseconds"),
            "nivel": registro.levelname,
            "servico": SERVICO,
            "execucao_id": execucao_id.get(),
            "etapa": etapa.get(),
            "tentativa": tentativa.get(),
            "msg": mascarar(registro.getMessage()),
        }
        contexto = trace.get_current_span().get_span_context()
        if contexto.is_valid:  # a linha nasceu dentro de um span: o mesmo trace_id leva do log ao trace no Tempo
            linha["trace_id"] = format(contexto.trace_id, "032x")
            linha["span_id"] = format(contexto.span_id, "016x")
        for chave, valor in vars(registro).items():
            if chave not in PADRAO and chave not in linha:
                linha[chave] = mascarar(valor) if isinstance(valor, str) else valor
        if registro.exc_info:
            linha["erro"] = mascarar(self.formatException(registro.exc_info))
        return json.dumps(linha, ensure_ascii=False, default=str)


def configurar(registro, arquivo=ARQUIVO):
    """Acrescenta ao registro um arquivo com uma linha de JSON por evento. Chamar duas vezes não duplica as linhas."""
    if any(getattr(h, "observabilidade", False) for h in registro.handlers):
        return
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    saida = logging.FileHandler(arquivo, encoding="utf-8")
    saida.setFormatter(FormatoJson())
    saida.observabilidade = True
    registro.addHandler(saida)


def novo_id():
    """Um id para quando o projeto roda sem o Prefect (rodar.py). No Prefect, o id é o do flow run."""
    return str(uuid.uuid4())


@contextmanager
def na_etapa(id_execucao, nome, numero_tentativa=None):
    """Tudo o que for registrado dentro do with sai com este id, esta etapa e esta tentativa. Um erro que sai do with
    fica registrado como WARNING, com o traceback, e sobe: quem decide se tenta de novo é o orquestrador."""
    marcas = [execucao_id.set(id_execucao), etapa.set(nome), tentativa.set(numero_tentativa)]
    try:
        yield
    except Exception as erro:
        logging.getLogger(SERVICO).warning("a etapa %s falhou na tentativa %s: %r", nome, numero_tentativa, erro, exc_info=True)
        raise
    finally:
        for var, marca in zip((execucao_id, etapa, tentativa), marcas):
            var.reset(marca)
