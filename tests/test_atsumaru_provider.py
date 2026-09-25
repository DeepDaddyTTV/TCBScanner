from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from app import scraper
from app.downloader import source_chapter_set_conflicts
from app.store import Store


class AtsumaruProviderTests(unittest.IsolatedAsyncioTestCase):
    def test_detects_atsu_domain_as_supported_source(self) -> None:
        url = "https://atsu.moe/manga/4xYnd"
        self.assertEqual(scraper.detect_provider(url), "atsumaru")
        self.assertTrue(scraper.host_is_supported(url))

    def test_source_count_handles_fractional_chapter_parts(self) -> None:
        chapters = [
            {"chapter_key": str(number), "sort_key": float(number), "source_chapter_count": 77}
            for number in range(1, 78)
        ]
        chapters.extend(
            {"chapter_key": f"{number}.1", "sort_key": number + 0.1, "source_chapter_count": 77}
            for number in range(1, 20)
        )
        self.assertFalse(source_chapter_set_conflicts(chapters, 77))
        self.assertTrue(source_chapter_set_conflicts(chapters, 60))

    async def test_uses_preferred_translator_and_falls_back_per_chapter(self) -> None:
        page = {
            "mangaPage": {
                "scanlators": [
                    {"id": "gamma", "name": "Gamma"},
                    {"id": "lht", "name": "LHT"},
                ],
                "sourcePreference": None,
            }
        }
        info = {
            "chapters": [
                {"id": "c1-g", "title": "Chapter 1", "number": 1, "scanId": "gamma", "index": 1},
                {"id": "c1-l", "title": "Chapter 1", "number": 1, "scanId": "lht", "index": 2},
                {"id": "c2-g", "title": "Chapter 2", "number": 2, "scanId": "gamma", "index": 3},
            ]
        }

        async def fetch_json(url: str) -> dict[str, object]:
            return page if "/api/manga/page" in url else info

        with patch.object(scraper, "fetch_json", new=AsyncMock(side_effect=fetch_json)):
            _, chapters = await scraper.discover_atsumaru_chapters(
                "https://atsu.moe/manga/series-id",
                preferred_translator="LHT",
            )

        self.assertEqual(len(chapters), 2)
        by_number = {chapter["chapter_key"]: chapter for chapter in chapters}
        self.assertEqual(by_number["1"]["translator"], "LHT")
        self.assertTrue(str(by_number["1"]["url"]).endswith("/read/series-id/c1-l"))
        self.assertEqual(by_number["2"]["translator"], "Gamma")

    async def test_maps_search_catalog_metadata(self) -> None:
        async def fetch_json(_url: str) -> dict[str, object]:
            return {
                "hits": [
                    {
                        "document": {
                            "id": "series-id",
                            "title": "Example Manga",
                            "otherNames": ["Example"],
                            "medium": "Comic",
                            "status": "Ongoing",
                            "chapterCount": 42,
                            "authors": ["Author"],
                            "year": 2020,
                            "poster": "/static/posters/example.jpg",
                        }
                    }
                ]
            }

        with patch.object(scraper, "fetch_json", new=AsyncMock(side_effect=fetch_json)):
            matches = await scraper.search_atsumaru_catalog("Example Manga")

        self.assertEqual(matches[0]["provider"], "atsumaru")
        self.assertEqual(matches[0]["chapter_count"], 42)
        self.assertEqual(matches[0]["url"], "https://atsu.moe/manga/series-id")
        self.assertEqual(
            matches[0]["cover_image_url"],
            "https://cdn.atsu.moe/static/posters/example.jpg",
        )

    async def test_reads_page_images_from_reader_json(self) -> None:
        async def fetch_json(_url: str) -> dict[str, object]:
            return {
                "readChapter": {
                    "pages": [
                        {"number": 1, "image": "/static/pages/chapter-id/second.avif"},
                        {"number": 0, "image": "/static/pages/chapter-id/first.avif"},
                    ]
                }
            }

        with patch.object(scraper, "fetch_json", new=AsyncMock(side_effect=fetch_json)):
            images = await scraper.discover_atsumaru_page_images(
                "https://atsu.moe/read/series-id/chapter-id"
            )

        self.assertEqual(len(images), 2)
        self.assertTrue(str(images[0]["url"]).endswith("/static/pages/chapter-id/first.avif"))
        self.assertEqual(scraper.extension_from_url(str(images[0]["url"])), "avif")


class AtsumaruPreferencePersistenceTests(unittest.TestCase):
    def test_preferred_translator_round_trips_in_library_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Store(Path(temp_dir) / "source.db")
            series = source.create_series(
                {
                    "title": "Example Manga",
                    "source_url": "https://atsu.moe/manga/series-id",
                    "folder": "Example Manga",
                    "check_interval_minutes": 1440,
                    "metadata_provider_override": "atsumaru",
                    "preferred_translator": "LHT",
                }
            )
            target = Store(Path(temp_dir) / "target.db")

            target.import_library_snapshot(source.export_library_snapshot())

            restored = target.get_series(int(series["id"]))
            self.assertEqual(restored["preferred_translator"], "LHT")
            self.assertEqual(restored["metadata_provider_override"], "atsumaru")


if __name__ == "__main__":
    unittest.main()
