"""De onde veio este preço? Dado o id de um produto, mostra o caminho de volta: a linha no banco e a execução que a
gravou, o arquivo do bronze e a página da API de onde o produto saiu, e a execução que baixou essa página, com o
trace_id do pedido. As duas execuções podem ser diferentes: a das 18h carrega o que a das 6h baixou.

Uso: uv run python linhagem.py 506094               o dia mais novo do produto
     uv run python linhagem.py 506094 2026-11-16"""

import json
import sys
from pathlib import Path

from banco import conectar
from coletar import endereco, pasta_do_dia
from observabilidade.logs import ARQUIVO

LINHA = """
SELECT p.dia, p.titulo, p.preco_final, p.execucao_id, c.id, c.feita_em
FROM precos p LEFT JOIN cargas c ON c.dia = p.dia AND c.execucao_id = p.execucao_id
WHERE p.id = %s AND (%s::date IS NULL OR p.dia = %s::date)
ORDER BY p.dia DESC LIMIT 1
"""


def pagina_do_produto(pasta, produto):
    """O arquivo do bronze em que o produto veio, ou None."""
    for arquivo in sorted(Path(pasta).glob("pagina-*.json")):
        if any(int(item["id"]) == produto for item in json.loads(arquivo.read_text(encoding="utf-8"))["data"]):
            return arquivo
    return None


def quem_baixou(arquivo):
    """A última linha de log que diz ter baixado este arquivo: o id da execução, a hora e o trace_id."""
    achada = None
    if ARQUIVO.exists():
        with ARQUIVO.open(encoding="utf-8") as linhas:
            for texto in linhas:
                linha = json.loads(texto)
                if linha["msg"].startswith("baixei a página") and linha["msg"].endswith(str(arquivo)):
                    achada = linha
    return achada


def main(produto, dia=None):
    with conectar() as conexao:
        achada = conexao.execute(LINHA, [produto, dia, dia]).fetchone()
    if not achada:
        raise SystemExit(f"O produto {produto} não está na tabela precos{' no dia ' + dia if dia else ''}.")
    dia, titulo, preco, gravou, carga, feita_em = achada
    reais = f"{preco / 100:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    print(f"banco     precos: {dia} · {titulo[:60]} · R$ {reais}")
    print(f"          gravada pela execução {gravou or '(sem id: carga de antes da coluna execucao_id)'}"
          + (f", carga {carga} às {feita_em.astimezone():%H:%M:%S}" if carga else ""))
    arquivo = pagina_do_produto(pasta_do_dia(dia), produto)
    if not arquivo:
        raise SystemExit(f"          o bronze de {dia} não tem o produto (a pasta foi barrada ou apagada?)")
    numero = int(arquivo.stem.split("-")[1])
    print(f"bronze    {arquivo}, página {numero} da API: {endereco(numero)}")
    baixou = quem_baixou(arquivo)
    if baixou:
        print(f"log       baixada pela execução {baixou['execucao_id']} em {baixou['ts']} (tentativa {baixou['tentativa']})")
        print(f"trace     {baixou.get('trace_id') or '(sem trace: antes da aula de traces)'}")
    else:
        print(f"log       nenhuma linha de {ARQUIVO} diz ter baixado esse arquivo")


if __name__ == "__main__":
    if not sys.argv[1:]:
        raise SystemExit(__doc__)
    main(int(sys.argv[1]), sys.argv[2] if sys.argv[2:] else None)
