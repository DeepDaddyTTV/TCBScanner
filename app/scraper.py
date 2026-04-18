from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import PurePosixPath
from typing import Iterable
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "TCB-CBZ-Monitor/1.0 (+local personal archiver)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


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


async def fetch_html(url: str) -> str:
    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_bytes(url: str, *, referer: str | None = None) -> tuple[bytes, str]:
    headers = dict(HEADERS)
    headers["Accept"] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    if referer:
        headers["Referer"] = referer
    async with httpx.AsyncClient(headers=headers, timeout=60, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content, response.headers.get("content-type", "")


def parse_chapter_links(html: str, base_url: str) -> list[dict[str, object]]:
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


def find_all_chapters_url(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    for anchor in soup.find_all("a", href=True):
        text = " ".join(anchor.get_text(" ", strip=True).split()).lower()
        href = str(anchor.get("href") or "")
        if "view all chapters" in text or "/mangas/" in href:
            return normalize_url(urljoin(base_url, href))
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


def parse_page_images(html: str, base_url: str) -> list[dict[str, object]]:
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
        if not looks_like_page_image(url, alt):
            continue
        page_number = parse_page_number(alt) or len(images) + 1
        images.append(PageImage(url, page_number, extension_from_url(url)))
        seen.add(url)
    return [
        page.__dict__
        for page in sorted(images, key=lambda item: (item.page_number, item.url))
    ]


def parse_chapter_key(title: str, url: str) -> tuple[str, float]:
    candidates = [title, url.replace("-", " ")]
    for candidate in candidates:
        match = re.search(r"\bchapter\s+(\d+(?:\.\d+)?)\b", candidate, re.IGNORECASE)
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


def looks_like_page_image(url: str, alt: str) -> bool:
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


def parse_page_number(text: str) -> int | None:
    match = re.search(r"\bpage\s+(\d+)\b", text, re.IGNORECASE)
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
    return "/chapters/" in urlparse(url).path


def host_is_supported(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host.endswith("tcbonepiecechapters.com")
