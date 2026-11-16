# Módulo 6 · Observar

O projeto conta o que acontece com ele: logs em JSON com o id da execução, métricas no Prometheus, alertas com o Alertmanager, logs no Loki e traces no Tempo pelo OpenTelemetry Collector, os sinais do dado publicado e um incidente provocado para investigar só pelos sinais. Tudo local e grátis, no `compose.yaml`, com o Grafana em http://127.0.0.1:3000.

| Aula | Pasta | No curso |
|---|---|---|
| 34 | [Um id que segue a execução](aula-34-logs-com-id) | P05-01 |
| 35 | [Métricas do pipeline](aula-35-metricas) | P05-02 |
| 36 | [Alertas, SLO e orçamento de erro](aula-36-alertas-e-slo) | P05-03 |
| 37 | [Loki e traces](aula-37-loki-e-traces) | P05-04 |
| 38 | [Observabilidade de dados](aula-38-observabilidade-de-dados) | P05-05 |
| 39 | [O incidente](aula-39-o-incidente) | P05-06 |

As pastas `projeto/` são cumulativas e partem da aula 26 (fim da etapa Orquestrar). Rodado em 16/11/2026, com Prometheus 3.16.0, Alertmanager 0.35.0, Pushgateway 1.11.4, Grafana 13.3.1, Loki 3.7.10, Tempo 3.1.1, OpenTelemetry Collector contrib 0.165.0 e Prefect 3.9.3. A pasta `final/` do repositório continua igual à da etapa Orquestrar: o módulo 5 (IA) parte dela. As saídas estão em [saidas/observar/](../saidas/observar).

Máquina: em repouso, os oito contêineres ocuparam cerca de 0,5 GB de memória, e uns 0,7 GB durante uma execução; as imagens novas somam uns 3,3 GB. Numa máquina de 4 GB, suba só o banco e leia os logs com `jq` (README do projeto, "A observação").
