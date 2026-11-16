"""A loja de ensaio: um servidor na sua máquina que responde como a API da Kabum, com as páginas de um dia que você já
coletou. Serve para rodar o projeto quantas vezes quiser sem pedir nada à loja de verdade, e para provocar falhas de
propósito: lentidão, recusa (429) depois de alguns pedidos, erro 503 e preço em texto. Na primeira vez, as páginas do
dia são copiadas para dados/ensaio/<dia>; a loja serve dessa cópia, e a pasta do dia no bronze pode ser refeita.

Uso: uv run python ensaio/loja.py 2026-11-16                     as páginas desse dia, como vieram
     uv run python ensaio/loja.py 2026-11-16 --atraso 2           cada resposta da API demora 2 s
     uv run python ensaio/loja.py 2026-11-16 --atraso 6 --so-pagina 3   só a página 3 demora 6 s
     uv run python ensaio/loja.py 2026-11-16 --recusar-depois 2   do terceiro pedido em diante, 429
     uv run python ensaio/loja.py 2026-11-16 --erro 503           toda resposta da API é 503
     uv run python ensaio/loja.py 2026-11-16 --preco-texto 0.4    40% dos produtos com o preço como "R$ 1.299,90"
     uv run python ensaio/loja.py 2026-11-16 --sem-fabricante     o campo manufacturer some de todos os produtos
     uv run python ensaio/loja.py 2026-11-16 --campo-novo         um campo a mais em cada produto (selo_black)
     uv run python ensaio/loja.py 2026-11-16 --metade             a categoria encolhe para as duas primeiras páginas
Deixe a loja ligada num terminal e, em outro, rode o projeto contra ela: uv run python ensaio/rodada.py
"""

import argparse
import json
import random
import shutil
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

opcoes = argparse.ArgumentParser(description="A loja de ensaio do projeto Kabum")
opcoes.add_argument("dia", help="o dia de dados/bronze/ que a loja serve, como 2026-11-16")
opcoes.add_argument("--porta", type=int, default=8099)
opcoes.add_argument("--atraso", type=float, default=0.0, help="segundos de espera antes de cada resposta da API")
opcoes.add_argument("--so-pagina", type=int, default=None, help="o atraso vale só para esta página")
opcoes.add_argument("--recusar-depois", type=int, default=None, help="depois de N pedidos à API, responde 429")
opcoes.add_argument("--erro", type=int, default=None, help="responde este status em todo pedido à API, como 503")
opcoes.add_argument("--preco-texto", type=float, default=0.0, help="fração dos produtos com o preço em texto")
opcoes.add_argument("--sem-fabricante", action="store_true", help="tira o campo manufacturer de todos os produtos")
opcoes.add_argument("--campo-novo", action="store_true", help="acrescenta o campo selo_black a todos os produtos")
opcoes.add_argument("--metade", action="store_true", help="a API passa a ter só as duas primeiras páginas")
ARGS = opcoes.parse_args()
ORIGEM = Path("dados/bronze") / ARGS.dia
PASTA = Path("dados/ensaio") / ARGS.dia  # a cópia que a loja serve
pedidos = 0
trava = threading.Lock()


def em_texto(valor):
    """1299.9 vira "R$ 1.299,90", como a página mostra para gente."""
    return "R$ " + f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def pagina(numero):
    conteudo = (PASTA / f"pagina-{numero:03d}.json").read_bytes()
    if not (ARGS.preco_texto or ARGS.sem_fabricante or ARGS.campo_novo or ARGS.metade):
        return conteudo
    dados = json.loads(conteudo)
    if ARGS.metade:  # a API diz que a categoria tem 2 páginas, com o total das duas
        dados["meta"]["total_pages_count"] = 2
        dados["meta"]["total_items_count"] = sum(len(json.loads((PASTA / f"pagina-{n:03d}.json").read_bytes())["data"]) for n in (1, 2))
    sorteio = random.Random(numero)  # a mesma semente em toda rodada: os mesmos produtos estragam
    for item in dados["data"]:
        atributos = item["attributes"]
        if ARGS.preco_texto and sorteio.random() < ARGS.preco_texto:
            atributos["price"] = em_texto(atributos["price"])
            atributos["price_with_discount"] = em_texto(atributos["price_with_discount"])
        if ARGS.sem_fabricante:
            atributos.pop("manufacturer", None)
        if ARGS.campo_novo:
            atributos["selo_black"] = True
    return json.dumps(dados).encode("utf-8")


class Loja(BaseHTTPRequestHandler):
    def responder(self, status, tipo, corpo):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        global pedidos
        endereco = urlparse(self.path)
        numero = int(parse_qs(endereco.query).get("page_number", ["1"])[0])
        if ARGS.so_pagina in (None, numero) and endereco.path != "/loja":
            time.sleep(ARGS.atraso)
        if endereco.path == "/loja":
            return self.responder(200, "text/html; charset=utf-8", (PASTA / "loja.html").read_bytes())
        with trava:
            pedidos += 1
            vez = pedidos
        if ARGS.erro:
            return self.responder(ARGS.erro, "text/html", b"<h1>erro de ensaio</h1>")
        if ARGS.recusar_depois is not None and vez > ARGS.recusar_depois:
            return self.responder(429, "text/html", b"<h1>Too Many Requests</h1>")
        self.responder(200, "application/json", pagina(numero))


if __name__ == "__main__":
    if not PASTA.exists():
        if not (ORIGEM / "pagina-001.json").exists():
            raise SystemExit(f"Não achei {ORIGEM}/pagina-001.json. Use um dia que você já coletou: ls dados/bronze")
        shutil.copytree(ORIGEM, PASTA)
    print(f"loja de ensaio em http://127.0.0.1:{ARGS.porta}, com as páginas de {PASTA} (Ctrl+C para parar)")
    ThreadingHTTPServer(("127.0.0.1", ARGS.porta), Loja).serve_forever()
