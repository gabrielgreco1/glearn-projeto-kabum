"""Métricas da execução no formato do Prometheus: quantos pedidos, com que status, em quanto tempo, quantos itens, e
quando foi a última execução que terminou bem.

O projeto é um lote: roda uns segundos e o processo acaba. O Prometheus busca (raspa) as métricas de 15 em 15 s, e um
processo que já acabou não tem o que mostrar. Por isso, no fim de cada execução, os números vão para o Pushgateway,
que os guarda até a próxima execução, e o Prometheus raspa o Pushgateway. Cada envio leva os números DESTA execução:
o contador começa do zero a cada processo.

São dois grupos no Pushgateway. O da execução é trocado inteiro a cada envio: um número que esta execução não mediu
não fica lá com o valor da anterior. O do sucesso só é trocado quando a execução dá certo: a hora da última execução boa
sobrevive às que falham."""

import logging
import os
import time

import httpx
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, disable_created_metrics, push_to_gateway

from observabilidade import logs

SERVICO = logs.SERVICO
disable_created_metrics()  # sem as séries *_created, que dizem quando cada contador nasceu: aqui, nasce a cada execução
REGISTRO = CollectorRegistry()  # os números desta execução; só o que está aqui vai para o Pushgateway
SUCESSO = CollectorRegistry()  # a hora da última execução boa, num grupo à parte

PEDIDOS = Counter("glearn_pedidos", "Pedidos HTTP à loja, por etapa e status (erro_rede quando não houve resposta)",
                  ["servico", "etapa", "status"], registry=REGISTRO)
DURACAO = Histogram("glearn_pedido_segundos", "Quanto tempo cada pedido à loja levou, em segundos", ["servico", "etapa"],
                    buckets=(0.25, 0.5, 1, 2, 4, 8, 16), registry=REGISTRO)
ITENS = Counter("glearn_itens", "Itens que passaram pela etapa: produtos conferidos, linhas carregadas",
                ["servico", "etapa"], registry=REGISTRO)
EXECUCAO = Gauge("glearn_execucao_segundos", "Quanto tempo a última execução levou, do começo ao fim", ["servico"],
                 registry=REGISTRO)
DEU_CERTO = Gauge("glearn_execucao_ok", "1 se a última execução terminou bem, 0 se falhou", ["servico"], registry=REGISTRO)
ULTIMA_OK = Gauge("glearn_ultima_execucao_ok_timestamp", "Quando terminou a última execução que deu certo (Unix, s)",
                  ["servico"], registry=SUCESSO)


def etapa_atual():
    return logs.etapa.get() or "fora"


def pedir(url, **opcoes):
    """httpx.get medido: conta o pedido pelo status, ou como erro_rede se não houve resposta, e guarda a duração."""
    inicio = time.perf_counter()
    try:
        resposta = httpx.get(url, **opcoes)
    except httpx.HTTPError:
        PEDIDOS.labels(SERVICO, etapa_atual(), "erro_rede").inc()
        raise
    finally:
        DURACAO.labels(SERVICO, etapa_atual()).observe(time.perf_counter() - inicio)
    PEDIDOS.labels(SERVICO, etapa_atual(), str(resposta.status_code)).inc()
    return resposta


def itens(quantos):
    ITENS.labels(SERVICO, etapa_atual()).inc(quantos)


def enviar(inicio, deu_certo):
    """No fim da execução: os números dela, trocando os da anterior, e, se deu certo, a hora no grupo do sucesso."""
    EXECUCAO.labels(SERVICO).set(time.time() - inicio)
    DEU_CERTO.labels(SERVICO).set(1 if deu_certo else 0)
    endereco = os.getenv("PUSHGATEWAY_URL", "http://127.0.0.1:9091")
    try:
        push_to_gateway(endereco, job=SERVICO, registry=REGISTRO, timeout=5)
        if deu_certo:
            ULTIMA_OK.labels(SERVICO).set_to_current_time()
            push_to_gateway(endereco, job=SERVICO, grouping_key={"grupo": "sucesso"}, registry=SUCESSO, timeout=5)
    except OSError as erro:  # sem Pushgateway, o projeto segue: métrica é para olhar, não para parar a coleta
        logging.getLogger(SERVICO).warning("não consegui mandar as métricas para %s: %s", endereco, erro)
