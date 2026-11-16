"""A rodada do dia: extrair (coletar, conferir e montar o histórico), transformar (silver, qualidade e gold) e carregar
no Postgres os dias novos e os que mudaram. Rode uma vez por dia, com o banco de pé."""

import carregar
import conferir
import tabela
import transformar
from coletar import coletar, registro
from observabilidade import logs


def main():
    logs.configurar(registro)
    execucao_id = logs.novo_id()  # sem o Prefect, o id nasce aqui
    with logs.na_etapa(execucao_id, "rodar"):
        etapas(execucao_id)


def etapas(execucao_id):
    registro.info("etapa 1 de 5: as páginas da categoria")
    coletar()
    registro.info("etapa 2 de 5: conferir a coleta")
    conferir.conferir()
    registro.info("etapa 3 de 5: o histórico de preços")
    tabela.gravar_csv(tabela.montar())
    registro.info("etapa 4 de 5: transformar")
    transformar.main()
    registro.info("etapa 5 de 5: carregar no banco")
    carregar.main(execucao_id=execucao_id)


if __name__ == "__main__":
    main()
