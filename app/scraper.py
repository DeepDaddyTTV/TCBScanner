from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from html import unescape
from pathlib import PurePosixPath
from time import monotonic
from urllib.parse import quote_plus, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "TCB-CBZ-Monitor/1.0 (+local personal archiver)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BROWSERLIKE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": HEADERS["Accept"],
    "Accept-Language": HEADERS["Accept-Language"],
}

ANILIST_GRAPHQL_URL = "https://graphql.anilist.co"
MANGAUPDATES_API_BASE = "https://api.mangaupdates.com/v1"
KITSU_API_BASE = "https://kitsu.io/api/edge"
JIKAN_API_BASE = "https://api.jikan.moe/v4"
MANGADEX_API_BASE = "https://api.mangadex.org"
MANGADEX_COVERS_BASE = "https://uploads.mangadex.org/covers"
MANGADEX_MAX_COVER_FETCH = 100
MANGADEX_ARTWORK_VARIANT_WORDS = {
    "official",
    "colored",
    "colour",
    "color",
    "digital",
    "comic",
    "comics",
    "edition",
    "editions",
    "deluxe",
    "premium",
    "full",
}
ARTWORK_SEARCH_LIMIT = 5
ARTWORK_MIN_POSTER_CHOICES = 5
ARTWORK_CACHE_TTL_SECONDS = 60 * 60 * 12
JIKAN_REQUEST_GAP_SECONDS = 1.25
PRIMARY_SOURCE_SEARCH_DOMAINS = {"weebcentral.com", "mangack.com"}

SERIES_ART_META_SELECTORS = (
    ("meta[property='og:image']", "content"),
    ("meta[name='twitter:image']", "content"),
    ("meta[itemprop='image']", "content"),
    ("meta[name='twitter:image:src']", "content"),
)

SERIES_ART_IMAGE_SELECTORS = (
    ".summary_image img",
    ".summary-content img",
    ".profile-manga.summary-layout-1 img",
    ".tab-summary img",
    ".post-content_item .summary_image img",
    ".series-information img",
    ".series-profile img",
    ".thumb img",
    ".post-title-item img",
)

TCB_SITES = (
    {
        "name": "TCB One Piece Chapters",
        "domain": "tcbonepiecechapters.com",
    },
)

WORDPRESS_MANGA_SITES = (
    {"name": "OP Chapters", "domain": "opchapters.com"},
    {"name": "Mangalink", "domain": "linkmanga.com"},
    {"name": "PAWMANGA", "domain": "pawmanga.com"},
    {"name": "Mangaclash", "domain": "toonclash.com"},
    {"name": "Aqua Manga", "domain": "aquareader.org"},
    {"name": "Mangahot", "domain": "manhuahot.com"},
    {"name": "CoffeeManga", "domain": "coffeemanga.ink"},
    {"name": "MangaSushi", "domain": "mangasushi.org"},
    {"name": "Mangazin", "domain": "mangazin.org"},
    {"name": "Manhwatoon", "domain": "manhwatoon.me"},
    {"name": "Kingofshojo", "domain": "kingofshojo.com"},
    {"name": "Rokari Comics", "domain": "rokaricomics.com"},
    {"name": "Reset Scans", "domain": "reset-scans.org"},
    {"name": "Flame Scans", "domain": "flamescans.lol"},
    {"name": "Mangack", "domain": "mangack.com"},
    {"name": "MangaRead", "domain": "mangaread.org"},
    {"name": "Lilymanga", "domain": "lilymanga.net"},
    {"name": "Rawkuma", "domain": "rawkuma.net"},
    {"name": "KDT Scans", "domain": "silentquill.net"},
    {"name": "Galaxy Manga", "domain": "galaxymanga.io"},
    {"name": "Manhuarm MTL", "domain": "manhuarmtl.com"},
)

TODAY_BOOK_SITES = (
    {"name": "Today Manga", "domain": "todaymanga.com"},
)

SERIALIZED_COMIC_SITES = (
    {"name": "Temple Scan", "domain": "templescan.net"},
    {
        "name": "Diva Scans",
        "domain": "divascans.org",
        "aliases": ["divascans.com"],
        "url": "https://divascans.com/",
    },
)

NEXT_SERIES_SITES = (
    {"name": "Flame Comics", "domain": "flamecomics.xyz"},
)

WEBTOON_PORTAL_SITES = (
    {"name": "ManhwaZ", "domain": "manhwaz.com"},
    {"name": "ManhwaHub", "domain": "manhwahub.net"},
)

KURAMANGA_SITES = (
    {"name": "KuraManga", "domain": "kuramanga.com"},
)

WEEBCENTRAL_SITES = (
    {"name": "WeebCentral", "domain": "weebcentral.com"},
)

SUPPORTED_SOURCE_GROUPS = (
    {
        "provider": "tcb",
        "family": "Custom TCB HTML",
        "sites": TCB_SITES,
    },
    {
        "provider": "wordpress_manga",
        "family": "WordPress-style manga HTML",
        "sites": WORDPRESS_MANGA_SITES,
    },
    {
        "provider": "today_book",
        "family": "Book chapter-list HTML",
        "sites": TODAY_BOOK_SITES,
    },
    {
        "provider": "serialized_comic",
        "family": "Serialized comic HTML",
        "sites": SERIALIZED_COMIC_SITES,
    },
    {
        "provider": "next_series",
        "family": "Next.js series HTML",
        "sites": NEXT_SERIES_SITES,
    },
    {
        "provider": "webtoon_portal",
        "family": "Webtoon portal HTML",
        "sites": WEBTOON_PORTAL_SITES,
    },
    {
        "provider": "kuramanga",
        "family": "Flat series slug HTML",
        "sites": KURAMANGA_SITES,
    },
    {
        "provider": "weebcentral",
        "family": "WeebCentral HTML fragments",
        "sites": WEEBCENTRAL_SITES,
    },
)

WORDPRESS_IMAGE_SELECTORS = (
    ".reading-content img",
    ".entry-content img",
    ".chapter-content img",
    ".container-chapter-reader img",
    ".text-left img",
    ".page-break img",
    ".main-content img",
    ".wp-manga-chapter-img",
)

WORDPRESS_CHAPTER_PATTERNS = (
    re.compile(r"/chapter(?:[-/]|%20)\d", re.IGNORECASE),
    re.compile(r"-chapter-\d", re.IGNORECASE),
    re.compile(r"/ch[-_ ]*\d", re.IGNORECASE),
    re.compile(r"/ch(?:apter)?[-_ ]*\d", re.IGNORECASE),
)

WORDPRESS_NUMERIC_IMAGE = re.compile(r"(\d{1,4})(?=\D*$)")


@dataclass(frozen=True)
class ChapterLink:
    url: str
    title: str
    chapter_key: str
    sort_key: float


@dataclass(frozen=True)
class PageImage:
    url: str
    page_number: int
    extension_hint: str


@dataclass(frozen=True)
class SourceSearchCandidate:
    title: str
    url: str
    score: int
    site_name: str
    site_domain: str
    provider: str
    family: str


@dataclass
class ArtworkMetadata:
    cover_image_url: str = ""
    hero_image_url: str = ""
    poster_choices: list[str] = field(default_factory=list)


ARTWORK_RESPONSE_CACHE: dict[tuple[str, str], tuple[float, dict[str, object]]] = {}
JIKAN_REQUEST_LOCK: asyncio.Lock | None = None
JIKAN_LAST_REQUEST_AT = 0.0


async def fetch_html(url: str) -> str:
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 403:
            raise
    return await asyncio.to_thread(fetch_html_with_requests, url)


async def post_html(url: str, data: dict[str, str]) -> str:
    return await asyncio.to_thread(post_html_with_requests, url, data)


async def fetch_bytes(url: str, *, referer: str | None = None) -> tuple[bytes, str]:
    headers = dict(HEADERS)
    headers["Accept"] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    if referer:
        headers["Referer"] = referer
    try:
        async with httpx.AsyncClient(headers=headers, timeout=60, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.content, response.headers.get("content-type", "")
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code != 403:
            raise
    return await asyncio.to_thread(fetch_bytes_with_requests, url, referer)


def fetch_html_with_requests(url: str) -> str:
    import requests

    response = requests.get(url, headers=BROWSERLIKE_HEADERS, timeout=30, allow_redirects=True)
    response.raise_for_status()
    return response.text


def post_html_with_requests(url: str, data: dict[str, str]) -> str:
    import requests

    headers = dict(BROWSERLIKE_HEADERS)
    headers["HX-Request"] = "true"
    response = requests.post(
        url,
        data=data,
        headers=headers,
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.text


def fetch_bytes_with_requests(url: str, referer: str | None = None) -> tuple[bytes, str]:
    import requests

    headers = dict(BROWSERLIKE_HEADERS)
    headers["Accept"] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    if referer:
        headers["Referer"] = referer
    response = requests.get(url, headers=headers, timeout=60, allow_redirects=True)
    response.raise_for_status()
    return response.content, response.headers.get("content-type", "")


def fetch_mangadex_search_with_requests(query: str, limit: int) -> dict[str, object]:
    import requests

    response = requests.get(
        f"{MANGADEX_API_BASE}/manga",
        params=[
            ("title", query),
            ("limit", limit),
            ("includes[]", "cover_art"),
        ],
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def fetch_mangadex_covers_with_requests(manga_id: str, limit: int) -> dict[str, object]:
    import requests

    response = requests.get(
        f"{MANGADEX_API_BASE}/cover",
        params=[
            ("manga[]", manga_id),
            ("limit", min(max(limit, 1), MANGADEX_MAX_COVER_FETCH)),
        ],
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def fetch_anilist_search_with_requests(query: str, limit: int) -> dict[str, object]:
    import requests

    response = requests.post(
        ANILIST_GRAPHQL_URL,
        json={
            "query": """
                query ($search: String, $perPage: Int) {
                  Page(perPage: $perPage) {
                    media(search: $search, type: MANGA, sort: SEARCH_MATCH) {
                      id
                      idMal
                      format
                      status
                      countryOfOrigin
                      chapters
                      volumes
                      siteUrl
                      title {
                        romaji
                        english
                        native
                        userPreferred
                      }
                      synonyms
                      coverImage {
                        extraLarge
                        large
                        medium
                      }
                      bannerImage
                    }
                  }
                }
            """,
            "variables": {
                "search": query,
                "perPage": max(1, min(limit, 10)),
            },
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": HEADERS["User-Agent"],
        },
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def fetch_mangaupdates_search_with_requests(query: str, limit: int) -> dict[str, object]:
    import requests

    response = requests.post(
        f"{MANGAUPDATES_API_BASE}/series/search",
        json={
            "search": query,
            "perpage": max(1, min(limit, 25)),
        },
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": HEADERS["User-Agent"],
        },
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def fetch_kitsu_search_with_requests(query: str, limit: int) -> dict[str, object]:
    import requests

    response = requests.get(
        f"{KITSU_API_BASE}/manga",
        params={
            "filter[text]": query,
            "page[limit]": max(1, min(limit, 10)),
        },
        headers={
            "Accept": "application/vnd.api+json",
            "User-Agent": HEADERS["User-Agent"],
        },
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def fetch_jikan_json_with_requests(path: str, params: dict[str, object] | None = None) -> dict[str, object]:
    import requests

    response = requests.get(
        f"{JIKAN_API_BASE}{path}",
        params=params or None,
        headers={
            "Accept": "application/json",
            "User-Agent": HEADERS["User-Agent"],
        },
        timeout=30,
        allow_redirects=True,
    )
    response.raise_for_status()
    return response.json()


def list_supported_sources() -> list[dict[str, object]]:
    return [
        {
            "provider": group["provider"],
            "family": group["family"],
            "count": len(group["sites"]),
            "sites": [
                {
                    "name": site["name"],
                    "domain": site["domain"],
                    "url": site.get("url") or f"https://{site['domain']}/",
                }
                for site in group["sites"]
            ],
        }
        for group in SUPPORTED_SOURCE_GROUPS
    ]


def supported_source_count() -> int:
    return sum(len(group["sites"]) for group in SUPPORTED_SOURCE_GROUPS)


def normalize_artwork_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        cleaned = normalize_url(url) if url else ""
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        ordered.append(cleaned)
    return ordered


def artwork_query_variants(title: str, source_url: str) -> list[str]:
    variants = [normalize_artwork_key(title)]
    slug = urlparse(source_url).path.rstrip("/").split("/")[-1] if source_url else ""
    slug = re.sub(r"[-_](?:\d+)$", "", slug)
    slug = normalize_artwork_key(slug)
    if slug:
        variants.append(slug)
    return [item for item in dict.fromkeys(variants) if item]


def artwork_match_rank(query_variants: set[str], candidate_titles: list[str]) -> int:
    candidate_keys = {
        normalize_artwork_key(candidate)
        for candidate in candidate_titles
        if normalize_artwork_key(candidate)
    }
    if query_variants & candidate_keys:
        return 2

    for candidate_key in candidate_keys:
        candidate_words = candidate_key.split()
        for query in query_variants:
            query_words = query.split()
            if not query_words or len(candidate_words) <= len(query_words):
                continue
            if candidate_words[: len(query_words)] != query_words:
                continue
            suffix_words = candidate_words[len(query_words) :]
            if suffix_words and all(word in MANGADEX_ARTWORK_VARIANT_WORDS for word in suffix_words):
                return 1
    return 0


def artwork_cache_key(title: str, source_url: str) -> tuple[str, str]:
    return normalize_artwork_key(title), normalize_url(source_url)


def get_cached_artwork(title: str, source_url: str) -> dict[str, object] | None:
    cache_entry = ARTWORK_RESPONSE_CACHE.get(artwork_cache_key(title, source_url))
    if not cache_entry:
        return None
    cached_at, payload = cache_entry
    if monotonic() - cached_at >= ARTWORK_CACHE_TTL_SECONDS:
        ARTWORK_RESPONSE_CACHE.pop(artwork_cache_key(title, source_url), None)
        return None
    return payload


def set_cached_artwork(title: str, source_url: str, payload: dict[str, object]) -> dict[str, object]:
    ARTWORK_RESPONSE_CACHE[artwork_cache_key(title, source_url)] = (monotonic(), payload)
    return payload


def preferred_artwork_url(*values: str) -> str:
    for value in values:
        cleaned = str(value or "").strip()
        if cleaned:
            return cleaned
    return ""


def merge_artwork_choices(*choice_groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in choice_groups:
        merged.extend(group)
    return dedupe_urls(merged)


def anilist_title_variants(item: dict[str, object]) -> list[str]:
    titles: list[str] = []
    title_block = item.get("title")
    if isinstance(title_block, dict):
        titles.extend(str(value).strip() for value in title_block.values() if str(value).strip())
    synonyms = item.get("synonyms")
    if isinstance(synonyms, list):
        titles.extend(str(value).strip() for value in synonyms if str(value).strip())
    return list(dict.fromkeys(titles))


def anilist_format_rank(value: object) -> int:
    normalized = str(value or "").strip().upper()
    return {
        "MANGA": 0,
        "ONE_SHOT": 1,
        "NOVEL": 8,
    }.get(normalized, 4)


def anilist_cover_url(item: dict[str, object]) -> str:
    cover_block = item.get("coverImage")
    if not isinstance(cover_block, dict):
        return ""
    return preferred_artwork_url(
        str(cover_block.get("extraLarge") or "").strip(),
        str(cover_block.get("large") or "").strip(),
        str(cover_block.get("medium") or "").strip(),
    )


def anilist_catalog_match(item: dict[str, object]) -> dict[str, object]:
    title_block = item.get("title") if isinstance(item.get("title"), dict) else {}
    preferred_title = preferred_artwork_url(
        str(title_block.get("english") or "").strip(),
        str(title_block.get("userPreferred") or "").strip(),
        str(title_block.get("romaji") or "").strip(),
        str(title_block.get("native") or "").strip(),
    )
    item_id = str(item.get("id") or "").strip()
    site_url = str(item.get("siteUrl") or "").strip()
    if not site_url and item_id:
        site_url = f"https://anilist.co/manga/{item_id}"
    return {
        "provider": "anilist",
        "id": item_id,
        "title": preferred_title,
        "url": site_url,
        "format": str(item.get("format") or "").strip(),
        "status": str(item.get("status") or "").strip(),
        "country_of_origin": str(item.get("countryOfOrigin") or "").strip(),
        "chapter_count": item.get("chapters") if isinstance(item.get("chapters"), int) else None,
        "volume_count": item.get("volumes") if isinstance(item.get("volumes"), int) else None,
        "cover_image_url": anilist_cover_url(item),
        "titles": anilist_title_variants(item),
    }


async def search_anilist_catalog(query: str, limit: int = 8) -> list[dict[str, object]]:
    cleaned = " ".join(str(query or "").strip().split())
    if len(cleaned) < 2:
        return []
    payload = await asyncio.to_thread(
        fetch_anilist_search_with_requests,
        cleaned,
        max(1, min(limit, 12)),
    )
    media = payload.get("data", {}).get("Page", {}).get("media", [])
    if not isinstance(media, list):
        return []

    query_variants = {normalize_artwork_key(cleaned)}
    ranked: list[tuple[int, int, str, dict[str, object]]] = []
    for item in media:
        if not isinstance(item, dict) or not item.get("id"):
            continue
        match_rank = artwork_match_rank(query_variants, anilist_title_variants(item))
        catalog_item = anilist_catalog_match(item)
        catalog_item["match_score"] = match_rank
        ranked.append(
            (
                -match_rank,
                anilist_format_rank(item.get("format")),
                str(catalog_item.get("title") or "").lower(),
                catalog_item,
            )
        )
    ranked.sort(key=lambda item: item[:3])
    return [item[3] for item in ranked[: max(1, min(limit, 12))]]


def mangaupdates_type_rank(value: object) -> int:
    normalized = str(value or "").strip().lower()
    return {
        "manhwa": 0,
        "manga": 1,
        "manhua": 2,
        "webtoon": 3,
        "novel": 9,
    }.get(normalized, 5)


def mangaupdates_catalog_match(record: dict[str, object]) -> dict[str, object]:
    image = record.get("image") if isinstance(record.get("image"), dict) else {}
    image_urls = image.get("url") if isinstance(image.get("url"), dict) else {}
    item_id = str(record.get("series_id") or "").strip()
    title = str(record.get("title") or "").strip()
    return {
        "provider": "mangaupdates",
        "id": item_id,
        "title": title,
        "url": str(record.get("url") or "").strip(),
        "format": str(record.get("type") or "").strip(),
        "status": "",
        "country_of_origin": "",
        # MangaUpdates does not expose a reliable current chapter total here.
        "chapter_count": None,
        "volume_count": None,
        "cover_image_url": preferred_artwork_url(
            str(image_urls.get("original") or "").strip(),
            str(image_urls.get("thumb") or "").strip(),
        ),
        "titles": [title] if title else [],
    }


async def search_mangaupdates_catalog(query: str, limit: int = 8) -> list[dict[str, object]]:
    cleaned = " ".join(str(query or "").strip().split())
    if len(cleaned) < 2:
        return []
    payload = await asyncio.to_thread(
        fetch_mangaupdates_search_with_requests,
        cleaned,
        max(1, min(limit, 12)),
    )
    results = payload.get("results", [])
    if not isinstance(results, list):
        return []

    query_variants = {normalize_artwork_key(cleaned)}
    ranked: list[tuple[int, int, str, dict[str, object]]] = []
    for result in results:
        record = result.get("record") if isinstance(result, dict) else None
        if not isinstance(record, dict) or not record.get("series_id"):
            continue
        catalog_item = mangaupdates_catalog_match(record)
        match_rank = artwork_match_rank(query_variants, catalog_item["titles"])
        catalog_item["match_score"] = match_rank
        ranked.append(
            (
                -match_rank,
                mangaupdates_type_rank(record.get("type")),
                str(catalog_item.get("title") or "").lower(),
                catalog_item,
            )
        )
    ranked.sort(key=lambda item: item[:3])
    return [item[3] for item in ranked[: max(1, min(limit, 12))]]


async def search_catalog(provider: str, query: str, limit: int = 8) -> list[dict[str, object]]:
    normalized_provider = str(provider or "anilist").strip().lower()
    if normalized_provider == "anilist":
        return await search_anilist_catalog(query, limit=limit)
    if normalized_provider == "mangaupdates":
        return await search_mangaupdates_catalog(query, limit=limit)
    raise ValueError(f"Unsupported catalog provider: {provider}")


def kitsu_title_variants(attributes: dict[str, object]) -> list[str]:
    titles: list[str] = []
    titles.append(str(attributes.get("canonicalTitle") or "").strip())
    titles.append(str(attributes.get("slug") or "").replace("-", " ").strip())
    abbreviated = attributes.get("abbreviatedTitles")
    if isinstance(abbreviated, list):
        titles.extend(str(value).strip() for value in abbreviated if str(value).strip())
    title_block = attributes.get("titles")
    if isinstance(title_block, dict):
        titles.extend(str(value).strip() for value in title_block.values() if str(value).strip())
    return [item for item in dict.fromkeys(titles) if item]


def kitsu_subtype_rank(value: object) -> int:
    normalized = str(value or "").strip().lower()
    return {
        "manga": 0,
        "manhwa": 0,
        "manhua": 0,
        "oel": 0,
        "oneshot": 1,
        "doujin": 2,
        "novel": 8,
    }.get(normalized, 4)


def kitsu_image_url(image_block: object) -> str:
    if not isinstance(image_block, dict):
        return ""
    return preferred_artwork_url(
        str(image_block.get("original") or "").strip(),
        str(image_block.get("large") or "").strip(),
        str(image_block.get("medium") or "").strip(),
        str(image_block.get("small") or "").strip(),
    )


def jikan_title_variants(item: dict[str, object]) -> list[str]:
    titles: list[str] = [
        str(item.get("title") or "").strip(),
        str(item.get("title_english") or "").strip(),
        str(item.get("title_japanese") or "").strip(),
    ]
    variants = item.get("titles")
    if isinstance(variants, list):
        for entry in variants:
            if isinstance(entry, dict):
                titles.append(str(entry.get("title") or "").strip())
    return [item for item in dict.fromkeys(titles) if item]


def jikan_type_rank(value: object) -> int:
    normalized = str(value or "").strip().lower()
    return {
        "manga": 0,
        "manhwa": 0,
        "manhua": 0,
        "one-shot": 1,
        "doujinshi": 2,
        "light novel": 8,
        "novel": 8,
    }.get(normalized, 4)


def jikan_primary_image_url(item: dict[str, object]) -> str:
    images = item.get("images")
    if not isinstance(images, dict):
        return ""
    for key in ("jpg", "webp"):
        image_block = images.get(key)
        if isinstance(image_block, dict):
            resolved = preferred_artwork_url(
                str(image_block.get("large_image_url") or "").strip(),
                str(image_block.get("image_url") or "").strip(),
                str(image_block.get("small_image_url") or "").strip(),
            )
            if resolved:
                return resolved
    return ""


def jikan_picture_urls(payload: dict[str, object], limit: int) -> list[str]:
    urls: list[str] = []
    for item in payload.get("data", []):
        if not isinstance(item, dict):
            continue
        urls.append(
            preferred_artwork_url(
                str(item.get("jpg", {}).get("large_image_url") or "").strip()
                if isinstance(item.get("jpg"), dict)
                else "",
                str(item.get("jpg", {}).get("image_url") or "").strip()
                if isinstance(item.get("jpg"), dict)
                else "",
                str(item.get("webp", {}).get("large_image_url") or "").strip()
                if isinstance(item.get("webp"), dict)
                else "",
                str(item.get("webp", {}).get("image_url") or "").strip()
                if isinstance(item.get("webp"), dict)
                else "",
            )
        )
    return dedupe_urls(urls)[:limit]


def mangadex_title_variants(attributes: dict[str, object]) -> list[str]:
    titles: list[str] = []
    title_block = attributes.get("title")
    if isinstance(title_block, dict):
        titles.extend(str(value).strip() for value in title_block.values() if str(value).strip())
    alt_titles = attributes.get("altTitles")
    if isinstance(alt_titles, list):
        for entry in alt_titles:
            if isinstance(entry, dict):
                titles.extend(str(value).strip() for value in entry.values() if str(value).strip())
    return list(dict.fromkeys(titles))


def mangadex_cover_sort_key(cover: dict[str, object]) -> tuple[int, int, Decimal, str, str]:
    raw_volume = str(cover.get("volume") or "").strip()
    locale = str(cover.get("locale") or "").strip().lower()
    try:
        volume_value = Decimal(raw_volume) if raw_volume else Decimal("9999")
    except InvalidOperation:
        volume_value = Decimal("9999")
    locale_rank = {"en": 0, "ja": 1, "ko": 2, "es": 3}.get(locale, 9)
    volume_rank = 0 if raw_volume == "1" else 1
    return (
        volume_rank,
        locale_rank,
        volume_value,
        locale,
        str(cover.get("file_name") or ""),
    )


def mangadex_cover_urls(manga_id: str, payload: dict[str, object], limit: int) -> list[str]:
    entries: list[dict[str, object]] = []
    for item in payload.get("data", []):
        if not isinstance(item, dict):
            continue
        attributes = item.get("attributes")
        if not isinstance(attributes, dict):
            continue
        file_name = str(attributes.get("fileName") or "").strip()
        if not file_name:
            continue
        entries.append(
            {
                "file_name": file_name,
                "locale": str(attributes.get("locale") or "").strip(),
                "volume": str(attributes.get("volume") or "").strip(),
            }
        )
    entries.sort(key=mangadex_cover_sort_key)
    return [
        f"{MANGADEX_COVERS_BASE}/{manga_id}/{entry['file_name']}.512.jpg"
        for entry in entries[:limit]
    ]


def absolute_image_url(base_url: str, raw_url: str) -> str:
    if not raw_url:
        return ""
    return normalize_url(urljoin(base_url, raw_url))


def is_generic_series_artwork_url(url: str) -> bool:
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    file_name = PurePosixPath(lowered_path).name
    stem = PurePosixPath(file_name).stem.lower()

    if lowered_path.endswith((".svg", ".gif")):
        return True

    if re.search(r"/img/ch\d+", lowered_path):
        return True

    blocked_tokens = (
        "logo",
        "favicon",
        "avatar",
        "placeholder",
        "default",
        "sprite",
        "site-icon",
    )
    return any(token in lowered_path or token in stem for token in blocked_tokens)


async def extract_series_page_artwork(source_url: str) -> list[str]:
    if detect_provider(source_url) == "tcb":
        return []

    html = await fetch_html(source_url)
    soup = BeautifulSoup(html, "lxml")
    image_urls: list[str] = []

    for selector, attribute in SERIES_ART_META_SELECTORS:
        for node in soup.select(selector):
            value = str(node.get(attribute) or "").strip()
            if value:
                resolved = absolute_image_url(source_url, value)
                if resolved and not is_generic_series_artwork_url(resolved):
                    image_urls.append(resolved)

    for selector in SERIES_ART_IMAGE_SELECTORS:
        for node in soup.select(selector):
            value = str(node.get("data-src") or node.get("src") or "").strip()
            if value:
                resolved = absolute_image_url(source_url, value)
                if resolved and not is_generic_series_artwork_url(resolved):
                    image_urls.append(resolved)

    return dedupe_urls(image_urls)


async def search_anilist_artwork(title: str, source_url: str) -> ArtworkMetadata:
    queries = artwork_query_variants(title, source_url)
    query_variants = set(queries)
    if not query_variants:
        return ArtworkMetadata()

    matches: list[tuple[int, int, dict[str, object]]] = []
    seen_ids: set[str] = set()
    for query in queries:
        payload = await asyncio.to_thread(fetch_anilist_search_with_requests, query, ARTWORK_SEARCH_LIMIT)
        media = payload.get("data", {}).get("Page", {}).get("media", [])
        if not isinstance(media, list):
            continue
        for item in media:
            if not isinstance(item, dict):
                continue
            match_rank = artwork_match_rank(query_variants, anilist_title_variants(item))
            if not match_rank:
                continue
            item_id = str(item.get("id") or "").strip()
            if not item_id or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            matches.append((match_rank, anilist_format_rank(item.get("format")), item))

    if not matches:
        return ArtworkMetadata()

    matches.sort(key=lambda item: (-item[0], item[1], str(item[2].get("id") or "")))
    best = matches[0][2]
    cover_url = anilist_cover_url(best)
    hero_url = preferred_artwork_url(str(best.get("bannerImage") or "").strip(), cover_url)
    return ArtworkMetadata(
        cover_image_url=cover_url,
        hero_image_url=hero_url,
        poster_choices=dedupe_urls([cover_url]),
    )


async def search_kitsu_artwork(title: str, source_url: str) -> ArtworkMetadata:
    queries = artwork_query_variants(title, source_url)
    query_variants = set(queries)
    if not query_variants:
        return ArtworkMetadata()

    matches: list[tuple[int, int, dict[str, object]]] = []
    seen_ids: set[str] = set()
    for query in queries:
        payload = await asyncio.to_thread(fetch_kitsu_search_with_requests, query, ARTWORK_SEARCH_LIMIT)
        results = payload.get("data", [])
        if not isinstance(results, list):
            continue
        for item in results:
            if not isinstance(item, dict):
                continue
            attributes = item.get("attributes")
            if not isinstance(attributes, dict):
                continue
            match_rank = artwork_match_rank(query_variants, kitsu_title_variants(attributes))
            if not match_rank:
                continue
            item_id = str(item.get("id") or "").strip()
            if not item_id or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            matches.append((match_rank, kitsu_subtype_rank(attributes.get("subtype")), attributes))

    if not matches:
        return ArtworkMetadata()

    matches.sort(key=lambda item: (-item[0], item[1], str(item[2].get("canonicalTitle") or "")))
    best = matches[0][2]
    poster_url = kitsu_image_url(best.get("posterImage"))
    hero_url = preferred_artwork_url(kitsu_image_url(best.get("coverImage")), poster_url)
    return ArtworkMetadata(
        cover_image_url=poster_url,
        hero_image_url=hero_url,
        poster_choices=dedupe_urls([poster_url, hero_url]),
    )


def get_jikan_request_lock() -> asyncio.Lock:
    global JIKAN_REQUEST_LOCK
    if JIKAN_REQUEST_LOCK is None:
        JIKAN_REQUEST_LOCK = asyncio.Lock()
    return JIKAN_REQUEST_LOCK


async def fetch_jikan_json(path: str, params: dict[str, object] | None = None) -> dict[str, object]:
    global JIKAN_LAST_REQUEST_AT

    for attempt in range(3):
        async with get_jikan_request_lock():
            wait_seconds = JIKAN_REQUEST_GAP_SECONDS - (monotonic() - JIKAN_LAST_REQUEST_AT)
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            JIKAN_LAST_REQUEST_AT = monotonic()
        try:
            return await asyncio.to_thread(fetch_jikan_json_with_requests, path, params)
        except Exception as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code == 429 and attempt < 2:
                await asyncio.sleep((attempt + 1) * 1.5)
                continue
            if status_code == 404:
                return {}
            raise
    return {}


async def search_jikan_artwork(title: str, source_url: str, limit: int = 8) -> ArtworkMetadata:
    queries = artwork_query_variants(title, source_url)
    query_variants = set(queries)
    if not query_variants:
        return ArtworkMetadata()

    matches: list[tuple[int, int, dict[str, object]]] = []
    seen_ids: set[str] = set()
    for query in queries:
        payload = await fetch_jikan_json(
            "/manga",
            {
                "q": query,
                "limit": ARTWORK_SEARCH_LIMIT,
                "sfw": "true",
            },
        )
        results = payload.get("data", [])
        if not isinstance(results, list):
            continue
        for item in results:
            if not isinstance(item, dict):
                continue
            match_rank = artwork_match_rank(query_variants, jikan_title_variants(item))
            if not match_rank:
                continue
            item_id = str(item.get("mal_id") or "").strip()
            if not item_id or item_id in seen_ids:
                continue
            seen_ids.add(item_id)
            matches.append((match_rank, jikan_type_rank(item.get("type")), item))

    if not matches:
        return ArtworkMetadata()

    matches.sort(key=lambda item: (-item[0], item[1], str(item[2].get("mal_id") or "")))
    best = matches[0][2]
    primary_url = jikan_primary_image_url(best)
    picture_urls: list[str] = []
    mal_id = str(best.get("mal_id") or "").strip()
    if mal_id:
        try:
            pictures_payload = await fetch_jikan_json(f"/manga/{mal_id}/pictures")
            picture_urls = jikan_picture_urls(pictures_payload, max(limit, 1))
        except Exception:
            picture_urls = []

    poster_choices = dedupe_urls([primary_url, *picture_urls])[: max(limit, 1)]
    cover_url = primary_url or (poster_choices[0] if poster_choices else "")
    return ArtworkMetadata(
        cover_image_url=cover_url,
        hero_image_url=cover_url,
        poster_choices=poster_choices,
    )


async def search_mangadex_cover_art(title: str, source_url: str, limit: int = 8) -> list[str]:
    queries = artwork_query_variants(title, source_url)
    query_variants = set(queries)
    if not query_variants:
        return []

    matched_manga_ids: list[tuple[int, str]] = []
    seen_manga_ids: set[str] = set()
    for query in queries:
        payload = await asyncio.to_thread(
            fetch_mangadex_search_with_requests,
            query,
            limit,
        )
        for item in payload.get("data", []):
            if not isinstance(item, dict):
                continue
            attributes = item.get("attributes")
            if not isinstance(attributes, dict):
                continue
            candidate_titles = mangadex_title_variants(attributes)
            match_rank = artwork_match_rank(query_variants, candidate_titles)
            if not match_rank:
                continue
            manga_id = str(item.get("id") or "").strip()
            if not manga_id or manga_id in seen_manga_ids:
                continue
            seen_manga_ids.add(manga_id)
            matched_manga_ids.append((match_rank, manga_id))

    if not matched_manga_ids:
        return []

    matched_manga_ids.sort(key=lambda item: (-item[0], item[1]))
    curated_urls: list[str] = []
    cover_fetch_limit = max(limit * 8, MANGADEX_MAX_COVER_FETCH)
    for index, (_, manga_id) in enumerate(matched_manga_ids[:2]):
        covers_payload = await asyncio.to_thread(
            fetch_mangadex_covers_with_requests,
            manga_id,
            cover_fetch_limit,
        )
        per_series_limit = max(2, limit if index == 0 else limit // 2)
        curated_urls.extend(mangadex_cover_urls(manga_id, covers_payload, per_series_limit))
        if len(dedupe_urls(curated_urls)) >= limit:
            break
    return dedupe_urls(curated_urls)[:limit]


async def resolve_series_artwork(title: str, source_url: str) -> dict[str, object]:
    cached = get_cached_artwork(title, source_url)
    if cached is not None:
        return cached

    source_choices: list[str] = []
    try:
        source_choices = await extract_series_page_artwork(source_url)
    except Exception:
        source_choices = []

    source_cover = source_choices[0] if source_choices else ""

    anilist_result: ArtworkMetadata
    kitsu_result: ArtworkMetadata
    jikan_result = ArtworkMetadata()

    metadata_results = await asyncio.gather(
        search_anilist_artwork(title, source_url),
        search_kitsu_artwork(title, source_url),
        return_exceptions=True,
    )
    anilist_result = metadata_results[0] if isinstance(metadata_results[0], ArtworkMetadata) else ArtworkMetadata()
    kitsu_result = metadata_results[1] if isinstance(metadata_results[1], ArtworkMetadata) else ArtworkMetadata()

    poster_choices = merge_artwork_choices(
        [source_cover],
        anilist_result.poster_choices,
        kitsu_result.poster_choices,
    )

    if len(poster_choices) < ARTWORK_MIN_POSTER_CHOICES:
        try:
            jikan_result = await search_jikan_artwork(
                title,
                source_url,
                limit=max(ARTWORK_MIN_POSTER_CHOICES, 8),
            )
        except Exception:
            jikan_result = ArtworkMetadata()
        poster_choices = merge_artwork_choices(
            [source_cover],
            anilist_result.poster_choices,
            kitsu_result.poster_choices,
            jikan_result.poster_choices,
        )

    cover_image_url = preferred_artwork_url(
        source_cover,
        anilist_result.cover_image_url,
        kitsu_result.cover_image_url,
        jikan_result.cover_image_url,
    )
    hero_image_url = preferred_artwork_url(
        anilist_result.hero_image_url,
        kitsu_result.hero_image_url,
        cover_image_url,
        jikan_result.hero_image_url,
    )

    return set_cached_artwork(title, source_url, {
        "cover_image_url": cover_image_url,
        "hero_image_url": hero_image_url or cover_image_url,
        "poster_choices": poster_choices,
    })


async def search_supported_series(query: str, limit: int = 12) -> list[dict[str, object]]:
    cleaned = " ".join(str(query or "").strip().split())
    if len(cleaned) < 2:
        return []

    searchable_providers = {"wordpress_manga", "webtoon_portal", "kuramanga", "weebcentral"}
    semaphore = asyncio.Semaphore(6)

    async def run_site_search(group: dict[str, object], site: dict[str, object]) -> list[SourceSearchCandidate]:
        async with semaphore:
            try:
                return await search_supported_site(
                    cleaned,
                    provider=str(group["provider"]),
                    family=str(group["family"]),
                    site=site,
                )
            except Exception:
                return []

    searchable_sites = [
        (group, site)
        for group in SUPPORTED_SOURCE_GROUPS
        if str(group["provider"]) in searchable_providers
        for site in group["sites"]
    ]

    primary_sites = [
        (group, site)
        for group, site in searchable_sites
        if str(site["domain"]) in PRIMARY_SOURCE_SEARCH_DOMAINS
    ]
    fallback_sites = [
        (group, site)
        for group, site in searchable_sites
        if str(site["domain"]) not in PRIMARY_SOURCE_SEARCH_DOMAINS
    ]

    primary_tasks = [run_site_search(group, site) for group, site in primary_sites]
    results = await asyncio.gather(*primary_tasks) if primary_tasks else []
    if not any(results):
        fallback_tasks = [run_site_search(group, site) for group, site in fallback_sites]
        results.extend(await asyncio.gather(*fallback_tasks) if fallback_tasks else [])

    deduped: dict[str, SourceSearchCandidate] = {}
    for batch in results:
        for candidate in batch:
            existing = deduped.get(candidate.url)
            if existing is None or candidate.score > existing.score:
                deduped[candidate.url] = candidate

    ranked = sorted(
        deduped.values(),
        key=lambda item: (-item.score, item.title.lower(), item.site_name.lower(), item.url),
    )
    return [
        {
            "title": item.title,
            "url": item.url,
            "site_name": item.site_name,
            "site_domain": item.site_domain,
            "provider": item.provider,
            "family": item.family,
        }
        for item in ranked[: max(1, limit)]
    ]


async def search_supported_site(
    query: str,
    *,
    provider: str,
    family: str,
    site: dict[str, object],
) -> list[SourceSearchCandidate]:
    base_url = site_home_url(site)
    if provider == "wordpress_manga":
        search_url = f"{base_url}?s={quote_plus(query)}&post_type=wp-manga"
        html = await fetch_html(search_url)
        return parse_wordpress_search_candidates(html, search_url, site, query, provider, family)
    if provider == "webtoon_portal":
        search_url = f"{base_url}?s={quote_plus(query)}"
        html = await fetch_html(search_url)
        return parse_webtoon_portal_search_candidates(html, search_url, site, query, provider, family)
    if provider == "kuramanga":
        search_url = f"{base_url}?s={quote_plus(query)}"
        html = await fetch_html(search_url)
        return parse_kuramanga_search_candidates(html, search_url, site, query, provider, family)
    if provider == "weebcentral":
        search_url = f"{base_url}search/simple?location=main"
        html = await post_html(search_url, {"text": query})
        return parse_weebcentral_search_candidates(html, search_url, site, query, provider, family)
    return []


async def discover_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    provider = detect_provider(source_url)
    if provider == "tcb":
        return await discover_tcb_chapters(source_url, request_delay=request_delay)
    if provider == "wordpress_manga":
        return await discover_wordpress_chapters(source_url, request_delay=request_delay)
    if provider == "today_book":
        return await discover_today_book_chapters(source_url, request_delay=request_delay)
    if provider == "serialized_comic":
        return await discover_serialized_comic_chapters(source_url, request_delay=request_delay)
    if provider == "next_series":
        return await discover_next_series_chapters(source_url, request_delay=request_delay)
    if provider == "webtoon_portal":
        return await discover_webtoon_portal_chapters(source_url, request_delay=request_delay)
    if provider == "kuramanga":
        return await discover_kuramanga_chapters(source_url, request_delay=request_delay)
    if provider == "weebcentral":
        return await discover_weebcentral_chapters(source_url, request_delay=request_delay)
    raise ValueError("This site is not in the current supported source list.")


async def discover_page_images(
    chapter_url: str,
    *,
    request_delay: float = 0.0,
) -> list[dict[str, object]]:
    html = await fetch_html(chapter_url)
    if detect_provider(chapter_url) == "weebcentral":
        images_url = derive_weebcentral_images_url(chapter_url)
        if not images_url:
            return []
        if request_delay > 0:
            await asyncio.sleep(request_delay)
        html = await fetch_html(images_url)
    return parse_page_images(html, chapter_url)


def parse_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    provider = detect_provider(base_url)
    if provider == "tcb":
        return parse_tcb_page_images(html, base_url)
    if provider == "wordpress_manga":
        return parse_wordpress_page_images(html, base_url)
    if provider == "today_book":
        return parse_today_book_page_images(html, base_url)
    if provider == "serialized_comic":
        return parse_serialized_comic_page_images(html, base_url)
    if provider == "next_series":
        return parse_next_series_page_images(html, base_url)
    if provider == "webtoon_portal":
        return parse_webtoon_portal_page_images(html, base_url)
    if provider == "kuramanga":
        return parse_kuramanga_page_images(html, base_url)
    if provider == "weebcentral":
        return parse_weebcentral_page_images(html, base_url)
    raise ValueError("This chapter source is not supported.")


async def discover_tcb_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url
    if is_tcb_chapter_url(source_url):
        all_chapters_url = find_tcb_all_chapters_url(html, source_url)
        if all_chapters_url:
            if request_delay > 0:
                await asyncio.sleep(request_delay)
            page_url = all_chapters_url
            html = await fetch_html(all_chapters_url)

    chapters = parse_tcb_chapter_links(html, page_url)
    if chapters:
        return page_url, chapters

    if is_tcb_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


async def discover_wordpress_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url

    if is_wordpress_chapter_url(source_url):
        series_url = find_wordpress_series_url(html, source_url)
        if series_url and normalize_url(series_url) != normalize_url(source_url):
            if request_delay > 0:
                await asyncio.sleep(request_delay)
            page_url = series_url
            html = await fetch_html(series_url)

    chapters = parse_wordpress_chapter_links(html, page_url)
    if chapters:
        return page_url, chapters

    if is_wordpress_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


async def discover_next_series_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url
    if is_next_series_chapter_url(source_url):
        series_url = derive_next_series_url(source_url)
        if series_url and normalize_url(series_url) != normalize_url(source_url):
            if request_delay > 0:
                await asyncio.sleep(request_delay)
            page_url = series_url
            html = await fetch_html(series_url)

    props = parse_next_data_page_props(html)
    series = props.get("series") if isinstance(props, dict) else None
    chapters = props.get("chapters") if isinstance(props, dict) else None
    if isinstance(series, dict) and isinstance(chapters, list):
        built = build_next_series_chapter_links(chapters, series, page_url)
        if built:
            return page_url, built

    if is_next_series_chapter_url(source_url):
        chapter_props = parse_next_data_page_props(html)
        chapter = chapter_props.get("chapter") if isinstance(chapter_props, dict) else None
        if isinstance(chapter, dict):
            series_title = str(chapter.get("title") or "Chapter").strip()
            chapter_number = normalize_decimal_label(str(chapter.get("chapter") or ""))
            chapter_title = build_series_chapter_title(
                series_title,
                chapter_number,
                str(chapter.get("chapter_title") or ""),
            )
            chapter_key, sort_key = parse_chapter_key(chapter_title, source_url)
            return source_url, [
                {
                    "url": source_url,
                    "title": chapter_title,
                    "chapter_key": chapter_key,
                    "sort_key": sort_key,
                }
            ]

    raise ValueError("No chapter links were found on that page.")


async def discover_today_book_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url

    series_url = derive_today_book_series_url(source_url)
    if series_url and normalize_url(series_url) != normalize_url(source_url):
        if request_delay > 0:
            await asyncio.sleep(request_delay)
        page_url = series_url
        html = await fetch_html(series_url)

    chapters = parse_today_book_chapter_links(html, page_url)
    if chapters:
        return page_url, chapters

    if is_today_book_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


async def discover_serialized_comic_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url

    if is_serialized_comic_chapter_url(source_url):
        series_url = derive_serialized_comic_series_url(source_url)
        if series_url and normalize_url(series_url) != normalize_url(source_url):
            if request_delay > 0:
                await asyncio.sleep(request_delay)
            page_url = series_url
            html = await fetch_html(series_url)

    chapters = parse_serialized_comic_chapter_links(html, page_url)
    if chapters:
        return page_url, chapters

    if is_serialized_comic_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


async def discover_webtoon_portal_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url

    if is_webtoon_portal_chapter_url(source_url):
        series_url = derive_webtoon_portal_series_url(source_url)
        if series_url and normalize_url(series_url) != normalize_url(source_url):
            if request_delay > 0:
                await asyncio.sleep(request_delay)
            page_url = series_url
            html = await fetch_html(series_url)

    chapters = parse_webtoon_portal_chapter_links(html, page_url)
    if chapters:
        return page_url, chapters

    if is_webtoon_portal_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


async def discover_kuramanga_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url

    if is_kuramanga_chapter_url(source_url):
        series_url = derive_kuramanga_series_url(source_url)
        if series_url and normalize_url(series_url) != normalize_url(source_url):
            if request_delay > 0:
                await asyncio.sleep(request_delay)
            page_url = series_url
            html = await fetch_html(series_url)

    chapters = parse_kuramanga_chapter_links(html, page_url)
    if chapters:
        return page_url, chapters

    if is_kuramanga_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


async def discover_weebcentral_chapters(
    source_url: str,
    *,
    request_delay: float = 0.0,
) -> tuple[str, list[dict[str, object]]]:
    html = await fetch_html(source_url)
    page_url = source_url

    if is_weebcentral_chapter_url(source_url):
        series_url = find_weebcentral_series_url(html, source_url)
        if series_url:
            page_url = series_url

    full_list_url = derive_weebcentral_full_list_url(page_url)
    if full_list_url:
        if request_delay > 0:
            await asyncio.sleep(request_delay)
        chapter_html = await fetch_html(full_list_url)
        chapters = parse_weebcentral_chapter_links(chapter_html, page_url)
        if chapters:
            return page_url, chapters

    if is_weebcentral_chapter_url(source_url):
        title = parse_chapter_title(html, source_url)
        chapter_key, sort_key = parse_chapter_key(title, source_url)
        return source_url, [
            {
                "url": source_url,
                "title": title,
                "chapter_key": chapter_key,
                "sort_key": sort_key,
            }
        ]

    raise ValueError("No chapter links were found on that page.")


def parse_tcb_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    found: dict[str, ChapterLink] = {}
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href") or "")
        if "/chapters/" not in href:
            continue
        url = normalize_url(urljoin(base_url, href))
        title = " ".join(anchor.get_text(" ", strip=True).split())
        if not title or title.lower() in {"prev", "next"}:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)
    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_wordpress_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    base_host = clean_host(urlparse(base_url).netloc)
    found: dict[str, ChapterLink] = {}
    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_url, raw_href))
        parsed = urlparse(url)
        if not host_matches(base_host, parsed.netloc):
            continue
        if parsed.query:
            continue
        if not looks_like_wordpress_chapter_path(parsed.path):
            continue

        title = " ".join(anchor.get_text(" ", strip=True).split())
        if not title or title.lower() in {"prev", "next", "previous"}:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)
    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_today_book_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    target_slug = today_book_slug(base_url)
    found: dict[str, ChapterLink] = {}
    base_reference = f"{normalize_url(base_url).rstrip('/')}/"

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_reference, raw_href))
        parsed = urlparse(url)
        if parsed.query or not is_today_book_chapter_url(url):
            continue
        if target_slug and today_book_slug(url) != target_slug:
            continue

        title = " ".join(anchor.get_text(" ", strip=True).split())
        if not title or title.lower() in {"prev", "next", "previous"}:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)

    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_serialized_comic_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    target_series = derive_serialized_comic_series_url(base_url) or normalize_url(base_url)
    found: dict[str, ChapterLink] = {}
    base_reference = f"{normalize_url(base_url).rstrip('/')}/"
    target_parts = [part for part in urlparse(target_series).path.split("/") if part]
    target_slug = target_parts[-1] if target_parts else ""
    target_origin = origin_from_url(target_series)

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_reference, raw_href))
        if (
            not is_serialized_comic_chapter_url(url)
            and target_parts[:1] == ["comic"]
            and target_slug
            and raw_href.startswith(f"{target_slug}/")
        ):
            url = normalize_url(urljoin(f"{target_origin}/", f"/comic/{raw_href}"))
        parsed = urlparse(url)
        if parsed.query or not is_serialized_comic_chapter_url(url):
            continue
        if derive_serialized_comic_series_url(url) != target_series:
            continue

        title = " ".join(anchor.get_text(" ", strip=True).split())
        if not title or title.lower() in {"prev", "next", "previous"}:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)

    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_webtoon_portal_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    target_series = derive_webtoon_portal_series_url(base_url) or normalize_url(base_url)
    found: dict[str, ChapterLink] = {}
    base_reference = f"{normalize_url(base_url).rstrip('/')}/"

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_reference, raw_href))
        parsed = urlparse(url)
        if parsed.query or not is_webtoon_portal_chapter_url(url):
            continue
        if derive_webtoon_portal_series_url(url) != target_series:
            continue

        title = " ".join(anchor.get_text(" ", strip=True).split())
        if not title or title.lower() in {"prev", "next", "previous"}:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)

    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_kuramanga_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    target_series = derive_kuramanga_series_url(base_url) or normalize_url(base_url)
    found: dict[str, ChapterLink] = {}
    base_reference = f"{normalize_url(base_url).rstrip('/')}/"

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_reference, raw_href))
        parsed = urlparse(url)
        if parsed.query or not is_kuramanga_chapter_url(url):
            continue
        if derive_kuramanga_series_url(url) != target_series:
            continue

        title = " ".join(anchor.get_text(" ", strip=True).split())
        if not title or title.lower() in {"prev", "next", "previous"}:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)

    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_weebcentral_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    found: dict[str, ChapterLink] = {}

    for anchor in soup.find_all("a", href=True):
        url = normalize_url(urljoin(base_url, str(anchor.get("href") or "").strip()))
        if not is_weebcentral_chapter_url(url):
            continue
        title_node = anchor.select_one("span.grow > span")
        title = " ".join(
            (title_node.get_text(" ", strip=True) if title_node else anchor.get_text(" ", strip=True)).split()
        )
        if not title:
            title = title_from_url(url)
        chapter_key, sort_key = parse_chapter_key(title, url)
        found[url] = ChapterLink(url, title, chapter_key, sort_key)

    return [
        link.__dict__
        for link in sorted(found.values(), key=lambda item: (item.sort_key, item.url))
    ]


def parse_wordpress_search_candidates(
    html: str,
    base_url: str,
    site: dict[str, object],
    query: str,
    provider: str,
    family: str,
) -> list[SourceSearchCandidate]:
    soup = BeautifulSoup(html, "lxml")
    base_host = clean_host(urlparse(base_url).netloc or str(site["domain"]))
    found: dict[str, SourceSearchCandidate] = {}

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_url, raw_href))
        parsed = urlparse(url)
        if not host_matches(base_host, parsed.netloc) or parsed.query:
            continue
        if not looks_like_wordpress_series_path(parsed.path):
            continue

        title = extract_search_result_title(anchor, url)
        score = search_candidate_score(query, title, url)
        if score < 24:
            continue
        candidate = build_source_search_candidate(site, title, url, score, provider, family)
        existing = found.get(url)
        if existing is None or candidate.score > existing.score:
            found[url] = candidate

    return list(found.values())


def parse_webtoon_portal_search_candidates(
    html: str,
    base_url: str,
    site: dict[str, object],
    query: str,
    provider: str,
    family: str,
) -> list[SourceSearchCandidate]:
    soup = BeautifulSoup(html, "lxml")
    base_host = clean_host(urlparse(base_url).netloc or str(site["domain"]))
    found: dict[str, SourceSearchCandidate] = {}

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_url, raw_href))
        parsed = urlparse(url)
        if not host_matches(base_host, parsed.netloc) or parsed.query:
            continue
        if not is_webtoon_portal_series_url(url):
            continue

        title = extract_search_result_title(anchor, url)
        score = search_candidate_score(query, title, url)
        if score < 18:
            continue
        candidate = build_source_search_candidate(site, title, url, score, provider, family)
        existing = found.get(url)
        if existing is None or candidate.score > existing.score:
            found[url] = candidate

    return list(found.values())


def parse_kuramanga_search_candidates(
    html: str,
    base_url: str,
    site: dict[str, object],
    query: str,
    provider: str,
    family: str,
) -> list[SourceSearchCandidate]:
    soup = BeautifulSoup(html, "lxml")
    base_host = clean_host(urlparse(base_url).netloc or str(site["domain"]))
    found: dict[str, SourceSearchCandidate] = {}

    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_url, raw_href))
        parsed = urlparse(url)
        if not host_matches(base_host, parsed.netloc):
            continue
        if not is_kuramanga_series_url(url):
            continue

        title = extract_search_result_title(anchor, url)
        score = search_candidate_score(query, title, url)
        if score < 16:
            continue
        candidate = build_source_search_candidate(site, title, url, score, provider, family)
        existing = found.get(url)
        if existing is None or candidate.score > existing.score:
            found[url] = candidate

    return list(found.values())


def parse_weebcentral_search_candidates(
    html: str,
    base_url: str,
    site: dict[str, object],
    query: str,
    provider: str,
    family: str,
) -> list[SourceSearchCandidate]:
    soup = BeautifulSoup(html, "lxml")
    found: dict[str, SourceSearchCandidate] = {}

    for anchor in soup.find_all("a", href=True):
        url = normalize_url(urljoin(base_url, str(anchor.get("href") or "").strip()))
        if not is_weebcentral_series_url(url):
            continue
        title = extract_search_result_title(anchor, url)
        score = search_candidate_score(query, title, url)
        if score < 18:
            continue
        candidate = build_source_search_candidate(site, title, url, score, provider, family)
        existing = found.get(url)
        if existing is None or candidate.score > existing.score:
            found[url] = candidate

    return list(found.values())


def find_tcb_all_chapters_url(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        text = " ".join(anchor.get_text(" ", strip=True).split()).lower()
        href = str(anchor.get("href") or "")
        if "view all chapters" in text or "/mangas/" in href:
            return normalize_url(urljoin(base_url, href))
    return None


def find_wordpress_series_url(html: str, base_url: str) -> str | None:
    derived = derive_wordpress_series_url(base_url)
    if derived:
        return derived

    soup = BeautifulSoup(html, "lxml")
    base_host = clean_host(urlparse(base_url).netloc)
    target_tokens = series_slug_tokens(base_url)
    candidates: list[tuple[int, int, int, str]] = []
    for anchor in soup.find_all("a", href=True):
        raw_href = str(anchor.get("href") or "").strip()
        if not raw_href or raw_href.startswith("#") or "{" in raw_href:
            continue

        url = normalize_url(urljoin(base_url, raw_href))
        parsed = urlparse(url)
        if not host_matches(base_host, parsed.netloc):
            continue
        if parsed.query or not looks_like_wordpress_series_path(parsed.path):
            continue

        parts = [part for part in parsed.path.split("/") if part]
        candidate_tokens = series_slug_tokens(url)
        overlap = len(target_tokens & candidate_tokens)
        exact = int(candidate_tokens == target_tokens and bool(candidate_tokens))
        candidates.append((-exact, -overlap, len(parts), url))

    if not candidates:
        return None
    candidates.sort()
    return candidates[0][3]


def find_weebcentral_series_url(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        url = normalize_url(urljoin(base_url, str(anchor.get("href") or "").strip()))
        if is_weebcentral_series_url(url):
            return url
    return None


def parse_chapter_title(html: str, fallback_url: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    heading = soup.find("h1")
    if heading:
        title = " ".join(heading.get_text(" ", strip=True).split())
        if title:
            return title
    if soup.title and soup.title.string:
        return " ".join(soup.title.string.split())
    return title_from_url(fallback_url)


def parse_tcb_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    images: list[PageImage] = []
    seen: set[str] = set()
    for image in soup.find_all("img"):
        raw_url = first_present(
            image.get("data-src"),
            image.get("data-lazy-src"),
            image.get("src"),
            first_srcset_url(image.get("data-srcset")),
            first_srcset_url(image.get("srcset")),
        )
        if not raw_url:
            continue
        url = normalize_url(urljoin(base_url, str(raw_url)))
        if url in seen:
            continue
        alt = " ".join(str(image.get("alt") or image.get("title") or "").split())
        if not looks_like_tcb_page_image(url, alt):
            continue
        page_number = parse_page_number(alt) or len(images) + 1
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)
    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_wordpress_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    if host_matches(urlparse(base_url).netloc, "opchapters.com"):
        reader_images = parse_opchapters_reader_images(html, base_url)
        if reader_images:
            return reader_images

    soup = BeautifulSoup(html, "lxml")
    selector = ", ".join(WORDPRESS_IMAGE_SELECTORS)
    image_nodes = soup.select(selector) or soup.find_all("img")
    images: list[PageImage] = []
    seen: set[str] = set()

    for image in image_nodes:
        raw_url = first_present(
            image.get("data-src"),
            image.get("data-lazy-src"),
            image.get("data-pagespeed-lazy-src"),
            image.get("data-cfsrc"),
            image.get("src"),
            first_srcset_url(image.get("data-srcset")),
            first_srcset_url(image.get("srcset")),
        )
        if not raw_url:
            continue

        url = normalize_url(urljoin(base_url, str(raw_url).strip()))
        if url in seen:
            continue

        alt = " ".join(str(image.get("alt") or image.get("title") or "").split())
        if not looks_like_wordpress_page_image(url, alt):
            continue

        page_number = (
            parse_page_number(alt)
            or parse_page_number_from_url(url)
            or len(images) + 1
        )
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)

    if len(images) < 3:
        for url in extract_embedded_image_urls(html, base_url):
            if url in seen or not looks_like_wordpress_page_image(url, ""):
                continue
            page_number = parse_page_number_from_url(url) or len(images) + 1
            images.append(PageImage(url, page_number, extension_from_url(url)))
            seen.add(url)

    images = prune_page_images_by_bucket(images)
    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_opchapters_reader_images(html: str, base_url: str) -> list[dict[str, object]]:
    match = re.search(
        r"ts_reader\.run\((\{.*?\})\);\s*</script>",
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return []
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []

    for source in payload.get("sources", []):
        if not isinstance(source, dict) or not isinstance(source.get("images"), list):
            continue
        pages: list[dict[str, object]] = []
        seen: set[str] = set()
        for page_number, raw_url in enumerate(source["images"], start=1):
            url = normalize_url(urljoin(base_url, str(raw_url or "").strip()))
            if not url or url in seen:
                continue
            path = urlparse(url).path.lower()
            if not re.search(r"\.(?:jpg|jpeg|png|webp|gif)$", path):
                continue
            seen.add(url)
            pages.append(
                PageImage(url, page_number, extension_from_url(url)).__dict__
            )
        if pages:
            return pages
    return []


def parse_today_book_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    images: list[PageImage] = []
    seen: set[str] = set()

    for image in soup.find_all("img"):
        raw_url = first_present(
            image.get("data-src"),
            image.get("data-lazy-src"),
            image.get("src"),
            first_srcset_url(image.get("data-srcset")),
            first_srcset_url(image.get("srcset")),
        )
        if not raw_url:
            continue

        url = normalize_url(urljoin(base_url, str(raw_url).strip()))
        if url in seen:
            continue

        alt = " ".join(str(image.get("alt") or image.get("title") or "").split())
        if not looks_like_today_book_page_image(url, alt):
            continue

        page_number = (
            parse_page_number(alt)
            or parse_page_number_from_url(url)
            or len(images) + 1
        )
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)

    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_serialized_comic_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    images: list[PageImage] = []
    seen: set[str] = set()

    for url in extract_embedded_image_urls(html, base_url):
        if url in seen or not looks_like_serialized_comic_page_image(url):
            continue
        page_number = parse_page_number_from_url(url) or len(images) + 1
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)

    all_images = list(images)
    images = prune_page_images_by_bucket(images)
    if images:
        lowest_page = min(page.page_number for page in images)
        if lowest_page > 1:
            prefix_pages = [
                page
                for page in sorted(all_images, key=lambda item: (item.page_number, item.url))
                if page.page_number < lowest_page
                and page.url not in {existing.url for existing in images}
            ]
            if prefix_pages:
                images = prefix_pages + images
    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_next_series_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    props = parse_next_data_page_props(html)
    chapter = props.get("chapter") if isinstance(props, dict) else None
    token = props.get("token") if isinstance(props, dict) else None
    if not isinstance(chapter, dict):
        return []

    series_id = chapter.get("series_id")
    image_map = chapter.get("images")
    if not series_id or not isinstance(image_map, dict):
        return []

    base_prefix = f"https://cdn.flamecomics.xyz/uploads/images/series/{series_id}/{token or chapter.get('token', '')}"
    revision = chapter.get("edit_time") or chapter.get("release_date") or ""
    pages: list[PageImage] = []
    for index_key, payload in sorted(image_map.items(), key=lambda item: int(item[0])):
        if not isinstance(payload, dict) or not payload.get("name"):
            continue
        image_url = f"{base_prefix}/{payload['name']}"
        if revision:
            image_url = f"{image_url}?{revision}"
        page_number = int(index_key) + 1
        pages.append(
            PageImage(
                image_url,
                page_number,
                extension_from_url(image_url),
            )
        )
    return [page.__dict__ for page in pages]


def parse_webtoon_portal_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    image_nodes = soup.select(".reading-content img, #chapter_content img, .page-break img")
    images: list[PageImage] = []
    seen: set[str] = set()

    for image in image_nodes:
        raw_url = first_present(
            image.get("data-src"),
            image.get("data-lazy-src"),
            image.get("src"),
            first_srcset_url(image.get("data-srcset")),
            first_srcset_url(image.get("srcset")),
        )
        if not raw_url:
            continue

        url = normalize_url(urljoin(base_url, str(raw_url).strip()))
        if url in seen or not looks_like_webtoon_portal_page_image(url):
            continue

        alt = " ".join(str(image.get("alt") or image.get("title") or "").split())
        page_number = (
            parse_page_number(alt)
            or parse_page_number_from_url(url)
            or len(images) + 1
        )
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)

    if len(images) < 3:
        for url in extract_embedded_image_urls(html, base_url):
            if url in seen or not looks_like_webtoon_portal_page_image(url):
                continue
            page_number = parse_page_number_from_url(url) or len(images) + 1
            images.append(PageImage(url, page_number, extension_from_url(url)))
            seen.add(url)

    images = prune_page_images_by_bucket(images)
    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_kuramanga_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    images: list[PageImage] = []
    seen: set[str] = set()

    for url in extract_embedded_image_urls(html, base_url):
        if url in seen or not looks_like_kuramanga_page_image(url):
            continue
        page_number = parse_page_number_from_url(url) or len(images) + 1
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)

    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_weebcentral_page_images(html: str, base_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "lxml")
    image_nodes = soup.select("#chapter-images img") or soup.find_all("img")
    images: list[PageImage] = []
    seen: set[str] = set()

    for image in image_nodes:
        raw_url = str(image.get("src") or "").strip()
        if not raw_url:
            continue
        url = normalize_url(urljoin(base_url, raw_url))
        alt = " ".join(str(image.get("alt") or "").split())
        if url in seen or not looks_like_weebcentral_page_image(url, alt):
            continue
        page_number = parse_page_number(alt) or parse_page_number_from_url(url) or len(images) + 1
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)

    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_chapter_key(title: str, url: str) -> tuple[str, float]:
    candidates = [title, url.replace("-", " ").replace("/", " ")]
    for candidate in candidates:
        match = re.search(
            r"\b(?:chapter|ch)\s*[-:]?\s*(\d+(?:\.\d+)?)\b",
            candidate,
            re.IGNORECASE,
        )
        if match:
            raw = match.group(1)
            return raw, decimal_to_float(raw)
    path_name = PurePosixPath(urlparse(url).path).name.replace("-", " ")
    match = re.search(r"(\d+(?:\.\d+)?)", path_name)
    if match:
        raw = match.group(1)
        return raw, decimal_to_float(raw)
    return path_name or "chapter", 0.0


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") if parsed.path != "/" else parsed.path
    return parsed._replace(scheme=scheme, netloc=netloc, path=path, fragment="").geturl()


def title_from_url(url: str) -> str:
    slug = PurePosixPath(urlparse(url).path).name
    return " ".join(part.capitalize() for part in slug.split("-") if part)


def first_present(*values: object) -> str | None:
    for value in values:
        if value:
            return str(value)
    return None


def first_srcset_url(value: object) -> str | None:
    if not value:
        return None
    first = str(value).split(",")[0].strip()
    return first.split()[0] if first else None


def looks_like_tcb_page_image(url: str, alt: str) -> bool:
    lowered_alt = alt.lower()
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    if " page " in f" {lowered_alt} " or re.search(r"\bpage\s+\d+\b", lowered_alt):
        return True
    file_name = PurePosixPath(lowered_path).name
    return (
        "cdn.onepiecechapters.com" in parsed.netloc
        and re.search(r"(?:^|[_-])\d{2,4}\.(?:jpg|jpeg|png|webp|gif)$", file_name)
        is not None
    )


def looks_like_wordpress_page_image(url: str, alt: str) -> bool:
    lowered_alt = alt.lower()
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    file_name = PurePosixPath(lowered_path).name

    if lowered_path.endswith(".svg"):
        return False
    if any(token in lowered_path for token in ("logo", "favicon", "avatar", "banner")):
        return False
    if any(token in parsed.netloc.lower() for token in ("doubleclick", "googlesyndication")):
        return False
    if "wp-content/uploads/wp-manga/data/" in lowered_path:
        return True
    if "/series/data/" in lowered_path:
        return True
    if " page " in f" {lowered_alt} " or re.search(r"\bpage\s+\d+\b", lowered_alt):
        return True
    if WORDPRESS_NUMERIC_IMAGE.search(PurePosixPath(file_name).stem):
        return True
    return False


def looks_like_today_book_page_image(url: str, alt: str) -> bool:
    lowered_alt = alt.lower()
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    lowered_host = parsed.netloc.lower()

    if not lowered_host.endswith("todaymanga.com"):
        return False
    if any(token in lowered_path for token in ("/static/", "/posters/", "logo", "favicon", "avatar", "banner")):
        return False
    if " pic-" in f" {lowered_alt} " or re.search(r"\bpic[-_ ]?\d+\b", lowered_alt):
        return True
    return re.search(r"/\d+\.(?:jpg|jpeg|png|webp|gif)$", lowered_path) is not None


def looks_like_serialized_comic_page_image(url: str) -> bool:
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    file_name = PurePosixPath(lowered_path).name

    if "/series/" not in lowered_path:
        return False
    if not re.search(r"\.(?:jpg|jpeg|png|webp|gif)$", file_name):
        return False
    if any(token in lowered_path for token in ("cover-", "opengraph-image", "thumbnail", "icon", "favicon", "logo")):
        return False
    if "/chapters/" in lowered_path:
        return True
    return re.search(r"/\d{1,4}\.(?:jpg|jpeg|png|webp|gif)$", lowered_path) is not None


def looks_like_webtoon_portal_page_image(url: str) -> bool:
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    file_name = PurePosixPath(lowered_path).name

    if not re.search(r"\.(?:jpg|jpeg|png|webp|gif)$", file_name):
        return False
    if any(token in lowered_path for token in ("logo", "favicon", "avatar", "banner", "cover", "thumb")):
        return False
    return True


def looks_like_kuramanga_page_image(url: str) -> bool:
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    file_name = PurePosixPath(lowered_path).name

    if "/chapters/" not in lowered_path:
        return False
    if not re.search(r"\.(?:jpg|jpeg|png|webp|gif)$", file_name):
        return False
    if any(token in lowered_path for token in ("cover", "thumbnail", "icon", "favicon", "logo")):
        return False
    return True


def looks_like_weebcentral_page_image(url: str, alt: str) -> bool:
    parsed = urlparse(url)
    lowered_path = parsed.path.lower()
    if any(token in lowered_path for token in ("broken_image", "logo", "favicon", "cover/")):
        return False
    if re.search(r"\bpage\s+\d+\b", alt, re.IGNORECASE):
        return True
    return re.search(r"/\d{3,5}-\d{3,4}\.(?:jpg|jpeg|png|webp|gif)$", lowered_path) is not None


def prune_page_images_by_bucket(images: list[PageImage]) -> list[PageImage]:
    if len(images) < 3:
        return images

    buckets: dict[str, list[PageImage]] = {}
    for image in images:
        key = image_bucket(image.url)
        buckets.setdefault(key, []).append(image)

    ranked = sorted(
        buckets.values(),
        key=lambda bucket: (-len(bucket), bucket[0].url),
    )
    if ranked and len(ranked[0]) >= 3:
        return ranked[0]
    return images


def image_bucket(url: str) -> str:
    parsed = urlparse(url)
    parent = str(PurePosixPath(parsed.path).parent)
    return f"{parsed.netloc.lower()}::{parent}"


def extract_embedded_image_urls(html: str, base_url: str) -> list[str]:
    payload = unescape(html).replace("\\/", "/")
    candidates = re.findall(r'(?:https?://|/)[^"\'\s<>]+', payload)
    found: list[str] = []
    seen: set[str] = set()

    for candidate in candidates:
        raw = candidate.rstrip("\\")
        parsed = urlparse(raw)
        if not re.search(r"\.(?:jpg|jpeg|png|webp|gif)$", parsed.path.lower()):
            continue
        url = normalize_url(urljoin(base_url, raw))
        if url in seen:
            continue
        found.append(url)
        seen.add(url)

    return found


def parse_numeric_filename(url: str) -> int | None:
    stem = PurePosixPath(urlparse(url).path).stem
    match = WORDPRESS_NUMERIC_IMAGE.search(stem)
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def parse_page_number_from_url(url: str) -> int | None:
    stem = PurePosixPath(urlparse(url).path).stem
    tagged = re.search(r"(?:page|pic|image|img)[-_ ]?(\d+)", stem, re.IGNORECASE)
    if tagged:
        return int(tagged.group(1))

    leading = re.match(r"^(\d{1,4})(?:[-_]\d+)?$", stem)
    if leading:
        return int(leading.group(1))

    numeric = parse_numeric_filename(url)
    if numeric is not None:
        return numeric

    path = PurePosixPath(urlparse(url).path)
    for part in reversed(path.parts[:-1]):
        if part.isdigit():
            return int(part)
    return None


def parse_next_data_page_props(html: str) -> dict[str, object]:
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return {}
    try:
        import json

        payload = json.loads(match.group(1))
    except Exception:
        return {}
    props = payload.get("props", {})
    page_props = props.get("pageProps", {})
    return page_props if isinstance(page_props, dict) else {}


def build_next_series_chapter_links(
    chapters: list[object],
    series: dict[str, object],
    page_url: str,
) -> list[dict[str, object]]:
    base_origin = origin_from_url(page_url)
    series_id = series.get("series_id")
    series_title = str(series.get("title") or "Series").strip()
    if not base_origin or not series_id:
        return []

    found: list[dict[str, object]] = []
    for item in chapters:
        if not isinstance(item, dict) or not item.get("token"):
            continue
        chapter_number = normalize_decimal_label(str(item.get("chapter") or ""))
        chapter_title = build_series_chapter_title(
            series_title,
            chapter_number,
            str(item.get("title") or ""),
        )
        found.append(
            {
                "url": f"{base_origin}/series/{series_id}/{item['token']}",
                "title": chapter_title,
                "chapter_key": chapter_number or parse_chapter_key(chapter_title, chapter_title)[0],
                "sort_key": decimal_to_float(chapter_number) if chapter_number else 0.0,
            }
        )
    return sorted(found, key=lambda item: (float(item["sort_key"]), item["url"]))


def build_series_chapter_title(series_title: str, chapter_number: str, chapter_title: str) -> str:
    pieces = [series_title.strip()]
    if chapter_number:
        pieces.append(f"Chapter {chapter_number}")
    if chapter_title.strip():
        pieces.append(chapter_title.strip())
    return " ".join(piece for piece in pieces if piece).strip()


def normalize_decimal_label(value: str) -> str:
    cleaned = str(value or "").strip()
    if not cleaned:
        return ""
    try:
        number = Decimal(cleaned)
    except InvalidOperation:
        return cleaned
    if number == number.to_integral():
        return str(number.quantize(Decimal("1")))
    return format(number.normalize(), "f").rstrip("0").rstrip(".")


def origin_from_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc.lower()}"


def parse_page_number(text: str) -> int | None:
    match = re.search(r"\b(?:page|pic)\s*[-_]?\s*(\d+)\b", text, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def extension_from_url(url: str) -> str:
    suffix = PurePosixPath(urlparse(url).path).suffix.lower().lstrip(".")
    if suffix in {"jpg", "jpeg", "png", "webp", "gif"}:
        return "jpg" if suffix == "jpeg" else suffix
    return "jpg"


def extension_from_content_type(content_type: str, fallback: str) -> str:
    lowered = content_type.lower().split(";")[0].strip()
    mapping = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
    }
    return mapping.get(lowered, fallback)


def decimal_to_float(value: str) -> float:
    try:
        return float(Decimal(value))
    except (InvalidOperation, ValueError):
        return 0.0


def is_chapter_url(url: str) -> bool:
    provider = detect_provider(url)
    if provider == "tcb":
        return is_tcb_chapter_url(url)
    if provider == "wordpress_manga":
        return is_wordpress_chapter_url(url)
    if provider == "today_book":
        return is_today_book_chapter_url(url)
    if provider == "serialized_comic":
        return is_serialized_comic_chapter_url(url)
    if provider == "next_series":
        return is_next_series_chapter_url(url)
    if provider == "webtoon_portal":
        return is_webtoon_portal_chapter_url(url)
    if provider == "kuramanga":
        return is_kuramanga_chapter_url(url)
    if provider == "weebcentral":
        return is_weebcentral_chapter_url(url)
    return False


def is_tcb_chapter_url(url: str) -> bool:
    return "/chapters/" in urlparse(url).path


def is_wordpress_chapter_url(url: str) -> bool:
    return looks_like_wordpress_chapter_path(urlparse(url).path)


def is_today_book_chapter_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return len(parts) >= 3 and parts[0].lower() == "book" and parts[2].lower().startswith("ch-")


def is_serialized_comic_chapter_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return (
        len(parts) >= 3
        and parts[0].lower() == "comic"
        and parts[2].lower().startswith("chapter-")
    ) or (
        len(parts) >= 5
        and parts[0].lower() == "series"
        and parts[1].lower() == "comic"
        and parts[3].lower() == "chapter"
    )


def is_next_series_chapter_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return len(parts) >= 3 and parts[0].lower() == "series"


def is_webtoon_portal_chapter_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return (
        len(parts) >= 3
        and parts[0].lower() == "webtoon"
        and parts[2].lower().startswith("chapter-")
    )


def is_kuramanga_chapter_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return len(parts) >= 2 and parts[1].lower().startswith("chapter-")


def is_weebcentral_chapter_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return len(parts) == 2 and parts[0].lower() == "chapters" and bool(parts[1])


def is_weebcentral_series_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    if not (2 <= len(parts) <= 3 and parts[0].lower() == "series" and bool(parts[1])):
        return False
    return len(parts) == 2 or parts[2].lower() not in {
        "full-chapter-list",
        "chapter-select",
        "subscribe",
        "rss",
    }


def is_webtoon_portal_series_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    return len(parts) == 2 and parts[0].lower() == "webtoon"


def is_kuramanga_series_url(url: str) -> bool:
    parts = [part for part in urlparse(url).path.split("/") if part]
    if len(parts) != 1:
        return False
    return parts[0].lower() not in {"search", "settings", "contact", "dmca", "privacy-policy"}


def host_is_supported(url: str) -> bool:
    return detect_provider(url) is not None


def detect_provider(url: str) -> str | None:
    host = clean_host(urlparse(url).netloc)
    for group in SUPPORTED_SOURCE_GROUPS:
        if any(site_matches(host, site) for site in group["sites"]):
            return str(group["provider"])
    return None


def clean_host(host: str) -> str:
    return host.strip().lower().strip(".")


def host_matches(host: str, domain: str) -> bool:
    left = clean_host(host)
    right = clean_host(domain)
    return left == right or left.endswith(f".{right}")


def site_matches(host: str, site: dict[str, object]) -> bool:
    domains = [str(site["domain"])]
    domains.extend(str(alias) for alias in site.get("aliases", []))
    return any(host_matches(host, domain) for domain in domains)


def looks_like_wordpress_chapter_path(path: str) -> bool:
    lowered = path.lower().strip()
    return any(pattern.search(lowered) for pattern in WORDPRESS_CHAPTER_PATTERNS)


def looks_like_wordpress_series_path(path: str) -> bool:
    parts = [part for part in path.lower().split("/") if part]
    if "manga" not in parts:
        return False
    idx = parts.index("manga")
    if idx >= len(parts) - 1:
        return False
    return not looks_like_wordpress_chapter_segment(parts[-1])


def looks_like_wordpress_chapter_segment(segment: str) -> bool:
    lowered = segment.lower()
    return (
        "chapter" in lowered
        or re.search(r"^ch[-_ ]*\d", lowered, re.IGNORECASE) is not None
    )


def derive_wordpress_series_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if "manga" not in parts or not parts:
        return None
    if not looks_like_wordpress_chapter_segment(parts[-1]):
        return None

    parts = parts[:-1]
    while len(parts) >= 3 and parts[-1] == parts[-2]:
        parts = parts[:-1]

    path = "/" + "/".join(parts)
    return parsed._replace(path=path, query="", fragment="").geturl()


def derive_today_book_series_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0].lower() != "book":
        return None
    path = f"/book/{parts[1]}/chapter-list"
    return parsed._replace(path=path, query="", fragment="").geturl()


def derive_serialized_comic_series_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[0].lower() == "comic":
        path = "/" + "/".join(parts[:2])
        return parsed._replace(path=path, query="", fragment="").geturl()
    if len(parts) >= 3 and parts[0].lower() == "series" and parts[1].lower() == "comic":
        path = "/" + "/".join(parts[:3])
        return parsed._replace(path=path, query="", fragment="").geturl()
    return None


def derive_next_series_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0].lower() != "series":
        return None
    path = "/" + "/".join(parts[:2])
    return parsed._replace(path=path, query="", fragment="").geturl()


def derive_webtoon_portal_series_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0].lower() != "webtoon":
        return None
    path = "/" + "/".join(parts[:2])
    return parsed._replace(path=path, query="", fragment="").geturl()


def derive_kuramanga_series_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    path = "/" + parts[0]
    return parsed._replace(path=path, query="", fragment="").geturl()


def derive_weebcentral_full_list_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2 or parts[0].lower() != "series":
        return None
    path = f"/series/{parts[1]}/full-chapter-list"
    return parsed._replace(path=path, query="", fragment="").geturl()


def derive_weebcentral_images_url(url: str) -> str | None:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2 or parts[0].lower() != "chapters":
        return None
    path = f"/chapters/{parts[1]}/images"
    query = "is_prev=False&reading_style=long_strip&current_page=1"
    return parsed._replace(path=path, query=query, fragment="").geturl()


def site_home_url(site: dict[str, object]) -> str:
    return str(site.get("url") or f"https://{site['domain']}/").rstrip("/") + "/"


def build_source_search_candidate(
    site: dict[str, object],
    title: str,
    url: str,
    score: int,
    provider: str,
    family: str,
) -> SourceSearchCandidate:
    return SourceSearchCandidate(
        title=title,
        url=normalize_url(url),
        score=score,
        site_name=str(site["name"]),
        site_domain=str(site["domain"]),
        provider=provider,
        family=family,
    )


def extract_search_result_title(anchor: BeautifulSoup, url: str) -> str:
    texts = [
        anchor.get_text(" ", strip=True),
        anchor.get("title"),
        anchor.get("aria-label"),
    ]
    image = anchor.find("img")
    if image is not None:
        texts.extend([image.get("alt"), image.get("title")])

    for value in texts:
        cleaned = clean_search_title(str(value or ""))
        if cleaned:
            return cleaned
    return title_from_url(url)


def clean_search_title(value: str) -> str:
    cleaned = " ".join(str(value or "").strip().split())
    if not cleaned:
        return ""
    cleaned = re.sub(r"^read\s+", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+(?:manga|manhwa|manhua|webtoon)\s+online.*$", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+\|\s+.*$", "", cleaned)
    cleaned = re.sub(r"\s+-\s+.*$", "", cleaned)
    cleaned = cleaned.strip(" -|")
    return cleaned


def search_candidate_score(query: str, title: str, url: str) -> int:
    target = normalize_search_phrase(query)
    title_phrase = normalize_search_phrase(title)
    url_phrase = normalize_search_phrase(title_from_url(url))
    all_tokens = set(search_tokens(f"{title_phrase} {url_phrase}"))
    query_tokens = search_tokens(target)
    overlap = sum(1 for token in query_tokens if token in all_tokens)

    score = 0
    if title_phrase == target or url_phrase == target:
        score += 220
    if title_phrase.startswith(target) or url_phrase.startswith(target):
        score += 120
    if target in title_phrase or target in url_phrase:
        score += 80
    score += overlap * 26
    if overlap == 0 and target not in title_phrase and target not in url_phrase:
        return 0
    return max(score, 0)


def normalize_search_phrase(value: str) -> str:
    return " ".join(str(value or "").strip().lower().split())


def search_tokens(value: str) -> list[str]:
    return [token for token in re.split(r"[^a-z0-9]+", normalize_search_phrase(value)) if token]


def series_slug_tokens(url: str) -> set[str]:
    parsed = urlparse(normalize_url(url))
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return set()

    candidate = parts[-1]
    if "manga" in parts and len(parts) >= 2 and looks_like_wordpress_chapter_segment(parts[-1]):
        candidate = parts[-2]

    candidate = re.sub(r"(?:[-_])chapter[-_ ]*\d.*$", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r"(?:[-_])ch[-_ ]*\d.*$", "", candidate, flags=re.IGNORECASE)
    return {token for token in re.split(r"[^a-z0-9]+", candidate.lower()) if token}


def today_book_slug(url: str) -> str:
    parts = [part for part in urlparse(normalize_url(url)).path.split("/") if part]
    if len(parts) >= 2 and parts[0].lower() == "book":
        return parts[1].lower()
    return ""
