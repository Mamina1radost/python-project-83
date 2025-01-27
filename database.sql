CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL
);


CREATE TABLE IF NOT EXISTS url_checks(
    id SERIAL PRIMARY KEY,
    url_id INT,
    status_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP NOT NULL
);