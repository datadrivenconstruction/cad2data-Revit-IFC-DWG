interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestPost: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const date =
    url.searchParams.get('date') ||
    new Date(Date.now() - 86400000).toISOString().slice(0, 10);

  const db = context.env.ANALYTICS_DB;

  // Aggregate into daily_stats
  await db
    .prepare(
      `INSERT OR REPLACE INTO daily_stats
         (date, package, version, arch, country, count, unique_ips, total_bytes)
       SELECT
         strftime('%Y-%m-%d', timestamp) as date,
         package, version, arch,
         COALESCE(country, 'unknown') as country,
         COUNT(*) as count,
         COUNT(DISTINCT ip_hash) as unique_ips,
         COALESCE(SUM(file_size), 0) as total_bytes
       FROM download_events
       WHERE status_code = 200
         AND strftime('%Y-%m-%d', timestamp) = ?
       GROUP BY date, package, version, arch, country`
    )
    .bind(date)
    .run();

  // Aggregate into monthly_stats
  const month = date.slice(0, 7);
  await db
    .prepare(
      `INSERT OR REPLACE INTO monthly_stats
         (month, package, version, count, unique_ips, total_bytes)
       SELECT ?, package, version,
              SUM(count), SUM(unique_ips), SUM(total_bytes)
       FROM daily_stats
       WHERE date LIKE ? || '%'
       GROUP BY package, version`
    )
    .bind(month, month)
    .run();

  return Response.json({
    ok: true,
    aggregated_date: date,
    aggregated_month: month,
  });
};
