"""Recebe os alertas que o Alertmanager manda (webhook) e escreve cada um no terminal e em avisos.log, ao lado dos
avisos do fluxo.py. Deixe ligado num terminal: uv run python alertas/receptor.py

Escuta em 0.0.0.0, todas as interfaces, porque no Linux o Alertmanager, de dentro do Docker, chega pela ponte do
Docker e não pelo 127.0.0.1. Numa rede que não é sua, desligue quando não estiver usando."""

import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

PORTA = int(sys.argv[1]) if sys.argv[1:] else 5001


class Receptor(BaseHTTPRequestHandler):
    def do_POST(self):
        corpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        agora = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
        linhas = [f"{agora} ALERTA ({corpo['status']}, {len(corpo['alerts'])} no grupo {corpo['groupLabels']})"]
        for alerta in corpo["alerts"]:
            nota = alerta["annotations"]
            linhas.append(f"{agora}   {alerta['status']:8} {alerta['labels']['alertname']}: {nota.get('resumo', '')}"
                          f" (o que fazer: {nota.get('oque_fazer', 'runbook.md')})")
        print("\n".join(linhas), flush=True)
        with open("avisos.log", "a", encoding="utf-8") as arquivo:
            arquivo.write("\n".join(linhas) + "\n")
        self.send_response(200)
        self.end_headers()

    def log_message(self, *args):  # sem a linha de acesso do http.server para cada pedido
        pass


if __name__ == "__main__":
    print(f"esperando alertas em http://0.0.0.0:{PORTA}/ (Ctrl+C para parar)", flush=True)
    HTTPServer(("0.0.0.0", PORTA), Receptor).serve_forever()
