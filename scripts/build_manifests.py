"""Bangun ulang apps/<id>.json dari GitHub Releases repo ini.

Setiap aplikasi di index.json punya tagPrefix, misalnya "otosora-v".
Rilis dengan tag otosora-v0.2.0 dianggap versi 0.2.0 milik Otosora.
APK di rilis itu harus bernama <id>-v<versi>-<abi>.apk supaya updater
di aplikasi bisa memilih APK yang cocok dengan HP.

Dijalankan oleh .github/workflows/manifests.yml. Bisa juga lokal:
    GITHUB_TOKEN=... GITHUB_REPOSITORY=Irana06/shicomp-apps python scripts/build_manifests.py
"""

import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = os.environ.get("GITHUB_REPOSITORY", "Irana06/shicomp-apps")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HISTORY_LIMIT = 20
ABI_RE = re.compile(r"-(arm64-v8a|armeabi-v7a|x86_64|universal)\.apk$")


def fetch_releases():
    releases, page = [], 1
    while True:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/releases?per_page=100&page={page}",
            headers={"Accept": "application/vnd.github+json"},
        )
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
        with urllib.request.urlopen(req, timeout=30) as res:
            batch = json.load(res)
        releases += batch
        if len(batch) < 100:
            return releases
        page += 1


def version_key(version):
    return tuple(int(p) if p.isdigit() else 0 for p in re.split(r"[.+\-]", version)[:3])


def apk_entries(release):
    apks = []
    for asset in release.get("assets", []):
        name = asset["name"]
        if not name.lower().endswith(".apk"):
            continue
        abi = ABI_RE.search(name)
        digest = asset.get("digest") or ""
        apks.append({
            "abi": abi.group(1) if abi else "universal",
            "name": name,
            "url": asset["browser_download_url"],
            "size": asset["size"],
            "sha256": digest.removeprefix("sha256:") or None,
        })
    return sorted(apks, key=lambda a: a["abi"])


def build(app, releases):
    prefix = app["tagPrefix"]
    mine = []
    for r in releases:
        tag = r["tag_name"]
        if r["draft"] or r["prerelease"] or not tag.startswith(prefix):
            continue
        mine.append((tag.removeprefix(prefix), r))
    mine.sort(key=lambda item: version_key(item[0]), reverse=True)

    latest = None
    if mine:
        version, r = mine[0]
        latest = {
            "version": version,
            "tag": r["tag_name"],
            "title": r.get("name") or r["tag_name"],
            "notes": r.get("body") or "",
            "publishedAt": r.get("published_at"),
            "pageUrl": r["html_url"],
            "apks": apk_entries(r),
        }

    return {
        "schemaVersion": 1,
        "id": app["id"],
        "name": app["name"],
        "packageName": app["packageName"],
        "latest": latest,
        "history": [
            {"version": v, "tag": r["tag_name"], "publishedAt": r.get("published_at"), "pageUrl": r["html_url"]}
            for v, r in mine[:HISTORY_LIMIT]
        ],
    }


def main():
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    releases = fetch_releases()
    for app in index["apps"]:
        out = ROOT / app["manifest"]
        out.parent.mkdir(parents=True, exist_ok=True)
        data = build(app, releases)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        latest = data["latest"]["version"] if data["latest"] else "belum ada rilis"
        print(f"{app['id']}: {latest}")


if __name__ == "__main__":
    main()
