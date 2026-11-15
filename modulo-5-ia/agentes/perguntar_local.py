"""O caminho de 8 GB: sem agente, só o modelo local lendo o que importa. Junta o diff do último commit e a falha dos
testes, manda ao Ollama e imprime a resposta, o tempo e os tokens. Quem edita o código é você.

    uv run --no-project python perguntar_local.py ../projeto-kabum llama3.2:3b HEAD

Só biblioteca padrão; roda igual no macOS, no Linux e no Windows (Ollama aberto, na porta 11434)."""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

pasta = Path(sys.argv[1]).resolve()
modelo = sys.argv[2] if len(sys.argv) > 2 else "llama3.2:3b"
commit = sys.argv[3] if len(sys.argv) > 3 else "HEAD"  # o commit suspeito


def rodar(*comando):
    return subprocess.run(comando, cwd=pasta, capture_output=True, text=True, encoding="utf-8").stdout


diff = rodar("git", "show", "--format=%s", commit)
falha = rodar("uv", "run", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider")[-2500:]
pedido = (f"Um commit quebrou testes de um projeto Python.\n\nO commit:\n{diff}\n\nA falha:\n{falha}\n\n"
          "Em português e em no máximo 6 linhas: qual linha do commit causa a falha e como desfazer. Não mude o teste.")
corpo = json.dumps({"model": modelo, "messages": [{"role": "user", "content": pedido}], "stream": False,
                    "options": {"num_ctx": 4096}}).encode()
inicio = time.time()
with urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/api/chat", corpo,
                                                   {"Content-Type": "application/json"}), timeout=600) as r:
    resposta = json.loads(r.read())
print(resposta["message"]["content"].strip())
print(f"\n{modelo}: {resposta.get('prompt_eval_count')} tokens de entrada, {resposta.get('eval_count')} de saída, "
      f"{time.time() - inicio:.1f} s")
