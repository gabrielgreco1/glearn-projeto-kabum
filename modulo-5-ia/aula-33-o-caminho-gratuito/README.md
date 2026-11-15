# O caminho gratuito e a prova final

Aula PI-07 do curso. O `opencode.json` com as permissões e a tabela final em `custos.md`. O modelo local lê, você edita: `../agentes/perguntar_local.py`.

Na pasta `projeto/`:

```
ollama pull llama3.2:3b
opencode run --auto -m ollama/llama3.2:3b "$(cat ../backlog/1-kabum-testes.md)"
uv run --no-project python ../agentes/perguntar_local.py . llama3.2:3b HEAD~1
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
