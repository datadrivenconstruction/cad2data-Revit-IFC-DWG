import { Env } from './types';
import { parseDebFilename, hashIP, logDownloadEvent } from './analytics';

export default {
  async fetch(
    request: Request,
    env: Env,
    ctx: ExecutionContext
  ): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method Not Allowed', { status: 405 });
    }

    // Strip leading slash to get R2 object key
    const objectKey = path.startsWith('/') ? path.slice(1) : path;

    // Handle root path
    if (!objectKey) {
      return new Response('DDC Package Repository', {
        status: 200,
        headers: { 'Content-Type': 'text/plain' },
      });
    }

    // Fetch the object from R2
    const object = await env.REPO_BUCKET.get(objectKey);

    if (!object) {
      // Log 404s for .deb requests to detect broken links
      if (objectKey.endsWith('.deb')) {
        const filename = objectKey.split('/').pop() || objectKey;
        const parsed = parseDebFilename(filename);
        if (parsed) {
          ctx.waitUntil(
            hashIP(
              request.headers.get('CF-Connecting-IP') || 'unknown',
              env.DAILY_SALT_PREFIX
            ).then((ipHash) =>
              logDownloadEvent(env.ANALYTICS_DB, {
                ...parsed,
                filename,
                ip_hash: ipHash,
                country: request.headers.get('CF-IPCountry'),
                region: (request.cf as any)?.region || null,
                city: (request.cf as any)?.city || null,
                latitude: (request.cf as any)?.latitude ? parseFloat((request.cf as any).latitude) : null,
                longitude: (request.cf as any)?.longitude ? parseFloat((request.cf as any).longitude) : null,
                asn_org: (request.cf as any)?.asOrganization || null,
                user_agent: request.headers.get('User-Agent'),
                file_size: null,
                status_code: 404,
              })
            )
          );
        }
      }
      return new Response('Not Found', { status: 404 });
    }

    // Build response headers
    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set('ETag', object.httpEtag);
    headers.set('Content-Length', object.size.toString());

    // For non-.deb files (Release, Packages, InRelease, GPG keys)
    // just serve without logging
    if (!objectKey.endsWith('.deb')) {
      return new Response(object.body, { headers });
    }

    // --- .deb file: serve AND log asynchronously ---
    const filename = objectKey.split('/').pop() || objectKey;
    const parsed = parseDebFilename(filename);

    if (parsed) {
      ctx.waitUntil(
        hashIP(
          request.headers.get('CF-Connecting-IP') || 'unknown',
          env.DAILY_SALT_PREFIX
        ).then((ipHash) =>
          logDownloadEvent(env.ANALYTICS_DB, {
            ...parsed,
            filename,
            ip_hash: ipHash,
            country: request.headers.get('CF-IPCountry'),
            region: (request.cf as any)?.region || null,
            city: (request.cf as any)?.city || null,
            latitude: (request.cf as any)?.latitude ? parseFloat((request.cf as any).latitude) : null,
            longitude: (request.cf as any)?.longitude ? parseFloat((request.cf as any).longitude) : null,
            asn_org: (request.cf as any)?.asOrganization || null,
            user_agent: request.headers.get('User-Agent'),
            file_size: object.size,
            status_code: 200,
          })
        )
      );
    }

    return new Response(object.body, { headers });
  },

  // Daily aggregation cron job
  async scheduled(
    event: ScheduledEvent,
    env: Env,
    ctx: ExecutionContext
  ): Promise<void> {
    const yesterday = new Date(Date.now() - 86400000)
      .toISOString()
      .slice(0, 10);

    try {
      // Aggregate into daily_stats
      await env.ANALYTICS_DB.prepare(
        `INSERT OR REPLACE INTO daily_stats
           (date, package, version, arch, country, count, unique_ips, total_bytes)
         SELECT
           strftime('%Y-%m-%d', timestamp) as date,
           package, version, arch,
           COALESCE(country, 'unknown'),
           COUNT(*),
           COUNT(DISTINCT ip_hash),
           COALESCE(SUM(file_size), 0)
         FROM download_events
         WHERE status_code = 200
           AND strftime('%Y-%m-%d', timestamp) = ?
         GROUP BY date, package, version, arch, country`
      )
        .bind(yesterday)
        .run();

      // Re-aggregate the month
      const month = yesterday.slice(0, 7);
      await env.ANALYTICS_DB.prepare(
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

      console.log(`Aggregation complete for ${yesterday}`);
    } catch (err) {
      console.error('Aggregation failed:', err);
    }
  },
};
