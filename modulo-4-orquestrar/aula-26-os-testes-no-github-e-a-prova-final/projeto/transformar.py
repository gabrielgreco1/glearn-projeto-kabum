"""A etapa Transformar inteira, sobre o que já está em dados/: a silver validada, o relatório de qualidade e a gold.

Não faz pedido nenhum ao site. Se o relatório disser para não publicar, nada é gravado na silver nem na gold:
os arquivos da rodada anterior continuam lá."""

import historico
import qualidade
import silver
import validar
from coletar import registro


def main():
    registro.info("transformar 1 de 3: montar e conferir a silver")
    tabela = silver.montar()
    validos, rejeitados, _ = validar.separar(tabela)
    registro.info("lidos %s = válidos %s + rejeitados %s", tabela.height, validos.height, rejeitados["linha"].n_unique())
    novos = silver.sem_mapa()
    if novos:
        registro.warning("fabricantes fora do %s: %s. Acrescente uma linha para cada um.", silver.MAPA, ", ".join(novos))
    registro.info("transformar 2 de 3: o relatório de qualidade")
    rel = qualidade.relatorio(tabela, validos, rejeitados)
    qualidade.gravar(rel)
    if not rel["publicado"]:
        raise SystemExit(f"Nada foi publicado: {rel['motivo']}. A silver e a gold da rodada anterior continuam em dados/.")
    validar.gravar(validos, rejeitados)
    registro.info("transformar 3 de 3: a gold")
    historico.main()


if __name__ == "__main__":
    main()
