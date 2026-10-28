"""Cloud sources and sinks: s3://, gs://, az:// URLs and https share links (OneDrive, SharePoint, Google Drive).

SDKs are optional and imported on demand: boto3 (Apache-2.0), google-cloud-storage (Apache-2.0),
azure-storage-blob (MIT). Share links and plain https use the standard library only.
"""
from __future__ import annotations

import base64
import html as _html
import os
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass
from email.message import Message
from pathlib import Path

MODEL_SUFFIXES = (".rvt", ".rfa")


class ConverterError(RuntimeError):
    pass


class CloudError(ConverterError):
    pass


@dataclass
class Remote:
    url: str
    size: int | None = None
    etag: str | None = None
    mtime: float | None = None


def is_remote(s) -> bool:
    return isinstance(s, str) and re.match(r"^(s3|gs|az|https?)://", s, re.I) is not None


def _split(url: str) -> tuple[str, str, str]:
    u = urllib.parse.urlsplit(url)
    if not u.netloc:
        raise CloudError(f"bad URL (no bucket/container): {url}")
    return u.scheme.lower(), u.netloc, urllib.parse.unquote(u.path.lstrip("/"))


def _safe_name(name: str, default: str = "download.rvt") -> str:
    name = name.replace("\\", "/").rsplit("/", 1)[-1].strip().strip(".")
    name = re.sub(r'[<>:"|?*\x00-\x1f]', "_", name)
    return name or default


def normalize_share_url(url: str) -> str:
    """Rewrite a OneDrive / SharePoint / Google Drive share link into a direct-download URL."""
    u = urllib.parse.urlsplit(url)
    host = (u.hostname or "").lower()
    q = urllib.parse.parse_qs(u.query)
    if host in ("drive.google.com", "docs.google.com"):
        m = re.search(r"/d/([\w-]+)", u.path)
        fid = m.group(1) if m else (q.get("id") or [None])[0]
        if fid:
            return f"https://drive.google.com/uc?export=download&id={fid}"
    elif host.endswith("sharepoint.com") or host.endswith("sharepoint.cn"):
        if "download" not in q:
            return urllib.parse.urlunsplit(u._replace(query=(u.query + "&" if u.query else "") + "download=1"))
    elif host in ("1drv.ms", "onedrive.live.com", "onedrive.com") or host.endswith(".1drv.com"):
        b = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
        return f"https://api.onedrive.com/v1.0/shares/u!{b}/root/content"
    return url


def _filename_from(headers, url: str) -> str:
    cd = headers.get("Content-Disposition") if headers else None
    if cd:
        m = Message()
        m["content-disposition"] = cd
        fn = m.get_param("filename*", header="content-disposition")
        if isinstance(fn, tuple):
            fn = urllib.parse.unquote(fn[2], encoding=fn[0] or "utf-8")
        fn = fn or m.get_filename()
        if fn:
            return _safe_name(fn)
    return _safe_name(urllib.parse.unquote(urllib.parse.urlsplit(url).path))


def _http_get(url: str, dest_dir: Path, timeout: float, max_hops: int = 3) -> Path:
    """Stream one URL into dest_dir. Follows the Google Drive large-file confirmation page."""
    for _ in range(max_hops):
        req = urllib.request.Request(url, headers={"User-Agent": "ddc-converter"})
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
        except Exception as e:
            raise CloudError(f"download failed for {url}: {e}") from e
        with resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if ctype.startswith("text/html"):
                if "drive.google.com" not in url:
                    raise CloudError(f"URL returned a web page, not a file: {url}")
                page = resp.read(2_000_000).decode("utf-8", "replace")
                form = re.search(r'<form[^>]+action="([^"]+)"', page)
                if not form:
                    raise CloudError("Google Drive returned a web page instead of a file (link not public?)")
                params = dict(re.findall(r'<input[^>]+name="([^"]+)"[^>]+value="([^"]*)"', page))
                url = _html.unescape(form.group(1)) + "?" + urllib.parse.urlencode(
                    {k: _html.unescape(v) for k, v in params.items()})
                continue
            name = _filename_from(resp.headers, resp.geturl())
            if "." not in name:
                name += ".rvt"
            dest = dest_dir / name
            want = resp.headers.get("Content-Length")
            n = 0
            with open(dest, "wb") as f:
                for chunk in iter(lambda: resp.read(1 << 20), b""):
                    f.write(chunk)
                    n += len(chunk)
            if want and want.isdigit() and int(want) != n:
                dest.unlink(missing_ok=True)
                raise CloudError(f"truncated download: got {n} of {want} bytes from {url}")
            return dest
    raise CloudError(f"too many confirmation pages: {url}")


def _s3():
    try:
        import boto3
    except ImportError as e:
        raise CloudError("s3:// needs boto3: pip install ddc-converter[s3]") from e
    return boto3.client("s3")


def _gcs():
    try:
        from google.cloud import storage
    except ImportError as e:
        raise CloudError("gs:// needs google-cloud-storage: pip install ddc-converter[gcs]") from e
    return storage.Client()


def _az_service():
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError as e:
        raise CloudError("az:// needs azure-storage-blob: pip install ddc-converter[azure]") from e
    cs = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    if cs:
        return BlobServiceClient.from_connection_string(cs)
    acct = os.environ.get("AZURE_STORAGE_ACCOUNT")
    if not acct:
        raise CloudError("az:// needs AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT")
    cred = os.environ.get("AZURE_STORAGE_KEY") or os.environ.get("AZURE_STORAGE_SAS_TOKEN")
    if cred is None:
        try:
            from azure.identity import DefaultAzureCredential
        except ImportError as e:
            raise CloudError("az:// needs AZURE_STORAGE_KEY, a SAS token or azure-identity") from e
        cred = DefaultAzureCredential()
    return BlobServiceClient(f"https://{acct}.blob.core.windows.net", credential=cred)


def _q(key: str) -> str:
    return urllib.parse.quote(key, safe="/")


def list_remote(url: str) -> list[Remote]:
    """Model files (.rvt/.rfa) under an s3/gs/az prefix, or the single object or link the URL names."""
    scheme, bucket, key = _split(url)
    if scheme in ("http", "https"):
        return [Remote(url)]
    base = f"{scheme}://{bucket}/"
    exact = bool(key) and not key.endswith("/") and key.lower().endswith(MODEL_SUFFIXES)
    if exact:
        return [Remote(url)]  # a named model; size/etag are not needed to fetch it
    prefix = key if (not key or key.endswith("/")) else key + "/"
    out: list[Remote] = []
    try:
        if scheme == "s3":
            for page in _s3().get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
                for o in page.get("Contents", []):
                    if o["Key"].lower().endswith(MODEL_SUFFIXES):
                        out.append(Remote(base + _q(o["Key"]), o["Size"], o["ETag"], o["LastModified"].timestamp()))
        elif scheme == "gs":
            for b in _gcs().list_blobs(bucket, prefix=prefix):
                if b.name.lower().endswith(MODEL_SUFFIXES):
                    out.append(Remote(base + _q(b.name), b.size, b.etag, b.updated.timestamp() if b.updated else None))
        elif scheme == "az":
            for b in _az_service().get_container_client(bucket).list_blobs(name_starts_with=prefix):
                if b.name.lower().endswith(MODEL_SUFFIXES):
                    out.append(Remote(base + _q(b.name), b.size, str(b.etag),
                                      b.last_modified.timestamp() if b.last_modified else None))
        else:
            raise CloudError(f"unsupported scheme: {scheme}")
    except CloudError:
        raise
    except Exception as e:
        raise CloudError(f"listing failed for {url}: {e}") from e
    return out


def fetch(url: str, dest_dir, timeout: float = 600, rel_to: str | None = None) -> Path:
    """Download one object or share link into dest_dir and return the local file.

    rel_to: a prefix URL; the object's path below it is kept as sub-folders under dest_dir.
    """
    dest_dir = Path(dest_dir)
    scheme, bucket, key = _split(url)
    if scheme in ("http", "https"):
        dest_dir.mkdir(parents=True, exist_ok=True)
        return _http_get(normalize_share_url(url), dest_dir, timeout)
    if not key or key.endswith("/"):
        raise CloudError(f"URL does not name an object: {url}")
    rel = _safe_name(key)
    if rel_to:
        pre = _split(rel_to)[2]
        if pre and not pre.endswith("/"):
            pre += "/"
        if key.startswith(pre):
            parts = [_safe_name(p, "_") for p in key[len(pre):].split("/") if p not in ("", ".", "..")]
            rel = "/".join(parts) or rel
    dest = dest_dir / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    try:
        if scheme == "s3":
            _s3().download_file(bucket, key, str(tmp))
        elif scheme == "gs":
            _gcs().bucket(bucket).blob(key).download_to_filename(str(tmp))
        elif scheme == "az":
            with open(tmp, "wb") as f:
                _az_service().get_blob_client(bucket, key).download_blob().readinto(f)
        else:
            raise CloudError(f"unsupported scheme: {scheme}")
    except CloudError:
        tmp.unlink(missing_ok=True)
        raise
    except Exception as e:
        tmp.unlink(missing_ok=True)
        raise CloudError(f"download failed for {url}: {e}") from e
    os.replace(tmp, dest)
    return dest


def upload_dir(local_dir, url: str) -> list[str]:
    """Upload every file under local_dir to the s3/gs/az prefix url. Returns the uploaded URLs."""
    local_dir = Path(local_dir)
    scheme, bucket, key = _split(url)
    if scheme not in ("s3", "gs", "az"):
        raise CloudError("upload target must be s3://, gs:// or az://")
    prefix = key.rstrip("/") + "/" if key else ""
    client = {"s3": _s3, "gs": _gcs, "az": _az_service}[scheme]()
    done = []
    for f in sorted(p for p in local_dir.rglob("*") if p.is_file()):
        k = prefix + f.relative_to(local_dir).as_posix()
        try:
            if scheme == "s3":
                client.upload_file(str(f), bucket, k)
            elif scheme == "gs":
                client.bucket(bucket).blob(k).upload_from_filename(str(f))
            else:
                with open(f, "rb") as fh:
                    client.get_blob_client(bucket, k).upload_blob(fh, overwrite=True)
        except Exception as e:
            raise CloudError(f"upload failed for {k}: {e}") from e
        done.append(f"{scheme}://{bucket}/{k}")
    return done
