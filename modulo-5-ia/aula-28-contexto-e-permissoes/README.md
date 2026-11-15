# Contexto e permissões

Aula PI-02 do curso. O `CLAUDE.md`, o `.claude/settings.json` e a issue 2 (`barato.py`) feita pelo agente com as regras.

Na pasta `projeto/`:

```
uv run pytest
uv run python barato.py "RTX 5070"
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
