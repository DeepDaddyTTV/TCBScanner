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
    user: "0:0"
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

Compose settings:

- `image`: Published container image. Use `ghcr.io/deepdaddyttv/tcbscanner:latest` for the current release.
- `container_name`: Friendly Docker container name.
- `restart`: Keeps the scanner running after Docker or host restarts.
- `user`: Runs the container as `root` by default so mounted manga folders can be written even when the host folder owner does not match a container user.
- `ports`: Maps the host web port to the container web port. `18080:8080` makes the app available at `http://localhost:18080`.
- `./data:/data`: Stores the SQLite database and temporary download work files.
- `./manga:/manga`: Stores finished CBZ files. Change the left side to attach an existing manga library, for example `D:/Media/Manga:/manga` or `/srv/manga:/manga`.
- `TZ`: Time zone used by the container for logs and scheduled checks.

Supported environment variables:

- `TZ`: Time zone used by the container for logs and scheduled checks. Default: Docker image default if unset.
- `DATA_DIR`: Container path for the database and state files. Default: `/data`.
- `LIBRARY_DIR`: Container path where finished CBZ files are written. Default: `/manga`.
- `WORK_DIR`: Container path for temporary image downloads before packaging. Default: `/data/work`.
- `TCB_SCHEDULER_INTERVAL_HOURS`: How often the background scheduler wakes up to look for due series, in hours. Default: `1`.
- `TCB_REQUEST_DELAY`: Delay between TCBScans requests, in seconds. Default: `0.8`.

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

## Naming Formats

Open the options menu in the web app to set the default CBZ naming format for every series. Each series card also has a `Naming format` field; leave it blank to use the default, or set a series-specific override.

Default:

```text
{ChapterFullTitle}
```

Example:

```text
{SeriesName} - Chapter {ChapterNumberPadded} - {ChapterTitle}
```

Available variables:

- `{SeriesName}`: Library title assigned to the series.
- `{ChapterNumber}`: Chapter number detected from the source, such as `1180`.
- `{ChapterNumberPadded}`: Chapter number padded to four digits, such as `0007` or `1180`.
- `{ChapterTitle}`: Chapter title with the series name and chapter number removed, such as `Omen`.
- `{ChapterName}`: Alias of `{ChapterTitle}`.
- `{ChapterFullTitle}`: Full chapter title from the source page, such as `One Piece Chapter 1180 Omen`.
- `{PageCount}`: Number of downloaded pages in the packaged CBZ.

Unknown variables are ignored. File names are sanitized before writing to the manga library.

## API

- `GET /api/series`
- `POST /api/series`
- `GET /api/settings`
- `POST /api/settings`
- `DELETE /api/series/{series_id}`
- `GET /api/series/{series_id}/chapters`
- `POST /api/series/{series_id}/check`
- `POST /api/series/{series_id}/download-missing`
- `POST /api/series/{series_id}/naming-format`
- `POST /api/series/{series_id}/queue-chapters`
- `POST /api/chapters/{chapter_id}/retry`
- `GET /api/events`

## Notes

- CBZ files are just ZIP files with images stored as `001.ext`, `002.ext`, and so on.
- The app downloads one chapter at a time to keep requests gentle.
