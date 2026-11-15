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
