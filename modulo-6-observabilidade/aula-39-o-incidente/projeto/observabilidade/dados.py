"""Observabilidade de dados: o pipeline pode terminar verde com o dado errado. Estas métricas olham o dado que acabou de
ser publicado, e não a execução: quantas linhas (volume), quantos vazios por coluna, que campos a fonte mandou
(esquema) e qual o dia mais novo (frescor do dado). Vão no mesmo envio das métricas da execução (metricas.py)."""

import hashlib
from datetime import datetime, time
from zoneinfo import ZoneInfo

from prometheus_client import Gauge

from observabilidade import metricas

SERVICO = metricas.SERVICO

LINHAS = Gauge("glearn_dado_linhas", "Linhas do dia novo na tabela publicada", ["servico", "tabela"],
               registry=metricas.REGISTRO)
NULOS = Gauge("glearn_dado_nulos_ratio", "Fração de vazios de cada coluna vigiada, no dia novo",
              ["servico", "tabela", "coluna"], registry=metricas.REGISTRO)
CAMPOS = Gauge("glearn_dado_campos", "Quantos campos a fonte mandou", ["servico", "fonte"], registry=metricas.REGISTRO)
ESQUEMA = Gauge("glearn_dado_esquema_hash", "Impressão digital dos nomes de campo da fonte (8 dígitos do sha256, como número)",
                ["servico", "fonte"], registry=metricas.REGISTRO)
DIA = Gauge("glearn_dado_dia_timestamp", "O dia mais novo da tabela publicada, à meia-noite de Brasília (Unix, s)",
            ["servico", "tabela"], registry=metricas.REGISTRO)


def impressao(campos):
    """Mesmos nomes de campo, em qualquer ordem, dão o mesmo número; um campo a mais ou a menos dá outro."""
    return int(hashlib.sha256(",".join(sorted(campos)).encode("utf-8")).hexdigest()[:8], 16)


def volume(tabela, linhas):
    LINHAS.labels(SERVICO, tabela).set(linhas)


def nulos(tabela, fracoes):
    for coluna, fracao in fracoes.items():
        NULOS.labels(SERVICO, tabela, coluna).set(fracao)


def esquema(fonte, campos):
    CAMPOS.labels(SERVICO, fonte).set(len(campos))
    ESQUEMA.labels(SERVICO, fonte).set(impressao(campos))


def dia_mais_novo(tabela, dia):
    # meia-noite no fuso do projeto (o da silver): o Grafana, no horário de Brasília, mostra o dia certo
    DIA.labels(SERVICO, tabela).set(datetime.combine(dia, time(), tzinfo=ZoneInfo("America/Sao_Paulo")).timestamp())
