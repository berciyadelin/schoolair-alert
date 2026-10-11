-- schema.sql: SchoolAir Alert (PostgreSQL)

CREATE TABLE IF NOT EXISTS schools (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    city          VARCHAR(100) NOT NULL,
    lat           NUMERIC(9,6) NOT NULL,
    lon           NUMERIC(9,6) NOT NULL,
    contact_email VARCHAR(150),
    contact_phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS aqi_readings (
    id         BIGSERIAL PRIMARY KEY,
    school_id  INT NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    aqi        INT NOT NULL CHECK (aqi >= 0),
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS alerts (
    id        BIGSERIAL PRIMARY KEY,
    school_id INT NOT NULL REFERENCES schools(id) ON DELETE CASCADE,
    level     VARCHAR(10) NOT NULL CHECK (level IN ('WARNING', 'SEVERE')),
    message   TEXT NOT NULL,
    sent_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Speeds up "latest reading per school" and the 6-hour repeat-alert check
CREATE INDEX IF NOT EXISTS idx_readings_school_time
    ON aqi_readings (school_id, fetched_at DESC);

CREATE INDEX IF NOT EXISTS idx_alerts_school_level_time
    ON alerts (school_id, level, sent_at DESC);
