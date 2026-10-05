PRAGMA foreign_keys = ON;

-- =========================================================
-- BESTORA FIT
-- Database Schema
-- =========================================================

-- =========================================================
-- PROVIDERS
-- =========================================================

CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,

    location TEXT,
    phone TEXT,
    email TEXT,

    experience_years INTEGER DEFAULT 0,

    rating REAL DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,

    completed_jobs INTEGER DEFAULT 0,
    response_rate REAL DEFAULT 0.0,

    verified INTEGER DEFAULT 0,

    trust_score REAL DEFAULT 0.0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- OFFERS
-- =========================================================

CREATE TABLE IF NOT EXISTS offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    provider_id INTEGER NOT NULL,

    title TEXT NOT NULL,
    description TEXT,

    category TEXT NOT NULL,

    price REAL NOT NULL,
    currency TEXT DEFAULT 'INR',

    delivery_time TEXT,

    availability TEXT DEFAULT 'available',

    rating REAL DEFAULT 0.0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (provider_id)
        REFERENCES providers(id)
        ON DELETE CASCADE
);


-- =========================================================
-- SERVICE REQUIREMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS service_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    requirement_text TEXT NOT NULL,

    category TEXT,
    location TEXT,

    budget_min REAL,
    budget_max REAL,

    preferred_date TEXT,

    urgency TEXT,

    extracted_requirements TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- MATCH RESULTS
-- =========================================================

CREATE TABLE IF NOT EXISTS match_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    requirement_id INTEGER NOT NULL,
    provider_id INTEGER NOT NULL,
    offer_id INTEGER,

    match_score REAL DEFAULT 0.0,

    price_score REAL DEFAULT 0.0,
    quality_score REAL DEFAULT 0.0,
    trust_score REAL DEFAULT 0.0,
    availability_score REAL DEFAULT 0.0,

    recommendation_reason TEXT,

    risk_level TEXT DEFAULT 'LOW',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requirement_id)
        REFERENCES service_requirements(id)
        ON DELETE CASCADE,

    FOREIGN KEY (provider_id)
        REFERENCES providers(id)
        ON DELETE CASCADE,

    FOREIGN KEY (offer_id)
        REFERENCES offers(id)
        ON DELETE SET NULL
);


-- =========================================================
-- NEGOTIATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS negotiations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    requirement_id INTEGER NOT NULL,
    provider_id INTEGER NOT NULL,
    offer_id INTEGER,

    original_price REAL,
    proposed_price REAL,
    final_price REAL,

    status TEXT DEFAULT 'pending',

    ai_message TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requirement_id)
        REFERENCES service_requirements(id)
        ON DELETE CASCADE,

    FOREIGN KEY (provider_id)
        REFERENCES providers(id)
        ON DELETE CASCADE,

    FOREIGN KEY (offer_id)
        REFERENCES offers(id)
        ON DELETE SET NULL
);


-- =========================================================
-- PRODUCTS
-- =========================================================

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,
    brand TEXT,

    category TEXT,

    description TEXT,

    price REAL,
    currency TEXT DEFAULT 'INR',

    rating REAL DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,

    seller TEXT,

    product_url TEXT,
    image_url TEXT,

    availability TEXT DEFAULT 'available',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- PRODUCT REQUIREMENTS
-- =========================================================

CREATE TABLE IF NOT EXISTS product_requirements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    requirement_text TEXT NOT NULL,

    category TEXT,

    budget_min REAL,
    budget_max REAL,

    preferred_brands TEXT,

    required_features TEXT,

    preferred_features TEXT,

    excluded_features TEXT,

    extracted_requirements TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- PRODUCT MATCH RESULTS
-- =========================================================

CREATE TABLE IF NOT EXISTS product_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    requirement_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,

    match_score REAL DEFAULT 0.0,

    price_score REAL DEFAULT 0.0,
    feature_score REAL DEFAULT 0.0,
    quality_score REAL DEFAULT 0.0,
    value_score REAL DEFAULT 0.0,

    recommendation_reason TEXT,

    deal_score REAL DEFAULT 0.0,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requirement_id)
        REFERENCES product_requirements(id)
        ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
);


-- =========================================================
-- RISK ALERTS
-- =========================================================

CREATE TABLE IF NOT EXISTS risk_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    provider_id INTEGER,
    offer_id INTEGER,
    product_id INTEGER,

    risk_score REAL DEFAULT 0.0,

    risk_level TEXT DEFAULT 'LOW',

    alert_type TEXT,
    alert_message TEXT,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (provider_id)
        REFERENCES providers(id)
        ON DELETE CASCADE,

    FOREIGN KEY (offer_id)
        REFERENCES offers(id)
        ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON DELETE CASCADE
); 