from __future__ import annotations

import unittest

from app import scraper


SERIES_URL = "https://opchapters.com/manga/one-piece/"


class OpChaptersProviderTests(unittest.TestCase):
    def test_provider_detection(self) -> None:
        self.assertEqual(scraper.detect_provider(SERIES_URL), "wordpress_manga")

    def test_chapter_list_parsing(self) -> None:
        html = """
        <section>
          <a href="/one-piece-chapter-1193/">One Piece Chapter 1193</a>
          <a href="https://opchapters.com/one-piece-chapter-1194/">One Piece Chapter 1194</a>
        </section>
        """
        chapters = scraper.parse_wordpress_chapter_links(html, SERIES_URL)
        self.assertEqual([item["chapter_key"] for item in chapters], ["1193", "1194"])
        self.assertEqual(
            chapters[-1]["url"],
            "https://opchapters.com/one-piece-chapter-1194",
        )

    def test_embedded_reader_images_are_parsed(self) -> None:
        html = """
        <script>
          ts_reader.run({"sources":[{"source":"Server 1","images":[
            "https://i1.wp.com/opchapters.com/wp-content/uploads/2026/09/OP1194-001.png",
            "https://i1.wp.com/opchapters.com/wp-content/uploads/2026/09/OP1194-002.png",
            "https://i1.wp.com/opchapters.com/wp-content/uploads/2026/09/OP1194-003.png"
          ]}]});
        </script>
        """
        images = scraper.parse_wordpress_page_images(
            html,
            "https://opchapters.com/one-piece-chapter-1194/",
        )
        self.assertEqual(len(images), 3)
        self.assertTrue(images[0]["url"].endswith("OP1194-001.png"))


if __name__ == "__main__":
    unittest.main()
