"""O projeto Kabum como um flow do Prefect: as cinco etapas do rodar.py, uma task cada, na ordem, sobre a pasta do
dia. A task que pede à Kabum é tentada de novo quando a rede falha; uma recusa da loja para sem nova tentativa.
Se a execução termina mal, fica um aviso em avisos.log."""

from datetime import date, datetime

from prefect import flow, task

import carregar as carga
import conferir as conferencia
import tabela
import transformar as transformacao
from coletar import coletar as coletar_paginas
from coletar import pasta_do_dia


@task(retries=3, retry_delay_seconds=10, timeout_seconds=300)
def coletar(pasta):
    """Tudo o que pede à Kabum: as páginas da API e a página da loja. O que já está na pasta do dia não é pedido de novo."""
    coletar_paginas(pasta)
    conferencia.pagina_da_loja(pasta)


conferir = task(conferencia.conferir, name="conferir")


@task
def historico():
    tabela.gravar_csv(tabela.montar())


transformar = task(transformacao.main, name="transformar")
carregar = task(carga.main, name="carregar")


def avisar(flow, flow_run, state):
    """O Prefect chama esta função quando a execução termina em Failed ou Crashed. O aviso diz o que olhar primeiro."""
    aviso = f"AVISO: {flow.name}, execução {flow_run.name}, terminou em {state.name}: {state.message}"
    print(aviso)
    with open("avisos.log", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {aviso} (o que fazer: runbook.md)\n")


@flow(log_prints=True, on_failure=[avisar], on_crashed=[avisar])
def projeto_kabum():
    pasta = pasta_do_dia(date.today())  # o dia é decidido uma vez: coletar e conferir olham a mesma pasta
    coletar(pasta)
    conferir(pasta)
    historico()
    transformar()
    carregar()
    print(f"coleta de {pasta.name} no banco")


if __name__ == "__main__":
    projeto_kabum()
