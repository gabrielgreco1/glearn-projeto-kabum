"""A rodada do dia: coletar, conferir e montar o histórico. Rode uma vez por dia."""

import conferir
import tabela
from coletar import coletar, registro


def main():
    registro.info("etapa 1 de 3: as páginas da categoria")
    coletar()
    registro.info("etapa 2 de 3: conferir a coleta")
    conferir.conferir()
    registro.info("etapa 3 de 3: o histórico de preços")
    tabela.gravar_csv(tabela.montar())


if __name__ == "__main__":
    main()
