-- Time-range queries on raw events
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON download_events(timestamp);

-- Filter by package
CREATE INDEX IF NOT EXISTS idx_events_package ON download_events(package);

-- Time-series per package
CREATE INDEX IF NOT EXISTS idx_events_pkg_ts ON download_events(package, timestamp);

-- Geography queries
CREATE INDEX IF NOT EXISTS idx_events_country ON download_events(country);

-- Unique IP counting
CREATE INDEX IF NOT EXISTS idx_events_ip_hash ON download_events(ip_hash);

-- Daily stats lookups
CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_stats(date);
CREATE INDEX IF NOT EXISTS idx_daily_pkg_date ON daily_stats(package, date);

-- Monthly stats lookups
CREATE INDEX IF NOT EXISTS idx_monthly_month ON monthly_stats(month);
