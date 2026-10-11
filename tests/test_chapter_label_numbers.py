from __future__ import annotations

import unittest

from app import scraper


class ChapterLabelNumberTests(unittest.TestCase):
    def test_label_number_wins_over_opaque_chapter_id(self) -> None:
        url = "https://weebcentral.com/chapters/01KNBD4EG6JTPEGXNR34P05ZEQ"
        for label, number in [
            ("Episode 252", "252"),
            ("episode 175.10", "175.10"),
            ("Ep. 10", "10"),
            ("Punch 219 (Official)", "219"),
            ("Punch 196 (Re-Draw)", "196"),
            ("Chapter 1.5", "1.5"),
            ("Ch. 11", "11"),
        ]:
            with self.subTest(label=label):
                self.assertEqual(scraper.parse_chapter_key(label, url), (number, float(number)))

    def test_episode_chapters_remain_distinct_and_numerically_ordered(self) -> None:
        html = """
          <a href="/chapters/01KBBBBBBBBBBBBBBBBBBBBBBBB"><span>Episode 11</span></a>
          <a href="/chapters/01KCCCCCCCCCCCCCCCCCCCCCCCC"><span>Episode 9</span></a>
          <a href="/chapters/01KDDDDDDDDDDDDDDDDDDDDDDDD"><span>Episode 10</span></a>
        """
        chapters = scraper.parse_weebcentral_chapter_links(
            html, "https://weebcentral.com/series/01J76XYE23859ZWDP7BJ520AKY/The-Beginning-After-The-End"
        )
        self.assertEqual([item["chapter_key"] for item in chapters], ["9", "10", "11"])
        self.assertEqual(len({item["url"] for item in chapters}), 3)

    def test_existing_explicit_url_number_fallback_is_preserved(self) -> None:
        self.assertEqual(
            scraper.parse_chapter_key("Bonus story", "https://example.com/chapter-23.5/"),
            ("23.5", 23.5),
        )


if __name__ == "__main__":
    unittest.main()
