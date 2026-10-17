# Shicomp Apps

Tempat download dan sumber update untuk aplikasi buatan Shicomp.

Halaman download: https://irana06.github.io/shicomp-apps/

| Aplikasi | Keterangan |
|---|---|
| **Otosora · 音空** | Music player tanpa iklan: lagu di HP, streaming, dan download |

Repo ini hanya berisi APK di [Releases](https://github.com/Irana06/shicomp-apps/releases) dan manifest untuk updater. Source code setiap aplikasi ada di repo masing-masing.

## Cara kerja

```
repo aplikasi (privat)          shicomp-apps (publik)
──────────────────────          ─────────────────────────────────────
git push tag v0.2.0  ──build──▶ Release otosora-v0.2.0 (APK per ABI)
                                       │
                                       ▼ workflow manifests.yml
                                apps/otosora.json  ◀── dibaca updater di aplikasi
```

1. Di repo aplikasi, dorong tag `vX.Y.Z`. Workflow dari [`templates/release-app.yml`](templates/release-app.yml) membangun dan menandatangani APK, lalu membuat rilis `<id>-vX.Y.Z` di repo ini.
2. Rilis baru memicu [`manifests.yml`](.github/workflows/manifests.yml), yang menjalankan [`scripts/build_manifests.py`](scripts/build_manifests.py) dan memperbarui `apps/<id>.json`.
3. Updater di aplikasi membaca manifest lewat GitHub Pages, membandingkan versi, lalu mengunduh APK yang cocok dengan ABI HP.

## Manifest

Updater membaca `https://irana06.github.io/shicomp-apps/apps/<id>.json`:

```json
{
  "schemaVersion": 1,
  "id": "otosora",
  "name": "Otosora",
  "packageName": "com.shicomp.otosora",
  "latest": {
    "version": "0.2.0",
    "tag": "otosora-v0.2.0",
    "title": "otosora v0.2.0",
    "notes": "markdown catatan rilis",
    "publishedAt": "2026-10-18T00:00:00Z",
    "pageUrl": "https://github.com/Irana06/shicomp-apps/releases/tag/otosora-v0.2.0",
    "apks": [
      { "abi": "arm64-v8a", "name": "otosora-v0.2.0-arm64-v8a.apk", "url": "…", "size": 12345678, "sha256": "…" }
    ]
  },
  "history": [ { "version": "0.2.0", "tag": "otosora-v0.2.0", "publishedAt": "…", "pageUrl": "…" } ]
}
```

`latest` bernilai `null` selama aplikasi belum punya rilis. Manifest dibaca lewat Pages, bukan API GitHub, jadi tidak kena batas 60 request per jam.

## Menambah aplikasi baru

1. Tambahkan entri di [`index.json`](index.json) (`id`, `name`, `packageName`, `tagPrefix` = `<id>-v`, `manifest` = `apps/<id>.json`).
2. Salin `templates/release-app.yml` ke repo aplikasi sebagai `.github/workflows/release.yml`, lalu isi `APP_ID` dan `RELEASE_SHA1`.
3. Isi secret di repo aplikasi: `KEYSTORE_BASE64`, `STORE_PASSWORD`, `KEY_PASSWORD`, `KEY_ALIAS`, dan `HUB_TOKEN`.
   `HUB_TOKEN` adalah fine-grained token dengan izin **Contents: Read and write** yang hanya untuk repo ini.
4. Simpan keystore baik-baik. Kalau keystore hilang atau berganti, APK baru tidak bisa memperbarui aplikasi yang sudah terpasang.
