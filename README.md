# TCBScanner

A Docker container that monitors TCBScans series pages, downloads chapter images in page order, packages each chapter as a `.cbz` file, and adds the result to a local manga library.

Use it only for content you are allowed to archive. The app does not bypass logins, paywalls, DRM, or access controls; it only reads public pages you provide and spaces requests out with a configurable delay.

## Docker Compose

Use this compose file as a starting point:

```yaml
services:
  tcbscanner:
    image: ghcr.io/deepdaddyttv/tcbscanner:latest
    container_name: tcb_scanner
    restart: unless-stopped
    ports:
      - 18080:8080
    volumes:
      - ./data:/data
      - ./manga:/manga
    environment:
      TZ: "America/New_York"
```

Clone and start the container:

```powershell
git clone https://github.com/DeepDaddyTTV/TCBScanner.git
cd TCBScanner
docker compose pull
docker compose up -d
```

Update an existing install:

```powershell
git pull
docker compose pull
docker compose up -d
```

Open [http://localhost:18080](http://localhost:18080).

The SQLite database and temporary working folders live under:

```text
./data
```

Finished CBZ files are written inside the container at:

```text
/manga
```

By default, `/manga` maps to `./manga` on the host. To attach an existing library, change the left side of the volume mount, for example `D:/Media/Manga:/manga` or `/srv/manga:/manga`.

## Add a Series

Paste a TCBScans series URL such as:

```text
https://tcbonepiecechapters.com/mangas/5/one-piece
```

You can also paste a chapter URL; the app will try to resolve its "View All Chapters" link and monitor the series page.

Fields:

- `Library title`: Used for chapter file names when the source title is missing.
- `Folder`: Relative folder under `/manga`. Leave it blank to use the library title.
- `Check interval (hours)`: Hours between automatic checks for new chapters.
- `Download all found chapters`: If enabled, all discovered chapters are queued immediately. If disabled, currently published chapters are scanned into the chapter list without downloading.
- `Monitor new chapters`: If enabled, future scans queue newly discovered chapters automatically.

## Select Chapters

Leave `Download all found chapters` off when you want to pick specific chapters. After the scan completes, open the series, select the chapters you want, and use `Queue selected`.

Each series card also has a `Monitor` checkbox. Turn it on to keep checking for new chapters; turn it off when you only want manual scans.

## API

- `GET /api/series`
- `POST /api/series`
- `DELETE /api/series/{series_id}`
- `GET /api/series/{series_id}/chapters`
- `POST /api/series/{series_id}/check`
- `POST /api/series/{series_id}/download-missing`
- `POST /api/series/{series_id}/queue-chapters`
- `POST /api/chapters/{chapter_id}/retry`
- `GET /api/events`

## Notes

- CBZ files are just ZIP files with images stored as `001.ext`, `002.ext`, and so on.
- The app downloads one chapter at a time to keep requests gentle.
