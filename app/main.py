from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from .downloader import MangaDownloader
from .store import Store


DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
LIBRARY_DIR = Path(os.getenv("LIBRARY_DIR", str(DATA_DIR / "library")))
WORK_DIR = Path(os.getenv("WORK_DIR", str(DATA_DIR / "work")))
SCHEDULER_INTERVAL_HOURS = max(
    1.0,
    float(os.getenv("TCB_SCHEDULER_INTERVAL_HOURS", "1")),
)
REQUEST_DELAY = max(0.2, float(os.getenv("TCB_REQUEST_DELAY", "0.8")))

app = FastAPI(title="TCBScanner")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

store = Store(DATA_DIR / "app.db")
downloader = MangaDownloader(
    store,
    library_dir=LIBRARY_DIR,
    work_dir=WORK_DIR,
    request_delay=REQUEST_DELAY,
)
monitor_task: asyncio.Task[None] | None = None


class SeriesCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    source_url: str = Field(min_length=1, max_length=500)
    folder: str = Field(default="", max_length=240)
    check_interval_hours: int = Field(default=1, ge=1, le=168)
    enabled: bool = True
    backfill_existing: bool = False

    @field_validator("source_url")
    @classmethod
    def require_http_url(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith(("http://", "https://")):
            raise ValueError("Enter a full http or https URL.")
        return cleaned

    @field_validator("title", "folder")
    @classmethod
    def trim_text(cls, value: str) -> str:
        return " ".join(value.strip().split())


class EnabledUpdate(BaseModel):
    enabled: bool


@app.on_event("startup")
async def startup() -> None:
    global monitor_task
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


@app.post("/api/series")
async def create_series(payload: SeriesCreate) -> dict[str, Any]:
    data = payload.model_dump()
    data["check_interval_minutes"] = data.pop("check_interval_hours") * 60
    if not data["folder"]:
        data["folder"] = data["title"]
    series = store.create_series(data)
    schedule_check(int(series["id"]))
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


@app.get("/api/series/{series_id}/chapters")
async def list_chapters(series_id: int) -> dict[str, Any]:
    if not store.get_series(series_id):
        raise HTTPException(status_code=404, detail="Series not found.")
    return {"chapters": store.list_chapters(series_id)}


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


@app.post("/api/chapters/{chapter_id}/retry")
async def retry_chapter(chapter_id: int) -> dict[str, Any]:
    chapter = store.get_chapter(chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found.")
    updated = store.mark_chapter_pending(chapter_id)
    schedule_download(int(chapter["series_id"]))
    return {"chapter": updated}


@app.get("/api/events")
async def list_events(limit: int = 100) -> dict[str, Any]:
    return {"events": store.list_events(max(1, min(limit, 250)))}


def schedule_check(series_id: int) -> None:
    asyncio.create_task(downloader.check_series(series_id))


def schedule_download(series_id: int) -> None:
    asyncio.create_task(downloader.download_pending(series_id))


async def monitor_loop() -> None:
    while True:
        try:
            now = datetime.now(timezone.utc)
            for series in store.list_series():
                if not series["enabled"]:
                    continue
                last_checked_at = parse_datetime(series.get("last_checked_at"))
                interval_minutes = int(series["check_interval_minutes"])
                due = last_checked_at is None
                if last_checked_at is not None:
                    elapsed = (now - last_checked_at).total_seconds()
                    due = elapsed >= interval_minutes * 60
                if due:
                    await downloader.check_series(int(series["id"]))
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - keep the scheduler alive
            store.add_event(None, None, "error", f"Monitor loop error: {exc}")
        await asyncio.sleep(SCHEDULER_INTERVAL_HOURS * 3600)


def parse_datetime(value: object) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
