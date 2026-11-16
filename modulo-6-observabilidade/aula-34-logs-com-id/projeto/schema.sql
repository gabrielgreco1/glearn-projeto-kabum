-- As tabelas do projeto no Postgres. O banco.py roda este arquivo antes de cada carga:
-- IF NOT EXISTS cria só o que falta, então rodar de novo não muda nada.

-- O histórico de preços: uma linha por produto por dia, como a silver. A chave é o par (dia, id).
-- As regras de erro do validar.py viram CHECK; os avisos ficam na coluna avisos, como dado.
CREATE TABLE IF NOT EXISTS precos (
    dia            date NOT NULL,
    id             bigint NOT NULL,
    titulo         text NOT NULL,
    e_placa        boolean NOT NULL,
    chip           text,
    modelo         text,
    marca          text,
    fabricante     text,
    preco_cartao   integer NOT NULL CHECK (preco_cartao BETWEEN 100 AND 50000000),
    preco_pix      integer NOT NULL,
    desconto_pix   smallint NOT NULL,
    preco_oferta   integer,
    oferta_termina timestamptz,
    em_oferta      boolean NOT NULL,
    preco_final    integer NOT NULL CHECK (preco_final > 0),
    estoque        integer,
    is_marketplace boolean NOT NULL,
    vendedor       text,
    link           text NOT NULL,
    avisos         text,
    PRIMARY KEY (dia, id),
    CHECK (preco_pix <= preco_cartao)
);

-- Uma linha por dia carregado: quantas linhas saíram, quantas entraram e a soma que confere o dia.
CREATE TABLE IF NOT EXISTS cargas (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    feita_em   timestamptz NOT NULL DEFAULT now(),
    dia        date NOT NULL,
    apagadas   integer NOT NULL,
    inseridas  integer NOT NULL CHECK (inseridas > 0),
    soma_final bigint NOT NULL
);

-- Colunas que vieram depois da primeira carga. ADD COLUMN IF NOT EXISTS muda a tabela que já existe, sem apagar nada.
-- O hash do dia diz se a silver daquele dia mudou desde a última carga; as cargas antigas ficam com ele vazio.
ALTER TABLE cargas ADD COLUMN IF NOT EXISTS hash_dia char(64);

-- O id da execução que gravou: o mesmo que está em cada linha de logs/kabum.jsonl e na URL do flow run no Prefect.
-- As linhas e as cargas de antes desta coluna ficam com ele vazio.
ALTER TABLE cargas ADD COLUMN IF NOT EXISTS execucao_id uuid;
ALTER TABLE precos ADD COLUMN IF NOT EXISTS execucao_id uuid;

-- A conferência de cada dia de coleta, do conferencia.csv: quantos produtos vieram e quantos a API declarou.
-- Conferir de novo o mesmo dia troca a linha dele, como no CSV.
CREATE TABLE IF NOT EXISTS coletas (
    dia        date PRIMARY KEY,
    diferentes integer NOT NULL,
    declarado  integer NOT NULL,
    loja       integer,
    cobertura  numeric(4, 3) NOT NULL CHECK (cobertura >= 0)
);

-- O que o histórico responde, como consultas guardadas. CREATE OR REPLACE VIEW troca a consulta e não guarda linha:
-- cada SELECT na view lê a tabela precos na hora, com o que acabou de ser carregado.

-- Uma linha por produto: o primeiro e o último dia em que ele veio, e o preço desse último dia.
CREATE OR REPLACE VIEW produtos AS
SELECT DISTINCT ON (id)
       id, titulo, marca, modelo, e_placa,
       min(dia) OVER (PARTITION BY id) AS primeiro_dia,
       dia AS ultimo_dia,
       preco_final AS ultimo_preco
FROM precos
ORDER BY id, dia DESC;

-- Os produtos que não vieram no último dia carregado, com a cobertura desse dia: abaixo de 1, pode ser a paginação.
CREATE OR REPLACE VIEW sumidos AS
WITH ultimo AS (SELECT max(dia) AS dia FROM precos)
SELECT p.id, p.titulo, p.ultimo_dia, p.ultimo_preco, ultimo.dia AS faltou_em, c.cobertura
FROM produtos p
JOIN ultimo ON p.ultimo_dia < ultimo.dia
LEFT JOIN coletas c ON c.dia = ultimo.dia
ORDER BY p.id;
