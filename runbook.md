# Runbook: o projeto Kabum não carregou

O que fazer quando chega um aviso. Siga as checagens na ordem: a primeira que explicar o aviso é a causa.

## Sintoma

Uma linha nova em `avisos.log`, com a execução terminada em `Failed` ou `Crashed`. No painel do Prefect (http://127.0.0.1:4200), a mesma execução aparece em vermelho ou laranja, com o log de cada task.

## Impacto

O banco continua com os dias que já tinham sido carregados, inteiros: cada dia é uma transação. Falta o dia de hoje. A API só devolve o preço de hoje: um dia que não for coletado até a meia-noite não volta mais.

## Checagens, nesta ordem

1. **`Crashed` com `Python system exit call`.** O programa parou de propósito. A mensagem do que fazer sai no fim do terminal onde o projeto rodou, depois do aviso, e não vai para o painel.
   - "respondeu 403", "respondeu 429" ou uma página em HTML: a loja recusou. Não rode de novo agora. Leia `dados/ultima_recusa.html` e espere até o dia seguinte; se a recusa continuar, pare o projeto.
   - "O banco não respondeu": suba o banco com `docker compose up -d --wait`.
   - "Falta ... no arquivo .env": copie a linha do `.env.example` para o `.env`.
   - "acima do teto de 20 páginas": a categoria cresceu ou a API mudou. Abra a página da categoria no navegador antes de mudar o teto.
2. **`Failed` em `coletar`, depois das tentativas.** É a internet ou a loja fora do ar. Abra https://www.kabum.com.br no navegador. Quando ela responder, rode de novo, no mesmo dia: o que já foi baixado não é pedido outra vez.
3. **`Failed` em `conferir`, com `A cobertura ficou em`.** A paginação da API perdeu mais de 10% dos produtos, e nada foi publicado. A coleta do dia foi para `dados/barrados/`: compare os repetidos no log da task com os da pasta barrada. Rode de novo, no mesmo dia: a coleta recomeça do zero. Se barrar de novo, a API mudou; não baixe o mínimo sem entender por quê.
4. **`Failed` em `transformar` ou `carregar`.** A mensagem diz o que barrou: uma regra da silver, ou um dia que não fecha contra o banco. O dia que falhou não foi gravado.
5. **`Crashed` com `interrupt signal`.** Alguém apertou Ctrl+C ou a máquina desligou no meio. Rode de novo.

Para rodar de novo: `uv run python fluxo.py`.
