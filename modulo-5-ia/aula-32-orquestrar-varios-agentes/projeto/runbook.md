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
   - "acima do teto de 40 por dia": as categorias, juntas, cresceram ou a API mudou. A mensagem mostra as páginas de cada uma; abra a página da categoria no navegador antes de mudar o teto.
2. **`Failed` em `coletar`, depois das tentativas.** É a internet ou a loja fora do ar. Abra https://www.kabum.com.br no navegador. Quando ela responder, rode de novo, no mesmo dia: o que já foi baixado não é pedido outra vez.
3. **`Failed` em `conferir`, com `A cobertura ficou em`.** A paginação da API perdeu mais de 10% dos produtos, e nada foi publicado. A coleta do dia foi para `dados/barrados/`: compare os repetidos no log da task com os da pasta barrada. Rode de novo, no mesmo dia: a coleta recomeça do zero. Se barrar de novo, a API mudou; não baixe o mínimo sem entender por quê.
4. **`Failed` em `transformar` ou `carregar`.** A mensagem diz o que barrou: uma regra da silver, ou um dia que não fecha contra o banco. O dia que falhou não foi gravado.
5. **`Crashed` com `interrupt signal`.** Alguém apertou Ctrl+C ou a máquina desligou no meio. Rode de novo, no mesmo dia: a coleta continua de onde parou. Se a queda foi horas antes, mova a pasta do dia para `dados/barrados/` antes de rodar: a coleta recomeça inteira, num momento só, sem misturar páginas de horas diferentes. Se o dia já passou, a pasta dele, sem o selo `conferida.txt`, fica fora do histórico: aquele dia faltou, e não há como pedir o preço dele de novo.
6. **`Failed` logo no começo, antes de qualquer task.** Com `must be created before acquiring slots`: o limite de uma execução por vez não existe neste servidor do Prefect. Crie uma vez: `uv run prefect gcl create projeto-kabum --limit 1`. Com `TimeoutError`: outra execução ficou com a vaga por 15 minutos. Veja no painel qual está em `Running`. Uma execução morta sem Ctrl+C, com o servidor do Prefect ligado, devolve a vaga sozinha em cerca de 5 minutos. Se o servidor caiu junto (a máquina desligada no meio de uma rodada), a vaga fica presa: confira que nenhuma execução está em `Running` e solte com `uv run prefect gcl update projeto-kabum --active-slots 0`.

## Linhas de ATENÇÃO

A execução terminou em `Completed` e o dia foi publicado, mas a vigia (`vigiar.py`) viu algo fora do normal no banco. Nada parou; a linha diz o que olhar.

1. **A cobertura ficou perto do mínimo.** Um dia entre 90% e 95% passa. Se a cobertura cair por dois ou três dias seguidos, a paginação da API mudou: confira os repetidos no log da task `conferir` e o `links.next` da primeira página.
2. **Sumiram muitos produtos, "pode ser só ela".** Os sumidos cabem no que a paginação perdeu naquele dia. Espere o dia seguinte: se eles voltarem, eram da paginação, e a gold mostra a cobertura ao lado.
3. **Sumiram muitos produtos, "mais do que a paginação perdeu".** A loja tirou produtos da categoria, ou a categoria mudou de endereço. Abra a página da categoria no navegador e compare o total com o `declarado` da tabela `coletas`.
4. **Faltam dias no histórico.** Nenhuma coleta passou pela conferência naqueles dias. Procure em `avisos.log` as linhas desses dias. O preço deles não volta: a API só devolve o de hoje.

Para rodar de novo, com o agendamento ligado (`uv run python fluxo.py agendar`, num terminal que fica aberto): `uv run prefect deployment run projeto-kabum/duas-vezes-por-dia`. Sem ele: `uv run python fluxo.py`.
