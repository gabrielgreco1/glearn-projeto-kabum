# Projeto Kabum

Objetivo: guardar, um dia depois do outro, o preço de todas as placas de vídeo da Kabum, para ter o histórico de cada produto.
Plano: a página da categoria busca os produtos numa API de catálogo. O programa pede essa mesma API, página por página, com pausa, e guarda cada resposta como veio. Se o site recusar, o programa para. Depois, a etapa Transformar limpa, confere e resume o histórico, sem pedir nada ao site.

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

Rode uma vez por dia. A rodada faz 4 pedidos à API e 1 à página da loja, com 3 segundos de pausa entre eles, e leva cerca de 20 segundos. Rodar de novo no mesmo dia não pede nada de novo: as páginas da API e a página da loja já estão na pasta do dia. A etapa Transformar roda no fim, em menos de um segundo, sobre todos os dias guardados.

Para rodar só a etapa Transformar, sem coleta: `uv run python transformar.py`. Para medir o `precos.csv`: `uv run python perfil.py`.

No Windows, os comandos são os mesmos no PowerShell.

## As etapas

| Etapa | Programa | O que faz |
|---|---|---|
| Extrair | `coletar.py` | Pede as páginas da API e guarda cada resposta em `dados/bronze/<dia>/` |
| Extrair | `conferir.py` | Mede a cobertura contra o total da API e da loja e anota o dia em `conferencia.csv` |
| Extrair | `tabela.py` | Monta o `precos.csv`, uma linha por produto por dia, com os campos como a API mandou |
| Transformar | `silver.py` | Preços em centavos, o fim da oferta no horário de Brasília, o preço final, placa ou acessório, chip, modelo e marca |
| Transformar | `validar.py` | Oito regras escritas: o que falha numa regra de erro vai para os rejeitados, com o motivo; os avisos ficam marcados |
| Transformar | `qualidade.py` | O relatório da rodada e a decisão de publicar |
| Transformar | `historico.py` | A gold, em SQL: mudanças de preço, produtos que sumiram e o menor preço de cada modelo por dia |

O `rodar.py` chama as três etapas da extração e depois o `transformar.py`, que chama as quatro da transformação.

## O que sai

Tudo fica em `dados/`, que não vai para o Git:

- `bronze/AAAA-MM-DD/pagina-001.json` a `pagina-004.json`: a resposta da API, como veio, uma pasta por dia. Na mesma pasta, `loja.html`: a página da categoria, de onde sai o total que a loja mostra.
- `conferencia.csv`: uma linha por dia de coleta, com o que faltou. Conferir de novo o mesmo dia troca a linha dele.
- `precos.csv`: uma linha por produto por dia, com os campos como a API mandou. O preço grande do cartão, quando o produto está em oferta, é o `oferta_price_with_discount`.
- `silver/precos.parquet`: a mesma linha por produto por dia, limpa e conferida. Os preços estão em centavos (`213918` é R$ 2.139,18). `preco_final` é o preço no Pix daquele dia, já com a oferta, quando havia uma. A coluna `avisos` diz que regra de aviso a linha não passou.
- `silver/rejeitados.csv`: uma linha por regra de erro quebrada, com o motivo e o valor. Na rodada de 15 de novembro de 2026, vazio.
- `qualidade/AAAA-MM-DD.json`: o relatório de cada rodada: lidos, válidos, rejeitados por regra, avisos por regra, cobertura e se a rodada foi publicada.
- `gold/mudancas.parquet`: cada vez que um produto mudou de preço ou entrou e saiu de oferta, comparado com o último dia em que apareceu.
- `gold/sumiram.parquet`: os produtos que estavam no dia anterior e não vieram no dia, com a cobertura daquele dia.
- `gold/modelos.parquet`: por dia e por modelo, quantos anúncios, o menor preço, a mediana e o produto mais barato.
- `ultima_recusa.html`: só aparece se o site recusar um pedido. É a resposta da recusa, para você ler.

A tabela `fabricantes.csv`, na raiz, troca o fabricante como a loja escreve pela marca. Ela vai para o Git. Quando aparece um fabricante novo, o `transformar.py` avisa, e você acrescenta uma linha.

## Regras de coleta

- Todo pedido leva um `User-Agent` com o nome do projeto e um contato de verdade.
- Um pedido de cada vez, com 3 segundos de espera depois de cada um. No máximo 20 páginas por dia.
- Só uma categoria: placas de vídeo.
- O pedido não usa ordenação (`sort`): o `robots.txt` da loja pede que programas não usem.
- Qualquer resposta que não seja um JSON com status 200 para o programa. Uma página de desafio, um 403 ou um 429 é o site dizendo não. O programa guarda a resposta e para. Não há troca de identidade, proxy nem navegador automatizado.

## O que a rodada de 14 de novembro de 2026 mostrou

- O `links.next` da API trocou o tamanho da página de 60 para 40 na página 7. Seguido ao pé da letra, ele levou a 12 páginas, 613 linhas e só 468 produtos diferentes. O programa monta o endereço de cada página com o tamanho fixo e para no total que a primeira página declara.
- A paginação da API perde produtos. A ordem padrão tem empates, e cada página desempata de um jeito: alguns produtos vêm em duas páginas e outros em nenhuma. Repetir a mesma página dá o mesmo resultado, então repetir a volta não resolve. Nas rodadas do dia, a cobertura ficou entre 92,4% e 100%.
- O `robots.txt` da loja pede que programas não usem `sort`, então o programa não troca a ordem.
- O programa tira os repetidos pelo `id`, mede a cobertura contra o total que a API declara e anota a conferência de cada dia em `dados/conferencia.csv`. Abaixo de 90%, ele para.
- O filtro por fabricante fecharia a lacuna, porque cada fabricante cabe numa página só. Mas são 42 fabricantes na categoria: seriam dezenas de pedidos por dia em vez de 4, com uma lista de fabricantes que também muda. Este projeto não usa: mede a falta e anota.
- A API aceita até 120 produtos por página (pedimos 500 e vieram 120). São 4 pedidos por dia.

## O que a etapa Transformar mostrou, com os dias 14 e 15 de novembro de 2026

- 953 linhas de 2 dias, 478 produtos. `old_price` é sempre 0 e `available` é sempre verdadeiro: a listagem só traz o que está à venda.
- A API manda três preços: `price` é o do cartão, `price_with_discount` é o do Pix, com o desconto de `discount_percentage`, e o bloco da oferta traz o preço da oferta. Em 136 linhas havia oferta; em 2 delas, a oferta custava o mesmo que o Pix.
- Em 46 das 953 linhas, multiplicar o preço por 100 e cortar as casas dá um centavo a menos (2139.18 vira 213917). O `silver.py` arredonda antes de converter.
- 112 linhas são acessórios (suportes, cabos e até uma caixa de som), no menu "Acessórios" da categoria. 74 linhas de placa ficaram sem modelo, como as G210 e as placas Quadro; elas ficam na silver com o aviso `placa_com_modelo`.
- A loja escreve o fabricante de 42 jeitos. "Outros", "Generico" e "OEM" não dizem quem fez; "Nvidia" e "RX" são nomes de chip; "PALIT" e "Palit Microsystem" são o mesmo. Depois da tabela `fabricantes.csv`, ficam 34 marcas, e 185 linhas sem marca.
- Nenhuma linha quebrou regra de erro. Quatro linhas passaram de três vezes a mediana do modelo: uma GTX 1660 Super a R$ 5.452,20 e uma GT 730 a R$ 1.569,90, nos dois dias.
- Entre os dois dias, 1 produto mudou de preço (um suporte Redragon, de R$ 73,36 para R$ 79,90) e 2 sumiram. A conferência do dia 15 diz que faltaram 2 produtos: os dois sumiços podem ser da paginação, e não da loja. Na prova numa cópia limpa, 44 minutos depois, os dois vieram de novo, cada um em duas páginas: eram da paginação.

## O que o projeto não faz

- O preço Prime, que a loja mostra só para assinantes com login, não entra. O projeto não entra em conta nenhuma.
- O modelo sai do título com uma expressão regular. Títulos sem RTX, GTX, GT ou RX antes do número (as G210, as Quadro, as R5 230) ficam sem modelo e com aviso.
- Um produto que some num dia de cobertura abaixo de 100% pode ter sido perdido pela paginação. A gold mostra a cobertura ao lado; não decide sozinha.
- A oferta vale pelo dia: o histórico guarda o dia da coleta, e não a hora. Uma oferta que termina às 10h59 conta como em oferta na coleta das 15h do mesmo dia.
- Nada roda sozinho: o programa roda quando você manda.
