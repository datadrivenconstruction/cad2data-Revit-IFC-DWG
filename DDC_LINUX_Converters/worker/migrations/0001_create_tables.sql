-- Raw download events (one row per .deb download)
CREATE TABLE IF NOT EXISTS download_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    package     TEXT    NOT NULL,
    version     TEXT    NOT NULL,
    arch        TEXT    NOT NULL,
    filename    TEXT    NOT NULL,
    ip_hash     TEXT    NOT NULL,
    country     TEXT,
    region      TEXT,
    city        TEXT,
    user_agent  TEXT,
    file_size   INTEGER,
    status_code INTEGER NOT NULL DEFAULT 200
);

-- Daily aggregate table
CREATE TABLE IF NOT EXISTS daily_stats (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL,
    package     TEXT    NOT NULL,
    version     TEXT    NOT NULL,
    arch        TEXT    NOT NULL,
    country     TEXT    NOT NULL DEFAULT 'unknown',
    count       INTEGER NOT NULL DEFAULT 0,
    unique_ips  INTEGER NOT NULL DEFAULT 0,
    total_bytes INTEGER NOT NULL DEFAULT 0,
    UNIQUE(date, package, version, arch, country)
);

-- Monthly aggregate table
CREATE TABLE IF NOT EXISTS monthly_stats (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    month       TEXT    NOT NULL,
    package     TEXT    NOT NULL,
    version     TEXT    NOT NULL,
    count       INTEGER NOT NULL DEFAULT 0,
    unique_ips  INTEGER NOT NULL DEFAULT 0,
    total_bytes INTEGER NOT NULL DEFAULT 0,
    UNIQUE(month, package, version)
);
