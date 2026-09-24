from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

from app.downloader import MangaDownloader
from app.store import Store


def series_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "Backup Test",
        "source_url": "https://mangack.com/manga/backup-test",
        "backup_source_urls": ["https://opchapters.com/manga/backup-test/"],
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


if __name__ == "__main__":
    unittest.main()
