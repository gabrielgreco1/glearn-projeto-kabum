"""Confere a coleta do dia: o total que a API declara, os produtos repetidos e o total que a página da loja mostra.

A paginação da API perde produtos: a ordem padrão tem empates, e cada página desempata de um jeito.
Alguns produtos vêm em duas páginas e outros em nenhuma. A conferência mede quanto faltou e guarda o número."""

import csv
import json
import re
import time
from collections import Counter
from pathlib import Path

import httpx

from coletar import CABECALHOS, PAUSA, pasta_do_dia, registro
from ler import ler_dia

PAGINA_DA_LOJA = "https://www.kabum.com.br/hardware/placa-de-video-vga"
COBERTURA_MINIMA = 0.90  # nas rodadas de 14/11/2026 a cobertura ficou entre 92% e 99,6%
REGISTRO = Path("dados/conferencia.csv")  # uma linha por conferência: o que faltou fica anotado


def total_declarado(pasta):
    """O total que a própria API diz ter, na primeira página guardada."""
    primeira = json.loads((Path(pasta) / "pagina-001.json").read_text(encoding="utf-8"))
    return primeira["meta"]["total_items_count"]


def total_da_pagina(html):
    """O total que a página da loja traz no bloco __NEXT_DATA__, o estado que o Next.js manda junto com o HTML."""
    bloco = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not bloco:
        return None
    estado = json.loads(bloco.group(1))
    dados = json.loads(estado["props"]["pageProps"]["data"])  # um JSON guardado dentro de um texto
    return dados["catalogServer"]["meta"]["totalItemsCount"]


def anotar(dia, lidos, diferentes, repetidos, declarado, loja, cobertura):
    """Acrescenta uma linha em dados/conferencia.csv. O arquivo só cresce."""
    novo = not REGISTRO.exists()
    with REGISTRO.open("a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        if novo:
            escritor.writerow(["dia", "lidos", "diferentes", "repetidos", "declarado", "loja", "cobertura"])
        escritor.writerow([dia, lidos, diferentes, repetidos, declarado, loja, f"{cobertura:.3f}"])


def conferir(pasta=None, olhar_a_loja=True):
    pasta = pasta or pasta_do_dia()
    produtos = ler_dia(pasta)
    ids = Counter(produto["id"] for produto in produtos)
    repetidos = {produto_id: vezes for produto_id, vezes in ids.items() if vezes > 1}
    declarado = total_declarado(pasta)
    registro.info("coleta: %s produtos lidos, %s diferentes; a API declara %s", len(produtos), len(ids), declarado)
    registro.info("repetidos entre páginas: %s", ", ".join(f"{i} ({n} vezes)" for i, n in repetidos.items()) or "nenhum")
    if olhar_a_loja:
        resposta = httpx.get(PAGINA_DA_LOJA, headers={**CABECALHOS, "Accept": "text/html"}, timeout=30)
        time.sleep(PAUSA)
        loja = total_da_pagina(resposta.text) if resposta.status_code == 200 else None
        registro.info("a página da loja mostra %s produtos (status %s)", loja, resposta.status_code)
    else:
        loja = None
    cobertura = len(ids) / declarado
    registro.info("cobertura: %s de %s, %.1f%%; faltaram %s", len(ids), declarado, cobertura * 100, declarado - len(ids))
    anotar(Path(pasta).name, len(produtos), len(ids), len(repetidos), declarado, loja, cobertura)
    if cobertura < COBERTURA_MINIMA:
        raise SystemExit(f"A cobertura ficou em {cobertura:.1%}, abaixo de {COBERTURA_MINIMA:.0%}. Confira os repetidos antes de seguir.")
    return len(ids)


if __name__ == "__main__":
    conferir()
