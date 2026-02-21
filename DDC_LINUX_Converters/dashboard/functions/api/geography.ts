interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const days = Math.min(parseInt(url.searchParams.get('days') || '30', 10), 365);

  const result = await context.env.ANALYTICS_DB
    .prepare(
      `SELECT country,
              COUNT(*) as count,
              COUNT(DISTINCT ip_hash) as unique_ips
       FROM download_events
       WHERE status_code = 200
         AND country IS NOT NULL
         AND timestamp >= datetime('now', '-' || ? || ' days')
       GROUP BY country
       ORDER BY count DESC`
    )
    .bind(days)
    .all();

  return Response.json({ days, data: result.results });
};
