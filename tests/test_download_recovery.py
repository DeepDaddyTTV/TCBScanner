from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.store import Store


class DownloadRecoveryTests(unittest.TestCase):
    def test_downloading_chapters_return_to_pending_once(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Store(Path(temp_dir) / "app.db")
            series = store.create_series(
                {
                    "title": "Recovery Test",
                    "source_url": "https://example.com/series/recovery-test",
                    "folder": "Recovery Test",
                    "check_interval_minutes": 60,
                    "enabled": True,
                    "backfill_existing": True,
                }
            )
            chapters = store.upsert_chapters(
                int(series["id"]),
                [
                    {
                        "url": "https://example.com/chapters/1",
                        "title": "Chapter 1",
                        "chapter_key": "1",
                        "sort_key": 1.0,
                    }
                ],
                "pending",
            )
            chapter_id = int(chapters[0]["id"])
            store.set_chapter_status(chapter_id, "downloading")

            self.assertEqual(
                store.recover_interrupted_downloads(),
                {int(series["id"]): 1},
            )
            self.assertEqual(store.get_chapter(chapter_id)["status"], "pending")
            self.assertEqual(store.recover_interrupted_downloads(), {})


if __name__ == "__main__":
    unittest.main()
