from __future__ import annotations

import asyncio
import os
import tempfile
import zipfile
from pathlib import Path

import pytest
from fastapi import HTTPException

_TEST_DATA_DIR = tempfile.TemporaryDirectory(prefix="sakurarr-local-import-test-")
os.environ.setdefault("DATA_DIR", _TEST_DATA_DIR.name)

from app import main
from app.store import Store


def make_cbz(path: Path, *, pages: int = 2) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for index in range(1, pages + 1):
            archive.writestr(f"page-{index:03}.jpg", b"image")


def test_import_local_series_indexes_cbz_without_moving_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "library"
    folder = root / "Manga" / "Blue Exorcist"
    folder.mkdir(parents=True)
    cbz = folder / "Blue Exorcist Chapter 12 The Visitor.cbz"
    make_cbz(cbz, pages=3)
    database = Store(tmp_path / "app.db")
    monkeypatch.setattr(main, "store", database)
    monkeypatch.setattr(main, "LIBRARY_ROOTS", [root])
    monkeypatch.setattr(main, "schedule_check", lambda _series_id: None)

    result = asyncio.run(main.import_local_series(main.LocalSeriesImport(
        folder_path=str(folder),
        title="Blue Exorcist",
    )))

    assert result["imported_chapters"] == 1
    assert cbz.exists()
    series = database.get_series(result["series"]["id"])
    assert series["local_only"] is True
    assert series["enabled"] is False
    chapter = database.list_chapters(series["id"])[0]
    assert chapter["status"] == "downloaded"
    assert chapter["page_count"] == 3
    assert chapter["cbz_path"] == str(cbz)

    snapshot = database.export_library_snapshot()
    restored = Store(tmp_path / "restored.db")
    restored.import_library_snapshot(snapshot)
    assert restored.get_series(series["id"])["local_only"] is True


def test_import_renaming_rejects_collision_before_renaming_anything(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "library"
    folder = root / "Manga" / "Example"
    folder.mkdir(parents=True)
    source = folder / "Chapter 1.cbz"
    target = folder / "Example Chapter 0001.cbz"
    make_cbz(source)
    make_cbz(target)
    database = Store(tmp_path / "app.db")
    monkeypatch.setattr(main, "store", database)
    monkeypatch.setattr(main, "LIBRARY_ROOTS", [root])

    with pytest.raises(HTTPException) as error:
        asyncio.run(main.import_local_series(main.LocalSeriesImport(
            folder_path=str(folder),
            title="Example",
            naming_format="{SeriesName} Chapter {ChapterNumberPadded}",
            rename_files=True,
        )))

    assert error.value.status_code == 409
    assert source.exists()
    assert target.exists()
    assert database.list_series() == []


def test_import_can_rename_existing_cbz_and_tracks_new_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = tmp_path / "library"
    folder = root / "Series"
    folder.mkdir(parents=True)
    original = folder / "Chapter 7 The Visitor.cbz"
    make_cbz(original)
    database = Store(tmp_path / "app.db")
    monkeypatch.setattr(main, "store", database)
    monkeypatch.setattr(main, "LIBRARY_ROOTS", [root])

    result = asyncio.run(main.import_local_series(main.LocalSeriesImport(
        folder_path=str(folder),
        title="Series",
        naming_format="{SeriesName} - {ChapterNumberPadded} - {ChapterTitle}",
        rename_files=True,
    )))

    renamed = folder / "Series - 0007 - The Visitor.cbz"
    assert renamed.exists()
    assert not original.exists()
    chapter = database.list_chapters(result["series"]["id"])[0]
    assert chapter["cbz_path"] == str(renamed)


def test_folder_browser_restricts_paths_to_configured_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "library"
    folder = root / "Series"
    folder.mkdir(parents=True)
    (root / "Other").mkdir()
    make_cbz(folder / "Chapter 1.cbz")
    monkeypatch.setattr(main, "LIBRARY_ROOTS", [root])

    result = asyncio.run(main.browse_library_folders(str(root)))
    assert result["is_root"] is True
    series_folder = next(item for item in result["folders"] if item["name"] == "Series")
    assert series_folder["cbz_count"] == 1

    with pytest.raises(HTTPException) as error:
        asyncio.run(main.browse_library_folders(str(tmp_path)))
    assert error.value.status_code == 400
