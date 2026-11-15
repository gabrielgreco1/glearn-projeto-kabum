"""A rodada do dia: extrair (coletar, conferir e montar o histórico), transformar (silver, qualidade e gold) e carregar
no Postgres os dias novos e os que mudaram. Rode uma vez por dia, com o banco de pé."""

import carregar
import conferir
import tabela
import transformar
from coletar import coletar, registro


def main():
    registro.info("etapa 1 de 5: as páginas das categorias")
    coletar()
    registro.info("etapa 2 de 5: conferir a coleta")
    conferir.conferir()
    registro.info("etapa 3 de 5: o histórico de preços")
    tabela.gravar_csv(tabela.montar())
    registro.info("etapa 4 de 5: transformar")
    transformar.main()
    registro.info("etapa 5 de 5: carregar no banco")
    carregar.main()


if __name__ == "__main__":
    main()
