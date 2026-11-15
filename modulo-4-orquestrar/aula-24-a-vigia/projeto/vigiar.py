"""Depois da carga, olha no banco o que o portão da conferência deixa passar: a cobertura perto do mínimo, muitos
produtos sumindo de um dia para o outro e um dia faltando no histórico. Não para nada: devolve os avisos, e cada aviso
diz o que olhar."""

from datetime import timedelta

from banco import conectar
from coletar import registro
from conferir import COBERTURA_MINIMA

COBERTURA_ATENCAO = 0.95  # o portão barra abaixo de 90%; entre 90% e 95% o dia passa, com aviso
SUMICO_ATENCAO = 0.05  # mais de 5% dos produtos do dia anterior sumindo de uma vez

# Os dois últimos dias carregados e, para o último, a cobertura e quantos produtos a paginação perdeu.
ULTIMOS = """
SELECT p.dia, c.cobertura, c.declarado - c.diferentes AS perdidos
FROM (SELECT DISTINCT dia FROM precos ORDER BY dia DESC LIMIT 2) p
LEFT JOIN coletas c USING (dia)
ORDER BY p.dia
"""

# Quantos produtos o dia anterior tinha, e quantos deles vieram de novo no último dia: o LEFT JOIN da gold SUMIRAM.
# count(hoje.id) não conta as linhas em que hoje.id ficou vazio, as dos produtos que não vieram.
SUMIRAM = """
SELECT count(*) AS anteriores, count(hoje.id) AS vieram
FROM precos ontem
LEFT JOIN precos hoje ON hoje.dia = %s AND hoje.id = ontem.id
WHERE ontem.dia = %s
"""


def dias_faltando(dias):
    """Os dias do calendário, entre o primeiro e o último da lista, que não estão nela."""
    if not dias:
        return []
    todos = {dias[0] + timedelta(days=n) for n in range((dias[-1] - dias[0]).days + 1)}
    return sorted(todos - set(dias))


def avisos_do_dia(dia, cobertura, perdidos, anterior, anteriores, sumiram):
    """As regras de atenção do último dia carregado. Devolve uma lista de textos, vazia se está tudo como sempre."""
    avisos = []
    if cobertura is not None and cobertura < COBERTURA_ATENCAO:
        avisos.append(f"a cobertura de {dia} ficou em {cobertura:.1%}, perto do mínimo de {COBERTURA_MINIMA:.0%}: "
                      f"a paginação perdeu {perdidos} produtos. Se cair de novo amanhã, confira os repetidos no log da task conferir.")
    if anterior is not None and sumiram > SUMICO_ATENCAO * anteriores:
        causa = (f"a paginação perdeu {perdidos} nesse dia, então pode ser só ela" if perdidos is not None and sumiram <= perdidos
                 else "mais do que a paginação perdeu: a loja tirou produtos ou a categoria mudou. Abra a página da categoria no navegador")
        avisos.append(f"sumiram {sumiram} dos {anteriores} produtos de {anterior} para {dia} ({sumiram / anteriores:.1%}); {causa}.")
    return avisos


def avisos():
    """Lê o banco e devolve os avisos do último dia carregado, com os dias que faltam entre ele e o anterior."""
    with conectar() as conexao:
        dias = [linha[0] for linha in conexao.execute("SELECT DISTINCT dia FROM precos ORDER BY dia").fetchall()]
        ultimos = conexao.execute(ULTIMOS).fetchall()
        if not ultimos:
            return []  # o banco ainda não tem dia nenhum
        dia, cobertura, perdidos = ultimos[-1]
        anterior, anteriores, sumiram = None, 0, 0
        if len(ultimos) == 2:
            anterior = ultimos[0][0]
            anteriores, vieram = conexao.execute(SUMIRAM, [dia, anterior]).fetchone()
            sumiram = anteriores - vieram
    lista = avisos_do_dia(dia, None if cobertura is None else float(cobertura), perdidos, anterior, anteriores, sumiram)
    faltando = dias_faltando([anterior, dia]) if anterior else []  # só o buraco novo: um antigo já foi avisado
    if faltando:
        lista.append(f"faltam dias no histórico: {', '.join(map(str, faltando))}. A API só devolve o preço de hoje: "
                     "esses dias ficam vazios. Veja em avisos.log o que aconteceu neles.")
    registro.info("vigia: %s dias no banco, o último %s; %s avisos", len(dias), dia, len(lista))
    return lista


if __name__ == "__main__":
    for aviso in avisos():
        print(aviso)
