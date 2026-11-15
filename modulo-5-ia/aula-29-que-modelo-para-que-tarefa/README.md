# Que modelo para que tarefa

Aula PI-03 do curso. Nenhum código novo: a issue 1 em cinco execuções (Haiku low e high, Sonnet, Opus, Fable) e a issue 3 com Haiku e Opus. A tabela está em `projeto/custos.md`.

Na pasta `projeto/`:

```
claude -p "$(cat ../backlog/1-kabum-testes.md)" --model haiku --effort low --permission-mode acceptEdits --allowedTools "Bash(uv run pytest*)" "Bash(git *)" --output-format json
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
