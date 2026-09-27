CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS stocks (
  id BIGSERIAL PRIMARY KEY,
  symbol VARCHAR(16) UNIQUE NOT NULL,
  company_name VARCHAR(160) NOT NULL,
  sector VARCHAR(80) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_prices (
  time TIMESTAMPTZ NOT NULL,
  stock_id BIGINT NOT NULL REFERENCES stocks(id),
  open NUMERIC(18,6) NOT NULL,
  high NUMERIC(18,6) NOT NULL,
  low NUMERIC(18,6) NOT NULL,
  close NUMERIC(18,6) NOT NULL,
  volume BIGINT NOT NULL DEFAULT 0,
  PRIMARY KEY (time, stock_id)
);
SELECT create_hypertable('daily_prices', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS financial_metrics (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT NOT NULL REFERENCES stocks(id),
  period_end DATE NOT NULL,
  period_type VARCHAR(12) NOT NULL,
  revenue NUMERIC,
  net_income NUMERIC,
  total_assets NUMERIC,
  equity NUMERIC,
  net_debt NUMERIC,
  pe_ratio NUMERIC,
  pb_ratio NUMERIC,
  ev_ebitda NUMERIC,
  roe NUMERIC,
  current_ratio NUMERIC,
  UNIQUE(stock_id, period_end, period_type)
);

CREATE TABLE IF NOT EXISTS stock_risk_metrics (
  id BIGSERIAL PRIMARY KEY,
  stock_id BIGINT NOT NULL REFERENCES stocks(id),
  metric_date DATE NOT NULL,
  var_95 NUMERIC,
  var_99 NUMERIC,
  volatility_20d NUMERIC,
  volatility_90d NUMERIC,
  sharpe NUMERIC,
  sortino NUMERIC,
  beta_bist100 NUMERIC,
  max_drawdown NUMERIC,
  altman_z_score NUMERIC,
  UNIQUE(stock_id, metric_date)
);
