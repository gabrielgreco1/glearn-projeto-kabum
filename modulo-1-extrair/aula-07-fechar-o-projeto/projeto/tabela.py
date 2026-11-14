"""Monta o histórico de preços: uma linha por produto por dia de coleta, com os valores como a API mandou."""

import csv
from pathlib import Path

from coletar import registro
from ler import CAMPOS, ler_dia

CSV = Path("dados/precos.csv")
COLUNAS = ["dia", *CAMPOS]


def montar():
    linhas = []
    for pasta in sorted(Path("dados/bronze").iterdir()):
        if not pasta.is_dir():
            continue
        vistos = set()
        for produto in ler_dia(pasta):
            if produto["id"] in vistos:  # o mesmo produto em duas páginas do mesmo dia entra uma vez
                continue
            vistos.add(produto["id"])
            linhas.append({"dia": pasta.name, **produto})
    return linhas


def gravar_csv(linhas, destino=CSV):
    with destino.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(linhas)
    dias = sorted({linha["dia"] for linha in linhas})
    registro.info("gravei %s linhas em %s, de %s dia(s): %s", len(linhas), destino, len(dias), ", ".join(dias))


if __name__ == "__main__":
    gravar_csv(montar())
