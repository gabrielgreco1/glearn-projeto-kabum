"""Confere a coleta do dia: o total que a API declara, os produtos repetidos e o total que a página da loja mostra.

A paginação da API perde produtos: a ordem padrão tem empates, e cada página desempata de um jeito.
Alguns produtos vêm em duas páginas e outros em nenhuma. A conferência mede quanto faltou e guarda o número.
Abaixo do mínimo, a coleta do dia sai do bronze, para dados/barrados/, e a rodada para antes de publicar. Acima dele,
a pasta do dia ganha o selo: só um dia com selo entra no histórico.

Uso: uv run python conferir.py               confere a coleta de hoje
     uv run python conferir.py 2026-11-14    confere de novo um dia guardado, sem pedir nada se a loja.html está lá"""

import csv
import json
import re
import sys
import time
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import httpx

from coletar import PAUSA, cabecalhos, pasta_do_dia, registro
from ler import ler_dia

PAGINA_DA_LOJA = "https://www.kabum.com.br/hardware/placa-de-video-vga"
COBERTURA_MINIMA = 0.90  # nas rodadas de 14/11/2026 a cobertura ficou entre 92% e 100%
REGISTRO = Path("dados/conferencia.csv")  # uma linha por dia de coleta: o que faltou fica anotado
COLUNAS = ["dia", "lidos", "diferentes", "repetidos", "declarado", "loja", "cobertura"]
BARRADOS = Path("dados/barrados")  # as coletas que a conferência barrou, guardadas para você ler
SELO = "conferida.txt"  # o arquivo que a conferência deixa na pasta do dia quando a cobertura passa


def total_declarado(pasta):
    """O total que a própria API diz ter, na primeira página guardada."""
    primeira = json.loads((Path(pasta) / "pagina-001.json").read_text(encoding="utf-8"))
    return primeira["meta"]["total_items_count"]


def pagina_da_loja(pasta):
    """O HTML da página da categoria, guardado na pasta do dia. Pedido uma vez por dia, como as páginas da API."""
    destino = Path(pasta) / "loja.html"
    if destino.exists():
        registro.info("já tenho %s, não peço de novo", destino)
        return destino.read_text(encoding="utf-8")
    resposta = httpx.get(PAGINA_DA_LOJA, headers={**cabecalhos(), "Accept": "text/html"}, timeout=30)
    time.sleep(PAUSA)
    if resposta.status_code != 200:
        registro.warning("a página da loja respondeu %s; a conferência segue só com o total da API", resposta.status_code)
        return None
    parcial = destino.with_suffix(".parcial")
    parcial.write_bytes(resposta.content)
    parcial.replace(destino)  # como as páginas: o arquivo só existe inteiro
    return resposta.text


def total_da_pagina(html):
    """O total que a página da loja traz no bloco __NEXT_DATA__, o estado que o Next.js manda junto com o HTML."""
    bloco = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not bloco:
        return None
    estado = json.loads(bloco.group(1))
    dados = json.loads(estado["props"]["pageProps"]["data"])  # um JSON guardado dentro de um texto
    return dados["catalogServer"]["meta"]["totalItemsCount"]


def anotar(linha, destino=REGISTRO):
    """Grava a conferência em dados/conferencia.csv, uma linha por dia. Conferir de novo o mesmo dia troca a linha dele."""
    linhas = []
    if destino.exists():
        with destino.open(encoding="utf-8", newline="") as arquivo:
            linhas = [antiga for antiga in csv.DictReader(arquivo) if antiga["dia"] != linha["dia"]]
    linhas.append(linha)
    with destino.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        escritor.writeheader()
        escritor.writerows(sorted(linhas, key=lambda item: item["dia"]))


def barrar(pasta):
    """Tira as placas da pasta do dia e guarda em dados/barrados/, com a hora no nome. Devolve o caminho novo.
    Só os arquivos da raiz vão: as subpastas das outras categorias, que a conferência não mede, ficam onde estão, para a
    rodada seguinte não pedir de novo as páginas delas (poupa uns 27 pedidos à loja). Sem subpastas, a pasta do dia some, e a
    próxima rodada do mesmo dia não acha a pasta e coleta tudo de novo."""
    pasta = Path(pasta)
    BARRADOS.mkdir(parents=True, exist_ok=True)
    destino = BARRADOS / f"{pasta.name}-{datetime.now():%H%M%S}"
    destino.mkdir()
    for arquivo in pasta.iterdir():
        if arquivo.is_file():
            arquivo.rename(destino / arquivo.name)
    if not any(pasta.iterdir()):
        pasta.rmdir()
    return destino


def conferir(pasta=None):
    pasta = pasta or pasta_do_dia()
    produtos = ler_dia(pasta)
    ids = Counter(produto["id"] for produto in produtos)
    repetidos = {produto_id: vezes for produto_id, vezes in ids.items() if vezes > 1}
    declarado = total_declarado(pasta)
    registro.info("coleta: %s produtos lidos, %s diferentes; a API declara %s", len(produtos), len(ids), declarado)
    registro.info("repetidos entre páginas: %s", ", ".join(f"{i} ({n} vezes)" for i, n in repetidos.items()) or "nenhum")
    html = pagina_da_loja(pasta)
    loja = total_da_pagina(html) if html else None
    registro.info("a página da loja mostra %s produtos", loja)
    cobertura = len(ids) / declarado
    registro.info("cobertura: %s de %s, %.1f%%; faltaram %s", len(ids), declarado, cobertura * 100, declarado - len(ids))
    anotar({"dia": Path(pasta).name, "lidos": len(produtos), "diferentes": len(ids), "repetidos": len(repetidos),
            "declarado": declarado, "loja": loja, "cobertura": f"{cobertura:.3f}"})
    if cobertura < COBERTURA_MINIMA:
        if Path(pasta).name != str(date.today()):  # um dia que passou não se coleta de novo: a pasta fica onde está
            raise RuntimeError(f"A cobertura de {Path(pasta).name} ficou em {cobertura * 100:.1f}%, abaixo de "
                               f"{COBERTURA_MINIMA * 100:.0f}%. O dia já passou: a pasta fica onde está.")
        destino = barrar(pasta)
        raise RuntimeError(f"A cobertura ficou em {cobertura * 100:.1f}%, abaixo de {COBERTURA_MINIMA * 100:.0f}%. "
                           f"Nada foi publicado. A coleta foi para {destino}; rode de novo para coletar o dia outra vez.")
    (Path(pasta) / SELO).write_text(f"{cobertura:.3f}\n", encoding="utf-8")  # o dia está inteiro: pode entrar no histórico
    return len(ids)


if __name__ == "__main__":
    conferir(pasta_do_dia(sys.argv[1]) if sys.argv[1:] else None)
