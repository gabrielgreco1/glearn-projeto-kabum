# O backlog e como o agente trabalha

Aula PI-01 do curso. O commit do colega (`git am ../backlog/colega.patch`) quebra dois testes; a issue 1 resolvida pelo Claude Code numa sessão em modo manual. A pasta `projeto/` é o Projeto Kabum depois do conserto.

Na pasta `projeto/`:

```
claude --model haiku --permission-mode manual
uv run pytest
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
