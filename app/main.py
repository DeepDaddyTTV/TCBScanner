from __future__ import annotations

import asyncio
import ipaddress
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .downloader import MangaDownloader, render_naming_template
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
    {"id": "atsumaru", "name": "Atsumaru"},
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
    source_url: str = Field(default="", max_length=500)
    backup_source_urls: list[str] = Field(default_factory=list, max_length=8)
    folder: str = Field(default="", max_length=240)
    check_interval_hours: float = Field(default=0.5, ge=0.5, le=168)
    naming_format: str | None = Field(default=None, max_length=180)
    poster_image_url: str | None = Field(default=None, max_length=1200)
    metadata_provider: str | None = Field(default=None, max_length=40)
    metadata_provider_override: str | None = Field(default=None, max_length=40)
    preferred_translator: str = Field(default="auto", max_length=120)
    metadata_id: str | None = Field(default=None, max_length=80)
    metadata_title: str | None = Field(default=None, max_length=240)
    metadata_url: str | None = Field(default=None, max_length=1200)
    metadata_chapter_count: int | None = Field(default=None, ge=1)
    enabled: bool = True
    backfill_existing: bool = False
    local_only: bool = False

    @field_validator("source_url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            return ""
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
        if cleaned not in {"anilist", "mangaupdates", "atsumaru"}:
            raise ValueError("Choose AniList, MangaUpdates, or Atsumaru as the metadata provider.")
        return cleaned

    @field_validator("preferred_translator")
    @classmethod
    def normalize_preferred_translator(cls, value: str) -> str:
        return " ".join(str(value or "auto").strip().split()) or "auto"

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
        if cleaned not in {"anilist", "mangaupdates", "atsumaru"}:
            raise ValueError("Choose AniList, MangaUpdates, or Atsumaru as the metadata provider.")
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


class LocalSeriesImport(BaseModel):
    folder_path: str = Field(min_length=1, max_length=2000)
    title: str = Field(min_length=1, max_length=120)
    source_url: str = Field(default="", max_length=500)
    naming_format: str | None = Field(default=None, max_length=180)
    rename_files: bool = False

    @field_validator("title")
    @classmethod
    def trim_local_title(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("source_url")
    @classmethod
    def validate_optional_source(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned and (not cleaned.startswith(("http://", "https://")) or not scraper.host_is_supported(cleaned)):
            raise ValueError("Enter a supported http or https manga source URL, or leave it blank for a local-only series.")
        return cleaned


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


@app.get("/api/source-options")
async def get_source_options(url: str) -> dict[str, Any]:
    cleaned_url = str(url or "").strip()
    provider = scraper.detect_provider(cleaned_url)
    if provider != "atsumaru":
        return {"provider": provider or "", "translators": []}
    try:
        translators = await scraper.atsumaru_source_options(cleaned_url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Unable to load Atsumaru translator groups.") from exc
    return {"provider": provider, "translators": translators}


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
    if normalized_provider not in {"anilist", "mangaupdates", "atsumaru"}:
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
        provider_name = next(
            (item["name"] for item in METADATA_PROVIDERS if item["id"] == normalized_provider),
            "Metadata provider",
        )
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


def _resolve_import_folder(raw_path: str) -> tuple[Path, Path]:
    candidate = Path(raw_path).expanduser().resolve()
    for configured_root in LIBRARY_ROOTS:
        root = configured_root.expanduser().resolve()
        if candidate == root or root in candidate.parents:
            if not candidate.is_dir():
                raise HTTPException(status_code=400, detail="Choose an existing folder inside a configured library root.")
            return root, candidate
    raise HTTPException(status_code=400, detail="Folder must stay inside one of the configured library roots.")


@app.get("/api/library/folders")
async def browse_library_folders(path: str | None = None) -> dict[str, Any]:
    if not path:
        roots = []
        for configured_root in LIBRARY_ROOTS:
            root = configured_root.expanduser().resolve()
            if root.is_dir():
                roots.append({"path": str(root), "name": root.name or str(root), "is_root": True})
        return {"roots": roots, "current_path": "", "parent_path": "", "folders": [], "cbz_count": 0}

    root, current = _resolve_import_folder(path)
    folders: list[dict[str, Any]] = []
    try:
        children = sorted(current.iterdir(), key=lambda item: item.name.casefold())
    except OSError as exc:
        raise HTTPException(status_code=400, detail="Unable to read this folder.") from exc
    for child in children:
        if not child.is_dir():
            continue
        resolved = child.resolve()
        if resolved != root and root not in resolved.parents:
            continue
        folders.append({
            "path": str(resolved),
            "name": child.name,
            "cbz_count": sum(1 for item in resolved.iterdir() if item.is_file() and item.suffix.lower() == ".cbz"),
        })
    cbz_count = sum(1 for item in current.iterdir() if item.is_file() and item.suffix.lower() == ".cbz")
    return {
        "roots": [],
        "current_path": str(current),
        "parent_path": str(current.parent) if current != root else "",
        "is_root": current == root,
        "folders": folders,
        "cbz_count": cbz_count,
    }


@app.post("/api/library/import-series")
async def import_local_series(payload: LocalSeriesImport) -> dict[str, Any]:
    root, folder = _resolve_import_folder(payload.folder_path)
    if folder == root:
        raise HTTPException(status_code=400, detail="Choose a series folder below the library root, not the root itself.")
    for existing_series in store.list_series():
        existing_folder = str(existing_series.get("folder") or "").strip()
        try:
            same_folder = existing_folder and Path(existing_folder).expanduser().resolve() == folder
        except OSError:
            same_folder = False
        if same_folder:
            raise HTTPException(
                status_code=409,
                detail=f"This folder is already tracked as {existing_series['title']}. Open that series instead.",
            )
    files = sorted(
        (item for item in folder.iterdir() if item.is_file() and item.suffix.lower() == ".cbz"),
        key=lambda item: item.name.casefold(),
    )
    if not files:
        raise HTTPException(status_code=400, detail="This folder has no CBZ files to import.")

    chapters: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for file_path in files:
        if file_path.is_symlink():
            raise HTTPException(status_code=400, detail=f"Cannot import linked file {file_path.name}; place the CBZ inside the selected series folder first.")
        try:
            with zipfile.ZipFile(file_path) as archive:
                bad_member = archive.testzip()
                if bad_member:
                    raise ValueError(f"{file_path.name} contains a damaged archive entry.")
                page_count = sum(
                    1 for name in archive.namelist()
                    if Path(name).suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
                )
                if not page_count:
                    raise ValueError(f"{file_path.name} contains no readable image pages.")
        except (OSError, zipfile.BadZipFile, RuntimeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=f"Cannot import {file_path.name}: {exc}") from exc
        stem = file_path.stem
        chapter_key, sort_key = scraper.parse_chapter_key(stem, stem)
        if chapter_key in seen_keys:
            raise HTTPException(status_code=400, detail=f"Multiple CBZ files resolve to chapter {chapter_key}; rename them to unique chapter numbers first.")
        seen_keys.add(chapter_key)
        chapters.append({
            "url": f"local://{file_path.name}",
            "chapter_key": chapter_key,
            "sort_key": sort_key,
            "title": stem,
            "page_count": page_count,
            "source_path": file_path,
        })

    naming_format = " ".join((payload.naming_format or store.get_default_naming_format()).strip().split())
    rename_plan: list[tuple[Path, Path]] = []
    if payload.rename_files:
        proposed: set[Path] = set()
        preview_series = {"title": payload.title}
        for chapter in chapters:
            target = folder / render_naming_template(
                preview_series,
                {"chapter_key": chapter["chapter_key"], "display_title": chapter["title"]},
                naming_format,
                chapter["page_count"],
            )
            source = chapter["source_path"]
            if target != source and (target.exists() or target in proposed):
                raise HTTPException(status_code=409, detail=f"Cannot rename safely: {target.name} already exists or is another chapter's target.")
            proposed.add(target)
            if target != source:
                rename_plan.append((source, target))

    renamed: list[tuple[Path, Path]] = []
    series: dict[str, Any] | None = None
    try:
        for source, target in rename_plan:
            source.rename(target)
            renamed.append((source, target))
            for chapter in chapters:
                if chapter["source_path"] == source:
                    chapter["source_path"] = target
                    chapter["url"] = f"local://{target.name}"
                    break

        has_source = bool(payload.source_url)
        series = store.create_series({
            "title": payload.title,
            "source_url": payload.source_url,
            "folder": str(folder),
            "check_interval_minutes": 1440,
            "enabled": has_source,
            "backfill_existing": False,
            "naming_format": naming_format,
            "local_only": not has_source,
            "metadata_provider": store.get_setting("default_metadata_provider") or DEFAULT_METADATA_PROVIDER,
            "preferred_translator": "auto",
        })
        created = store.upsert_chapters(int(series["id"]), chapters, "downloaded")
        if len(created) != len(chapters):
            raise RuntimeError("One or more chapters conflicted with an existing imported record.")
        for chapter, record in zip(chapters, created):
            store.set_chapter_status(
                int(record["id"]),
                "downloaded",
                cbz_path=str(chapter["source_path"]),
                page_count=int(chapter["page_count"]),
            )
        store.add_event(
            int(series["id"]),
            None,
            "info",
            f"Imported {len(chapters)} existing CBZ chapter(s) from {folder.name}.",
        )
    except Exception as exc:
        if series:
            store.delete_series(int(series["id"]))
        restore_failures: list[str] = []
        for source, target in reversed(renamed):
            try:
                target.rename(source)
            except OSError:
                restore_failures.append(source.name)
        if isinstance(exc, HTTPException):
            raise
        message = "The local import failed; no series entry was kept."
        if restore_failures:
            message += f" Could not restore renamed file(s): {', '.join(restore_failures)}. Check the selected folder."
        raise HTTPException(status_code=500, detail=message) from exc

    if payload.source_url and series:
        schedule_check(int(series["id"]))
    return {"ok": True, "series": store.get_series(int(series["id"])), "imported_chapters": len(chapters)}


@app.post("/api/series")
async def create_series(payload: SeriesCreate) -> dict[str, Any]:
    data = payload.model_dump()
    if not data["source_url"]:
        raise HTTPException(status_code=400, detail="A source URL is required when tracking a new series. Use local import for existing CBZ files.")
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
    existing = store.get_series(series_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Series not found.")
    data = payload.model_dump()
    if data["source_url"]:
        data["local_only"] = False
    elif not data.get("local_only"):
        raise HTTPException(status_code=400, detail="A source URL is required unless this is a local-only import.")
    if data.get("local_only") and data.get("enabled"):
        data["enabled"] = False
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
    existing = store.get_series(series_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Series not found.")
    if payload.enabled and existing.get("local_only"):
        raise HTTPException(status_code=400, detail="Add a supported source URL in Series Settings before enabling monitoring.")
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
    if payload.rescan and not series.get("local_only"):
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
    series = store.get_series(series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found.")
    if series.get("local_only"):
        raise HTTPException(status_code=400, detail="Add a supported source URL in Series Settings before scanning this local-only series.")
    schedule_check(series_id)
    return {"ok": True}


@app.post("/api/series/{series_id}/download-missing")
async def download_missing(series_id: int) -> dict[str, Any]:
    series = store.get_series(series_id)
    if not series:
        raise HTTPException(status_code=404, detail="Series not found.")
    if series.get("local_only"):
        raise HTTPException(status_code=400, detail="Add a supported source URL in Series Settings before scanning for missing chapters.")
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
