CREATE TABLE IF NOT EXISTS urls (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(50) UNIQUE,
  created_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS url_checks (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id BIGINT REFERENCES urls(id),
  status_code INT,
  h1 TEXT,
  title TEXT,
  description TEXT,
  created_at TIMESTAMP
);