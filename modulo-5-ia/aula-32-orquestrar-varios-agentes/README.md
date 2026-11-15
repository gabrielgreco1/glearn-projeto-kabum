# Orquestrar vários agentes

Aula PI-06 do curso. O Kabum não muda nesta aula. As issues 5 e 6 do G1 saem do roteiro `../agentes/orquestrar.py`; o resultado está no repositório do Projeto G1, em `modulo-5-ia/aula-32-orquestrar-varios-agentes/`.

Na pasta `projeto/`:

```
cd ../agentes
uv run --no-project python orquestrar.py tarefas.json --ver
uv run --no-project python orquestrar.py tarefas.json
```

No PowerShell, os mesmos comandos; troque `$(cat arquivo)` por `(Get-Content arquivo -Raw)` e o `<` do psql por `Get-Content papel_leitura.sql | docker compose exec -T banco psql -U postgres -q`.
