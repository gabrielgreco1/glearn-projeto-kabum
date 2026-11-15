"""Gancho PreToolUse: o Claude Code chama antes de cada Bash, Edit e Write, com o pedido em JSON na entrada.
Sair com código 2 barra a chamada, e o que este programa escreve no stderr volta para o modelo como motivo.
Só biblioteca padrão: roda igual no macOS, no Linux e no Windows."""

import json
import re
import sys

COMANDOS = [
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r|Remove-Item\b.*-Recurse", "apagar pasta inteira"),
    (r"git\s+push\b.*(--force|-f\b)", "push forçado"),
    (r"git\s+reset\s+--hard", "reset --hard"),
    (r"docker\s+compose\s+down\b.*-v", "apagar o volume do banco"),
    (r"\b(DROP|TRUNCATE)\s+(TABLE|SCHEMA|DATABASE)\b", "apagar tabela"),
]


def regra_da_loja(texto):
    """Uma edição do coletar.py que baixa a pausa de 3 s ou tira o teto de páginas."""
    pausa = re.search(r"^PAUSA\s*=\s*([0-9.]+)", texto, re.M)
    if pausa and float(pausa.group(1)) < 3.0:
        return f"PAUSA = {pausa.group(1)}: a pausa entre pedidos à loja é de 3 segundos, no mínimo"
    if "LIMITE_PAGINAS" in texto and re.search(r"^LIMITE_PAGINAS\s*=\s*(None|0)\b", texto, re.M):
        return "LIMITE_PAGINAS sem valor: o teto de páginas por dia não sai"
    return None


def main():
    pedido = json.load(sys.stdin)
    ferramenta = pedido.get("tool_name")
    entrada = pedido.get("tool_input") or {}
    if ferramenta == "Bash":
        comando = entrada.get("command", "")
        for padrao, nome in COMANDOS:
            if re.search(padrao, comando, re.I):
                print(f"Barrado pelo gancho do projeto ({nome}): {comando[:120]}. Peça à pessoa para rodar, se for mesmo preciso.", file=sys.stderr)
                sys.exit(2)
    elif ferramenta in ("Edit", "Write") and str(entrada.get("file_path", "")).replace("\\", "/").endswith("coletar.py"):
        texto = entrada.get("new_string") or entrada.get("content") or ""
        motivo = regra_da_loja(texto)
        if motivo:
            print(f"Barrado pelo gancho do projeto: {motivo}. É regra do projeto (CLAUDE.md, 'A loja').", file=sys.stderr)
            sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
