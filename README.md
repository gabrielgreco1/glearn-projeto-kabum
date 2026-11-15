# Projeto Kabum (G learn)

Repositório de referência do Projeto Kabum do curso G learn: um programa em Python que guarda, uma vez por dia, o preço de todas as placas de vídeo da Kabum, pela API de catálogo que a própria página da loja usa, e mede quanto da categoria cada coleta trouxe. Na segunda etapa, o mesmo programa limpa, confere e resume esse histórico: preços em centavos, regras escritas, um relatório por rodada e as mudanças de preço de um dia para o outro. Na terceira, ele guarda o histórico num Postgres que roda no Docker, um dia por vez, só com os dias novos e os que mudaram. Na quarta, ele roda sozinho, num flow do Prefect, às 6h e às 18h, só publica um dia inteiro, avisa o que falhou e o que precisa de olho, uma rodada por vez.

## Como usar

Você faz o projeto na SUA pasta, `projeto-kabum/`, no SEU repositório, seguindo as aulas na plataforma. Este repositório serve para conferir: a pasta `projeto/` de cada aula mostra como a sua pasta deve estar no fim daquela aula.

## As aulas

| Aula | Pasta | O que roda |
|---|---|---|
| 1 | [Onde a página busca o preço](modulo-1-extrair/aula-01-onde-a-pagina-busca-o-preco) | Nada para rodar. Só o `README.md` com o plano. |
| 2 | [O pedido da página, em Python](modulo-1-extrair/aula-02-pedir-a-primeira-pagina) | `uv run python coletar.py` |
| 3 | [Do JSON ao produto](modulo-1-extrair/aula-03-do-json-ao-produto) | `uv run python ler.py` e `uv run pytest` |
| 4 | [Todas as páginas, sem seguir o links.next](modulo-1-extrair/aula-04-todas-as-paginas) | `uv run python coletar.py` |
| 5 | [Conferir a coleta: o que faltou](modulo-1-extrair/aula-05-conferir-a-coleta) | `uv run python conferir.py` |
| 6 | [O histórico de preços](modulo-1-extrair/aula-06-o-historico-de-precos) | `uv run python tabela.py` |
| 7 | [Fechar o projeto: uma rodada, um comando](modulo-1-extrair/aula-07-fechar-o-projeto) | `uv run python rodar.py` e `uv run pytest` |

### Etapa Transformar

| Aula | Pasta | O que roda |
|---|---|---|
| 8 | [Medir o histórico antes de mexer](modulo-2-transformar/aula-08-medir-o-historico-antes-de-mexer) | `uv run python perfil.py` |
| 9 | [Reprocessar o bronze: os campos que faltavam](modulo-2-transformar/aula-09-reprocessar-o-bronze) | `uv run python tabela.py` |
| 10 | [Três preços, em centavos](modulo-2-transformar/aula-10-tres-precos-em-centavos) | `uv run python silver.py` |
| 11 | [O que é placa, quem fez e qual modelo](modulo-2-transformar/aula-11-o-que-e-placa-e-quem-fez) | `uv run python silver.py` |
| 12 | [Regras, avisos e rejeitados](modulo-2-transformar/aula-12-regras-avisos-e-rejeitados) | `uv run python validar.py` |
| 13 | [O que mudou de um dia para o outro](modulo-2-transformar/aula-13-o-que-mudou-de-um-dia-para-o-outro) | `uv run python historico.py` |
| 14 | [Extrair e transformar num comando só](modulo-2-transformar/aula-14-extrair-e-transformar-num-comando) | `uv run python rodar.py` e `uv run pytest` |

### Etapa Carregar

| Aula | Pasta | O que roda |
|---|---|---|
| 15 | [Um banco para o histórico](modulo-3-carregar/aula-15-um-banco-para-o-historico) | `docker compose up -d --wait` e `uv run python banco.py` |
| 16 | [Um dia de cada vez](modulo-3-carregar/aula-16-um-dia-de-cada-vez) | `uv run python carregar.py AAAA-MM-DD` |
| 17 | [A marca d'água: só os dias novos](modulo-3-carregar/aula-17-a-marca-dagua) | `uv run python carregar.py` |
| 18 | [Um dia que passou](modulo-3-carregar/aula-18-um-dia-que-passou) | `uv run python carregar.py` e `uv run python carregar.py AAAA-MM-DD` |
| 19 | [O que sumiu e o último preço](modulo-3-carregar/aula-19-o-que-sumiu-e-o-ultimo-preco) | `uv run python carregar.py` e as views no `psql` |
| 20 | [Extrair, transformar e carregar num comando](modulo-3-carregar/aula-20-extrair-transformar-e-carregar) | `uv run python rodar.py` e `uv run pytest` |

### Etapa Orquestrar

| Aula | Pasta | O que roda |
|---|---|---|
| 21 | [O projeto Kabum no Prefect](modulo-4-orquestrar/aula-21-o-projeto-no-prefect) | `uv run python fluxo.py` |
| 22 | [A cobertura como portão](modulo-4-orquestrar/aula-22-a-cobertura-como-portao) | `uv run python fluxo.py` |
| 23 | [Só o dia inteiro, e a segunda chance](modulo-4-orquestrar/aula-23-so-o-dia-inteiro-e-a-segunda-chance) | `uv run python conferir.py AAAA-MM-DD` e `uv run python fluxo.py agendar` |
| 24 | [A vigia: o que o portão deixa passar](modulo-4-orquestrar/aula-24-a-vigia) | `uv run python vigiar.py` e `uv run python fluxo.py` |
| 25 | [Uma execução por vez](modulo-4-orquestrar/aula-25-uma-execucao-por-vez) | `uv run prefect gcl create projeto-kabum --limit 1` e `uv run python fluxo.py` |
| 26 | [Os testes no GitHub e a prova final](modulo-4-orquestrar/aula-26-os-testes-no-github-e-a-prova-final) | `uv run pytest` e `uv run python fluxo.py` |

O README de cada pasta diz a ordem dos comandos. As pastas são cumulativas: a de cada aula tem tudo o que veio antes. O projeto pronto está em [final/](final), igual à aula 26. A partir da aula 15, o projeto precisa do Docker: o Postgres roda num container, na porta 5434. A partir da aula 21, ele precisa também do servidor do Prefect ligado (`uv run prefect server start`).

## O que foi rodado

Em 14 de novembro de 2026, com Python 3.13, uv, httpx 0.28.1, python-dotenv 1.2.4 e pytest 9.2.0. As saídas estão em [saidas/](saidas).

- A sequência das aulas 2 a 7, às 13h59: 472 produtos lidos, 458 diferentes, cobertura de 97,0%. A falta vem do empate na ordem padrão da API; a aula 5 explica.
- Do zero, três minutos depois (`rm -rf dados` e `uv run python rodar.py`): 4 pedidos à API e 1 à página da loja, 472 produtos lidos, 467 diferentes, cobertura de 98,9%, em 21 segundos.
- A prova da aula 7, às 23h34, num clone limpo do repositório, só com o `.env` copiado (`saidas/prova-copia-limpa.txt`): `uv sync`, `uv run python rodar.py` e `uv run pytest`. 478 produtos lidos, 477 diferentes, cobertura de 99,8%, em 20 segundos, e os 8 testes passando. Não apague o `dados/` para provar nada: o bronze guarda dias que a API não devolve mais.
- Mais cedo, no mesmo dia, a cobertura foi de 95,6% e de 100% em duas rodadas de 120 por página.
- Com 60 produtos por página, na primeira versão: o `links.next` levou a 12 páginas sobrepostas, e a cobertura variou entre 92,4% e 99,2% (`saidas/com-60-por-pagina/` e `saidas/armadilha-links-next*.txt`).
- `uv run pytest`: 8 testes no fim da aula 7, sem internet.

Em 15 de novembro de 2026, a etapa Transformar, com Polars 2.1.0 e DuckDB 2.0.0, sobre o bronze de 14 e 15 de novembro (`saidas/transformar/`):

- `uv run python rodar.py` na pasta do aluno com o `final/` e os dois dias (`saidas/transformar/rodada-final-dois-dias.txt`): sem pedido novo, a transformação de 953 linhas de 2 dias, 0 rejeitadas, 1 mudança de preço e 2 produtos que sumiram, no mesmo dia em que a conferência anotou 2 faltando. O relatório do dia 15: 476 linhas do dia, 0 rejeitadas, avisos 1 + 37 + 2, publicado.
- `uv run pytest`: 32 testes, sem internet.
- A prova da aula 14 num clone limpo da pasta do aluno, só com o `.env` copiado, às 1h07 (`saidas/transformar/prova-copia-limpa.txt`): 4 pedidos à API e 1 à loja, 479 produtos, cobertura de 100%, a transformação de um dia só (479 linhas, 0 mudanças, 0 sumiços), em 26 segundos; 32 testes passando. Uma primeira prova, às 0h51, antes da correção do portão para olhar só o dia novo (`prova-copia-limpa-0h51.txt`), mostrou os dois produtos que tinham sumido às 0h07 de volta, cada um em duas páginas.
- Cada pasta `aula-08` a `aula-14` foi rodada numa cópia limpa, com o mesmo bronze (`saidas/transformar/aula-NN.txt`).

Em 15 de novembro de 2026, a etapa Carregar, com Docker 29.5.2, Postgres 18.7 (imagem `postgres:18`) e psycopg 3.3.9, sobre o mesmo bronze de 14 e 15 de novembro (`saidas/carregar/`):

- As seis aulas rodadas na ordem, numa pasta de aluno nova e com o banco zerado, às 5h23 (`aula-15.txt` a `aula-20.txt`): 953 linhas em 2 dias (477 e 476), cada dia conferido pela contagem e pela soma dos preços finais (217.122.953 e 216.105.707 centavos). Carregar o dia 14 de novo apagou 477 linhas e gravou 477, e o banco ficou igual.
- A carga caiu no meio de propósito, com uma regra posta só no dia 15: o dia 14 ficou confirmado na tabela `cargas`, e a rodada seguinte começou no dia 15 (`aula-17.txt`).
- Sem a linha `Power` do `fabricantes.csv` e com ela de volta, a marca d'água disse que não havia nada a carregar, e o banco ficou com a marca vazia no produto 991784; o hash de cada dia achou os dois dias e recarregou (`aula-18.txt`).
- `uv run pytest`: 40 testes no fim da aula 20, sem internet e sem banco.
- A prova da aula 20 num clone da pasta do aluno, só com o `.env` copiado, contra a loja ao vivo, às 5h23 (`prova-copia-limpa.txt`): 5 pedidos à API e 1 à loja (a categoria tinha 481 produtos, 5 páginas de 120), cobertura de 100%, 481 linhas carregadas num banco novo; a segunda rodada sem pedido e sem carga.
- O `final/` num `git clone` deste repositório, numa pasta temporária, contra a loja ao vivo, às 5h44 (`prova-final-clone-do-repositorio.txt`): 5 páginas, 481 produtos lidos e 458 diferentes (cobertura de 95,2%: a paginação da aula 5 de novo), 458 linhas carregadas; a segunda rodada sem pedido e sem carga; o dia pedido pelo nome apagou 458 e gravou 458, com a mesma soma; 40 testes.
- Cada pasta `aula-15` a `aula-20` rodada numa cópia limpa, com o mesmo bronze e o banco zerado (`limpas.txt`).

Em 15 de novembro de 2026, a etapa Orquestrar, com Prefect 3.9.3 (servidor local), sobre as coletas de 14 e 15 de novembro e a loja ao vivo (`saidas/orquestrar/`):

- As seis aulas rodadas em ordem na pasta do aluno, das 9h10 às 9h32 (`a1-*.txt` a `a6-*.txt`), com as falhas provocadas de verdade: a rede fora (3 tentativas e Failed), o banco desligado (Crashed), uma página repetida de propósito (74,9%: a coleta foi para `dados/barrados/`, e a rodada seguinte coletou o dia de novo, com 100%), Ctrl+C no meio da coleta (a retomada pediu só as páginas que faltavam), duas rodadas ao mesmo tempo (sem o limite, 10 pedidos à loja e as duas em Failed no DuckDB; com ele, a segunda esperou 20 segundos e não pediu nada).
- A cobertura de coletas inteiras do mesmo dia variou entre 94,2% e 100%: a página 2 da API vem de dois jeitos. Com 94,2%, a vigia avisou a cobertura perto do mínimo e 28 sumidos, os mesmos 28 que a paginação perdeu.
- A agenda das 6h e das 18h, com o fuso de Brasília, marcou as execuções para 21:00 e 09:00 de UTC (`a3-agenda-run.txt`). Numa cópia do `fluxo.py` com um cron de dois em dois minutos, a execução marcada rodou sozinha (`verifica-cron.txt`).
- Os testes no GitHub, na branch `prova-ci-orquestracao` deste repositório, com o projeto na raiz: o primeiro push vermelho (o `SystemExit` do contato no import), os seguintes verdes, 47 testes.
- A prova da aula 26 num clone da pasta do aluno, com Ctrl+C depois da página 2 e uma execução pedida ao agendamento (`a6-prova-*.txt`): 99,0% de cobertura, 475 linhas, a rodada do agendamento sem pedido e sem carga.
- Uma vaga do limite presa: com o servidor do Prefect morto no meio de uma execução e ligado de novo, `active_slots` ficou em 1 por mais de 7 minutos (`vaga-presa-servidor-reiniciado.txt`); o runbook diz como soltar.
- Cada pasta `aula-21` a `aula-26` rodada numa cópia limpa, com banco novo e a loja ao vivo, duas vezes (`limpas.txt`).

## Regras do projeto

Estão em [PADROES.md](PADROES.md).
