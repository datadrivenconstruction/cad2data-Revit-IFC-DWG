interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const url = new URL(context.request.url);
  const granularity = url.searchParams.get('granularity') || 'day';
  const pkg = url.searchParams.get('package');
  const days = Math.min(parseInt(url.searchParams.get('days') || '30', 10), 365);

  let dateExpr: string;
  switch (granularity) {
    case 'month':
      dateExpr = `strftime('%Y-%m', timestamp)`;
      break;
    case 'week':
      dateExpr = `strftime('%Y-W%W', timestamp)`;
      break;
    default:
      dateExpr = `strftime('%Y-%m-%d', timestamp)`;
  }

  let sql = `
    SELECT ${dateExpr} as period,
           package,
           COUNT(*) as count,
           COUNT(DISTINCT ip_hash) as unique_ips
    FROM download_events
    WHERE status_code = 200
      AND timestamp >= datetime('now', '-${days} days')
  `;

  const bindings: string[] = [];
  if (pkg) {
    sql += ` AND package = ?`;
    bindings.push(pkg);
  }

  sql += ` GROUP BY period, package ORDER BY period ASC`;

  const stmt = context.env.ANALYTICS_DB.prepare(sql);
  const result =
    bindings.length > 0
      ? await stmt.bind(...bindings).all()
      : await stmt.all();

  return Response.json({ granularity, days, data: result.results });
};
