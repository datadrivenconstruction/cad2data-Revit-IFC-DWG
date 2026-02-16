import { DownloadEvent, ParsedDebFilename } from './types';

/**
 * Parse a .deb filename into its components.
 * Expected format: {package}_{version}_{arch}.deb
 * Example: ddc-rvtconverter_17.1.2.0_amd64.deb
 */
export function parseDebFilename(filename: string): ParsedDebFilename | null {
  const match = filename.match(
    /^([a-z0-9][a-z0-9.+\-]+)_([a-zA-Z0-9.+\-~:]+)_([a-z0-9]+)\.deb$/
  );
  if (!match) return null;
  return {
    package: match[1],
    version: match[2],
    arch: match[3],
  };
}

/**
 * Hash an IP address with a daily-rotating salt for privacy.
 * Same IP produces different hashes on different days.
 */
export async function hashIP(
  ip: string,
  saltPrefix: string
): Promise<string> {
  const today = new Date().toISOString().slice(0, 10);
  const data = new TextEncoder().encode(`${saltPrefix}:${today}:${ip}`);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Insert a download event into D1.
 * Called inside waitUntil() so it does not block the response.
 */
export async function logDownloadEvent(
  db: D1Database,
  event: DownloadEvent
): Promise<void> {
  try {
    await db
      .prepare(
        `INSERT INTO download_events
          (package, version, arch, filename, ip_hash,
           country, region, city, user_agent,
           file_size, status_code)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      )
      .bind(
        event.package,
        event.version,
        event.arch,
        event.filename,
        event.ip_hash,
        event.country,
        event.region,
        event.city,
        event.user_agent,
        event.file_size,
        event.status_code
      )
      .run();
  } catch (err) {
    console.error('Failed to log download event:', err);
  }
}
