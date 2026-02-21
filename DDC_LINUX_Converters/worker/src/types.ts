export interface Env {
  REPO_BUCKET: R2Bucket;
  ANALYTICS_DB: D1Database;
  DAILY_SALT_PREFIX: string;
}

export interface DownloadEvent {
  package: string;
  version: string;
  arch: string;
  filename: string;
  ip_hash: string;
  country: string | null;
  region: string | null;
  city: string | null;
  latitude: number | null;
  longitude: number | null;
  asn_org: string | null;
  user_agent: string | null;
  file_size: number | null;
  status_code: number;
}

export interface ParsedDebFilename {
  package: string;
  version: string;
  arch: string;
}
