"""Small, credential-free parsers for common manga reading-list exports."""

from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from typing import Any


PROVIDERS = {
    "atsumaru": "Atsumaru",
    "mal": "MyAnimeList",
    "anilist": "AniList",
    "kenmei": "Kenmei",
    "mangaupdates": "MangaUpdates",
    "kitsu": "Kitsu",
    "comick": "Comick",
}
MAX_IMPORT_BYTES = 5 * 1024 * 1024
MAX_IMPORT_ENTRIES = 2500


def normalize_title_key(value: Any) -> str:
    normalized = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").lower())


def _pick(row: dict[str, Any], *names: str) -> Any:
    by_key = {_key(key): value for key, value in row.items()}
    for name in names:
        if _key(name) in by_key and by_key[_key(name)] not in (None, ""):
            return by_key[_key(name)]
    return None


def _number(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return max(0, int(float(str(value).replace(",", ""))))
    except (TypeError, ValueError):
        return None


def _score(value: Any) -> float | int | None:
    if value in (None, ""):
        return None
    try:
        number = float(str(value).replace(",", ""))
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return None


def _entry(row: dict[str, Any], provider: str = "") -> dict[str, Any] | None:
    title = _pick(row, "title", "series_title", "manga_title", "manga name", "name", "series", "media.title.english", "media.title.romaji")
    if isinstance(title, dict):
        title = title.get("english") or title.get("romaji") or title.get("userPreferred")
    if not title:
        nested = row.get("media") or row.get("manga") or row.get("series")
        if isinstance(nested, dict):
            title = nested.get("title") or nested.get("name")
            if isinstance(title, dict):
                title = title.get("english") or title.get("romaji") or title.get("userPreferred")
    if not title and isinstance(row.get("attributes"), dict):
        attributes = row["attributes"]
        title = attributes.get("canonicalTitle") or attributes.get("title")
    title = " ".join(str(title or "").split())
    if not title:
        return None
    status = _pick(row, "status", "bookmark_status", "my_status", "reading_status", "list_status")
    if isinstance(status, dict):
        status = status.get("name") or status.get("status")
    progress = _pick(row, "progress", "last_read_chapter", "chapters_read", "my_read_chapters", "chapter", "chapter_number", "read_chapters")
    score = _score(_pick(row, "score", "rating") or (row.get("attributes") or {}).get("rating"))
    external_id = _pick(row, "id", "atsu_id", "anilist_id", "my_anime_list_id", "mal_id", "series_mangadb_id", "kitsu_id", "manga_updates_id", "mangaupdates_id", "comick_id", "kenmei_id")
    if external_id is None:
        for nested_key in ("media", "manga", "series"):
            nested = row.get(nested_key)
            if isinstance(nested, dict) and nested.get("id") is not None:
                external_id = nested["id"]
                break
    return {
        "title": title[:120],
        "status": str(status or "").strip()[:80],
        "progress": _number(progress),
        "score": score,
        "external_id": str(external_id).strip()[:100] if external_id is not None else "",
        "provider": provider,
    }


def _walk_json(payload: Any, provider: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [entry for item in payload if isinstance(item, dict) if (entry := _entry(item, provider))]
    if not isinstance(payload, dict):
        return []
    # Handle AniList API responses and the common Atsumaru export envelopes.
    data = payload.get("data")
    if isinstance(data, dict):
        user = data.get("User") or data.get("user")
        if isinstance(user, dict):
            lists = user.get("mediaList") or user.get("mangaList") or []
            if isinstance(lists, dict):
                lists = lists.get("lists", [])
            flattened = (
                [entry for group in lists if isinstance(group, dict) for entry in group.get("entries", [])]
                if lists and isinstance(lists[0], dict) and "entries" in lists[0]
                else lists
            ) if isinstance(lists, list) else []
            return [entry for item in flattened if isinstance(item, dict) if (entry := _entry(item, provider))]
    for key in ("bookmarks", "entries", "items", "manga", "series", "list", "data"):
        value = payload.get(key)
        if isinstance(value, list):
            result = [entry for item in value if isinstance(item, dict) if (entry := _entry(item, provider))]
            if result:
                return result
    for value in payload.values():
        if isinstance(value, list):
            result = _walk_json(value, provider)
            if result:
                return result
    entry = _entry(payload, provider)
    return [entry] if entry else []


def parse_reading_list(contents: str, filename: str, provider: str = "") -> list[dict[str, Any]]:
    if len(contents.encode("utf-8")) > MAX_IMPORT_BYTES:
        raise ValueError("Import files must be 5 MB or smaller.")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    cleaned_provider = provider.strip().lower()
    if cleaned_provider and cleaned_provider not in PROVIDERS:
        raise ValueError("Choose a supported reading-list provider.")
    if suffix == "json" or contents.lstrip().startswith(("{", "[")):
        entries = _walk_json(json.loads(contents), cleaned_provider)
    elif suffix == "xml" or contents.lstrip().startswith("<"):
        try:
            root = ET.fromstring(contents)
        except ET.ParseError as exc:
            raise ValueError("The XML file is malformed or incomplete.") from exc
        entries = []
        for node in root.iter():
            if node.tag.rsplit("}", 1)[-1].lower() not in {"manga", "entry", "bookmark", "series"}:
                continue
            row = {child.tag.rsplit("}", 1)[-1]: child.text for child in node}
            entry = _entry(row, cleaned_provider)
            if entry:
                entries.append(entry)
    else:
        reader = csv.DictReader(io.StringIO(contents))
        if not reader.fieldnames:
            raise ValueError("This file does not contain a recognizable CSV header.")
        entries = [entry for row in reader if (entry := _entry(dict(row), cleaned_provider))]
    # Deduplicate within the upload while retaining the first provider record.
    unique: dict[str, dict[str, Any]] = {}
    for entry in entries:
        unique.setdefault(normalize_title_key(entry["title"]), entry)
    entries = list(unique.values())
    if not entries:
        raise ValueError("No manga titles were found. Upload a supported CSV, JSON, or XML reading-list export.")
    if len(entries) > MAX_IMPORT_ENTRIES:
        raise ValueError(f"Reading lists are limited to {MAX_IMPORT_ENTRIES} titles per import.")
    return entries
