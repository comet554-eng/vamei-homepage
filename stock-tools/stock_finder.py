#!/usr/bin/env python3
"""Public stock-video search and download, Python 3.9+, no packages or API keys.

Sources: Mixkit's public pages and the Wikimedia Commons Action API.
Does not bypass logins/challenges or invent media URLs. Search results are
candidates: the calling agent must inspect frames before using them.
"""
import argparse
import datetime
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "StockMaterialHelper/1.0 (user-initiated public video search)"
HOSTS = {"mixkit.co", "assets.mixkit.co", "commons.wikimedia.org",
         "upload.wikimedia.org", "thumb.wikimedia.org"}


def allowed(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme != "https" or p.hostname not in HOSTS or p.port not in (None, 443):
        raise ValueError("Unexpected media host; review before allowing: " + url)
    return url


class CheckedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        allowed(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


OPENER = urllib.request.build_opener(CheckedRedirect())


def request(url, headers=None):
    return OPENER.open(urllib.request.Request(allowed(url), headers={
        "User-Agent": UA, **(headers or {})}), timeout=25)


def read_text(url):
    with request(url) as r:
        body = r.read(4 * 1024 * 1024 + 1)
        if len(body) > 4 * 1024 * 1024:
            raise ValueError("Unexpectedly large search response")
        text = body.decode("utf-8", errors="replace")
        if r.headers.get("cf-mitigated") == "challenge" or "<title>Just a moment" in text:
            raise RuntimeError("Website challenge; use the other provider")
        return text


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", "", str(text)))).strip()


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def unique(values):
    return list(dict.fromkeys(values))


def slug(query):
    return re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-") or "video"


def error_record(provider, url, error):
    info = {"source": provider, "url": url, "error": str(error)}
    if isinstance(error, urllib.error.HTTPError):
        info["http_status"] = error.code
        info["challenge"] = error.headers.get("cf-mitigated") == "challenge"
        info["note"] = "HTTP rejection: distinguish proxy allowlist and site policy from response headers."
    return info


def mixkit_search(query, limit, errors, quality):
    search_url = "https://mixkit.co/free-stock-video/discover/" + slug(query) + "/"
    page = read_text(search_url)
    links = unique(urllib.parse.urljoin(search_url, a["href"])
                   for tag, a in Tags(page).tags if tag == "a"
                   and re.fullmatch(r"/free-stock-video/[a-z0-9-]+-\d+/", a.get("href", "")))
    results = []
    for url in links[:max(limit * 3, 6)]:
        if len(results) >= limit:
            break
        try:
            text = read_text(url)
            tags = Tags(text).tags
            # Reject restricted/unclear licenses rather than assuming all Mixkit clips are free.
            licenses = {a.get("data-license") for _, a in tags if a.get("data-license")}
            if "videoFree" not in licenses or "videoRestricted" in licenses:
                continue
            options = [a.get("value", "") for tag, a in tags
                       if tag == "input" and a.get("name") == "download-option"]
            options = [x for x in options if x.startswith("/free-stock-video/download/")]
            if not options:
                continue
            wanted = [x for x in options if "type=" + quality in x]
            modal_url = urllib.parse.urljoin(url, (wanted or options)[0])
            modal = Tags(read_text(modal_url)).tags
            media = next((a["data-download--modal-url-value"] for _, a in modal
                          if a.get("data-download--modal-url-value")), None)
            if not media:
                raise ValueError("Public download response has no media URL")
            allowed(media)
            match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
            meta = {a.get("property", a.get("name", "")): a.get("content", "")
                    for tag, a in tags if tag == "meta"}
            resolution = re.search(r"type=(\w+)", modal_url)
            results.append({"id": "mixkit-" + re.search(r"-(\d+)/$", url).group(1),
                "source": "mixkit", "query": query,
                "title": clean(match.group(1)) if match else url,
                "description": meta.get("description", ""),
                "page_url": url, "download_url": media,
                "thumbnail_url": meta.get("og:image", ""),
                "license": "Mixkit Stock Video Free License",
                "license_url": "https://mixkit.co/license/#videoFree",
                "author": "See original item page", "auto_download_eligible": True,
                "quality_requested": quality,
                "quality_selected": resolution.group(1) if resolution else "unknown",
                "selection_note": "Visually inspect before use; verify dimensions with ffprobe."})
        except Exception as exc:
            errors.append(error_record("mixkit", url, exc))
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (403, 429):
                break
        time.sleep(0.2)
    return results


def commons_search(query, limit, errors, quality):
    params = {"action": "query", "format": "json", "generator": "search",
              "gsrsearch": "filetype:video " + query, "gsrnamespace": 6,
              "gsrlimit": limit, "prop": "imageinfo",
              "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 480}
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    data = json.loads(read_text(url))
    if "error" in data:
        raise RuntimeError(str(data["error"]))
    results = []
    for p in sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        for item in p.get("imageinfo", []):
            if not item.get("mime", "").startswith("video/"):
                continue
            metadata = item.get("extmetadata", {})
            def field(name):
                return clean(metadata.get(name, {}).get("value", ""))
            license_name = field("LicenseShortName")
            simple_license = (license_name in ("CC0", "CC0 1.0", "Public domain")
                              or re.fullmatch(r"CC BY \d+\.\d+", license_name) is not None)
            restrictions = field("Restrictions")
            categories = field("Categories").lower()
            questionable = any(x in categories for x in ("copyright violation", "deletion request", "missing permission"))
            results.append({"id": "commons-" + str(p["pageid"]), "source": "commons",
                "query": query, "title": p["title"], "description": field("ImageDescription"),
                "page_url": item.get("descriptionurl", ""), "download_url": item["url"],
                "thumbnail_url": item.get("thumburl", ""), "mime": item["mime"],
                "width": item.get("width"), "height": item.get("height"),
                "duration": item.get("duration"), "bytes": item.get("size"),
                "license": license_name, "license_url": field("LicenseUrl"),
                "author": field("Artist"), "credit": field("Credit"),
                "attribution_required": field("AttributionRequired"), "restrictions": restrictions,
                "auto_download_eligible": bool(simple_license and not restrictions and not questionable),
                "selection_note": "Keep attribution. Other licenses (including BY-SA) require review before download."})
    return results


def media_signature(prefix):
    return b"ftyp" in prefix[:32] or prefix.startswith((b"\x1aE\xdf\xa3", b"OggS"))


def probe(record):
    with request(record["download_url"], {"Range": "bytes=0-4095"}) as r:
        prefix = r.read(64)
        if not media_signature(prefix):
            raise ValueError("Response is not an MP4/WebM/Ogg video; refusing to save HTML")
        return {"status": r.status, "content_type": r.headers.get("Content-Type"),
                "final_url": r.url, "video_signature": True}


def download(record, folder, max_mb):
    cap = int(max_mb * 1024 * 1024)
    deadline = time.monotonic() + 120
    if record.get("bytes", 0) > cap:
        raise ValueError("File exceeds download size limit")
    path_suffix = Path(urllib.parse.urlsplit(record["download_url"]).path).suffix.lower()
    if path_suffix not in (".mp4", ".webm", ".ogv", ".ogg"):
        raise ValueError("Unsupported video extension")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / (record["id"] + path_suffix)
    if path.exists():
        return {"path": str(path), "status": "already_exists_not_revalidated"}
    part = path.with_suffix(path.suffix + ".part")
    owned = False
    try:
        with request(record["download_url"]) as r:
            if int(r.headers.get("Content-Length", 0)) > cap:
                raise ValueError("File exceeds download size limit")
            prefix = r.read(64)
            if not media_signature(prefix):
                raise ValueError("Download is not a video")
            with part.open("xb") as f:
                owned = True
                digest = hashlib.sha256()
                total = 0
                chunk = prefix
                while chunk:
                    if time.monotonic() > deadline:
                        raise TimeoutError("Download exceeded 120 seconds; try the next candidate")
                    total += len(chunk)
                    if total > cap:
                        raise ValueError("Download exceeded size limit")
                    f.write(chunk)
                    digest.update(chunk)
                    # read1 returns available bytes; read(n) can stall while a server trickles data.
                    chunk = r.read1(65536)
            expected = r.headers.get("Content-Length")
            if expected and total != int(expected):
                raise ValueError("Incomplete response body")
        part.rename(path)
        return {"path": str(path), "status": "downloaded", "bytes": total,
                "sha256": digest.hexdigest()}
    finally:
        if owned and part.exists():
            part.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queries", nargs="*", default=["cycling"])
    parser.add_argument("--sources", default="mixkit,commons")
    parser.add_argument("--limit", type=int, default=4, help="Candidates per query per source, 1-20")
    parser.add_argument("--quality", choices=["720p", "1080p", "2160p"], default="1080p")
    parser.add_argument("--probe", action="store_true", help="Verify first 4 KiB of every candidate")
    parser.add_argument("--download", type=int, default=0, help="Download up to N eligible clips per query")
    parser.add_argument("--ids", default="", help="Download only these comma-separated result IDs")
    parser.add_argument("--max-mb", type=float, default=150)
    parser.add_argument("--out", default="stock-results")
    parser.add_argument("--manifest", help="Use a prior manifest instead of repeating search")
    args = parser.parse_args()
    providers = {"mixkit": mixkit_search, "commons": commons_search}
    sources = [s.strip() for s in args.sources.split(",")]
    if not 1 <= args.limit <= 20 or any(s not in providers for s in sources) or args.download < 0 or args.max_mb <= 0:
        parser.error("Check --limit, --sources, --download, --max-mb")
    errors, results = [], []
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    def save_progress():
        manifest = {"created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "requires_api_key": False, "tested_environment": "where_this_script_was_run",
                    "results": results, "errors": errors}
        (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.manifest:
        results = json.loads(Path(args.manifest).read_text(encoding="utf-8"))["results"]
    else:
        for query in args.queries or ["cycling"]:
            for source in sources:
                print("Searching", source, repr(query), file=sys.stderr, flush=True)
                try:
                    results.extend(providers[source](query, args.limit, errors, args.quality))
                except Exception as exc:
                    errors.append(error_record(source, query, exc))
                save_progress()
    # Keep all keyword matches, but only one copy of any physical asset.
    merged = {}
    for item in results:
        if item["id"] in merged:
            previous = merged[item["id"]]
            previous["matched_queries"] = unique(previous["matched_queries"] + [item["query"]])
        else:
            merged[item["id"]] = {**item, "matched_queries": item.get("matched_queries", [item["query"]])}
    results = list(merged.values())
    selected_ids = set(x for x in args.ids.split(",") if x)
    unknown_ids = selected_ids - set(merged)
    if unknown_ids:
        parser.error("IDs missing from manifest: " + ",".join(sorted(unknown_ids)))
    downloaded = {}
    for item in results:
        if selected_ids and item["id"] not in selected_ids:
            continue
        if args.probe:
            print("Probing", item["id"], file=sys.stderr, flush=True)
            try:
                item["probe"] = probe(item)
            except Exception as exc:
                item["probe"] = {"error": str(exc)}
                errors.append(error_record(item["source"], item["download_url"], exc))
                save_progress()
                continue
        if args.download and downloaded.get(item["query"], 0) < args.download and item["auto_download_eligible"]:
            print("Downloading", item["id"], file=sys.stderr, flush=True)
            try:
                item["download"] = download(item, output / "clips", args.max_mb)
                downloaded[item["query"]] = downloaded.get(item["query"], 0) + 1
            except Exception as exc:
                errors.append(error_record(item["source"], item["download_url"], exc))
        save_progress()
    save_progress()
    lines = ["# Stock video candidates", "", "Inspect representative frames before choosing; relevance is not guaranteed.", ""]
    for item in results:
        lines.extend(["## " + item["id"], "", item["title"], "",
            "- Page: " + item["page_url"], "- Media: " + item["download_url"],
            "- License: " + item["license"] + " " + item.get("license_url", ""),
            "- Author: " + item.get("author", ""),
            "- Description: " + item.get("description", ""),
            "- Review: " + item.get("selection_note", ""), ""])
    (output / "CANDIDATES.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"candidates": len(results), "downloaded_or_existing": sum(downloaded.values()),
                      "errors": len(errors), "manifest": str(output / "manifest.json")}, ensure_ascii=False))
    if not results:
        return 2
    if args.download and not downloaded:
        return 3
    if args.probe and not any(x.get("probe", {}).get("video_signature") for x in results):
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())

