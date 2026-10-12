from __future__ import annotations

import asyncio
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from app import scraper
from app.canonical_identity import CanonicalIdentities, canonical_chapter, comic_info
from app.downloader import MangaDownloader
from app.store import Store


def registry(tmp_path: Path, **overrides: object) -> CanonicalIdentities:
    data = {
        "version": 1,
        "author_aliases": {"doe, jane": "Jane Doe"},
        "comic_series": {
            "Moon Hero": {
                "folder": "Moon Hero",
                "aliases": ["Moon Hero Alternate"],
                "writers": ["Doe, Jane"],
                "artists": ["A. Artist"],
                "source_urls": ["https://weebcentral.com/series/KNOWN-ID/Moon-Hero"],
                "metadata_ids": ["anilist:123"],
            },
            "Moon Hero (Color)": {"folder": "Moon Hero (Color)", "writers": ["Jane Doe"]},
        },
    }
    data.update(overrides)
    file = tmp_path / "identities.json"
    file.write_text(json.dumps(data), encoding="utf-8")
    return CanonicalIdentities(file)


def test_curated_aliases_share_export_names_and_creator_roles(tmp_path: Path) -> None:
    source = {"title": "Moon Hero Alternate", "folder": "/manga/Moon Hero Alternate"}
    resolved = registry(tmp_path).resolve(source)
    assert resolved["title"] == "Moon Hero"
    assert resolved["folder"] == "/manga/Moon Hero"
    assert resolved["writers"] == ["Jane Doe"]
    assert resolved["artists"] == ["A. Artist"]
    assert source["title"] == "Moon Hero Alternate"


def test_source_id_survives_slug_change_and_metadata_id_resolves_unknown_alias(tmp_path: Path) -> None:
    identities = registry(tmp_path)
    assert identities.resolve({"title": "Provider title", "source_url": "https://weebcentral.com/series/KNOWN-ID/New-Slug?tracking=1"})["title"] == "Moon Hero"
    assert identities.resolve({"title": "Another provider title", "metadata_provider": "anilist", "metadata_id": "123"})["writers"] == ["Jane Doe"]


def test_editions_unknown_titles_and_custom_folders_remain_distinct(tmp_path: Path) -> None:
    identities = registry(tmp_path)
    assert identities.resolve({"title": "Moon Hero (Color)"})["title"] == "Moon Hero (Color)"
    unknown = {"title": "Moon Hero (ONE)", "folder": "/manga/My Custom Folder"}
    assert identities.resolve(unknown) == unknown
    assert identities.resolve({"title": "Moon Hero", "folder": "/manga/My Custom Folder"})["folder"] == "/manga/My Custom Folder"


def test_conflicting_edition_and_source_id_stop_export(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Conflicting"):
        registry(tmp_path).resolve({"title": "Moon Hero (Color)", "metadata_provider": "anilist", "metadata_id": "123"})


def test_known_default_folder_uses_configured_category_root(tmp_path: Path) -> None:
    root = tmp_path / "manhwa"
    identities = registry(tmp_path, comic_series={"Moon Hero": {"aliases": ["Alternate"], "library_root": str(root)}})
    assert identities.resolve({"title": "Alternate", "folder": "Alternate"}, [root])["folder"] == str(root / "Moon Hero")
    with pytest.raises(ValueError, match="configured library root"):
        identities.resolve({"title": "Alternate", "folder": "Alternate"}, [tmp_path / "manga"])


@pytest.mark.parametrize("number", ["1", "2", "10", "11", "0.5", "175.10", "extra-1"])
def test_comicinfo_preserves_numbers_roles_pages_and_xml_text(tmp_path: Path, number: str) -> None:
    series = registry(tmp_path).resolve({"title": "Moon Hero Alternate"})
    chapter = canonical_chapter(series, {"chapter_key": number, "display_title": "Moon Hero Alternate - A & B <Return>"})
    node = ET.fromstring(comic_info(series, chapter, 2))
    assert node.findtext("Title") == "Moon Hero - A & B <Return>"
    assert node.findtext("Series") == "Moon Hero"
    assert node.findtext("Number") == number
    assert node.findtext("Writer") == "Jane Doe"
    assert node.findtext("Penciller") == "A. Artist"
    assert node.findtext("PageCount") == "2"
    assert [x.attrib["Image"] for x in node.findall("Pages/Page")] == ["0", "1"]


def test_no_registry_preserves_existing_series_and_still_writes_metadata(tmp_path: Path) -> None:
    series = {"title": "Distinct New Title", "folder": "Custom"}
    assert CanonicalIdentities(tmp_path / "not-configured.json").resolve(series) == series
    node = ET.fromstring(comic_info(series, {"chapter_key": "1.5"}, 1))
    assert node.findtext("Series") == "Distinct New Title"
    assert node.findtext("Number") == "1.5"
    assert node.find("Writer") is None


def test_real_download_path_adds_metadata_before_placement_without_changing_pages(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    database = Store(tmp_path / "app.db")
    series = database.create_series({"title": "Moon Hero Alternate", "folder": "Moon Hero Alternate", "source_url": "https://example.com/series", "check_interval_minutes": 60})
    database.set_setting("default_naming_format", "{SeriesName} - Ch. {ChapterNumberPadded}")
    chapter = database.upsert_chapters(series["id"], [{"url": "https://example.com/chapter-10.5", "title": "Moon Hero Alternate Chapter 10.5", "chapter_key": "10.5", "sort_key": 10.5}], "pending")[0]
    images = [b"first-page-original-bytes", b"second-page-original-bytes"]
    monkeypatch.setattr(scraper, "discover_page_images", AsyncMock(return_value=[{"url": "https://example.com/1"}, {"url": "https://example.com/2"}]))
    monkeypatch.setattr(scraper, "fetch_bytes", AsyncMock(side_effect=[(x, "image/png") for x in images]))
    downloader = MangaDownloader(database, library_roots=[tmp_path / "manga"], work_dir=tmp_path / "work", request_delay=0, identities=registry(tmp_path))
    asyncio.run(downloader.download_pending(series["id"]))
    saved = database.get_chapter(chapter["id"])
    assert saved["status"] == "downloaded"
    destination = Path(saved["cbz_path"])
    assert destination == tmp_path / "manga" / "Moon Hero" / "Moon Hero - Ch. 0010.5.cbz"
    with zipfile.ZipFile(destination) as archive:
        assert [archive.read(f"{index:03}.png") for index in [1, 2]] == images
        metadata = ET.fromstring(archive.read("ComicInfo.xml"))
        assert metadata.findtext("Series") == "Moon Hero"
        assert metadata.findtext("Number") == "10.5"
        assert metadata.findtext("Writer") == "Jane Doe"
        assert archive.testzip() is None
    assert saved["page_count"] == 2
    assert database.get_series(series["id"])["title"] == "Moon Hero Alternate"


@pytest.mark.parametrize("content", ['{"version": 2}', '{"version": 1, "comic_series": {"Moon Hero": {"writers": "wrong type"}}}', 'not json'])
def test_bad_config_stops_before_any_pages_are_downloaded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str) -> None:
    identities = registry(tmp_path)
    identities.path.write_text(content, encoding="utf-8")
    database = Store(tmp_path / "app.db")
    series = database.create_series({"title": "Moon Hero", "folder": "Moon Hero", "source_url": "https://example.com/series", "check_interval_minutes": 60})
    chapter = database.upsert_chapters(series["id"], [{"url": "https://example.com/chapter-1", "title": "Chapter 1", "chapter_key": "1", "sort_key": 1}], "pending")[0]
    fetch = AsyncMock()
    monkeypatch.setattr(scraper, "discover_page_images", fetch)
    downloader = MangaDownloader(database, library_roots=[tmp_path / "manga"], work_dir=tmp_path / "work", request_delay=0, identities=identities)
    asyncio.run(downloader.download_pending(series["id"]))
    assert database.get_chapter(chapter["id"])["status"] == "failed"
    fetch.assert_not_called()
    assert list((tmp_path / "manga").rglob("*.cbz")) == []
