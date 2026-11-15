"""Dispara as issues do backlog com o Claude Code sem tela (claude -p), cada uma na sua worktree, com o modelo, o
esforço, o teto de turnos e o teto em dólar escolhidos por issue. Lê o JSON de cada execução e grava a tabela de custo.

    uv run python orquestrar.py tarefas.json          # roda as tarefas, no máximo 2 ao mesmo tempo
    uv run python orquestrar.py tarefas.json --ver    # só mostra os comandos, sem rodar

Só biblioteca padrão: roda igual no macOS, no Linux e no Windows (no PowerShell, o mesmo comando)."""

import csv
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

AO_MESMO_TEMPO = 2
FERRAMENTAS = ["Read", "Edit", "Write", "Grep", "Glob", "Bash(uv run pytest*)", "Bash(git status*)", "Bash(git diff*)",
               "Bash(git log*)", "Bash(git add*)", "Bash(git commit*)"]


def preparar(tarefa, base):
    """Cria a worktree da issue, numa pasta irmã do repositório, numa branch nova a partir do main."""
    repo = (base / tarefa["repo"]).resolve()
    pasta = repo.parent / f"{repo.name}-{tarefa['id']}"
    if not pasta.exists():
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", str(pasta), "-b", f"issue-{tarefa['id']}", "main"],
                       check=True)
    return pasta


def comando(tarefa, prompt):
    return ["claude", "-p", prompt, "--model", tarefa["modelo"], "--effort", tarefa["esforco"],
            "--max-turns", str(tarefa["max_turnos"]), "--max-budget-usd", str(tarefa["max_usd"]),
            "--permission-mode", "acceptEdits", "--allowedTools", *FERRAMENTAS,
            # Sem as suas configurações pessoais e sem servidor MCP que a tarefa não pediu: roda igual em toda máquina.
            "--setting-sources", "project,local", "--strict-mcp-config",
            "--output-format", "json"]


def rodar(tarefa, base):
    pasta = preparar(tarefa, base)
    issue = (base / tarefa["issue"]).read_text(encoding="utf-8")
    prompt = f"Issue do backlog do projeto. Resolva e faça o commit na branch atual:\n\n{issue}"
    inicio = time.time()
    feito = subprocess.run(comando(tarefa, prompt), cwd=pasta, capture_output=True, text=True, encoding="utf-8")
    segundos = round(time.time() - inicio)
    try:
        r = json.loads(feito.stdout)
    except json.JSONDecodeError:
        r = {"subtype": "sem_json", "result": feito.stdout[-300:] + feito.stderr[-300:]}
    testes = subprocess.run(["uv", "run", "pytest", "-q"], cwd=pasta, capture_output=True, text=True, encoding="utf-8")
    commits = subprocess.run(["git", "-C", str(pasta), "log", "--oneline", "main..HEAD"], capture_output=True, text=True,
                             encoding="utf-8").stdout.strip().splitlines()
    u = r.get("usage") or {}
    return {
        "issue": tarefa["id"], "modelo": tarefa["modelo"], "esforco": tarefa["esforco"],
        "fim": r.get("subtype"), "turnos": r.get("num_turns"), "usd": round(r.get("total_cost_usd") or 0, 4),
        "entrada": u.get("input_tokens"), "saida": u.get("output_tokens"),
        "cache_lido": u.get("cache_read_input_tokens"), "cache_gravado": u.get("cache_creation_input_tokens"),
        "segundos": segundos, "testes": testes.stdout.strip().splitlines()[-1] if testes.stdout.strip() else "?",
        "commits": len(commits), "negadas": len(r.get("permission_denials") or []),
        "aviso": feito.stderr.strip().splitlines()[0][:120] if feito.stderr.strip() else "",
    }


def main():
    arquivo = Path(sys.argv[1])
    base = arquivo.parent
    tarefas = json.loads(arquivo.read_text(encoding="utf-8"))
    if "--ver" in sys.argv:
        for t in tarefas:
            print(t["id"], " ".join(comando(t, "<issue>")))
        return
    with ThreadPoolExecutor(max_workers=AO_MESMO_TEMPO) as fila:
        linhas = list(fila.map(lambda t: rodar(t, base), tarefas))
    saida = base / "custos.csv"
    novo = not saida.exists()
    with saida.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0]))
        if novo:
            escritor.writeheader()
        escritor.writerows(linhas)
    for l in linhas:
        print(f"{l['issue']:<10} {l['modelo']:<7} {l['fim']:<24} turnos {l['turnos']}  US$ {l['usd']:<7} "
              f"{l['segundos']} s  {l['testes']}  commits {l['commits']}  negadas {l['negadas']}")
        if l["aviso"]:
            print("           aviso:", l["aviso"])
    print(f"total US$ {sum(l['usd'] for l in linhas):.4f}; a tabela está em {saida.name}")


if __name__ == "__main__":
    main()
