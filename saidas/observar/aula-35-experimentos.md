# Experimentos da p05-02 (rodados em 16/11/2026, fora do verify.sh)

- `prometheus-vivo.yml` + `rascunho_vivo.py` (abaixo): um Prometheus à parte (`p05-exp-prom`, porta 32190) raspando de 15 em 15 s um `/metrics` aberto pelo próprio processo do Kabum (`start_http_server(32800)`) durante uma execução com a loja de ensaio, das 17:24:42 às 17:24:59. Resultado (`vivo.txt` é a saída do processo):
  - `up{job="kabum-ao-vivo"}[2m]`: 17:24:40 = 0, 17:24:55 = 1, 17:25:10 = 0, 17:25:25 = 0, 17:25:40 = 0.
  - `glearn_pedidos_total[2m]`: uma amostra só, às 17:24:55, valor 4 (a execução terminou com 5 pedidos).
  - `glearn_pedidos_total` (consulta instantânea, 17:25:45): vazio.
- `rascunho_cardinalidade.py`: o preço de cada placa como rótulo `produto`, empurrado para o Pushgateway num grupo `job=kabum-rascunho`. Antes: `count({__name__=~"glearn_.*"})` = 15 e `prometheus_tsdb_head_series` = 857. Depois de uma raspagem: 475 e 1342; `/api/v1/status/tsdb`: `glearn_preco_reais` com 460 séries, rótulo `produto` com 460 valores.
- Contador por execução: `increase(glearn_pedidos_total{status="200"}[1h])` = 10,73 numa hora em que as execuções empurraram 5, 2, 5 e 5 pedidos com 200.
- Média e cauda (loja com `--atraso 6 --so-pagina 3`): pedidos de 18, 12, 6020 e 12 ms à API e 1 à página da loja; `histogram_quantile(0.5, …)` = 0,156 s, `histogram_quantile(0.95, …)` = 7,0 s, `_sum/_count` = 1,216 s.

```python
# rascunho_vivo.py, apagado depois
import sys
from prometheus_client import start_http_server
from observabilidade import metricas
start_http_server(32800, registry=metricas.REGISTRO)
sys.argv = ["ensaio/rodada.py", "32099"]
exec(open("ensaio/rodada.py", encoding="utf-8").read())
```
