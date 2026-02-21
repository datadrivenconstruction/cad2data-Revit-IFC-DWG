-- Add geolocation coordinates and ASN organization from Cloudflare
ALTER TABLE download_events ADD COLUMN latitude REAL;
ALTER TABLE download_events ADD COLUMN longitude REAL;
ALTER TABLE download_events ADD COLUMN asn_org TEXT;
