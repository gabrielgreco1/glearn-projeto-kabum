# Padrões do Projeto Kabum

## Código

- Python 3.13, a versão que o `uv python pin` gravou no `.python-version`.
- Rodamos tudo com `uv`: `uv sync` para instalar, `uv run python arquivo.py` para rodar, `uv run pytest` para testar.
- Os programas ficam na raiz da pasta do projeto, um arquivo por etapa: `coletar.py`, `ler.py`, `conferir.py`, `tabela.py`, `rodar.py`.
- Nomes de arquivos, funções e variáveis em português. Os campos que vêm da API mantêm o nome da API.
- O programa registra com `logging`.
- Testes com pytest. Os testes usam amostras escritas à mão e rodam sem internet.

## Configuração e segredos

- O contato do `User-Agent` fica no arquivo `.env`. O `.env.example` mostra o campo, sem dado de verdade.
- O `.env` nunca vai para o Git. Ele está no `.gitignore`.
- Nenhuma senha, chave ou conta. O projeto não entra em conta nenhuma da loja.

## Dados

- Tudo o que o programa baixa ou gera fica em `dados/`. O que veio da API fica em `dados/bronze/<dia>/`, como veio.
- Os valores ficam como a API mandou. Converter e limpar é da etapa Transformar.
- A pasta `dados/` não vai para o Git. O catálogo é da Kabum.
- Rodar duas vezes no mesmo dia não pede de novo o que já está guardado.

## Educação com o site da Kabum

- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 3 segundos de espera depois de cada um. Uma categoria só. No máximo 20 páginas por dia.
- O pedido não usa `sort`: o `robots.txt` da loja pede que programas não usem.
- Qualquer resposta que não seja JSON com status 200 para o programa, que guarda a resposta em `dados/ultima_recusa.html`. Não tente contornar: sem trocar de identidade, sem proxy, sem navegador automatizado, sem resolver desafio.

## Git

- O aluno trabalha na pasta dele, `projeto-kabum/`, criada na aula 1. Ela é o repositório do aluno.
- Este repositório do curso é a referência.
- Um commit por aula, com push ao fim de cada aula.
