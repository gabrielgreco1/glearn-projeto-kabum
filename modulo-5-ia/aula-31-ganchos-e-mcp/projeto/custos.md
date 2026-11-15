# Custo e acerto de cada execução

Claude Code 2.1.325, 15/11/2026. Custo: o `total_cost_usd` que o próprio Claude Code calcula, a preço de tabela (na assinatura, não é cobrado). Uma execução por linha: rodar de novo dá outros números.

| Issue | Ferramenta e modelo | Esforço | Pedidos | Tempo | Custo (US$) | Resultado |
|---|---|---|---|---|---|---|
| 1, testes quebrados | Claude Code, Haiku 5.5 (sessão, modo manual) | medium | 5 | 23 s de modelo | 0,0085 | consertou as duas linhas, 47 passed |
| 1, testes quebrados | Claude Code, Haiku 5.5 | low | 10 | 34 s | 0,0064 | 47 passed |
| 1, testes quebrados | Claude Code, Haiku 5.5 | high | 11 | 40 s | 0,0075 | 47 passed, 2 commits |
| 1, testes quebrados | Claude Code, Sonnet 5.5 | high | 5 | 28 s | 0,0643 | 47 passed |
| 1, testes quebrados | Claude Code, Opus 5.5 | medium | 5 | 32 s | 0,1697 | 47 passed |
| 1, testes quebrados | Claude Code, Fable 5.2 | medium | 3 | 38 s | 0,2472 | 47 passed |
| 2, barato.py, sem CLAUDE.md | Claude Code, Haiku 5.5 | medium | 17 | 81 s | 0,0166 | funciona; inglês, sem commit |
| 2, barato.py, com CLAUDE.md | Claude Code, Haiku 5.5 | medium | 11 | 63 s | 0,0126 | funciona; português, commit |
| 3, categorias | Claude Code, Haiku 5.5 | medium | 15 | 176 s | 0,0227 | subiu o teto para 35 sozinho |
| 3, categorias | Claude Code, Opus 5.5 | medium | 4 | 44 s | 0,1486 | parou e deu três opções |
| 3, categorias, com a decisão | Claude Code, Sonnet 5.5 + pesquisador (Haiku) + revisor (Sonnet) | high | 29 + 12 | 289 s | 0,7306 | 63 passed |
| 4, README | Claude Code, Haiku 5.5 | medium | 10 | 67 s | 0,0100 | só o README |
| 5, G1 Economia | Claude Code, Sonnet 5.5 (orquestrar.py) | high | 37 | 180 s | 0,5069 | 64 passed |
| 6, G1 Windows no CI | Claude Code, Haiku 5.5 (orquestrar.py) | low | 5 | 40 s | 0,0032 | 52 passed |
| 1, testes quebrados | opencode 2.3.0, llama3.2:3b (8k) | — | 1 | 64 s | 0 | nada mudou |
| 1, testes quebrados | aider 0.86.2, llama3.2:3b | — | — | interrompido | 0 | propôs apagar testes |
| 1, testes quebrados | perguntar_local.py, llama3.2:3b (4k) | — | 1 | 15,5 s | 0 | apontou a linha do regex |
