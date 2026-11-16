"""Desfaz o incidente que o provocar.py sorteou, diz qual foi e roda o projeto de novo, contra a loja de ensaio sem
falha: o painel volta ao normal e os alertas se resolvem.

Uso: uv run python incidente/desfazer.py"""

import os
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
SORTEIO = Path("incidente/.sorteio")
NOMES = {"recusa": "a loja recusou com 429 depois de dois pedidos",
         "senha": "a senha do banco foi trocada, e o .env ficou com a antiga",
         "preco": "a API mandou o preço como texto (\"R$ 1.299,90\") em 40% dos produtos"}


def main():
    if not SORTEIO.exists():
        raise SystemExit("Não há incidente aberto.")
    falha = SORTEIO.read_text(encoding="utf-8").strip()
    if falha == "senha":
        subprocess.run(["docker", "compose", "exec", "-T", "banco", "psql", "-U", "postgres", "-c",
                        f"ALTER USER postgres PASSWORD '{os.environ['POSTGRES_PASSWORD']}'"], check=True, capture_output=True)
    porta = os.getenv("LOJA_PORTA", "8099")
    loja = subprocess.Popen([sys.executable, "ensaio/loja.py", str(date.today()), "--porta", porta],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(2)
        subprocess.run([sys.executable, "ensaio/rodada.py", porta], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        loja.terminate()
    SORTEIO.unlink()
    print(f"O incidente foi: {NOMES[falha]}. Desfeito, e o projeto rodou de novo às {time.strftime('%H:%M:%S')}.")


if __name__ == "__main__":
    main()
