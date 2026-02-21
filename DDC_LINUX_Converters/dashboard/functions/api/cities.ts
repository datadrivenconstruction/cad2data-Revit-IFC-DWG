interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const days = Math.min(parseInt(url.searchParams.get('days') || '30', 10), 365);

  const result = await context.env.ANALYTICS_DB
    .prepare(
      `SELECT country, region, city,
              COUNT(*) as count,
              COUNT(DISTINCT ip_hash) as unique_ips
       FROM download_events
       WHERE status_code = 200
         AND city IS NOT NULL
         AND city != ''
         AND timestamp >= datetime('now', '-' || ? || ' days')
       GROUP BY country, region, city
       ORDER BY count DESC
       LIMIT 100`
    )
    .bind(days)
    .all();

  return Response.json({ days, data: result.results });
};
