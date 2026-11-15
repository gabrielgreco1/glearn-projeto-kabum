"""Gancho PostToolUse: depois de cada Edit ou Write num arquivo .py, roda o lint rápido (ruff, só erros que quebram)
e os testes. Se algo falha, sai com código 2: o arquivo já mudou, mas o modelo lê o erro no stderr e conserta.
Só biblioteca padrão: roda igual no macOS, no Linux e no Windows."""

import json
import subprocess
import sys


def rodar(comando):
    feito = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return feito.returncode, (feito.stdout + feito.stderr).strip()


def main():
    pedido = json.load(sys.stdin)
    arquivo = str((pedido.get("tool_input") or {}).get("file_path", ""))
    if not arquivo.endswith(".py"):
        sys.exit(0)
    codigo, saida = rodar(["uvx", "ruff", "check", "--select", "E9,F63,F7,F82", "--quiet", arquivo])
    if codigo != 0:
        print(f"O lint achou erro em {arquivo}:\n{saida[-1500:]}", file=sys.stderr)
        sys.exit(2)
    codigo, saida = rodar(["uv", "run", "pytest", "-q", "-x", "--no-header", "-p", "no:cacheprovider"])
    if codigo != 0:
        print(f"Os testes falharam depois da edição de {arquivo}:\n{saida[-1500:]}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
