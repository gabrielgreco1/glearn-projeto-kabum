"""Pede à API de catálogo da Kabum, a mesma que a página da categoria usa, as placas de vídeo, os SSDs, as memórias RAM
e os processadores, página por página.

Cada resposta vai para o disco como veio, numa pasta com o dia da coleta: as placas na raiz da pasta, as outras
categorias numa subpasta cada uma. O que já está guardado hoje não é pedido de novo."""

import json
import logging
import os
import time
from datetime import date
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

API = "https://servicespub.prod.api.aws.grupokabum.com.br"
PREFIXO = "/catalog/v2/products-by-category/"
CATEGORIA = PREFIXO + "hardware/placa-de-video-vga"
# As categorias e a subpasta de cada uma dentro da pasta do dia. As placas ficam na raiz ("" = sem subpasta): o histórico,
# a silver e o banco leem dali. Nada lê ainda as subpastas ssd/, memoria/ e processador/.
CATEGORIAS = {
    "placa-de-video": (CATEGORIA, ""),
    "ssd": (PREFIXO + "hardware/ssd-2-5", "ssd"),
    "memoria": (PREFIXO + "hardware/memoria-ram", "memoria"),
    "processador": (PREFIXO + "hardware/processadores", "processador"),
}
TAMANHO = 120  # produtos por página, o máximo que a API aceita; o mesmo em todos os pedidos
PAUSA = 3.0  # segundos de espera depois de cada pedido
LIMITE_PAGINAS = 40  # o teto por dia, somando as quatro categorias: em 15/11/2026 eram cerca de 32 páginas

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
logging.getLogger("httpx").setLevel(logging.WARNING)
registro = logging.getLogger("kabum")
registro.setLevel(logging.INFO)  # o nível fica no nosso registro: o Prefect troca o do logging inteiro para WARNING


def cabecalhos():
    """O User-Agent, lido do .env na hora do pedido, e não no import: quem só importa este arquivo, como os testes no
    GitHub, não precisa do .env."""
    contato = os.getenv("KABUM_USER_AGENT")
    if not contato:
        raise SystemExit("Falta KABUM_USER_AGENT no arquivo .env. Copie o .env.example para .env e preencha.")
    return {"User-Agent": contato, "Accept": "application/json"}


def pasta_do_dia(dia=None):
    """dados/bronze/2026-11-14/: uma pasta por dia de coleta."""
    return Path("dados/bronze") / f"{dia or date.today()}"


def pedir(caminho):
    """Pede um endereço da API e devolve os bytes da resposta. Um 5xx sobe como erro comum, para ser tentado de novo;
    qualquer outra resposta que não seja um JSON com status 200 para o programa."""
    resposta = httpx.get(API + caminho, headers=cabecalhos(), timeout=30)
    time.sleep(PAUSA)
    if resposta.status_code >= 500:
        # 500, 502, 503: um problema da loja, que passa. Um erro comum, e o orquestrador tenta de novo.
        raise RuntimeError(f"{caminho} respondeu {resposta.status_code}: erro da loja, vale tentar de novo")
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
    parcial = destino.with_suffix(".parcial")
    parcial.write_bytes(conteudo)
    parcial.replace(destino)  # o nome troca de uma vez: uma queda no meio da gravação não deixa uma página pela metade
    registro.info("baixei a página %s: %s bytes em %s", numero, len(conteudo), destino)
    return json.loads(conteudo)


def endereco(numero, categoria=CATEGORIA):
    """O endereço da página, sempre com o mesmo tamanho de página."""
    return f"{categoria}?page_number={numero}&page_size={TAMANHO}"


def coletar(pasta=None):
    """Pede a página 1 de cada categoria, soma quantas páginas elas têm e, só se a soma couber no teto, pede as outras,
    uma por vez. Devolve o total de páginas do dia.

    O teto vale para as quatro categorias juntas e é conferido antes de qualquer página além da primeira de cada uma:
    se estourar, o programa para depois de 4 pedidos.

    O links.next da API não é seguido: na rodada de 14/11/2026 ele trocou o tamanho da página no meio do caminho,
    e as páginas seguintes repetiram produtos já baixados (saidas/armadilha-links-next.txt)."""
    pasta = Path(pasta or pasta_do_dia())
    totais = {}
    for nome, (caminho, subpasta) in CATEGORIAS.items():
        primeira = coletar_pagina(1, endereco(1, caminho), pasta / subpasta)
        totais[nome] = primeira["meta"]["total_pages_count"]
    total_paginas = sum(totais.values())
    if total_paginas > LIMITE_PAGINAS:
        raise SystemExit(f"As categorias dizem ter {total_paginas} páginas juntas ({totais}), acima do teto de "
                         f"{LIMITE_PAGINAS} por dia. Confira antes de seguir.")
    for nome, (caminho, subpasta) in CATEGORIAS.items():
        for numero in range(2, totais[nome] + 1):
            coletar_pagina(numero, endereco(numero, caminho), pasta / subpasta)
    registro.info("coleta do dia: %s páginas em %s (%s)", total_paginas, pasta, totais)
    return total_paginas


if __name__ == "__main__":
    coletar()
