-- Vercel Postgres Schema for Poland House Hunter

CREATE TABLE IF NOT EXISTS properties (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT,
    developer VARCHAR(255),
    price_pln_gross NUMERIC,
    price_per_sqm NUMERIC,
    rooms INTEGER,
    area_sqm NUMERIC,
    floor INTEGER,
    district VARCHAR(100),
    city VARCHAR(100) DEFAULT 'Warszawa',
    opportunity_score NUMERIC,
    annual_yield_percent NUMERIC,
    market_diff_percent NUMERIC,
    layout_quality VARCHAR(50),
    distance_to_metro_m INTEGER,
    nearest_metro VARCHAR(100),
    projected_capital_gain_pct NUMERIC,
    monthly_mortgage_pln NUMERIC,
    break_even_years NUMERIC,
    url TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    property_id VARCHAR(255) REFERENCES properties(id) ON DELETE CASCADE,
    price_pln_gross NUMERIC,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast ranking loading
CREATE INDEX idx_opportunity_score ON properties(opportunity_score DESC);
