# Projeto Kabum (G learn)

Repositório de referência do Projeto Kabum do curso G learn: um programa em Python que guarda, uma vez por dia, o preço de todas as placas de vídeo da Kabum, pela API de catálogo que a própria página da loja usa, e mede quanto da categoria cada coleta trouxe.

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

O README de cada pasta diz a ordem dos comandos. O projeto pronto está em [final/](final), igual à aula 7.

## O que foi rodado

Em 14 de novembro de 2026, com Python 3.13, uv, httpx 0.28.1, python-dotenv 1.2.4 e pytest 9.2.0. As saídas estão em [saidas/](saidas).

- Do zero (`rm -rf dados` e `uv run python rodar.py`): 4 pedidos à API e 1 à página da loja, 474 produtos, cobertura de 100%, em 22 segundos.
- A sequência das aulas 2 a 7, minutos antes: 472 produtos lidos, 451 diferentes, cobertura de 95,6%. A falta vem do empate na ordem padrão da API; a aula 5 explica.
- Com 60 produtos por página, na primeira versão: o `links.next` levou a 12 páginas sobrepostas, e a cobertura variou entre 92,4% e 99,2% (`saidas/com-60-por-pagina/` e `saidas/armadilha-links-next*.txt`).
- `uv run pytest`: 7 testes, sem internet.

## Regras do projeto

Estão em [PADROES.md](PADROES.md).
