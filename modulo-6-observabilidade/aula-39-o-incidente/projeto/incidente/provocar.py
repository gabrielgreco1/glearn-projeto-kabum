"""Provoca um incidente no Kabum, sorteado entre três falhas que você já conhece, e roda o projeto uma vez com ela,
contra a loja de ensaio. Você não sabe qual foi: investigue só pelo Grafana (painéis, Explore com Loki e Tempo) e
pelos alertas em avisos.log, sem abrir o código nem este arquivo antes de terminar.

Antes: o banco e a observabilidade de pé (docker compose up -d --wait), o receptor de alertas ligado num terminal
(uv run python alertas/receptor.py) e a loja de ensaio desligada (este programa liga a dele).
Uso: uv run python incidente/provocar.py
Depois de achar a causa: uv run python incidente/desfazer.py"""

import os
import random
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

SORTEIO = Path("incidente/.sorteio")  # qual foi: só o desfazer.py lê
FALHAS = {
    "recusa": ["--recusar-depois", "2"],  # a loja passa a recusar com 429 depois de dois pedidos
    "senha": [],  # alguém trocou a senha do banco, e o .env ficou com a antiga
    "preco": ["--preco-texto", "0.4"],  # a API passa a mandar o preço como texto em 40% dos produtos
}


def compose(*args):
    return subprocess.run(["docker", "compose", *args], check=True, capture_output=True, text=True)


def main():
    if SORTEIO.exists():
        raise SystemExit("Já há um incidente aberto. Termine a investigação e rode: uv run python incidente/desfazer.py")
    falha = os.getenv("INCIDENTE") or random.choice(list(FALHAS))  # INCIDENTE=recusa escolhe; só para a prova do curso
    porta = os.getenv("LOJA_PORTA", "8099")
    hoje = str(date.today())
    if not (Path("dados/ensaio") / hoje).exists():
        raise SystemExit(f"Falta a cópia de hoje para a loja de ensaio. Rode uma vez: uv run python ensaio/loja.py {hoje} "
                         "(e Ctrl+C depois que ela disser que está ligada)")
    SORTEIO.write_text(falha + "\n", encoding="utf-8")
    if falha == "senha":
        compose("exec", "-T", "banco", "psql", "-U", "postgres", "-c", "ALTER USER postgres PASSWORD 'trocada-no-incidente'")
    loja = subprocess.Popen([sys.executable, "ensaio/loja.py", hoje, "--porta", porta, *FALHAS[falha]],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2)
        print(f"{time.strftime('%H:%M:%S')} incidente provocado; rodando o projeto como às 6h...", flush=True)
        subprocess.run([sys.executable, "ensaio/rodada.py", porta], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        loja.terminate()
    print(f"{time.strftime('%H:%M:%S')} pronto. Espere o alerta no terminal do receptor e abra o Grafana.")


if __name__ == "__main__":
    main()
