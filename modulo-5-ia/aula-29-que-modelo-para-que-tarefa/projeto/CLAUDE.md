# Projeto Kabum

Histórico diário do preço das placas de vídeo da Kabum, pela API de catálogo que a página da loja usa.
Etapas: extrair (`coletar.py`, `conferir.py`, `tabela.py`), transformar (`silver.py`, `validar.py`, `qualidade.py`,
`historico.py`), carregar (`banco.py`, `carregar.py`) e orquestrar (`fluxo.py`, `vigiar.py`). Regras completas: `README.md`.

## Como trabalhar aqui

- Responda e escreva commits em português do Brasil.
- Python 3.13 com `uv`: `uv run pytest` para testar, `uv run python arquivo.py` para rodar. Nunca `pip install`.
- Nomes de arquivos, funções e variáveis em português. Os campos da API mantêm o nome da API.
- Tabelas com Polars, perguntas em SQL com DuckDB. Preço sempre em centavos, como inteiro.
- Caminhos com `pathlib.Path`. O projeto roda em macOS, Linux e Windows: nada de comando de shell dentro do código.

## Testes

- Teste é a especificação. Nunca apague, pule ou mude um teste para ele passar; se o teste parece errado, pare e explique.
- Teste novo usa tabela escrita à mão ou um arquivo em `testes/`, sem internet e sem banco.
- Rode `uv run pytest` antes de dizer que terminou.

## A loja

- Você NÃO roda `coletar.py`, `rodar.py` nem `fluxo.py`: eles pedem à loja de verdade. Quem roda é a pessoa.
- Um pedido por vez, 3 segundos de pausa (`PAUSA`) depois de cada um, no máximo 20 páginas por dia (`LIMITE_PAGINAS`)
  somando tudo. Mudança que aumenta o número de pedidos por dia precisa ser dita no começo da resposta, com a conta.
- Nada de `sort` no pedido, troca de User-Agent, proxy ou navegador automatizado.

## Git

- Uma branch por issue, um commit por mudança, mensagem que diz o porquê. Não faça push nem abra PR.
- `dados/` e `.env` não vão para o Git, e você não lê o `.env`.
