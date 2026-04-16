-- PostgreSQL schema for Telegram Managed Bots training project.
-- Tokens must be encrypted before storage.

CREATE TABLE IF NOT EXISTS managed_bots (
    id SERIAL PRIMARY KEY,
    bot_id BIGINT UNIQUE NOT NULL,
    bot_username VARCHAR(64),
    user_id BIGINT NOT NULL,
    bot_token_encrypted TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP,
    status VARCHAR(16) DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    message_count INT DEFAULT 0,
    sentiment FLOAT,
    intent VARCHAR(50),
    qualified BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS managed_bot_messages (
    id SERIAL PRIMARY KEY,
    bot_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    user_message TEXT,
    bot_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bot_id) REFERENCES managed_bots(bot_id)
);
