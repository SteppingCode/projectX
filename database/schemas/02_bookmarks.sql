CREATE TABLE IF NOT EXISTS bookmarks (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title VARCHAR(255),
    description TEXT,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

ALTER TABLE bookmarks ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('russian', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('russian', coalesce(description, '')), 'B')
) STORED;

CREATE INDEX IF NOT EXISTS bookmarks_search_idx ON bookmarks USING GIN (search_vector);