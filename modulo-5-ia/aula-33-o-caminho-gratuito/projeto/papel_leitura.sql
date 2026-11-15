-- O papel que o servidor MCP usa: entra no banco e só lê. Rodar de novo não muda nada.
-- docker compose exec -T banco psql -U postgres < papel_leitura.sql
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'kabum_leitura') THEN
    CREATE ROLE kabum_leitura LOGIN PASSWORD 'leitura';
  END IF;
END $$;
GRANT CONNECT ON DATABASE postgres TO kabum_leitura;
GRANT USAGE ON SCHEMA public TO kabum_leitura;
GRANT SELECT ON precos, coletas, cargas, produtos, sumidos TO kabum_leitura;
ALTER ROLE kabum_leitura SET statement_timeout = '3s';
ALTER ROLE kabum_leitura SET default_transaction_read_only = on;
