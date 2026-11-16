# Postmortem: a carga parou porque a senha do banco foi trocada

Data do incidente: 2026-11-16. Escrito na prova do curso (incidente/provocar.py, falha "senha"). Sem culpados.

## Resumo

A execução das 18:11 coletou, conferiu e transformou o dia, e parou na carga: o Postgres recusou a senha do `.env`. O dado do banco ficou com a carga anterior por pouco mais de um minuto, até a senha voltar. O log dizia só "Crashed: Execution was aborted by Python system exit call"; a causa estava no trace.

## Impacto

- Tempo com a carga de hoje faltando: das 18:12:10 às 18:13:18, cerca de 1 minuto. O dado ainda tinha menos de 13 horas: o SLO de frescor não foi tocado.
- Dado errado publicado: não. Cada dia é uma transação; a carga nem abriu a conexão.

## Linha do tempo (horário de Brasília)

| Hora | O que aconteceu | Onde se viu |
|---|---|---|
| 18:11:50 | a senha do usuário postgres muda no banco | (provocado) |
| 18:12:10 | a execução grinning-jackal termina em Crashed na task carregar | Prefect; métrica glearn_execucao_ok = 0 |
| 18:12:50 | o alerta KabumExecucaoFalhou chega ao receptor | avisos.log |
| 18:12:50 a 18:13:10 | painel: 5 pedidos, todos 200, a coleta está boa; logs: só "a execução terminou em Crashed", sem a causa; trace: o span carregar-ed9 com SystemExit "password authentication failed for user postgres" | Kabum · saúde; Explore, Loki e Tempo |
| 18:13:18 | a senha volta e a execução seguinte termina Completed | avisos.log |

## Causa

A senha do banco mudou e o `.env` ficou com a antiga. O programa parou de propósito (SystemExit), mas a mensagem da parada só aparecia no terminal e no trace: o log JSON não a registrava, e a mensagem dizia "O banco não respondeu. Ele está de pé?", o que manda olhar o lugar errado (o banco estava de pé).

## O que funcionou e o que não

- Funcionou: o alerta em menos de um minuto; o trace, com a exceção inteira no span da task.
- Não funcionou: o log sem a mensagem da parada; a mensagem do banco.py confundindo "não respondeu" com "recusou a senha".

## Ações

| Ação | Tipo | Feito em |
|---|---|---|
| Registrar como ERROR, no log JSON, a mensagem de toda parada de propósito (SystemExit) dentro de uma etapa | detectar | observabilidade/logs.py, na_etapa |
| banco.py: separar "recusou a senha" de "não respondeu" | mitigar | banco.py, conectar |
| Teste: a parada aparece no log com a mensagem | prevenir | testes/test_logs.py |
