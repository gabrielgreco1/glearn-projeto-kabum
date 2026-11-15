"""O relatório de qualidade de cada rodada e a decisão de publicar ou não a silver e a gold.

Um arquivo por dia em dados/qualidade/, com o que entrou, o que saiu e por quê. Rodar de novo no mesmo dia troca o arquivo."""

import json
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from coletar import registro
from conferir import REGISTRO as CONFERENCIA
from validar import REGRAS

PASTA = Path("dados/qualidade")
LIMITE_ERRO = 0.02  # uma regra de erro que derruba mais de 2% das linhas é sinal de que a fonte mudou, não de um produto ruim


def cobertura_do_dia(dia, conferencia=CONFERENCIA):
    """A cobertura que o conferir.py anotou para o dia, ou None se o dia não foi conferido."""
    if not Path(conferencia).exists():
        return None
    linhas = pl.read_csv(conferencia).filter(pl.col("dia").cast(pl.String) == str(dia))
    return linhas["cobertura"][0] if linhas.height else None


def decidir(rel):
    """Publica quando há linhas válidas e nenhuma regra de erro passou do limite. Devolve (publicar, motivo)."""
    if rel["validos"] == 0:
        return False, "nenhuma linha válida"
    for regra, n in rel["rejeitados_por_regra"].items():
        if n / rel["lidos"] > LIMITE_ERRO:
            return False, f"{regra}: {n / rel['lidos']:.1%} das linhas rejeitadas, acima de {LIMITE_ERRO:.0%}"
    return True, f"nenhuma regra de erro acima de {LIMITE_ERRO:.0%}"


def relatorio(tabela, validos, rejeitados, falhas):
    """Junta os números da rodada num dicionário, com a decisão no fim."""
    dia = tabela["dia"].max()
    rel = {
        "dia": str(dia),
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dias_na_silver": tabela["dia"].n_unique(),
        "lidos": tabela.height,
        "validos": validos.height,
        "rejeitados": rejeitados["linha"].n_unique(),
        "rejeitados_por_regra": {r["id"]: falhas[r["id"]] for r in REGRAS if r["severidade"] == "erro"},
        "avisos_por_regra": {r["id"]: falhas[r["id"]] for r in REGRAS if r["severidade"] == "aviso"},
        "cobertura": cobertura_do_dia(dia),
    }
    rel["publicado"], rel["motivo"] = decidir(rel)
    return rel


def gravar(rel):
    PASTA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / f"{rel['dia']}.json"
    destino.write_text(json.dumps(rel, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registro.info("relatório de qualidade em %s: %s", destino, rel["motivo"])
    return destino
