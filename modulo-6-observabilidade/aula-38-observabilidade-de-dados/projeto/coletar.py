"""Pede à API de catálogo da Kabum, a mesma que a página da categoria usa, as placas de vídeo, página por página.

Cada resposta vai para o disco como veio, numa pasta com o dia da coleta. O que já está guardado hoje não é pedido de novo."""

import json
import logging
import os
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from observabilidade import metricas

load_dotenv()

# A API da loja. No .env, KABUM_API troca o endereço pela loja de ensaio (ensaio/loja.py), na sua máquina.
API = os.getenv("KABUM_API", "https://servicespub.prod.api.aws.grupokabum.com.br")
CATEGORIA = "/catalog/v2/products-by-category/hardware/placa-de-video-vga"
TAMANHO = 120  # produtos por página, o máximo que a API aceita; o mesmo em todos os pedidos
PAUSA = 3.0  # segundos de espera depois de cada pedido
LIMITE_PAGINAS = 20  # um teto: a categoria tinha 4 páginas em 14/11/2026

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
    inicio = time.perf_counter()
    resposta = metricas.pedir(API + caminho, headers=cabecalhos(), timeout=30)
    duracao_ms = round((time.perf_counter() - inicio) * 1000)
    registro.info("pedi %s: %s em %s ms", caminho, resposta.status_code, duracao_ms,
                  extra={"status": resposta.status_code, "duracao_ms": duracao_ms})
    time.sleep(PAUSA)
    if resposta.status_code >= 500:
        # 500, 502, 503: um problema da loja, que passa. Um erro comum, e o orquestrador tenta de novo.
        registro.warning("a loja respondeu %s: vale tentar de novo", resposta.status_code, extra={"status": resposta.status_code})
        raise RuntimeError(f"{caminho} respondeu {resposta.status_code}: erro da loja, vale tentar de novo")
    tipo = resposta.headers.get("content-type", "")
    if resposta.status_code != 200 or "json" not in tipo:
        # 403, 429 ou uma página de desafio em HTML no lugar do JSON: o site disse não. O programa para aqui.
        registro.error("a loja recusou: %s respondeu %s (%s)", caminho, resposta.status_code, tipo, extra={"status": resposta.status_code})
        Path("dados").mkdir(exist_ok=True)
        Path("dados/ultima_recusa.html").write_bytes(resposta.content)
        raise SystemExit(f"{caminho} respondeu {resposta.status_code} ({tipo}). A resposta está em dados/ultima_recusa.html. Pare e leia.")
    return resposta.content


def coletar_pagina(numero, caminho, pasta):
    """Devolve o JSON da página, do disco se já foi baixada hoje, ou pedindo à API."""
    destino = pasta / f"pagina-{numero:03d}.json"
    if destino.exists():
        registro.debug("já tenho %s, não peço de novo", destino)
        return json.loads(destino.read_text(encoding="utf-8"))
    conteudo = pedir(caminho)
    pasta.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_suffix(".parcial")
    parcial.write_bytes(conteudo)
    parcial.replace(destino)  # o nome troca de uma vez: uma queda no meio da gravação não deixa uma página pela metade
    registro.info("baixei a página %s: %s bytes em %s", numero, len(conteudo), destino)
    return json.loads(conteudo)


def endereco(numero):
    """O endereço da página, sempre com o mesmo tamanho de página."""
    return f"{CATEGORIA}?page_number={numero}&page_size={TAMANHO}"


def coletar(pasta=None):
    """Pede a página 1, lê quantas páginas a categoria tem e pede as outras, uma por vez.

    O links.next da API não é seguido: na rodada de 14/11/2026 ele trocou o tamanho da página no meio do caminho,
    e as páginas seguintes repetiram produtos já baixados (saidas/armadilha-links-next.txt)."""
    pasta = pasta or pasta_do_dia()
    primeira = coletar_pagina(1, endereco(1), pasta)
    total_paginas = primeira["meta"]["total_pages_count"]
    if total_paginas > LIMITE_PAGINAS:
        raise SystemExit(f"A categoria diz ter {total_paginas} páginas, acima do teto de {LIMITE_PAGINAS}. Confira antes de seguir.")
    for numero in range(2, total_paginas + 1):
        coletar_pagina(numero, endereco(numero), pasta)
    registro.info("coleta do dia: %s páginas em %s", total_paginas, pasta)
    return total_paginas


if __name__ == "__main__":
    coletar()
