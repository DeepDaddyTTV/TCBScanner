from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from app.downloader import (
    DownloadCancelled,
    MangaDownloader,
    render_naming_template,
    source_chapter_set_conflicts,
)
from app.store import Store


def series_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "Backup Test",
        "source_url": "https://mangack.com/manga/backup-test",
        "backup_source_urls": ["https://opchapters.com/manga/backup-test/"],
        "metadata_provider": "anilist",
        "metadata_provider_override": "anilist",
        "metadata_id": "179445",
        "metadata_title": "Solo Leveling: Ragnarok",
        "metadata_url": "https://anilist.co/manga/179445",
        "metadata_chapter_count": 69,
        "folder": "Backup Test",
        "check_interval_minutes": 60,
        "enabled": True,
        "backfill_existing": True,
    }
    payload.update(overrides)
    return payload


class BackupSourceStoreTests(unittest.TestCase):
    def test_backup_sources_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir) / "app.db")
            series = store.create_series(series_payload())
            self.assertEqual(
                series["backup_source_urls"],
                ["https://opchapters.com/manga/backup-test/"],
            )
            self.assertEqual(series["metadata_id"], "179445")
            self.assertEqual(series["metadata_provider_override"], "anilist")
            self.assertEqual(series["metadata_chapter_count"], 69)

            updated_payload = series_payload(
                backup_source_urls=[
                    "https://opchapters.com/manga/backup-test/",
                    "https://opchapters.com/manga/backup-test/",
                ]
            )
            updated = store.update_series(int(series["id"]), updated_payload)
            self.assertEqual(
                updated["backup_source_urls"],
                ["https://opchapters.com/manga/backup-test/"],
            )

    def test_reset_series_clears_index_but_preserves_catalog_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir) / "app.db")
            series = store.create_series(series_payload())
            series_id = int(series["id"])
            store.upsert_chapters(
                series_id,
                [{"url": "https://example.com/1", "title": "Chapter 1", "chapter_key": "1", "sort_key": 1}],
                "pending",
            )
            self.assertEqual(store.reset_series(series_id), 1)
            reset = store.get_series(series_id)
            self.assertEqual(reset["chapter_count"], 0)
            self.assertFalse(reset["initialized"])
            self.assertEqual(reset["metadata_id"], "179445")
            self.assertIn("Reset chapter index", store.list_events(series_id=series_id)[0]["message"])

    def test_backup_chapter_replaces_failed_primary_without_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir) / "app.db")
            series = store.create_series(series_payload())
            series_id = int(series["id"])
            chapters = store.upsert_chapters(
                series_id,
                [
                    {
                        "url": "https://mangack.com/chapter/7",
                        "title": "Chapter 7",
                        "chapter_key": "7",
                        "sort_key": 7.0,
                    }
                ],
                "pending",
            )
            store.set_chapter_status(int(chapters[0]["id"]), "failed", error="Primary failed")

            store.upsert_chapters(
                series_id,
                [
                    {
                        "url": "https://opchapters.com/backup-test-chapter-7/",
                        "title": "Backup Test Chapter 7",
                        "chapter_key": "7",
                        "sort_key": 7.0,
                    }
                ],
                "pending",
            )

            saved = store.list_chapters(series_id)
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]["status"], "pending")
            self.assertIsNone(saved[0]["error"])
            self.assertEqual(
                saved[0]["source_url"],
                "https://opchapters.com/backup-test-chapter-7/",
            )


class BackupSourceDownloaderTests(unittest.IsolatedAsyncioTestCase):
    async def test_legacy_naming_tokens_remain_unique(self) -> None:
        filename = render_naming_template(
            {"title": "Solo Leveling Ragnarok"},
            {"chapter_key": "12", "display_title": "Chapter 12 Awakening"},
            "{series} - Chapter {chapter.pad} - {chapter.title}",
            42,
        )
        self.assertEqual(
            filename,
            "Solo Leveling Ragnarok - Chapter 0012 - Awakening.cbz",
        )

    async def test_series_download_can_be_cancelled_for_reset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = Store(root / "app.db")
            downloader = MangaDownloader(
                store,
                library_roots=[root / "manga"],
                work_dir=root / "work",
                request_delay=0.2,
            )
            downloader.request_cancel(8)
            with self.assertRaises(DownloadCancelled):
                downloader._raise_if_cancelled(8)
            downloader.clear_cancel(8)
            downloader._raise_if_cancelled(8)

    async def test_check_falls_back_to_backup_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = Store(root / "app.db")
            series = store.create_series(series_payload())
            downloader = MangaDownloader(
                store,
                library_roots=[root / "manga", root / "manhwa"],
                work_dir=root / "work",
                request_delay=0.2,
            )
            downloader._discover_chapters = AsyncMock(
                side_effect=[
                    RuntimeError("primary unavailable"),
                    (
                        "https://opchapters.com/manga/backup-test/",
                        [
                            {
                                "url": "https://opchapters.com/backup-test-chapter-8/",
                                "title": "Backup Test Chapter 8",
                                "chapter_key": "8",
                                "sort_key": 8.0,
                            }
                        ],
                    ),
                ]
            )

            await downloader.check_series(int(series["id"]), force_download=False)

            saved_series = store.get_series(int(series["id"]))
            self.assertIsNone(saved_series["last_error"])
            self.assertEqual(saved_series["source_url"], series["source_url"])
            self.assertEqual(
                store.list_chapters(int(series["id"]))[0]["source_url"],
                "https://opchapters.com/backup-test-chapter-8/",
            )
            messages = [event["message"] for event in store.list_events(series_id=int(series["id"]))]
            self.assertTrue(any("Using backup source opchapters.com" in message for message in messages))

    async def test_primary_and_backup_chapters_are_merged_by_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = Store(root / "app.db")
            series = store.create_series(series_payload(metadata_chapter_count=None))
            downloader = MangaDownloader(
                store,
                library_roots=[root / "manga"],
                work_dir=root / "work",
                request_delay=0.2,
            )
            downloader._discover_chapters = AsyncMock(
                side_effect=[
                    (
                        series["source_url"],
                        [
                            {"url": "https://primary/1", "title": "Chapter 1", "chapter_key": "1", "sort_key": 1},
                            {"url": "https://primary/2", "title": "Chapter 2", "chapter_key": "2", "sort_key": 2},
                        ],
                    ),
                    (
                        series["backup_source_urls"][0],
                        [
                            {"url": "https://backup/2", "title": "Chapter 2", "chapter_key": "2", "sort_key": 2},
                            {"url": "https://backup/3", "title": "Chapter 3", "chapter_key": "3", "sort_key": 3},
                        ],
                    ),
                ]
            )

            await downloader.check_series(int(series["id"]), force_download=False)

            chapters = sorted(store.list_chapters(int(series["id"])), key=lambda item: item["sort_key"])
            self.assertEqual([item["chapter_key"] for item in chapters], ["1", "2", "3"])
            self.assertEqual(chapters[1]["source_url"], "https://primary/2")
            self.assertEqual(chapters[2]["source_url"], "https://backup/3")

    def test_catalog_count_rejects_implausible_source_set(self) -> None:
        chapters = [
            {"chapter_key": str(number), "sort_key": float(number), "url": f"https://wrong/{number}"}
            for number in range(1, 202)
        ]
        self.assertTrue(source_chapter_set_conflicts(chapters, 69))
        self.assertFalse(source_chapter_set_conflicts(chapters[:68], 69))


if __name__ == "__main__":
    unittest.main()
