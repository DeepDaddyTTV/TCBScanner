from __future__ import annotations

import asyncio
import ipaddress
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .downloader import MangaDownloader
from . import scraper
from .store import DEFAULT_NAMING_FORMAT, Store


DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
LIBRARY_DIR = Path(os.getenv("LIBRARY_DIR", str(DATA_DIR / "library")))
WORK_DIR = Path(os.getenv("WORK_DIR", str(DATA_DIR / "work")))
REQUEST_DELAY = max(0.2, float(os.getenv("TCB_REQUEST_DELAY", "0.8")))
APP_VERSION = (os.getenv("APP_VERSION", "0.2.0").strip() or "0.2.0")
DEFAULT_METADATA_PROVIDER = "anilist"
DEFAULT_SCAN_TIME = "20:00"
SCAN_TIME_ZONE = ZoneInfo("America/New_York")
METADATA_PROVIDERS = [
    {"id": "anilist", "name": "AniList"},
    {"id": "mangaupdates", "name": "MangaUpdates"},
]
NAMING_VARIABLES = [
    {
        "name": "SeriesName",
        "description": "Library title assigned to the series.",
    },
    {
        "name": "ChapterNumber",
        "description": "Chapter number detected from the source, such as 1180.",
    },
    {
        "name": "ChapterNumberPadded",
        "description": "Chapter number padded to four digits, such as 1180 or 0007.",
    },
    {
        "name": "ChapterTitle",
        "description": "Chapter title with the series name and chapter number removed, such as Omen.",
    },
    {
        "name": "ChapterName",
        "description": "Alias of ChapterTitle.",
    },
    {
        "name": "ChapterFullTitle",
        "description": "Full chapter title from the source page, such as One Piece Chapter 1180 Omen.",
    },
    {
        "name": "PageCount",
        "description": "Number of downloaded pages in the CBZ.",
    },
]


def scheduler_poll_seconds() -> float:
    raw_seconds = os.getenv("TCB_SCHEDULER_INTERVAL_SECONDS", "").strip()
    if raw_seconds:
        return max(15.0, float(raw_seconds))
    raw_hours = os.getenv("TCB_SCHEDULER_INTERVAL_HOURS", "").strip()
    if raw_hours:
        return max(15.0, float(raw_hours) * 3600)
    return 30.0


def parse_library_roots() -> list[Path]:
    raw = (
        os.getenv("LIBRARY_DIRS", "").strip()
        or os.getenv("TCB_LIBRARY_ROOTS", "").strip()
        or os.getenv("LIBRARY_ROOTS", "").strip()
    )
    candidates = (
        [item.strip() for item in re.split(r"[\n,;]+", raw) if item.strip()]
        if raw
        else [str(LIBRARY_DIR)]
    )
    unique: list[Path] = []
    seen: set[str] = set()
    for item in candidates:
        normalized = str(Path(item)).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique.append(Path(normalized))
    return unique or [LIBRARY_DIR]


def artwork_url_is_public(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    if parsed.scheme not in {"http", "https"}:
        return False

    host = (parsed.hostname or "").strip()
    if not host:
        return False

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None

    if address is not None:
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
            return False
    elif host.lower() in {"localhost"}:
        return False

    return True


SCHEDULER_POLL_SECONDS = scheduler_poll_seconds()
LIBRARY_ROOTS = parse_library_roots()

app = FastAPI(title="Sakurarr")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

store = Store(DATA_DIR / "app.db")
downloader = MangaDownloader(
    store,
    library_roots=LIBRARY_ROOTS,
    work_dir=WORK_DIR,
    request_delay=REQUEST_DELAY,
)
monitor_task: asyncio.Task[None] | None = None


class SeriesCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    source_url: str = Field(min_length=1, max_length=500)
    backup_source_urls: list[str] = Field(default_factory=list, max_length=8)
    folder: str = Field(default="", max_length=240)
    check_interval_hours: float = Field(default=0.5, ge=0.5, le=168)
    naming_format: str | None = Field(default=None, max_length=180)
    poster_image_url: str | None = Field(default=None, max_length=1200)
    metadata_provider: str | None = Field(default=None, max_length=40)
    metadata_provider_override: str | None = Field(default=None, max_length=40)
    metadata_id: str | None = Field(default=None, max_length=80)
    metadata_title: str | None = Field(default=None, max_length=240)
    metadata_url: str | None = Field(default=None, max_length=1200)
    metadata_chapter_count: int | None = Field(default=None, ge=1)
    enabled: bool = True
    backfill_existing: bool = False

    @field_validator("source_url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("Enter a full http or https URL.")
        return cleaned

    @field_validator("backup_source_urls")
    @classmethod
    def require_http_backup_urls(cls, values: list[str]) -> list[str]:
        cleaned_urls: list[str] = []
        seen: set[str] = set()
        for value in values:
            cleaned = str(value or "").strip()
            if not cleaned.startswith(("http://", "https://")):
                raise ValueError("Each backup source must be a full http or https URL.")
            key = cleaned.rstrip("/").lower()
            if key in seen:
                continue
            seen.add(key)
            cleaned_urls.append(cleaned)
        return cleaned_urls

    @field_validator("title", "folder")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("metadata_provider", "metadata_provider_override")
    @classmethod
    def validate_metadata_provider(cls, value: str | None) -> str | None:
        cleaned = str(value or "").strip().lower()
        if not cleaned:
            return None
        if cleaned not in {"anilist", "mangaupdates"}:
            raise ValueError("Choose AniList or MangaUpdates as the metadata provider.")
        return cleaned

    @field_validator("metadata_url")
    @classmethod
    def validate_metadata_url(cls, value: str | None) -> str | None:
        cleaned = str(value or "").strip()
        if not cleaned:
            return None
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("Metadata links must use http or https.")
        return cleaned


class EnabledUpdate(BaseModel):
    enabled: bool


class NamingFormatUpdate(BaseModel):
    naming_format: str | None = Field(default=None, max_length=180)


class SettingsUpdate(BaseModel):
    default_naming_format: str = Field(
        default=DEFAULT_NAMING_FORMAT,
        min_length=1,
        max_length=180,
    )
    kavita_url: str | None = Field(default=None, max_length=600)
    komga_url: str | None = Field(default=None, max_length=600)
    default_metadata_provider: str = DEFAULT_METADATA_PROVIDER
    global_scan_time: str = Field(default=DEFAULT_SCAN_TIME, pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$")

    @field_validator("default_metadata_provider")
    @classmethod
    def validate_default_metadata_provider(cls, value: str) -> str:
        cleaned = str(value or "").strip().lower()
        if cleaned not in {"anilist", "mangaupdates"}:
            raise ValueError("Choose AniList or MangaUpdates as the metadata provider.")
        return cleaned


class QueueChapters(BaseModel):
    chapter_ids: list[int] = Field(default_factory=list, max_length=1000)


class SeriesUpdate(SeriesCreate):
    pass


class PosterUpdate(BaseModel):
    poster_image_url: str | None = Field(default=None, max_length=1200)


class SeriesReset(BaseModel):
    delete_files: bool = False
    rescan: bool = True


@app.on_event("startup")
async def startup() -> None:
    global monitor_task
    for series_id, chapter_count in store.recover_interrupted_downloads().items():
        store.add_event(
            series_id,
            None,
            "info",
            f"Recovered {chapter_count} interrupted download(s) after restart.",
        )
        schedule_download(series_id)
    monitor_task = asyncio.create_task(monitor_loop())


@app.on_event("shutdown")
async def shutdown() -> None:
    if monitor_task:
        monitor_task.cancel()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/api/series")
async def list_series() -> dict[str, Any]:
    return {"series": store.list_series()}


@app.get("/api/settings")
async def get_settings() -> dict[str, Any]:
    return {
        "default_naming_format": store.get_default_naming_format(),
        "variables": NAMING_VARIABLES,
        "kavita_url": store.get_setting("kavita_url") or "",
        "komga_url": store.get_setting("komga_url") or "",
        "default_metadata_provider": store.get_setting("default_metadata_provider")
        or DEFAULT_METADATA_PROVIDER,
        "global_scan_time": store.get_setting("global_scan_time") or DEFAULT_SCAN_TIME,
        "scan_time_zone": "America/New_York",
        "library_roots": [str(path) for path in LIBRARY_ROOTS],
    }


@app.get("/api/meta")
async def get_meta() -> dict[str, Any]:
    return {
        "app_name": "Sakurarr",
        "version": APP_VERSION,
        "version_label": display_version(APP_VERSION),
        "supported_source_count": scraper.supported_source_count(),
        "supported_sources": scraper.list_supported_sources(),
        "metadata_providers": METADATA_PROVIDERS,
    }


@app.get("/api/artwork")
async def get_artwork(title: str, source_url: str) -> dict[str, Any]:
    cleaned_title = " ".join(str(title or "").strip().split())
    cleaned_url = str(source_url or "").strip()
    if not cleaned_title or not cleaned_url.startswith(("http://", "https://")):
        return {
            "cover_image_url": "",
            "hero_image_url": "",
            "poster_choices": [],
        }
    return await scraper.resolve_series_artwork(cleaned_title, cleaned_url)


@app.get("/api/metadata/anilist")
async def search_anilist_metadata(query: str, limit: int = 8) -> dict[str, Any]:
    cleaned = " ".join(str(query or "").strip().split())
    if len(cleaned) < 2:
        return {"query": cleaned, "matches": []}
    try:
        matches = await scraper.search_anilist_catalog(cleaned, limit=max(1, min(limit, 12)))
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AniList metadata lookup failed.") from exc
    return {"query": cleaned, "matches": matches}


@app.get("/api/metadata/catalog")
async def search_catalog_metadata(
    query: str,
    provider: str = "anilist",
    limit: int = 8,
) -> dict[str, Any]:
    cleaned = " ".join(str(query or "").strip().split())
    normalized_provider = str(provider or "anilist").strip().lower()
    if normalized_provider not in {"anilist", "mangaupdates"}:
        raise HTTPException(status_code=400, detail="Unsupported metadata provider.")
    if len(cleaned) < 2:
        return {"query": cleaned, "provider": normalized_provider, "matches": []}
    try:
        matches = await scraper.search_catalog(
            normalized_provider,
            cleaned,
            limit=max(1, min(limit, 12)),
        )
    except Exception as exc:
        provider_name = "AniList" if normalized_provider == "anilist" else "MangaUpdates"
        raise HTTPException(status_code=502, detail=f"{provider_name} metadata lookup failed.") from exc
    return {"query": cleaned, "provider": normalized_provider, "matches": matches}


@app.get("/api/artwork/image")
async def get_artwork_image(url: str) -> Response:
    cleaned_url = str(url or "").strip()
    if not artwork_url_is_public(cleaned_url):
        raise HTTPException(status_code=400, detail="Enter a public artwork URL.")

    try:
        payload, content_type = await scraper.fetch_bytes(cleaned_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Unable to fetch artwork image.") from exc

    media_type = (content_type or "image/jpeg").split(";")[0].strip() or "image/jpeg"
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@app.post("/api/settings")
async def update_settings(payload: SettingsUpdate) -> dict[str, Any]:
    store.set_setting(
        "default_naming_format",
        " ".join(payload.default_naming_format.strip().split()),
    )
    store.set_setting("kavita_url", str(payload.kavita_url or "").strip())
    store.set_setting("komga_url", str(payload.komga_url or "").strip())
    store.set_setting("default_metadata_provider", payload.default_metadata_provider)
    store.set_setting("global_scan_time", payload.global_scan_time)
    return await get_settings()


@app.get("/api/library/export")
async def export_library() -> JSONResponse:
    snapshot = store.export_library_snapshot()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return JSONResponse(
        content=snapshot,
        headers={
            "Content-Disposition": f'attachment; filename="tcbscanner-library-{timestamp}.json"'
        },
    )


@app.post("/api/library/import")
async def import_library(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        counts = store.import_library_snapshot(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "ok": True,
        "counts": counts,
    }


@app.post("/api/series")
async def create_series(payload: SeriesCreate) -> dict[str, Any]:
    data = payload.model_dump()
    data["backup_source_urls"] = without_primary_source(
        data["source_url"],
        data.get("backup_source_urls", []),
    )
    data["check_interval_minutes"] = int(round(float(data.pop("check_interval_hours")) * 60))
    if not data.get("metadata_id"):
        provider = str(
            data.get("metadata_provider_override")
            or store.get_setting("default_metadata_provider")
            or DEFAULT_METADATA_PROVIDER
        ).strip().lower()
        try:
            matches = await scraper.search_catalog(provider, data["title"], limit=1)
        except Exception:
            matches = []
        if matches and int(matches[0].get("match_score") or 0) >= 2:
            apply_catalog_match(data, matches[0])
    if not data["folder"]:
        data["folder"] = data["title"]
    series = store.create_series(data)
    schedule_check(int(series["id"]))
    return {"series": series}


@app.put("/api/series/{series_id}")
async def update_series(series_id: int, payload: SeriesUpdate) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    data = payload.model_dump()
    data["backup_source_urls"] = without_primary_source(
        data["source_url"],
        data.get("backup_source_urls", []),
    )
    data["check_interval_minutes"] = int(round(float(data.pop("check_interval_hours")) * 60))
    if not data["folder"]:
        data["folder"] = data["title"]
    series = store.update_series(series_id, data)
    return {"series": series}


@app.delete("/api/series/{series_id}")
async def delete_series(series_id: int) -> dict[str, bool]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    store.delete_series(series_id)
    return {"ok": True}


@app.post("/api/series/{series_id}/enabled")
async def set_enabled(series_id: int, payload: EnabledUpdate) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    series = store.set_series_enabled(series_id, payload.enabled)
    return {"series": series}


@app.post("/api/series/{series_id}/naming-format")
async def set_naming_format(series_id: int, payload: NamingFormatUpdate) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    series = store.set_series_naming_format(series_id, payload.naming_format)
    return {"series": series}


@app.post("/api/series/{series_id}/poster")
async def set_series_poster(series_id: int, payload: PosterUpdate) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    series = store.set_series_poster(series_id, payload.poster_image_url)
    return {"series": series}


@app.post("/api/series/{series_id}/reset")
async def reset_series(series_id: int, payload: SeriesReset) -> dict[str, Any]:
    series = store.get_series(series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found.")
    chapters = store.list_chapters(series_id)
    cancellation_requested = any(
        chapter.get("status") == "downloading" for chapter in chapters
    )
    if cancellation_requested:
        downloader.request_cancel(series_id)
        for _ in range(450):
            await asyncio.sleep(0.1)
            chapters = store.list_chapters(series_id)
            if not any(chapter.get("status") == "downloading" for chapter in chapters):
                break
        else:
            downloader.clear_cancel(series_id)
            raise HTTPException(
                status_code=409,
                detail="The active download did not stop in time. Try the reset again.",
            )

    deleted_files = 0
    missing_files = 0
    try:
        if payload.delete_files:
            file_paths = {
                Path(str(chapter.get("cbz_path") or "").strip())
                for chapter in chapters
                if str(chapter.get("cbz_path") or "").strip()
            }
            for file_path in file_paths:
                if file_path.suffix.lower() != ".cbz" or not path_within_library_roots(file_path):
                    raise HTTPException(
                        status_code=400,
                        detail="A recorded chapter file is outside the configured library roots.",
                    )
            for file_path in file_paths:
                try:
                    file_path.unlink()
                    deleted_files += 1
                except FileNotFoundError:
                    missing_files += 1
                except OSError as exc:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Unable to delete {file_path.name}.",
                    ) from exc

        try:
            removed_records = store.reset_series(series_id)
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
    finally:
        if cancellation_requested:
            downloader.clear_cancel(series_id)
    if payload.rescan:
        schedule_check(series_id)
    return {
        "ok": True,
        "removed_records": removed_records,
        "deleted_files": deleted_files,
        "missing_files": missing_files,
        "rescan_queued": payload.rescan,
    }


@app.get("/api/series/{series_id}/chapters")
async def list_chapters(series_id: int) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    return {"chapters": [decorate_chapter(chapter) for chapter in store.list_chapters(series_id)]}


@app.post("/api/series/{series_id}/check")
async def check_series(series_id: int) -> dict[str, bool]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    schedule_check(series_id)
    return {"ok": True}


@app.post("/api/series/{series_id}/download-missing")
async def download_missing(series_id: int) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    changed = store.mark_missing_pending(series_id)
    store.add_event(series_id, None, "info", f"Queued {changed} skipped or failed chapter(s).")
    schedule_download(series_id)
    return {"queued": changed}


@app.post("/api/series/{series_id}/queue-failed")
async def queue_failed(series_id: int) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    changed = store.mark_failed_pending(series_id)
    store.add_event(series_id, None, "info", f"Queued {changed} failed chapter(s).")
    schedule_download(series_id)
    return {"queued": changed}


@app.post("/api/series/{series_id}/queue-chapters")
async def queue_chapters(series_id: int, payload: QueueChapters) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    changed = store.mark_selected_pending(series_id, payload.chapter_ids)
    store.add_event(series_id, None, "info", f"Queued {changed} selected chapter(s).")
    schedule_download(series_id)
    return {"queued": changed}


@app.post("/api/chapters/{chapter_id}/retry")
async def retry_chapter(chapter_id: int) -> dict[str, Any]:
    chapter = store.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found.")
    updated = store.mark_chapter_pending(chapter_id)
    schedule_download(int(chapter["series_id"]))
    return {"chapter": updated}


@app.get("/api/chapters/{chapter_id}/file")
async def get_chapter_file(chapter_id: int) -> FileResponse:
    chapter = store.get_chapter(chapter_id)
    if not chapter or not chapter.get("cbz_path"):
        raise HTTPException(status_code=404, detail="Chapter file not found.")
    file_path = Path(str(chapter["cbz_path"]))
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chapter file not found.")
    return FileResponse(
        file_path,
        media_type="application/vnd.comicbook+zip",
        filename=file_path.name,
    )


@app.get("/api/events")
async def list_events(limit: int = 100, series_id: int | None = None) -> dict[str, Any]:
    bounded = max(1, min(limit, 250))
    return {"events": store.list_events(bounded, series_id=series_id)}


@app.get("/api/queue")
async def get_queue(limit: int = 120) -> dict[str, Any]:
    bounded = max(10, min(limit, 250))
    downloading = [
        decorate_chapter(chapter)
        for chapter in store.list_queue_items(("downloading",), limit=bounded)
    ]
    pending = [
        decorate_chapter(chapter)
        for chapter in store.list_queue_items(("pending",), limit=bounded)
    ]
    return {
        "downloading": downloading,
        "pending": pending,
        "downloading_count": len(downloading),
        "pending_count": len(pending),
    }


@app.get("/api/search")
async def search_series(query: str, limit: int = 12) -> dict[str, Any]:
    cleaned = " ".join(str(query or "").strip().split())
    bounded = max(1, min(limit, 20))
    if len(cleaned) < 2:
        return {
            "query": cleaned,
            "library_matches": [],
            "source_matches": [],
        }
    library_matches = store.search_series(cleaned, limit=bounded)
    source_matches = await scraper.search_supported_series(cleaned, limit=bounded)
    return {
        "query": cleaned,
        "library_matches": library_matches,
        "source_matches": source_matches,
    }


def schedule_check(series_id: int) -> None:
    asyncio.create_task(downloader.check_series(series_id))


def schedule_download(series_id: int) -> None:
    asyncio.create_task(downloader.download_pending(series_id))


async def monitor_loop() -> None:
    while True:
        try:
            local_now = datetime.now(SCAN_TIME_ZONE)
            try:
                scan_time = datetime.strptime(
                    store.get_setting("global_scan_time") or DEFAULT_SCAN_TIME,
                    "%H:%M",
                ).time()
            except ValueError:
                scan_time = datetime.strptime(DEFAULT_SCAN_TIME, "%H:%M").time()
            last_scan_date = store.get_setting("last_global_scan_date")
            if local_now.time() >= scan_time and last_scan_date != local_now.date().isoformat():
                # Mark the daily run before starting so a restart cannot fan out duplicate scans.
                store.set_setting("last_global_scan_date", local_now.date().isoformat())
                for series in store.list_series():
                    if series["enabled"]:
                        await downloader.check_series(int(series["id"]))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - keep the scheduler alive
            store.add_event(None, None, "error", f"Monitor loop error: {exc}")
        await asyncio.sleep(SCHEDULER_POLL_SECONDS)


def decorate_chapter(chapter: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(chapter)
    cbz_path = enriched.get("cbz_path")
    if not cbz_path:
        enriched["file_size_bytes"] = None
        enriched["file_size_label"] = "—"
        return enriched

    try:
        size_bytes = Path(str(cbz_path)).stat().st_size
    except OSError:
        size_bytes = None

    enriched["file_size_bytes"] = size_bytes
    enriched["file_size_label"] = format_file_size(size_bytes)
    return enriched


def format_file_size(size_bytes: int | None) -> str:
    if not size_bytes:
        return "—"
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def display_version(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return "0.2.0"
    if re.fullmatch(r"[0-9a-f]{40}", cleaned):
        return cleaned[:7]
    return cleaned


def without_primary_source(primary_url: str, backup_urls: list[str]) -> list[str]:
    primary_key = str(primary_url or "").strip().rstrip("/").lower()
    return [
        url
        for url in backup_urls
        if str(url or "").strip().rstrip("/").lower() != primary_key
    ]


def apply_catalog_match(data: dict[str, Any], match: dict[str, object]) -> None:
    data["metadata_provider"] = str(match.get("provider") or "anilist").strip() or "anilist"
    data["metadata_id"] = str(match.get("id") or "").strip() or None
    data["metadata_title"] = str(match.get("title") or "").strip() or None
    data["metadata_url"] = str(match.get("url") or "").strip() or None
    chapter_count = match.get("chapter_count")
    data["metadata_chapter_count"] = chapter_count if isinstance(chapter_count, int) else None


def path_within_library_roots(file_path: Path) -> bool:
    try:
        resolved = file_path.resolve()
    except OSError:
        resolved = file_path.absolute()
    for library_root in LIBRARY_ROOTS:
        try:
            resolved.relative_to(library_root.resolve())
        except (OSError, ValueError):
            continue
        return True
    return False
