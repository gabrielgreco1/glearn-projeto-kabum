# Projeto Kabum

Objetivo: guardar, um dia depois do outro, o preço de todas as placas de vídeo da Kabum, para ter o histórico de cada produto.
Plano: a página da categoria busca os produtos numa API de catálogo. O programa pede essa mesma API, página por página, com pausa, e guarda cada resposta como veio. Se o site recusar, o programa para. Depois, a etapa Transformar limpa, confere e resume o histórico, sem pedir nada ao site, e a etapa Carregar guarda esse histórico num Postgres que roda no Docker, um dia por vez. A etapa Orquestrar põe tudo num flow do [Prefect](https://docs.prefect.io/), que roda sozinho às 6h e às 18h, só publica um dia inteiro e avisa quando algo sai do normal.

## Como rodar

Você precisa do [uv](https://docs.astral.sh/uv/) e do [Docker](https://docs.docker.com/get-started/get-docker/) instalados. No Windows e no Mac, o Docker é o Docker Desktop, e ele precisa estar aberto.

```
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu. Depois:

```
docker compose up -d --wait
uv sync
uv run pytest
```

Os testes não precisam do banco, do `.env` nem da pasta `dados/`: é assim que eles rodam no GitHub, a cada push (`.github/workflows/testes.yml`).

O projeto roda de três jeitos. Os dois primeiros precisam do servidor do Prefect ligado, num terminal só dele: `uv run prefect server start`. Uma vez na sua máquina: `uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api` e `uv run prefect gcl create projeto-kabum --limit 1`, o limite de uma execução por vez. O painel fica em http://127.0.0.1:4200.

| Comando | O que faz |
|---|---|
| `uv run python fluxo.py agendar` | fica ligado e roda o projeto todo dia às 6h e às 18h, no horário de Brasília. Para rodar agora, noutro terminal: `uv run prefect deployment run projeto-kabum/duas-vezes-por-dia` |
| `uv run python fluxo.py` | roda uma vez, agora, como um flow do Prefect |
| `uv run python rodar.py` | roda as cinco etapas sem o Prefect, sem aviso, sem vigia e sem o limite |
| `uv run python barato.py "RTX 5070"` | mostra os 3 anúncios mais baratos do modelo no último dia da silver, com título e link. Não pede nada à loja nem usa o banco; precisa da silver, então rode `transformar.py` antes |

Uma rodada por dia basta; a das 18h é a segunda chance. A rodada faz um pedido à API para cada 120 produtos de cada categoria (cerca de 32 em novembro de 2026: 5 de placas, 9 de SSD, 12 de memória e 6 de processadores) e 1 à página da loja, com 3 segundos de pausa entre eles, e leva cerca de 2 minutos. Rodar de novo no mesmo dia não pede nada de novo: as páginas da API e a página da loja já estão na pasta do dia. A etapa Transformar roda em seguida, em menos de um segundo, sobre todos os dias guardados, e a etapa Carregar leva ao banco só os dias novos e os que mudaram.

O banco fica de pé até você desligar o computador ou rodar `docker compose stop`. Se o `rodar.py` disser que o banco não respondeu, suba de novo com `docker compose up -d --wait`: os dados ficam no volume do Docker.

Para rodar só a etapa Transformar, sem coleta: `uv run python transformar.py`. Só a carga: `uv run python carregar.py`. Para carregar de novo um dia que passou, mesmo sem mudança: `uv run python carregar.py 2026-11-14`. Para medir o `precos.csv`: `uv run python perfil.py`. Para ver o anúncio mais barato de um modelo no último dia, sem abrir o banco: `uv run python barato.py "RTX 5070"`, que imprime o preço final, o título e o link de cada um dos 3.

No Windows, os comandos são os mesmos no PowerShell.

## As etapas

| Etapa | Programa | O que faz |
|---|---|---|
| Extrair | `coletar.py` | Pede as páginas da API e guarda cada resposta em `dados/bronze/<dia>/` |
| Extrair | `conferir.py` | Mede a cobertura contra o total da API e da loja e anota o dia em `conferencia.csv` |
| Extrair | `tabela.py` | Monta o `precos.csv`, uma linha por produto por dia, com os campos como a API mandou |
| Transformar | `silver.py` | Preços em centavos, o fim da oferta no horário de Brasília, o preço final, placa ou acessório, chip, modelo e marca |
| Transformar | `validar.py` | Oito regras escritas: o que falha numa regra de erro vai para os rejeitados, com o motivo; os avisos ficam marcados |
| Transformar | `qualidade.py` | O relatório da rodada e a decisão de publicar |
| Transformar | `historico.py` | A gold, em SQL: mudanças de preço, produtos que sumiram e o menor preço de cada modelo por dia |
| Carregar | `banco.py` | Conecta ao Postgres do `compose.yaml` e cria as tabelas do `schema.sql` que ainda não existem |
| Carregar | `carregar.py` | Leva ao banco os dias novos e os que mudaram, um dia por transação, e confere cada dia contra a silver |
| Orquestrar | `fluxo.py` | As etapas como tasks de um flow do Prefect, com novas tentativas na coleta, aviso de falha, uma execução por vez e o agendamento |
| Orquestrar | `vigiar.py` | Depois da carga, olha no banco a cobertura, os sumiços e os dias que faltam, e devolve os avisos |
| Consulta (fora das etapas) | `barato.py` | Lê só a silver do último dia e mostra os 3 anúncios mais baratos de um modelo, com link. Não pede nada à loja e não usa o banco. Exemplo: `uv run python barato.py "RTX 5070"` |

O `rodar.py` chama as três etapas da extração, depois o `transformar.py`, que chama as quatro da transformação, e por último o `carregar.py`. O `fluxo.py` faz o mesmo, uma task por etapa, e acrescenta a vigia. O `barato.py` não faz parte dessas cadeias: ele só lê o que a Transformar já deixou na silver.

## Trabalhar com um agente de código

O projeto tem três arquivos que dizem ao agente de código (o Claude Code, por exemplo) como trabalhar aqui. Eles estão no Git.

- `CLAUDE.md`, na raiz: as regras do projeto em texto. Idioma, como rodar testes, o que nunca mexer, as regras da loja e as regras do Git. O agente lê esse arquivo no começo de cada sessão.
- `.claude/settings.json`: o que o agente pode rodar sem perguntar, o que pergunta antes e o que nunca roda. É a parte que o programa aplica, não só um pedido escrito.
- `.claude/agents/`: dois subagentes. O `pesquisador` procura no código onde uma mudança vai mexer e só lê. O `revisor` revisa o diff da branch contra o `CLAUDE.md` e as regras de coleta, e não edita nada.

Pelo `.claude/settings.json`, o agente:

- Roda sem perguntar: `uv run pytest`, `uv run python barato.py`, e `git status`, `git diff`, `git log`, `git add`, `git commit` e `git switch`.
- Pergunta antes: `uv add`, que mexe nas dependências.
- Nunca roda: `coletar.py`, `rodar.py` e `fluxo.py` (eles pedem à loja de verdade), `git push`, `curl`, o `WebFetch`, e a leitura do `.env`.

Mesmo sem a regra no `settings.json`, o `CLAUDE.md` pede que o agente não faça push nem abra PR, e que não leia o `.env`, que não vai para o Git. Quem coleta e publica é sempre uma pessoa.

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/AAAA-MM-DD/pagina-001.json`, `pagina-002.json` e as seguintes: a resposta da API, como veio, uma pasta por dia. Essas são as placas de vídeo; SSD, memória e processador ficam nas subpastas `ssd/`, `memoria/` e `processador/` da mesma pasta, com os mesmos nomes de arquivo, e ainda não são lidos por nada. Na raiz da pasta, `loja.html`: a página da categoria de placas, de onde sai o total que a loja mostra. Quando a conferência barra o dia, só as placas saem da pasta; as subpastas ficam, e a nova rodada repete as páginas das placas e a `loja.html` (cerca de 6 pedidos), então um dia barrado uma vez chega a cerca de 39 pedidos.
- `conferencia.csv`: uma linha por dia de coleta, com o que faltou. Conferir de novo o mesmo dia troca a linha dele.
- `precos.csv`: uma linha por produto por dia, com os campos como a API mandou. O preço grande do cartão, quando o produto está em oferta, é o `oferta_price_with_discount`.
- `silver/precos.parquet`: a mesma linha por produto por dia, limpa e conferida. Os preços estão em centavos (`213918` é R$ 2.139,18). `preco_final` é o preço no Pix daquele dia, já com a oferta, quando havia uma. A coluna `avisos` diz que regra de aviso a linha não passou.
- `silver/rejeitados.csv`: uma linha por regra de erro quebrada, com o motivo e o valor. Na rodada de 15 de novembro de 2026, vazio.
- `qualidade/AAAA-MM-DD.json`: o relatório de cada rodada: lidos, válidos, rejeitados por regra, avisos por regra, cobertura e se a rodada foi publicada.
- `gold/mudancas.parquet`: cada vez que um produto mudou de preço ou entrou e saiu de oferta, comparado com o último dia em que apareceu.
- `gold/sumiram.parquet`: os produtos que estavam no dia anterior e não vieram no dia, com a cobertura daquele dia.
- `gold/modelos.parquet`: por dia e por modelo, quantos anúncios, o menor preço, a mediana e o produto mais barato.
- `ultima_recusa.html`: só aparece se o site recusar um pedido. É a resposta da recusa, para você ler.

No banco, um Postgres 18 que roda no Docker na porta 5434 (o `compose.yaml`), com os dados num volume do Docker, fora da pasta:

- `precos`: o histórico, uma linha por produto por dia, com as colunas da silver. A chave é o par (dia, id).
- `cargas`: uma linha por dia carregado, com quantas linhas saíram, quantas entraram, a soma dos preços finais e o hash do dia.
- `coletas`: a conferência de cada dia, do `conferencia.csv`, com a cobertura.
- `produtos`, uma view: uma linha por produto, com o primeiro e o último dia em que ele veio e o último preço.
- `sumidos`, uma view: os produtos que não vieram no último dia carregado, com a cobertura desse dia.

Para consultar: `docker compose exec banco psql -U postgres`, ou qualquer programa com o endereço do `DATABASE_URL`.

A tabela `fabricantes.csv`, na raiz, troca o fabricante como a loja escreve pela marca. Ela vai para o Git. Quando aparece um fabricante novo, o `transformar.py` avisa, e você acrescenta uma linha.

## Regras de coleta

- A coleta só é rodada por uma pessoa, nunca pelo agente de código: `coletar.py`, `rodar.py` e `fluxo.py` pedem à loja de verdade, e a pessoa é quem roda. O agente roda os testes e o `barato.py`, que não fala com a loja.
- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 3 segundos de espera depois de cada um. No máximo 40 páginas por dia, somando as quatro categorias (em 15/11/2026: 5 + 9 + 12 + 6 = 32).
- Quatro categorias: placas de vídeo (na raiz da pasta do dia), SSD (`ssd/`), memória RAM (`memoria/`) e processadores (`processador/`). A conferência com a página da loja é só das placas, e por enquanto nada lê as três categorias novas.
- O pedido não usa ordenação (`sort`): o `robots.txt` da loja pede que programas não usem.
- Qualquer resposta que não seja um JSON com status 200 para o programa. Uma página de desafio, um 403 ou um 429 é o site dizendo não. O programa guarda a resposta e para. Não há troca de identidade, proxy nem navegador automatizado.

## O que a rodada de 14 de novembro de 2026 mostrou

- O `links.next` da API trocou o tamanho da página de 60 para 40 na página 7. Seguido ao pé da letra, ele levou a 12 páginas, 613 linhas e só 468 produtos diferentes. O programa monta o endereço de cada página com o tamanho fixo e para no total que a primeira página declara.
- A paginação da API perde produtos. A ordem padrão tem empates, e cada página desempata de um jeito: alguns produtos vêm em duas páginas e outros em nenhuma. Repetir a mesma página dá o mesmo resultado, então repetir a volta não resolve. Nas rodadas do dia, a cobertura ficou entre 92,4% e 100%.
- O `robots.txt` da loja pede que programas não usem `sort`, então o programa não troca a ordem.
- O programa tira os repetidos pelo `id`, mede a cobertura contra o total que a API declara e anota a conferência de cada dia em `dados/conferencia.csv`. Abaixo de 90%, ele para.
- O filtro por fabricante fecharia a lacuna, porque cada fabricante cabe numa página só. Mas são 42 fabricantes na categoria: seriam dezenas de pedidos por dia em vez de 4, com uma lista de fabricantes que também muda. Este projeto não usa: mede a falta e anota.
- A API aceita até 120 produtos por página (pedimos 500 e vieram 120). Eram 4 pedidos por dia em 14/11/2026; em 15/11, com 481 produtos, foram 5.

## O que a etapa Transformar mostrou, com os dias 14 e 15 de novembro de 2026

- 953 linhas de 2 dias, 478 produtos. `old_price` é sempre 0 e `available` é sempre verdadeiro: a listagem só traz o que está à venda.
- A API manda três preços: `price` é o do cartão, `price_with_discount` é o do Pix, com o desconto de `discount_percentage`, e o bloco da oferta traz o preço da oferta. Em 136 linhas havia oferta; em 2 delas, a oferta custava o mesmo que o Pix.
- Em 46 das 953 linhas, multiplicar o preço por 100 e cortar as casas dá um centavo a menos (2139.18 vira 213917). O `silver.py` arredonda antes de converter.
- 112 linhas são acessórios (suportes, cabos e até uma caixa de som), no menu "Acessórios" da categoria. 74 linhas de placa ficaram sem modelo, como as G210 e as placas Quadro; elas ficam na silver com o aviso `placa_com_modelo`.
- A loja escreve o fabricante de 42 jeitos. "Outros", "Generico" e "OEM" não dizem quem fez; "Nvidia" e "RX" são nomes de chip; "PALIT" e "Palit Microsystem" são o mesmo. Depois da tabela `fabricantes.csv`, ficam 34 marcas, e 185 linhas sem marca.
- Nenhuma linha quebrou regra de erro. Quatro linhas passaram de três vezes a mediana do modelo: uma GTX 1660 Super a R$ 5.452,20 e uma GT 730 a R$ 1.569,90, nos dois dias.
- Entre os dois dias, 1 produto mudou de preço (um suporte Redragon, de R$ 73,36 para R$ 79,90) e 2 sumiram. A conferência do dia 15 diz que faltaram 2 produtos: os dois sumiços podem ser da paginação, e não da loja. Na prova numa cópia limpa, 44 minutos depois, os dois vieram de novo, cada um em duas páginas: eram da paginação.

## A carga

- Um dia por vez, e cada dia numa transação: o dia é apagado no banco e gravado de novo, inteiro, com COPY. Se algo falha no meio, o dia volta a ser o que era, e os dias anteriores da mesma rodada ficam.
- O que vai: os dias cujo hash na silver é diferente do hash da última carga. Um dia novo não tem carga; um dia antigo que a transformação mudou (uma linha nova no `fabricantes.csv`, por exemplo) tem outro hash. O resto não é tocado.
- Antes de confirmar, o banco tem de ter as mesmas linhas e a mesma soma dos preços finais que a silver tem naquele dia. Se não fecha, o dia é desfeito.
- Carregar de novo um dia que já está no banco deixa o banco igual: o dia é trocado inteiro, e não somado.

## O que a etapa Carregar mostrou, com os dias 14 e 15 de novembro de 2026

- 953 linhas em 2 dias: 477 no dia 14 e 476 no dia 15, com somas de 217.122.953 e 216.105.707 centavos.
- Com uma marca d'água (o último dia carregado), a carga seguinte só olhava os dias depois dela. Quando a linha `Power` do `fabricantes.csv` mudou a marca do produto 991784 nos dois dias, a marca d'água disse que não havia nada a carregar, e o banco ficou com a marca vazia. O hash de cada dia vê a mudança e recarrega os dois.
- 478 produtos diferentes; 2 não vieram no dia 15, que teve cobertura de 99,6%: os mesmos dois que a prova da etapa Transformar mostrou de volta uma hora depois.

## A orquestração

- A coleta é a única task que fala com a loja, e é tentada de novo 3 vezes, com 10 segundos entre elas, quando a rede falha ou a loja responde um erro 5xx. Uma recusa da loja (403, 429, uma página de desafio) para a execução sem nova tentativa.
- Uma execução que termina em `Failed` ou `Crashed` deixa uma linha `AVISO` em `avisos.log`. Uma que termina bem, mas com algo estranho no banco, deixa uma linha `ATENÇÃO`. O `runbook.md` diz o que fazer com cada uma.
- A cobertura abaixo de 90% é um portão: nada é publicado, e a coleta de hoje vai para `dados/barrados/`, para a próxima rodada coletar de novo. A de um dia que passou fica onde está, sem selo.
- A conferência deixa um selo, `conferida.txt`, na pasta do dia. Só um dia com selo entra no histórico: uma coleta interrompida que ninguém terminou fica fora.
- Uma coleta interrompida no mesmo dia continua de onde parou: o que está na pasta do dia não é pedido de novo. Cada página é gravada com outro nome e trocada de uma vez, então uma queda não deixa página pela metade.
- Uma execução por vez, pelo limite `projeto-kabum` do Prefect. A segunda espera a primeira terminar, até 15 minutos. Se o servidor do Prefect cair no meio de uma rodada, a vaga fica presa: o `runbook.md` diz como soltar.
- A API só devolve o preço de hoje. Um dia sem coleta não volta: o que se refaz é a transformação e a carga de um dia guardado (`uv run python carregar.py 2026-11-14`).

## O que a etapa Orquestrar mostrou, em 15 de novembro de 2026

- Duas rodadas ao mesmo tempo, sem o limite, pediram as mesmas 4 páginas e a página da loja duas vezes, 10 pedidos em vez de 5, e as duas terminaram em `Failed` no DuckDB, escrevendo a mesma gold. Com o limite, a segunda esperou 20 segundos e não pediu nada.
- Uma página repetida de propósito derrubou a cobertura para 74,9%. Sem o portão novo, a rodada parava com `SystemExit`, e a seguinte, no mesmo dia, achava as mesmas páginas e parava de novo. Com ele, a coleta foi para `dados/barrados/`, e a rodada seguinte coletou o dia de novo, com 100%.
- A cobertura mudou de uma coleta para outra, no mesmo dia: 100%, 94,2%, 95,4% e 98,8%. A página 2 veio de dois jeitos diferentes. É o empate da ordenação que a etapa Extrair mediu.
- Com 94,2%, o dia passou pelo portão, e a vigia avisou duas vezes: a cobertura perto do mínimo e 28 produtos sumidos, o mesmo número que a paginação perdeu.
- Uma execução morta com `kill -9` segurou a vaga do limite por cerca de 5 minutos. Com Ctrl+C, ela voltou em poucos segundos, e a rodada que esperava continuou a coleta de onde a outra parou. Com o servidor do Prefect morto junto e ligado de novo, a vaga continuou ocupada por mais de 7 minutos, até ser solta com `gcl update --active-slots 0`.
- Sem fuso, o Prefect lê o cron em UTC. O `Cron("0 6,18 * * *", timezone="America/Sao_Paulo")` marcou as execuções para as 21:00 e as 09:00 de UTC: 18h e 6h em Brasília.

## O que o projeto não faz

- O preço Prime, que a loja mostra só para assinantes com login, não entra. O projeto não entra em conta nenhuma.
- O modelo sai do título com uma expressão regular. Títulos sem RTX, GTX, GT ou RX antes do número (as G210, as Quadro, as R5 230) ficam sem modelo e com aviso.
- Um produto que some num dia de cobertura abaixo de 100% pode ter sido perdido pela paginação. A gold mostra a cobertura ao lado; não decide sozinha.
- A oferta vale pelo dia: o histórico guarda o dia da coleta, e não a hora. Uma oferta que termina às 10h59 conta como em oferta na coleta das 15h do mesmo dia.
- O banco guarda os dias que a silver tem. Um dia que saiu da silver não sai do banco sozinho.
- O banco é de treino: a senha do `.env` é simples, e o Docker abre a porta 5434 também para a sua rede local. Não guarde nele nada que precise de proteção.
- O agendamento roda enquanto o `fluxo.py agendar` e o servidor do Prefect estão ligados, na sua máquina. Com o computador desligado às 6h e às 18h, o dia não é coletado.
