from __future__ import annotations

import asyncio
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

import httpx

from . import scraper
from .store import Store


class MangaDownloader:
    def __init__(
        self,
        store: Store,
        *,
        library_dir: Path,
        work_dir: Path,
        request_delay: float,
    ) -> None:
        self.store = store
        self.library_dir = library_dir
        self.work_dir = work_dir
        self.request_delay = request_delay
        self._download_lock = asyncio.Lock()
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)

    async def check_series(self, series_id: int, *, force_download: bool = True) -> None:
        series = self.store.get_series(series_id)
        if not series:
            return
        self.store.record_check_start(series_id)
        try:
            source_url, chapters = await self._discover_chapters(series["source_url"])
            if source_url != series["source_url"]:
                self.store.update_series_source(series_id, source_url)
                self.store.add_event(series_id, None, "info", "Resolved chapter URL to series page.")

            initial = not series["initialized"]
            status_for_new = "pending"
            if initial and not series["backfill_existing"]:
                status_for_new = "skipped"

            created = self.store.upsert_chapters(series_id, chapters, status_for_new)
            if created:
                pending_count = sum(1 for item in created if item["status"] == "pending")
                skipped_count = sum(1 for item in created if item["status"] == "skipped")
                bits = []
                if pending_count:
                    bits.append(f"{pending_count} queued")
                if skipped_count:
                    bits.append(f"{skipped_count} indexed")
                self.store.add_event(
                    series_id,
                    None,
                    "info",
                    f"Discovered {len(created)} new chapter(s): {', '.join(bits)}.",
                )
            else:
                self.store.add_event(series_id, None, "info", "No new chapters found.")

            if initial:
                self.store.set_initialized(series_id)

            self.store.record_check_finish(series_id)
            if force_download:
                await self.download_pending(series_id)
        except Exception as exc:  # noqa: BLE001 - surfaced to the UI event log
            message = str(exc)
            self.store.record_check_finish(series_id, message)
            self.store.add_event(series_id, None, "error", f"Check failed: {message}")

    async def download_pending(self, series_id: int) -> None:
        async with self._download_lock:
            series = self.store.get_series(series_id)
            if not series:
                return
            for chapter in self.store.pending_chapters(series_id):
                await self._download_chapter(series, chapter)

    async def _discover_chapters(self, source_url: str) -> tuple[str, list[dict[str, object]]]:
        if not scraper.host_is_supported(source_url):
            raise ValueError("Only tcbonepiecechapters.com URLs are supported.")

        html = await scraper.fetch_html(source_url)
        page_url = source_url
        if scraper.is_chapter_url(source_url):
            all_chapters_url = scraper.find_all_chapters_url(html, source_url)
            if all_chapters_url:
                await asyncio.sleep(self.request_delay)
                page_url = all_chapters_url
                html = await scraper.fetch_html(all_chapters_url)

        chapters = scraper.parse_chapter_links(html, page_url)
        if chapters:
            return page_url, chapters

        if scraper.is_chapter_url(source_url):
            title = scraper.parse_chapter_title(html, source_url)
            chapter_key, sort_key = scraper.parse_chapter_key(title, source_url)
            return source_url, [
                {
                    "url": source_url,
                    "title": title,
                    "chapter_key": chapter_key,
                    "sort_key": sort_key,
                }
            ]

        raise ValueError("No chapter links were found on that page.")

    async def _download_chapter(self, series: dict[str, Any], chapter: dict[str, Any]) -> None:
        chapter_id = int(chapter["id"])
        self.store.set_chapter_status(chapter_id, "downloading", error=None)
        self.store.add_event(
            int(series["id"]),
            chapter_id,
            "info",
            f"Downloading {chapter['display_title']}.",
        )
        staging_dir = self.work_dir / f"series-{series['id']}" / f"chapter-{chapter_id}"
        try:
            if staging_dir.exists():
                shutil.rmtree(staging_dir)
            staging_dir.mkdir(parents=True, exist_ok=True)

            await asyncio.sleep(self.request_delay)
            html = await scraper.fetch_html(str(chapter["source_url"]))
            images = scraper.parse_page_images(html, str(chapter["source_url"]))
            if not images:
                raise ValueError("No chapter page images were found.")

            image_paths: list[Path] = []
            width = max(3, len(str(len(images))))
            for index, image in enumerate(images, start=1):
                await asyncio.sleep(self.request_delay)
                content, content_type = await scraper.fetch_bytes(
                    str(image["url"]),
                    referer=str(chapter["source_url"]),
                )
                extension = scraper.extension_from_content_type(
                    content_type,
                    str(image.get("extension_hint") or "jpg"),
                )
                image_path = staging_dir / f"{index:0{width}d}.{extension}"
                image_path.write_bytes(content)
                image_paths.append(image_path)

            destination = self._chapter_cbz_path(series, chapter)
            destination.parent.mkdir(parents=True, exist_ok=True)
            temp_destination = destination.with_suffix(destination.suffix + ".tmp")
            with zipfile.ZipFile(temp_destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for image_path in image_paths:
                    archive.write(image_path, image_path.name)
            temp_destination.replace(destination)

            self.store.set_chapter_status(
                chapter_id,
                "downloaded",
                cbz_path=str(destination),
                page_count=len(image_paths),
                error=None,
            )
            self.store.add_event(
                int(series["id"]),
                chapter_id,
                "info",
                f"Packaged {len(image_paths)} page(s) into {destination.name}.",
            )
        except (httpx.HTTPError, OSError, ValueError) as exc:
            self.store.set_chapter_status(chapter_id, "failed", error=str(exc))
            self.store.add_event(
                int(series["id"]),
                chapter_id,
                "error",
                f"Download failed for {chapter['display_title']}: {exc}",
            )
        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)

    def _chapter_cbz_path(self, series: dict[str, Any], chapter: dict[str, Any]) -> Path:
        folder = resolve_library_folder(
            self.library_dir,
            str(series.get("folder") or ""),
            str(series.get("title") or "Manga"),
        )
        chapter_title = str(chapter.get("display_title") or "")
        if not chapter_title:
            chapter_title = f"{series['title']} Chapter {chapter['chapter_key']}"
        file_name = safe_component(chapter_title, "chapter") + ".cbz"
        return folder / file_name


def resolve_library_folder(library_dir: Path, folder: str, title: str) -> Path:
    root = library_dir.resolve()
    raw_parts = re.split(r"[\\/]+", folder.strip()) if folder.strip() else [title]
    parts = [safe_component(part, "") for part in raw_parts]
    clean_parts = [part for part in parts if part and part not in {".", ".."}]
    if not clean_parts:
        clean_parts = [safe_component(title, "Manga")]
    destination = root.joinpath(*clean_parts).resolve()
    if destination != root and root not in destination.parents:
        raise ValueError("Folder must stay inside the configured library directory.")
    return destination


def safe_component(value: str, default: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned:
        cleaned = default
    return cleaned[:140]
