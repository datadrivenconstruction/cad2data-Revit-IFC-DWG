interface Env {
  ANALYTICS_DB: D1Database;
}

export const onRequestGet: PagesFunction<Env> = async (context) => {
  const result = await context.env.ANALYTICS_DB
    .prepare(
      `SELECT package,
              version,
              arch,
              COUNT(*) as total_downloads,
              COUNT(DISTINCT ip_hash) as unique_downloaders,
              MAX(timestamp) as last_downloaded
       FROM download_events
       WHERE status_code = 200
       GROUP BY package, version, arch
       ORDER BY package ASC, version DESC`
    )
    .all();

  return Response.json({ packages: result.results });
};
