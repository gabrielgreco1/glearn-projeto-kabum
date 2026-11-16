"""Uma rodada do projeto contra a loja de ensaio (ensaio/loja.py, ligada em outro terminal): a pasta de hoje no bronze
é refeita, pedindo tudo à loja de ensaio, e o fluxo roda inteiro, como às 6h. A loja de verdade não recebe nada.

Uso: uv run python ensaio/rodada.py           a loja de ensaio na porta 8099
     uv run python ensaio/rodada.py 8100      em outra porta"""

import os
import shutil
import sys
from datetime import date
from pathlib import Path

porta = sys.argv[1] if sys.argv[1:] else "8099"
os.environ["KABUM_API"] = f"http://127.0.0.1:{porta}"  # antes de importar o projeto: o coletar.py lê o endereço no import
os.environ["KABUM_LOJA"] = f"http://127.0.0.1:{porta}/loja"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # a pasta do projeto, para importar o fluxo.py

hoje = Path("dados/bronze") / str(date.today())
if hoje.exists() and not (Path("dados/ensaio") / hoje.name).exists():
    raise SystemExit(f"{hoje} não tem cópia em dados/ensaio. Ligue a loja de ensaio com o dia de hoje antes: "
                     f"uv run python ensaio/loja.py {hoje.name}")
shutil.rmtree(hoje, ignore_errors=True)  # a cópia está em dados/ensaio: a loja de ensaio devolve as mesmas páginas

from fluxo import projeto_kabum  # noqa: E402

projeto_kabum()
