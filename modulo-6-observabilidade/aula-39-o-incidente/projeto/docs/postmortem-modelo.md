# Postmortem: <o que aconteceu, em uma linha>

Data do incidente: AAAA-MM-DD. Escrito por: <quem>. Sem culpados: o texto fala do sistema, não de pessoas.

## Resumo

<Três frases: o que o usuário do dado sentiu, por quanto tempo, e o que resolveu.>

## Impacto

- Tempo com o dado velho ou errado: <minutos>, que saem do orçamento de erro do mês (docs/slo.md: 36 horas).
- Orçamento que sobrou depois: <valor do painel Kabum · SLO>.
- Dado errado publicado? <sim ou não; se sim, quais dias e quantas linhas>.

## Linha do tempo (horário de Brasília)

| Hora | O que aconteceu | Onde se viu |
|---|---|---|
| HH:MM | a falha começa | |
| HH:MM | o alerta chega | avisos.log, linha ALERTA |
| HH:MM | a etapa suspeita, no painel | Kabum · saúde |
| HH:MM | a causa, no log ou no trace | Explore: Loki ou Tempo |
| HH:MM | o conserto | |
| HH:MM | o painel volta ao normal e o alerta se resolve | avisos.log, linha resolved |

## Causa

<O que mudou, e por que o sistema deixou isso virar um incidente.>

## O que funcionou e o que não

- Funcionou: <o sinal que levou à causa>.
- Não funcionou: <o sinal que faltou ou enganou>.

## Ações

| Ação | Tipo (prevenir, detectar, mitigar) | Feito em |
|---|---|---|
| | | |
