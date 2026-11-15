# Ganchos e MCP

Aula PI-05 do curso. Os ganchos `.claude/hooks/barrar.py` e `testar.py`, o servidor MCP só de leitura (`mcp_kabum.py`, `.mcp.json`, `papel_leitura.sql`) e o aviso de anúncio suspeito no `barato.py`. O exercício da instrução escondida está em `../backlog/plantar.sql`.

Na pasta `projeto/`:

```
docker compose up -d --wait
uv run python carregar.py
docker compose exec -T banco psql -U postgres -q < papel_leitura.sql
claude
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
