from __future__ import annotations

import asyncio
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from . import scraper
from .store import Store


class MangaDownloader:
    def __init__(
        self,
        store: Store,
        *,
        library_roots: list[Path],
        work_dir: Path,
        request_delay: float,
    ) -> None:
        self.store = store
        self.library_roots = [path.resolve() for path in library_roots if str(path).strip()]
        self.primary_library_dir = self.library_roots[0] if self.library_roots else Path("/library").resolve()
        self.work_dir = work_dir
        self.request_delay = request_delay
        self._download_lock = asyncio.Lock()
        for library_root in self.library_roots or [self.primary_library_dir]:
            library_root.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)

    async def check_series(self, series_id: int, *, force_download: bool = True) -> None:
        series = self.store.get_series(series_id)
        if not series:
            return
        self.store.record_check_start(series_id)
        try:
            source_url, chapters, source_index = await self._discover_series_chapters(series)
            if source_index == 0 and source_url != series["source_url"]:
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
            raise ValueError("This site is not in the current supported source list.")
        return await scraper.discover_chapters(source_url, request_delay=self.request_delay)

    async def _discover_series_chapters(
        self,
        series: dict[str, Any],
    ) -> tuple[str, list[dict[str, object]], int]:
        primary_url = str(series.get("source_url") or "").strip()
        backup_urls = [
            str(url).strip()
            for url in series.get("backup_source_urls", [])
            if str(url).strip()
        ]
        candidates = [primary_url, *backup_urls]
        failures: list[str] = []

        for index, source_url in enumerate(candidates):
            try:
                resolved_url, chapters = await self._discover_chapters(source_url)
            except Exception as exc:  # noqa: BLE001 - try the next configured source
                host = urlparse(source_url).netloc or source_url
                failures.append(f"{host}: {exc}")
                if index < len(candidates) - 1:
                    next_host = urlparse(candidates[index + 1]).netloc or candidates[index + 1]
                    self.store.add_event(
                        int(series["id"]),
                        None,
                        "warning",
                        f"Source {host} failed; checking backup {next_host}.",
                    )
                continue

            if index > 0:
                used_host = urlparse(source_url).netloc or source_url
                self.store.add_event(
                    int(series["id"]),
                    None,
                    "info",
                    f"Using backup source {used_host} for this check.",
                )
            return resolved_url, chapters, index

        detail = "; ".join(failures) or "No source URLs are configured."
        raise RuntimeError(f"All configured sources failed. {detail}")

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
            images = await scraper.discover_page_images(
                str(chapter["source_url"]),
                request_delay=self.request_delay,
            )
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

            destination = self._chapter_cbz_path(series, chapter, page_count=len(image_paths))
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

    def _chapter_cbz_path(
        self,
        series: dict[str, Any],
        chapter: dict[str, Any],
        *,
        page_count: int,
    ) -> Path:
        folder = resolve_library_folder(
            self.library_roots or [self.primary_library_dir],
            str(series.get("folder") or ""),
            str(series.get("title") or "Manga"),
        )
        template = str(series.get("naming_format") or self.store.get_default_naming_format())
        file_name = render_naming_template(series, chapter, template, page_count)
        return folder / file_name


def render_naming_template(
    series: dict[str, Any],
    chapter: dict[str, Any],
    template: str,
    page_count: int,
) -> str:
    series_name = str(series.get("title") or "Manga")
    chapter_full_title = str(chapter.get("display_title") or "").strip()
    chapter_number = str(chapter.get("chapter_key") or "").strip()
    if not chapter_full_title:
        chapter_full_title = f"{series_name} Chapter {chapter_number}".strip()
    chapter_title = extract_chapter_name(series_name, chapter_full_title, chapter_number)
    values = {
        "SeriesName": series_name,
        "ChapterNumber": chapter_number,
        "ChapterNumberPadded": padded_chapter_number(chapter_number),
        "ChapterTitle": chapter_title,
        "ChapterName": chapter_title,
        "ChapterFullTitle": chapter_full_title,
        "PageCount": str(page_count),
    }

    def replace(match: re.Match[str]) -> str:
        return values.get(match.group(1), "")

    rendered = re.sub(r"\{([A-Za-z0-9_]+)\}", replace, template or "{ChapterFullTitle}")
    rendered = re.sub(r"\s+", " ", rendered).strip(" -_.")
    return safe_component(rendered, safe_component(chapter_full_title, "chapter")) + ".cbz"


def extract_chapter_name(series_name: str, chapter_title: str, chapter_number: str) -> str:
    name = chapter_title.strip()
    if series_name:
        name = re.sub(rf"^{re.escape(series_name)}\s*", "", name, flags=re.IGNORECASE).strip()
    if chapter_number:
        name = re.sub(
            rf"^[-:\s]*(?:chapter\s*)?{re.escape(chapter_number)}\b[-:\s]*",
            "",
            name,
            flags=re.IGNORECASE,
        ).strip()
    name = re.sub(r"^chapter\s+[-:\s]*", "", name, flags=re.IGNORECASE).strip()
    return name or chapter_title


def padded_chapter_number(chapter_number: str) -> str:
    match = re.fullmatch(r"(\d+)(\.\d+)?", chapter_number.strip())
    if not match:
        return chapter_number
    whole, decimal = match.groups()
    return whole.zfill(4) + (decimal or "")


def resolve_library_folder(library_roots: list[Path], folder: str, title: str) -> Path:
    roots = [root.resolve() for root in library_roots if str(root).strip()]
    primary_root = roots[0] if roots else Path("/library").resolve()
    raw_folder = str(folder or "").strip()

    if raw_folder.startswith("/"):
        candidate = Path(raw_folder).resolve()
        for root in roots or [primary_root]:
            if candidate == root or root in candidate.parents:
                return candidate
        raise ValueError("Folder must stay inside one of the configured library roots.")

    raw_parts = re.split(r"[\\/]+", raw_folder) if raw_folder else [title]
    parts = [safe_component(part, "") for part in raw_parts]
    clean_parts = [part for part in parts if part and part not in {".", ".."}]
    if not clean_parts:
        clean_parts = [safe_component(title, "Manga")]

    destination = primary_root.joinpath(*clean_parts).resolve()
    if destination != primary_root and primary_root not in destination.parents:
        raise ValueError("Folder must stay inside the configured library directory.")
    return destination


def safe_component(value: str, default: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", value)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .")
    if not cleaned:
        cleaned = default
    return cleaned[:140]
