from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from app import main
from app.reading_list_import import parse_reading_list
from app.store import Store


@pytest.mark.parametrize(
    ("filename", "provider", "contents", "title", "status", "progress", "external_id"),
    [
        (
            "atsu.json", "atsumaru",
            json.dumps({"bookmarks": [{"title": "Blue Exorcist", "bookmark_status": "Reading", "last_read_chapter": 25, "anilist_id": 991}]}),
            "Blue Exorcist", "Reading", 25, "991",
        ),
        (
            "list.xml", "mal",
            "<myanimelist><manga><series_mangadb_id>321</series_mangadb_id><series_title>Blue Exorcist</series_title><my_status>Reading</my_status><my_read_chapters>25</my_read_chapters></manga></myanimelist>",
            "Blue Exorcist", "Reading", 25, "321",
        ),
        (
            "list.csv", "kenmei",
            "Title,Status,Chapters Read\nBlue Exorcist,Reading,25\n",
            "Blue Exorcist", "Reading", 25, "",
        ),
        (
            "list.json", "anilist",
            json.dumps({"data": {"User": {"mediaList": [{"status": "CURRENT", "progress": 25, "score": 8, "media": {"id": 991, "title": {"english": "Blue Exorcist"}}}]}}}),
            "Blue Exorcist", "CURRENT", 25, "991",
        ),
    ],
)
def test_reading_list_formats_normalize_entries(filename, provider, contents, title, status, progress, external_id):
    [entry] = parse_reading_list(contents, filename, provider)
    assert entry["title"] == title
    assert entry["status"] == status
    assert entry["progress"] == progress
    assert entry["external_id"] == external_id


def test_reading_list_rejects_unrecognized_content():
    with pytest.raises(ValueError, match="No manga titles"):
        parse_reading_list("title,status\n,\n", "list.csv", "comick")


def test_reading_list_parser_preserves_japanese_and_decimal_score():
    [entry] = parse_reading_list(
        json.dumps({"entries": [{"title": "葬送のフリーレン", "score": 8.5}]}),
        "list.json",
        "kitsu",
    )
    assert entry["title"] == "葬送のフリーレン"
    assert entry["score"] == 8.5


def test_reading_list_import_is_paused_and_backup_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    database = Store(tmp_path / "app.db")
    monkeypatch.setattr(main, "store", database)
    payload = main.ReadingListImport(provider="mal", entries=[
        main.ReadingListEntry(title="Blue Exorcist", status="Reading", progress=25, external_id="321"),
    ])

    result = asyncio.run(main.import_reading_list(payload))
    assert result["imported_count"] == 1
    series = database.get_series(result["imported"][0]["id"])
    assert series["local_only"] is True
    assert series["enabled"] is False
    assert series["reading_list_data"] == {
        "provider": "mal", "status": "Reading", "progress": 25,
        "score": None, "external_id": "321",
    }

    configured = asyncio.run(main.update_series(series["id"], main.SeriesUpdate(
        title="Blue Exorcist",
        source_url="https://mangadex.org/title/example/blue-exorcist",
        enabled=False,
        local_only=False,
    )))
    assert configured["series"]["reading_list_data"] == series["reading_list_data"]
    assert configured["series"]["local_only"] is False

    restored = Store(tmp_path / "restored.db")
    snapshot = database.export_library_snapshot()
    assert snapshot["schema_version"] == 7
    restored.import_library_snapshot(snapshot)
    assert restored.get_series(series["id"])["reading_list_data"] == series["reading_list_data"]
    duplicate = asyncio.run(main.import_reading_list(payload))
    assert duplicate["imported_count"] == 0
    assert duplicate["skipped"] == ["Blue Exorcist"]


def test_reading_list_import_attaches_selected_source_and_schedules_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    database = Store(tmp_path / "app.db")
    monkeypatch.setattr(main, "store", database)
    scheduled: list[int] = []
    monkeypatch.setattr(main, "schedule_check", scheduled.append)
    payload = main.ReadingListImport(provider="kenmei", entries=[
        main.ReadingListEntry(
            title="Blue Exorcist",
            source_url="https://mangack.com/manga/blue-exorcist",
        ),
    ])

    result = asyncio.run(main.import_reading_list(payload))
    series = database.get_series(result["imported"][0]["id"])
    assert result["monitored_count"] == 1
    assert series["source_url"] == "https://mangack.com/manga/blue-exorcist"
    assert series["enabled"] is True
    assert series["local_only"] is False
    assert scheduled == [series["id"]]


def test_reading_list_source_matching_uses_fast_primary_domains(monkeypatch: pytest.MonkeyPatch):
    calls: list[str] = []

    async def fake_search(title: str, limit: int):
        calls.append(title)
        return [{"title": f"{title} matched", "url": "https://weebcentral.com/series/test", "site_name": "WeebCentral"}]

    monkeypatch.setattr(main.scraper, "search_primary_supported_series", fake_search)
    result = asyncio.run(main.match_reading_list_sources(main.ReadingListMatchRequest(
        titles=["Blue Exorcist", "Solo Leveling"],
    )))
    assert calls == ["Blue Exorcist", "Solo Leveling"]
    assert result["searched_sites"] == ["weebcentral.com", "mangack.com"]
    assert [item["matches"][0]["site_name"] for item in result["matches"]] == ["WeebCentral", "WeebCentral"]


def test_primary_source_search_does_not_fan_out_to_fallback_sites(monkeypatch: pytest.MonkeyPatch):
    import app.scraper as scraper

    sites = [
        {"provider": "weebcentral", "family": "WeebCentral", "sites": [{"domain": "weebcentral.com"}]},
        {"provider": "wordpress_manga", "family": "WordPress", "sites": [{"domain": "mangack.com"}]},
        {"provider": "wordpress_manga", "family": "WordPress", "sites": [{"domain": "fallback.example"}]},
    ]
    requested: list[str] = []

    async def fake_search(query, *, provider, family, site):
        requested.append(site["domain"])
        return []

    monkeypatch.setattr(scraper, "SUPPORTED_SOURCE_GROUPS", sites)
    monkeypatch.setattr(scraper, "search_supported_site", fake_search)
    assert asyncio.run(scraper.search_primary_supported_series("Blue Exorcist")) == []
    assert set(requested) == {"weebcentral.com", "mangack.com"}
