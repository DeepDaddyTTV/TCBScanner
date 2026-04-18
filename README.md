# TCBScanner

A Docker container that monitors TCBScans series pages, downloads chapter images in page order, packages each chapter as a `.cbz` file, and adds the result to a local manga library.

Use it only for content you are allowed to archive. The app does not bypass logins, paywalls, DRM, or access controls; it only reads public pages you provide and spaces requests out with a configurable delay.

## Run

Copy the example environment file and edit the host paths if you want the data or manga library somewhere else:

```powershell
Copy-Item .env.example .env
notepad .env
```

Start the container:

```powershell
docker compose up -d --build
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

By default, `/manga` maps to `./manga` on the host. To attach an existing library, set `TCBSCANNER_MANGA_DIR` in `.env`.

Example for a Windows library path:

```text
TCBSCANNER_MANGA_DIR=D:/Media/Manga
```

The compose variables are:

- `TCBSCANNER_PORT`: Host web UI port. Defaults to `18080`.
- `TCBSCANNER_DATA_DIR`: Host folder for SQLite and temporary work. Defaults to `./data`.
- `TCBSCANNER_MANGA_DIR`: Host manga library folder mounted as `/manga`. Defaults to `./manga`.
- `TZ`: Container time zone. Defaults to `America/New_York`.
- `TCB_SCHEDULER_INTERVAL_HOURS`: Scheduler wake-up interval in hours. Defaults to `1`.
- `TCB_REQUEST_DELAY`: Delay between TCBScans requests in seconds. Defaults to `0.8`.

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
- `Backfill existing chapters`: If enabled, all discovered chapters are queued. If disabled, currently published chapters are indexed and only future chapters are downloaded.

## API

- `GET /api/series`
- `POST /api/series`
- `DELETE /api/series/{series_id}`
- `GET /api/series/{series_id}/chapters`
- `POST /api/series/{series_id}/check`
- `POST /api/series/{series_id}/download-missing`
- `POST /api/chapters/{chapter_id}/retry`
- `GET /api/events`

## Notes

- CBZ files are just ZIP files with images stored as `001.ext`, `002.ext`, and so on.
- The app downloads one chapter at a time to keep requests gentle.
- Set `TCB_REQUEST_DELAY` in `docker-compose.yml` to increase or reduce the delay between page/image requests.
