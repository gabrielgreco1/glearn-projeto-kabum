"""Pede à API de catálogo da Kabum, a mesma que a página da categoria usa, as placas de vídeo, página por página.

Cada resposta vai para o disco como veio, numa pasta com o dia da coleta. O que já está guardado hoje não é pedido de novo."""

import json
import logging
import os
import time
from datetime import date
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

USER_AGENT = os.getenv("KABUM_USER_AGENT")
if not USER_AGENT:
    raise SystemExit("Falta KABUM_USER_AGENT no arquivo .env. Copie o .env.example para .env e preencha.")

API = "https://servicespub.prod.api.aws.grupokabum.com.br"
CATEGORIA = "/catalog/v2/products-by-category/hardware/placa-de-video-vga"
TAMANHO = 120  # produtos por página, o máximo que a API aceita; o mesmo em todos os pedidos
CABECALHOS = {"User-Agent": USER_AGENT, "Accept": "application/json"}
PAUSA = 3.0  # segundos de espera depois de cada pedido

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("httpx").setLevel(logging.WARNING)
registro = logging.getLogger("kabum")


def pasta_do_dia(dia=None):
    """dados/bronze/2026-11-14/: uma pasta por dia de coleta."""
    return Path("dados/bronze") / f"{dia or date.today()}"


def pedir(caminho):
    """Pede um endereço da API e devolve o JSON. Para em qualquer resposta que não seja um JSON com status 200."""
    resposta = httpx.get(API + caminho, headers=CABECALHOS, timeout=30)
    time.sleep(PAUSA)
    tipo = resposta.headers.get("content-type", "")
    if resposta.status_code != 200 or "json" not in tipo:
        # 403, 429 ou uma página de desafio em HTML no lugar do JSON: o site disse não. O programa para aqui.
        Path("dados").mkdir(exist_ok=True)
        Path("dados/ultima_recusa.html").write_bytes(resposta.content)
        raise SystemExit(f"{caminho} respondeu {resposta.status_code} ({tipo}). A resposta está em dados/ultima_recusa.html. Pare e leia.")
    return resposta.content


def coletar_pagina(numero, caminho, pasta):
    """Devolve o JSON da página, do disco se já foi baixada hoje, ou pedindo à API."""
    destino = pasta / f"pagina-{numero:03d}.json"
    if destino.exists():
        registro.info("já tenho %s, não peço de novo", destino)
        return json.loads(destino.read_text(encoding="utf-8"))
    conteudo = pedir(caminho)
    pasta.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(conteudo)
    registro.info("baixei a página %s: %s bytes em %s", numero, len(conteudo), destino)
    return json.loads(conteudo)


def endereco(numero):
    """O endereço da página, sempre com o mesmo tamanho de página."""
    return f"{CATEGORIA}?page_number={numero}&page_size={TAMANHO}"


def coletar(pasta=None):
    """Por enquanto, só a página 1. As outras vêm na aula 4."""
    pasta = pasta or pasta_do_dia()
    primeira = coletar_pagina(1, endereco(1), pasta)
    registro.info("a categoria tem %s produtos em %s páginas", primeira["meta"]["total_items_count"], primeira["meta"]["total_pages_count"])


if __name__ == "__main__":
    coletar()
