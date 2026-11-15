"""Servidor MCP do banco do Projeto Kabum, só de leitura, para o agente de código consultar o histórico antes de mudar
a coleta. Fala com o Claude Code pela entrada e saída padrão (stdio): nada de print aqui, o stdout é do protocolo.

Três ferramentas com parâmetros, nenhuma com SQL livre. O papel kabum_leitura só tem SELECT, e toda consulta tem
LIMIT e tempo máximo. Rode pelo .mcp.json; para testar à mão: uv run --with mcp python mcp_kabum.py"""

import os
from datetime import date

import psycopg
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

load_dotenv()
ENDERECO = os.getenv("KABUM_LEITURA_URL", "postgresql://kabum_leitura:leitura@localhost:5434/postgres")
TETO_LINHAS = 50

servidor = MCPServer("kabum", instructions="Histórico de preços das placas de vídeo da Kabum. Só leitura.")


def consultar(sql, parametros=()):
    with psycopg.connect(ENDERECO, connect_timeout=5, options="-c statement_timeout=3000") as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(sql, parametros)
            colunas = [c.name for c in cursor.description]
            return [dict(zip(colunas, linha)) for linha in cursor.fetchmany(TETO_LINHAS)]


@servidor.tool()
def coletas(ultimos: int = 7) -> list[dict]:
    """A conferência dos últimos dias coletados: dia, produtos diferentes que vieram, total que a API declarou,
    total que a página da loja mostrou e a cobertura (de 0 a 1)."""
    ultimos = max(1, min(ultimos, 30))
    return consultar("SELECT * FROM coletas ORDER BY dia DESC LIMIT %s", (ultimos,))


@servidor.tool()
def resumo_do_dia(dia: date | None = None) -> dict:
    """Quantos produtos, placas e anúncios em oferta houve num dia (o último carregado, se não vier o dia)."""
    linhas = consultar(
        """SELECT dia, count(*) AS produtos, count(*) FILTER (WHERE e_placa) AS placas,
                  count(*) FILTER (WHERE em_oferta) AS em_oferta, min(preco_final) AS menor_centavos
           FROM precos WHERE dia = coalesce(%s, (SELECT max(dia) FROM precos)) GROUP BY dia""", (dia,))
    return linhas[0] if linhas else {"erro": f"nenhum dado em {dia}"}


@servidor.tool()
def mais_baratos(modelo: str, limite: int = 5) -> list[dict]:
    """Os anúncios mais baratos de um modelo (ex.: 'RTX 5070') no último dia carregado, com título e preço em centavos."""
    limite = max(1, min(limite, 20))
    return consultar(
        """SELECT dia, id, titulo, preco_final FROM precos
           WHERE dia = (SELECT max(dia) FROM precos) AND upper(modelo) = upper(%s)
           ORDER BY preco_final LIMIT %s""", (modelo, limite))


if __name__ == "__main__":
    servidor.run()
