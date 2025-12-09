-- ============================================================================
-- Base de données TV Series - SAE501
-- ============================================================================

DROP DATABASE IF EXISTS tvseries;
CREATE DATABASE tvseries CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tvseries;

-- ============================================================================
-- Table des utilisateurs
-- ============================================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    email VARCHAR(100),
    language_preference ENUM('vf', 'vo') DEFAULT 'vf',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username)
) ENGINE=InnoDB;

-- ============================================================================
-- Table des séries
-- ============================================================================
CREATE TABLE series (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    language ENUM('vf', 'vo') NOT NULL,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    num_ratings INT DEFAULT 0,
    popularity_score DECIMAL(6,2) DEFAULT 0.00,
    INDEX idx_title (title),
    INDEX idx_language (language),
    INDEX idx_popularity (popularity_score DESC)
) ENGINE=InnoDB;

-- ============================================================================
-- Table des mots-clés
-- ============================================================================
CREATE TABLE keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    serie_id INT NOT NULL,
    keyword VARCHAR(100) NOT NULL,
    score DECIMAL(10,6) NOT NULL,
    FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE,
    INDEX idx_serie_id (serie_id),
    INDEX idx_keyword (keyword)
) ENGINE=InnoDB;

-- ============================================================================
-- Table des notations
-- ============================================================================
CREATE TABLE ratings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    serie_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (serie_id) REFERENCES series(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_serie (user_id, serie_id),
    INDEX idx_user_id (user_id),
    INDEX idx_serie_id (serie_id)
) ENGINE=InnoDB;

-- ============================================================================
-- Table des sessions
-- ============================================================================
CREATE TABLE sessions (
    token VARCHAR(64) PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB;

-- ============================================================================
-- Vue pour les statistiques des séries
-- ============================================================================
CREATE VIEW series_stats AS
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

-- ============================================================================
-- Données de test (utilisateurs existants)
-- ============================================================================
-- Les mots de passe sont hashés en SHA256
INSERT INTO users (username, password_hash, email, language_preference) VALUES
('alice', SHA2('password123', 256), 'alice@example.com', 'vf'),
('bob', SHA2('password123', 256), 'bob@example.com', 'vf'),
('charlie', SHA2('password123', 256), 'charlie@example.com', 'vo'),
('diana', SHA2('password123', 256), 'diana@example.com', 'vf'),
('eve', SHA2('password123', 256), 'eve@example.com', 'vo'),
('frank', SHA2('password123', 256), 'frank@example.com', 'vf');

-- Les séries et leurs données seront importées depuis les fichiers JSON
