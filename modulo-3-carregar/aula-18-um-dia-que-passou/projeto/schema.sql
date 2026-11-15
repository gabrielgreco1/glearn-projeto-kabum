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
