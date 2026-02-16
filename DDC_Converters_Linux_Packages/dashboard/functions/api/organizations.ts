interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const days = Math.min(parseInt(url.searchParams.get('days') || '30', 10), 365);

  const result = await context.env.ANALYTICS_DB
    .prepare(
      `SELECT asn_org,
              COUNT(*) as count,
              COUNT(DISTINCT ip_hash) as unique_ips,
              COUNT(DISTINCT country) as countries
       FROM download_events
       WHERE status_code = 200
         AND asn_org IS NOT NULL AND asn_org != ''
         AND timestamp >= datetime('now', '-' || ? || ' days')
       GROUP BY asn_org
       ORDER BY count DESC
       LIMIT 50`
    )
    .bind(days)
    .all();

  return Response.json({ days, data: result.results });
};
