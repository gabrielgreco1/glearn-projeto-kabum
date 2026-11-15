# Subagentes e trabalho em paralelo

Aula PI-04 do curso. Os subagentes `pesquisador` e `revisor` em `.claude/agents/`, a issue 3 com a decisão do time (quatro categorias, teto de 40 páginas por dia) e a issue 4 (README), feitas ao mesmo tempo em duas worktrees.

Na pasta `projeto/`:

```
git worktree add ../p4-categorias -b issue-categorias main
git worktree add ../p4-readme -b issue-readme main
uv run pytest
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
