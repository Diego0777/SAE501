-- ============================================================================
-- Base de données TV Series - SQLite
-- ============================================================================

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    language_preference TEXT DEFAULT 'vf' CHECK(language_preference IN ('vf', 'vo')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);

-- Table des séries
CREATE TABLE IF NOT EXISTS series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE NOT NULL,
    language TEXT NOT NULL CHECK(language IN ('vf', 'vo')),
    average_rating REAL DEFAULT 0.0,
    num_ratings INTEGER DEFAULT 0,
    popularity_score REAL DEFAULT 0.0,
    poster_url TEXT,
    poster_data BLOB
);

CREATE INDEX idx_series_title ON series(title);
CREATE INDEX idx_series_language ON series(language);
CREATE INDEX idx_series_popularity ON series(popularity_score DESC);

-- Table des mots-clés
CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serie_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    score REAL NOT NULL,
    FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE
);

CREATE INDEX idx_keywords_serie_id ON keywords(serie_id);
CREATE INDEX idx_keywords_keyword ON keywords(keyword);

-- Table des notations
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    serie_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE,
    UNIQUE(user_id, serie_id)
);

CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_serie_id ON ratings(serie_id);

-- Table des sessions
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);

-- Vue pour les statistiques des séries
CREATE VIEW IF NOT EXISTS series_stats AS
SELECT 
    s.id,
    s.title,
    s.language,
    COALESCE(AVG(r.rating), 0) as avg_rating,
    COUNT(r.id) as num_ratings,
    COALESCE(AVG(r.rating) * LOG(1 + COUNT(r.id)), 0) as popularity_score
FROM series s
LEFT JOIN ratings r ON s.id = r.serie_id
GROUP BY s.id, s.title, s.language;

-- Utilisateurs de test (SHA256 de 'password123')
INSERT OR IGNORE INTO users (username, password_hash, email, language_preference) VALUES
('alice', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'alice@example.com', 'vf'),
('bob', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'bob@example.com', 'vf'),
('charlie', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'charlie@example.com', 'vo'),
('diana', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'diana@example.com', 'vf'),
('eve', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'eve@example.com', 'vo'),
('frank', 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f', 'frank@example.com', 'vf');
