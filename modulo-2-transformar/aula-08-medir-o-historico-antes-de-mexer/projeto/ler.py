"""Lê as páginas guardadas e devolve um dicionário por produto, com os campos como a API mandou."""

import json
import sys
from pathlib import Path

CAMPOS = ["id", "title", "price", "price_with_discount", "old_price", "discount_percentage",
          "oferta_price", "oferta_price_with_discount", "oferta_ends_at", "available", "stock", "fabricante", "product_link"]


def ler_pagina(conteudo):
    """Recebe o JSON de uma página e devolve os produtos dela."""
    resposta = json.loads(conteudo)
    produtos = []
    for item in resposta["data"]:
        atributos = item["attributes"]
        oferta = atributos.get("offer") or {}  # só os produtos em oferta têm este bloco; o preço grande do cartão sai dele
        produtos.append({
            "id": item["id"],
            "title": atributos.get("title"),
            "price": atributos.get("price"),
            "price_with_discount": atributos.get("price_with_discount"),
            "old_price": atributos.get("old_price"),
            "discount_percentage": atributos.get("discount_percentage"),
            "oferta_price": oferta.get("price"),
            "oferta_price_with_discount": oferta.get("price_with_discount"),
            "oferta_ends_at": oferta.get("ends_at"),
            "available": atributos.get("available"),
            "stock": atributos.get("stock"),
            "fabricante": (atributos.get("manufacturer") or {}).get("name"),
            "product_link": atributos.get("product_link"),
        })
    return produtos


def ler_dia(pasta):
    """Todos os produtos de um dia de coleta, na ordem das páginas."""
    produtos = []
    for arquivo in sorted(Path(pasta).glob("pagina-*.json")):
        produtos += ler_pagina(arquivo.read_bytes())
    return produtos


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pasta = Path(sys.argv[1])
    else:
        dias = sorted(Path("dados/bronze").glob("*"))  # vazio se a pasta ainda não existe
        if not dias:
            raise SystemExit("Ainda não há coleta em dados/bronze. Rode antes: uv run python coletar.py")
        pasta = dias[-1]
    produtos = ler_dia(pasta)
    print(f"{pasta}: {len(produtos)} produtos")
    for campo, valor in produtos[0].items():
        print(f"  {campo}: {valor}")
