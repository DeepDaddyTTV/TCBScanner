from __future__ import annotations

import unittest

from app import scraper


SERIES_URL = "https://weebcentral.com/series/01J76XY7EBJ4EG5QDZJYFTF8K8/Ao-No-Exorcist"
CHAPTER_URL = "https://weebcentral.com/chapters/01M1KX3K9REENM12DB1QPPB1QG"


class WeebCentralProviderTests(unittest.TestCase):
    def test_primary_search_domains_stay_narrow(self) -> None:
        self.assertEqual(
            scraper.PRIMARY_SOURCE_SEARCH_DOMAINS,
            {"weebcentral.com", "mangack.com"},
        )

    def test_provider_and_endpoint_detection(self) -> None:
        self.assertEqual(scraper.detect_provider(SERIES_URL), "weebcentral")
        self.assertTrue(scraper.is_weebcentral_series_url(SERIES_URL))
        self.assertTrue(scraper.is_weebcentral_chapter_url(CHAPTER_URL))
        self.assertEqual(
            scraper.derive_weebcentral_full_list_url(SERIES_URL),
            "https://weebcentral.com/series/01J76XY7EBJ4EG5QDZJYFTF8K8/full-chapter-list",
        )
        self.assertEqual(
            scraper.derive_weebcentral_images_url(CHAPTER_URL),
            "https://weebcentral.com/chapters/01M1KX3K9REENM12DB1QPPB1QG/images"
            "?is_prev=False&reading_style=long_strip&current_page=1",
        )

    def test_chapter_list_parsing(self) -> None:
        html = """
        <div id="chapter-list">
          <a href="/chapters/older"><span>Chapter 1.5</span></a>
          <a href="/chapters/newer">
            <span class="grow"><span>Chapter 169</span><span>Last Read</span></span>
            <time>2026-09-03T15:09:57Z</time>
          </a>
        </div>
        """
        chapters = scraper.parse_weebcentral_chapter_links(html, SERIES_URL)
        self.assertEqual([item["chapter_key"] for item in chapters], ["1.5", "169"])
        self.assertEqual(chapters[-1]["title"], "Chapter 169")
        self.assertEqual(chapters[-1]["url"], "https://weebcentral.com/chapters/newer")

    def test_image_fragment_parsing(self) -> None:
        html = """
        <section id="chapter-images">
          <img src="https://scans.example/manga/Ao-No-Exorcist/0169-002.png" alt="Page 2">
          <img src="https://scans.example/manga/Ao-No-Exorcist/0169-001.png" alt="Page 1">
          <img src="/static/images/broken_image.jpg" alt="Broken">
        </section>
        """
        images = scraper.parse_weebcentral_page_images(html, CHAPTER_URL)
        self.assertEqual([item["page_number"] for item in images], [1, 2])
        self.assertTrue(images[0]["url"].endswith("0169-001.png"))

    def test_search_result_parsing(self) -> None:
        html = """
        <section>
          <a href="/series/01J76XY7EBJ4EG5QDZJYFTF8K8/Ao-No-Exorcist">
            <img alt="Blue Exorcist cover">
            <div>Blue Exorcist</div>
          </a>
        </section>
        """
        site = {"name": "WeebCentral", "domain": "weebcentral.com"}
        results = scraper.parse_weebcentral_search_candidates(
            html,
            "https://weebcentral.com/search/simple?location=main",
            site,
            "Blue Exorcist",
            "weebcentral",
            "WeebCentral HTML fragments",
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Blue Exorcist")

    def test_anilist_catalog_match_preserves_identity_metadata(self) -> None:
        match = scraper.anilist_catalog_match(
            {
                "id": 179445,
                "format": "MANGA",
                "status": "RELEASING",
                "countryOfOrigin": "KR",
                "chapters": None,
                "siteUrl": "https://anilist.co/manga/179445",
                "title": {
                    "english": "Solo Leveling: Ragnarok",
                    "userPreferred": "Na Honjaman Level Up: Ragnarok",
                },
                "synonyms": [],
                "coverImage": {"large": "https://images.example/cover.jpg"},
            }
        )
        self.assertEqual(match["id"], "179445")
        self.assertEqual(match["title"], "Solo Leveling: Ragnarok")
        self.assertIsNone(match["chapter_count"])

    def test_mangaupdates_catalog_match_preserves_manhwa_identity(self) -> None:
        match = scraper.mangaupdates_catalog_match(
            {
                "series_id": 47955563021,
                "title": "Solo Leveling: Ragnarok",
                "url": "https://www.mangaupdates.com/series/m13i58t/solo-leveling-ragnarok",
                "type": "Manhwa",
                "image": {
                    "url": {
                        "original": "https://cdn.mangaupdates.com/image/i505562.jpg",
                    }
                },
            }
        )

        self.assertEqual(match["provider"], "mangaupdates")
        self.assertEqual(match["id"], "47955563021")
        self.assertEqual(match["format"], "Manhwa")
        self.assertIsNone(match["chapter_count"])
        self.assertEqual(
            match["cover_image_url"],
            "https://cdn.mangaupdates.com/image/i505562.jpg",
        )


if __name__ == "__main__":
    unittest.main()
