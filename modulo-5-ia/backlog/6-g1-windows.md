# G1: os testes também no Windows, no CI

Metade da turma usa Windows. O workflow `.github/workflows/testes.yml` só roda em `ubuntu-latest`.

Pronto quando:
- O workflow roda os testes em `ubuntu-latest` e em `windows-latest`, numa matriz.
- Nada mais muda.
- `uv run pytest` passa na sua máquina.
