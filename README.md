# Projeto Kabum (G learn)

Repositório de referência do Projeto Kabum do curso G learn: um programa em Python que guarda, uma vez por dia, o preço de todas as placas de vídeo da Kabum, pela API de catálogo que a própria página da loja usa, e mede quanto da categoria cada coleta trouxe. Na segunda etapa, o mesmo programa limpa, confere e resume esse histórico: preços em centavos, regras escritas, um relatório por rodada e as mudanças de preço de um dia para o outro.

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

O README de cada pasta diz a ordem dos comandos. As pastas são cumulativas: a de cada aula tem tudo o que veio antes. O projeto pronto está em [final/](final), igual à aula 14.

## O que foi rodado

Em 14 de novembro de 2026, com Python 3.13, uv, httpx 0.28.1, python-dotenv 1.2.4 e pytest 9.2.0. As saídas estão em [saidas/](saidas).

- A sequência das aulas 2 a 7, às 13h59: 472 produtos lidos, 458 diferentes, cobertura de 97,0%. A falta vem do empate na ordem padrão da API; a aula 5 explica.
- Do zero, três minutos depois (`rm -rf dados` e `uv run python rodar.py`): 4 pedidos à API e 1 à página da loja, 472 produtos lidos, 467 diferentes, cobertura de 98,9%, em 21 segundos.
- A prova da aula 7, às 23h34, num clone limpo do repositório, só com o `.env` copiado (`saidas/prova-copia-limpa.txt`): `uv sync`, `uv run python rodar.py` e `uv run pytest`. 478 produtos lidos, 477 diferentes, cobertura de 99,8%, em 20 segundos, e os 8 testes passando. Não apague o `dados/` para provar nada: o bronze guarda dias que a API não devolve mais.
- Mais cedo, no mesmo dia, a cobertura foi de 95,6% e de 100% em duas rodadas de 120 por página.
- Com 60 produtos por página, na primeira versão: o `links.next` levou a 12 páginas sobrepostas, e a cobertura variou entre 92,4% e 99,2% (`saidas/com-60-por-pagina/` e `saidas/armadilha-links-next*.txt`).
- `uv run pytest`: 8 testes no fim da aula 7, sem internet.

Em 15 de novembro de 2026, a etapa Transformar, com Polars 2.1.0 e DuckDB 2.0.0, sobre o bronze de 14 e 15 de novembro (`saidas/transformar/`):

- `uv run python rodar.py` na pasta `final/`: a coleta do dia 15 (476 de 478 produtos, 99,6%) e a transformação de 953 linhas de 2 dias: 953 válidas, 0 rejeitadas, 80 avisos, 1 mudança de preço e 2 produtos que sumiram, no mesmo dia em que a conferência anotou 2 faltando.
- `uv run pytest`: 31 testes, sem internet.
- Cada pasta `aula-08` a `aula-14` foi rodada numa cópia limpa, com o mesmo bronze.

## Regras do projeto

Estão em [PADROES.md](PADROES.md).
