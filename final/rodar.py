"""A rodada do dia: extrair (coletar, conferir e montar o histórico) e transformar (silver, qualidade e gold). Rode uma vez por dia."""

import conferir
import tabela
import transformar
from coletar import coletar, registro


def main():
    registro.info("etapa 1 de 4: as páginas da categoria")
    coletar()
    registro.info("etapa 2 de 4: conferir a coleta")
    conferir.conferir()
    registro.info("etapa 3 de 4: o histórico de preços")
    tabela.gravar_csv(tabela.montar())
    registro.info("etapa 4 de 4: transformar")
    transformar.main()


if __name__ == "__main__":
    main()
