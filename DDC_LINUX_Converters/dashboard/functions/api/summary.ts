interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const db = context.env.ANALYTICS_DB;

  const results = await db.batch([
    // Total downloads all time
    db.prepare(
      `SELECT COUNT(*) as total FROM download_events WHERE status_code = 200`
    ),
    // Downloads today
    db.prepare(
      `SELECT COUNT(*) as today FROM download_events
       WHERE status_code = 200
         AND timestamp >= strftime('%Y-%m-%dT00:00:00Z', 'now')`
    ),
    // Downloads this month
    db.prepare(
      `SELECT COUNT(*) as this_month FROM download_events
       WHERE status_code = 200
         AND timestamp >= strftime('%Y-%m-01T00:00:00Z', 'now')`
    ),
    // Per-package totals
    db.prepare(
      `SELECT package, COUNT(*) as count
       FROM download_events WHERE status_code = 200
       GROUP BY package ORDER BY count DESC`
    ),
    // Unique IPs today
    db.prepare(
      `SELECT COUNT(DISTINCT ip_hash) as unique_today
       FROM download_events
       WHERE status_code = 200
         AND timestamp >= strftime('%Y-%m-%dT00:00:00Z', 'now')`
    ),
    // Downloads this week
    db.prepare(
      `SELECT COUNT(*) as this_week FROM download_events
       WHERE status_code = 200
         AND timestamp >= strftime('%Y-%m-%dT00:00:00Z', 'now', '-7 days')`
    ),
  ]);

  return Response.json({
    total_downloads: (results[0].results[0] as any).total,
    downloads_today: (results[1].results[0] as any).today,
    downloads_this_month: (results[2].results[0] as any).this_month,
    per_package: results[3].results,
    unique_ips_today: (results[4].results[0] as any).unique_today,
    downloads_this_week: (results[5].results[0] as any).this_week,
  });
};
