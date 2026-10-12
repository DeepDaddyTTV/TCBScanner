"""Optional private identities, shared by download paths and ComicInfo metadata."""
from __future__ import annotations

import json
import os
import re
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def identity_key(value: str) -> str:
    # Keep edition qualifiers and punctuation; only known aliases are equivalent.
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip().casefold()


def source_key(value: str) -> str:
    url = urlsplit(value)
    path = url.path.rstrip("/")
    if url.hostname == "weebcentral.com":
        match = re.match(r"^/series/([^/]+)(?:/|$)", path)
        if match:
            path = "/series/" + match.group(1)
    return urlunsplit((url.scheme.lower(), url.netloc.lower(), path, "", ""))


class CanonicalIdentities:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(os.getenv(
            "CANONICAL_IDENTITIES_FILE",
            str(Path(os.getenv("DATA_DIR", "/data")) / "canonical-identities.json"),
        ))

    def resolve(self, series: dict[str, Any], library_roots: list[Path] | None = None) -> dict[str, Any]:
        if not self.path.exists():
            return dict(series)
        try:
            registry = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("The canonical identity file cannot be read; download export stopped.") from exc
        if registry.get("version") != 1 or not isinstance(registry.get("comic_series"), dict):
            raise ValueError("Unsupported canonical identity file; download export stopped.")

        profiles = registry["comic_series"]
        aliases = registry.get("author_aliases", {})
        if not isinstance(aliases, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in aliases.items()):
            raise ValueError("Invalid canonical author aliases.")
        matches: set[str] = set()
        source_urls = [series.get("source_url"), *series.get("backup_source_urls", [])]
        for name, profile in profiles.items():
            if not isinstance(name, str) or not isinstance(profile, dict):
                raise ValueError("Invalid canonical series profile.")
            for field in ["source_urls", "metadata_ids", "aliases", "writers", "artists"]:
                values = profile.get(field, [])
                if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
                    raise ValueError("Invalid canonical series profile.")
            for field in ["folder", "library_root", "language"]:
                if field in profile and not isinstance(profile[field], str):
                    raise ValueError("Invalid canonical series path.")
            if profile.get("manga") not in [None, "Unknown", "No", "Yes", "YesAndRightToLeft"]:
                raise ValueError("Invalid canonical reading direction.")
            sources = {source_key(url) for url in profile.get("source_urls", [])}
            if sources.intersection(source_key(str(url)) for url in source_urls if url):
                matches.add(name)
            provider = series.get("metadata_provider")
            ident = series.get("metadata_id")
            if provider and ident and f"{provider}:{ident}" in profile.get("metadata_ids", []):
                matches.add(name)
        title = identity_key(str(series.get("title") or ""))
        known_title = False
        for name, profile in profiles.items():
            known_names = {identity_key(name), *(identity_key(x) for x in profile.get("aliases", []))}
            if title in known_names:
                known_title = True
                matches.add(name)
        if matches and not known_title and re.search(r"\([^()]+\)\s*$", str(series.get("title") or "")):
            raise ValueError("Unrecognized edition qualifier; add an explicit canonical profile before export.")
        if len(matches) > 1:
            raise ValueError("Conflicting canonical series identities; download export stopped.")
        if not matches:
            return dict(series)

        name = next(iter(matches))
        profile = profiles[name]
        resolved = dict(series)
        resolved.update(
            title=name,
            writers=list(dict.fromkeys(aliases.get(identity_key(x), x) for x in profile.get("writers", []))),
            artists=list(dict.fromkeys(aliases.get(identity_key(x), x) for x in profile.get("artists", []))),
            canonical_identity=name,
            canonical_title_aliases=[name, *profile.get("aliases", []), str(series.get("title") or "")],
            language=profile.get("language"),
            manga=profile.get("manga"),
        )
        # Already configured paths may have a deliberate spelling or custom location.
        # Rewrite only the known alias component, retaining the selected root/category.
        folder = str(series.get("folder") or "")
        basename = re.split(r"[\\/]+", folder.rstrip("/\\"))[-1]
        known = {identity_key(name), title, *(identity_key(x) for x in profile.get("aliases", []))}
        canonical_folder = str(profile.get("folder") or name)
        root = profile.get("library_root")
        if root and (not folder or ("/" not in folder and "\\" not in folder and identity_key(folder) in known)):
            allowed = {path.resolve() for path in library_roots or []}
            if Path(root).resolve() not in allowed:
                raise ValueError("Canonical series root is not a configured library root.")
            resolved["folder"] = str(Path(root) / canonical_folder)
        elif not folder:
            resolved["folder"] = canonical_folder
        elif basename != canonical_folder and identity_key(basename) in known:
            resolved["folder"] = folder[:len(folder) - len(basename)] + canonical_folder
        return resolved


def canonical_chapter(series: dict[str, Any], chapter: dict[str, Any]) -> dict[str, Any]:
    resolved = dict(chapter)
    title = str(chapter.get("display_title") or "")
    for alias in sorted(series.get("canonical_title_aliases", []), key=len, reverse=True):
        if not alias:
            continue
        match = re.match(rf"^{re.escape(alias)}(?=$|\s|[-:])", title, re.IGNORECASE)
        if match:
            resolved["display_title"] = str(series["title"]) + title[match.end():]
            break
    return resolved


def comic_info(series: dict[str, Any], chapter: dict[str, Any], page_count: int) -> bytes:
    """Standard metadata travels inside the archive; page bytes stay untouched."""
    root = ET.Element("ComicInfo")
    number = str(chapter.get("chapter_key") or "").strip()
    fields = {
        "Title": str(chapter.get("display_title") or "").strip() or (f"Chapter {number}" if number else "Chapter"),
        "Series": str(series.get("title") or "Manga"),
        "Number": number,
        "Writer": ", ".join(series.get("writers") or []),
        "Penciller": ", ".join(series.get("artists") or []),
        "Web": str(chapter.get("source_url") or series.get("source_url") or ""),
        "PageCount": str(page_count),
        "LanguageISO": str(series.get("language") or ""),
        "Format": "Chapter",
        "Manga": str(series.get("manga") or ""),
    }
    for key, value in fields.items():
        if value:
            ET.SubElement(root, key).text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", value)
    pages = ET.SubElement(root, "Pages")
    for index in range(page_count):
        ET.SubElement(pages, "Page", Image=str(index), **({"Type": "FrontCover"} if index == 0 else {}))
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)
