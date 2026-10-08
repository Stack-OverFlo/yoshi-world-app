
CREATE TABLE IF NOT EXISTS yoshis (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    color VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO yoshis (name, color)
VALUES
    ('Yoshi', 'green'),
    ('Red Yoshi', 'red'),
    ('Blue Yoshi', 'blue');
