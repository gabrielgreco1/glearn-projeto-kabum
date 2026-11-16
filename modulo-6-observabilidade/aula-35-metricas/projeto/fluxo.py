"""O projeto Kabum como um flow do Prefect: as cinco etapas do rodar.py, uma task cada, na ordem, sobre a pasta do
dia. A task que pede à Kabum é tentada de novo quando a rede falha; uma recusa da loja para sem nova tentativa.
Se a execução termina mal, fica um aviso em avisos.log. Se termina bem, mas a vigia vê algo estranho no banco, também.
Toda linha de log da execução vai também para logs/kabum.jsonl, em JSON, com o id do flow run: o mesmo id fica em
cada linha que a carga grava no banco. Uma execução por vez: a segunda espera a vaga do limite projeto-kabum, criado uma vez no servidor do Prefect com
uv run prefect gcl create projeto-kabum --limit 1

Uso: uv run python fluxo.py            roda uma vez, agora
     uv run python fluxo.py agendar    fica ligado e roda todo dia às 6h e às 18h (Ctrl+C para parar)
"""

import sys
import time
from datetime import date, datetime

from prefect import flow, task
from prefect.concurrency.sync import concurrency
from prefect.runtime import flow_run as execucao_atual
from prefect.runtime import task_run
from prefect.schedules import Cron

import carregar as carga
import conferir as conferencia
import tabela
import transformar as transformacao
import vigiar as vigia
from coletar import coletar as coletar_paginas
from coletar import pasta_do_dia, registro
from observabilidade import logs, metricas


def etapa(execucao_id, nome):
    """Dentro da task: o id da execução, o nome da etapa e a tentativa (1, 2, 3...) em toda linha de log."""
    return logs.na_etapa(execucao_id, nome, task_run.run_count)


# Cada task recebe o execucao_id como parâmetro, e não só pelo contextvars do flow: uma task que roda em outro processo
# ou em outra máquina não enxerga as variáveis de quem a chamou. Parâmetro viaja; contexto, não.
@task(retries=3, retry_delay_seconds=10, timeout_seconds=300)
def coletar(pasta, execucao_id):
    """Tudo o que pede à Kabum: as páginas da API e a página da loja. O que já está na pasta do dia não é pedido de novo."""
    with etapa(execucao_id, "coletar"):
        coletar_paginas(pasta)
        conferencia.pagina_da_loja(pasta)


@task
def conferir(pasta, execucao_id):
    with etapa(execucao_id, "conferir"):
        return conferencia.conferir(pasta)


@task
def historico(execucao_id):
    with etapa(execucao_id, "historico"):
        tabela.gravar_csv(tabela.montar())


@task
def transformar(execucao_id):
    with etapa(execucao_id, "transformar"):
        transformacao.main()


@task
def carregar(execucao_id):
    with etapa(execucao_id, "carregar"):
        carga.main(execucao_id=execucao_id)


def anotar(aviso):
    """Mostra o aviso no log e acrescenta uma linha em avisos.log, com a hora."""
    print(aviso)
    with open("avisos.log", "a", encoding="utf-8") as arquivo:
        arquivo.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} {aviso} (o que fazer: runbook.md)\n")


def avisar(flow, flow_run, state):
    """O Prefect chama esta função quando a execução termina em Failed ou Crashed. O aviso diz o que olhar primeiro."""
    with logs.na_etapa(str(flow_run.id), "fluxo"):
        registro.error("a execução terminou em %s: %s", state.name, state.message)
    anotar(f"AVISO: {flow.name}, execução {flow_run.name} ({flow_run.id}), terminou em {state.name}: {state.message}")


@task
def vigiar(execucao_id):
    """O que o portão deixa passar: cada aviso da vigia vira uma linha de ATENÇÃO, e a execução continua Completed."""
    with etapa(execucao_id, "vigiar"):
        for aviso in vigia.avisos():
            registro.warning("atenção: %s", aviso)
            anotar(f"ATENÇÃO: {aviso}")


@flow(log_prints=True, on_failure=[avisar], on_crashed=[avisar])
def projeto_kabum():
    logs.configurar(registro)
    execucao_id = str(execucao_atual.id)  # o id do flow run: o mesmo da URL da execução no painel do Prefect
    inicio, deu_certo = time.time(), False
    try:
        # Uma execução por vez, da coleta à vigia: duas ao mesmo tempo pediriam as mesmas páginas duas vezes à loja
        # e escreveriam os mesmos arquivos. strict=True: sem o limite criado no servidor, para aqui.
        with concurrency("projeto-kabum", occupy=1, timeout_seconds=900, strict=True):
            pasta = pasta_do_dia(date.today())  # o dia é decidido uma vez: coletar e conferir olham a mesma pasta
            coletar(pasta, execucao_id)
            conferir(pasta, execucao_id)
            historico(execucao_id)
            transformar(execucao_id)
            carregar(execucao_id)
            vigiar(execucao_id)
        deu_certo = True
    finally:  # deu certo ou não, os números desta execução vão para o Pushgateway
        metricas.enviar(inicio, deu_certo)
    print(f"coleta de {pasta.name} no banco, execução {execucao_id}")


if __name__ == "__main__":
    if sys.argv[1:] == ["agendar"]:
        # Às 6h e às 18h, no horário de Brasília. A das 18h é a segunda chance do dia: se a das 6h coletou tudo, ela não
        # pede nada; se a das 6h falhou, ela coleta. Depois da meia-noite, o preço daquele dia não volta mais.
        projeto_kabum.serve(name="duas-vezes-por-dia", schedule=Cron("0 6,18 * * *", timezone="America/Sao_Paulo"))
    else:
        projeto_kabum()
