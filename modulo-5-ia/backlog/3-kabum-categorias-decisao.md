# Kabum: coletar mais três categorias

O time quer o histórico de preço também de SSD, memória RAM e processador, além das placas de vídeo. Os caminhos na API de catálogo, conferidos no navegador em 15/11/2026:

- `hardware/ssd-2-5`
- `hardware/memoria-ram`
- `hardware/processadores`

Na primeira página de cada uma, em 15/11/2026: SSD com 1.002 produtos (9 páginas de 120), memória com 1.393 (12 páginas) e processadores com 615 (6 páginas).

Pronto quando:
- `coletar.py` coleta as quatro categorias, cada uma na sua pasta dentro da pasta do dia.
- As regras de coleta do projeto continuam valendo.
- Testes novos, sem internet.
- `uv run pytest` passa.

## Decisão do time (comentário na issue, 15/11/2026)

O agente apontou que as quatro categorias somam 31 a 32 páginas por dia, acima do teto de 20. Decidimos:

- Teto novo: 40 páginas por dia, somando as quatro categorias. Atualize o `LIMITE_PAGINAS`, o `CLAUDE.md` e a seção "Regras de coleta" do `README.md`.
- As placas continuam na raiz da pasta do dia (o histórico, a silver e o banco leem dali); as outras três vão para `ssd/`, `memoria/` e `processador/`.
- A conferência com a página da loja continua só para as placas.
- Nada lê as três categorias novas ainda: isso é outra issue. Diga isso no commit.

Como trabalhar: antes de mudar, peça ao subagente `pesquisador` quem lê as páginas da pasta do dia. No fim, com os testes passando, peça ao subagente `revisor` para revisar o diff e corrija o que ele marcar como BLOQUEIA.
