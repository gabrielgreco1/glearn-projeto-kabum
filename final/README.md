# Projeto Kabum

Objetivo: guardar, um dia depois do outro, o preço de todas as placas de vídeo da Kabum, para ter o histórico de cada produto.
Plano: a página da categoria busca os produtos numa API de catálogo. O programa pede essa mesma API, página por página, com pausa, e guarda cada resposta como veio. Se o site recusar, o programa para.

## Como rodar

Você precisa do [uv](https://docs.astral.sh/uv/) instalado.

```
cp .env.example .env
```

Abra o `.env` e troque o contato pelo seu. Depois:

```
uv sync
uv run python rodar.py
uv run pytest
```

Rode uma vez por dia. A rodada faz 4 pedidos à API e 1 à página da loja, com 3 segundos de pausa entre eles, e leva cerca de 20 segundos. Rodar de novo no mesmo dia não pede as páginas de novo.

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/AAAA-MM-DD/pagina-001.json` a `pagina-004.json`: a resposta da API, como veio, uma pasta por dia.
- `conferencia.csv`: uma linha por conferência, com o que faltou.
- `precos.csv`: uma linha por produto por dia, com os campos como a API mandou. O preço grande do cartão, quando o produto está em oferta, é o `oferta_price_with_discount`.
- `ultima_recusa.html`: só aparece se o site recusar um pedido. É a resposta da recusa, para você ler.

## Regras de coleta

- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 3 segundos de espera depois de cada um. No máximo 20 páginas por dia.
- Só uma categoria: placas de vídeo.
- O pedido não usa ordenação (`sort`): o `robots.txt` da loja pede que programas não usem.
- Qualquer resposta que não seja um JSON com status 200 para o programa. Uma página de desafio, um 403 ou um 429 é o site dizendo não. O programa guarda a resposta e para. Não há troca de identidade, proxy nem navegador automatizado.

## O que a rodada de 14 de novembro de 2026 mostrou

- O `links.next` da API trocou o tamanho da página de 60 para 40 na página 7. Seguido ao pé da letra, ele levou a 12 páginas, 613 linhas e só 468 produtos diferentes. O programa monta o endereço de cada página com o tamanho fixo e para no total que a primeira página declara.
- A paginação da API perde produtos. A ordem padrão tem empates, e cada página desempata de um jeito: alguns produtos vêm em duas páginas e outros em nenhuma. Repetir a mesma página dá o mesmo resultado, então repetir a volta não resolve. Nas rodadas do dia, a cobertura ficou entre 92,4% e 99,6%.
- O `robots.txt` da loja pede que programas não usem `sort`, então o programa não troca a ordem.
- O programa tira os repetidos pelo `id`, mede a cobertura contra o total que a API declara e anota cada conferência em `dados/conferencia.csv`. Abaixo de 90%, ele para.
- O filtro por fabricante fecharia a lacuna, porque cada fabricante cabe numa página só. Ele usa um texto em base64, que o curso ensina na aula E10-05. Este projeto não usa.
- A API aceita até 120 produtos por página (pedimos 500 e vieram 120). São 4 pedidos por dia.

## O que o projeto não faz

- Os preços ficam como a API mandou, sem conversão nem limpeza. Isso é da etapa Transformar.
- O preço Prime, que a loja mostra só para assinantes com login, não entra. O projeto não entra em conta nenhuma.
- Nada roda sozinho: o programa roda quando você manda.
