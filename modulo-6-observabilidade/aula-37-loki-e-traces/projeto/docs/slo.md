# O combinado do Kabum (SLO)

Escrito em 16/11/2026. Quem usa: quem consulta o histórico de preços no banco (a tabela `precos`).

## O que prometemos

**O preço no banco tem no máximo 13 horas em 95% do tempo, medido em janelas de 30 dias.**

- O projeto roda às 6h e às 18h (horário de Brasília). Com as duas rodadas boas, o dado nunca passa de 12 horas; a 13ª hora é a folga para uma rodada que atrasa.
- O SLI (o indicador) é `kabum:fresco` no Prometheus: 1 quando `kabum:horas_desde_ok` está até 13, 0 quando passa.
- A janela é de 30 dias corridos: `avg_over_time(kabum:fresco[30d])`.

## O orçamento de erro

5% de 30 dias são 36 horas. É quanto o dado pode ficar velho no mês sem quebrar o combinado. Uma rodada perdida deixa o dado velho por umas 11 horas (da 13ª hora até a rodada seguinte dar certo, 24 horas depois da última boa): o mês aguenta três, com 33 horas.

## O que fazemos com ele

- **Sobrando orçamento:** mudanças no coletor e na transformação seguem normalmente.
- **Orçamento zerado:** nenhuma mudança no coletor até a janela de 30 dias voltar a ter folga. Só correção do que quebrou.
- **Alerta `KabumOrcamentoQueimando`:** o dado está velho há mais de uma hora; quem estiver de plantão para o que faz e abre o runbook.md.

## O que fica de fora

- Dia sem coleta porque a Kabum recusou (429 ou 403): conta contra o orçamento. Recusa não é desculpa: é o sinal de que pedimos demais.
- Manutenção combinada com antecedência: não existe neste projeto; se existir, entra aqui com data.
