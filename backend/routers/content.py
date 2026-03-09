import asyncio
import re
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.fetcher import fetch_page

router = APIRouter()


class BrokenLink(BaseModel):
    url: str
    status_code: int | None
    error: str | None


class ContentResult(BaseModel):
    word_count: int
    sentence_count: int
    paragraph_count: int
    avg_words_per_sentence: float
    flesch_reading_ease: float
    readability_label: str
    content_to_html_ratio: float
    internal_links_total: int
    internal_links_checked: int
    broken_links: list[BrokenLink]
    external_links_total: int
    has_favicon: bool
    has_meta_viewport: bool
    text_preview: str


# ---------------------------------------------------------------------------
# Readability helpers
# ---------------------------------------------------------------------------

def _count_syllables(word: str) -> int:
    word = word.lower().strip(".,!?;:'\"")
    if not word:
        return 1
    # Simple heuristic: count vowel groups
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent e
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _flesch(words: list[str], sentence_count: int) -> float:
    if not words or sentence_count == 0:
        return 0.0
    syllables = sum(_count_syllables(w) for w in words)
    word_count = len(words)
    score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllables / word_count)
    return round(max(0.0, min(100.0, score)), 1)


def _readability_label(score: float) -> str:
    if score >= 90:
        return "Very Easy"
    if score >= 80:
        return "Easy"
    if score >= 70:
        return "Fairly Easy"
    if score >= 60:
        return "Standard"
    if score >= 50:
        return "Fairly Difficult"
    if score >= 30:
        return "Difficult"
    return "Very Confusing"


def _extract_text(soup) -> str:
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)


# ---------------------------------------------------------------------------
# Link checking
# ---------------------------------------------------------------------------

async def _check_link(client: httpx.AsyncClient, url: str) -> BrokenLink | None:
    try:
        r = await client.head(url, follow_redirects=True, timeout=6.0)
        if r.status_code >= 400:
            return BrokenLink(url=url, status_code=r.status_code, error=None)
        return None
    except Exception as e:
        return BrokenLink(url=url, status_code=None, error=str(e)[:100])


@router.get("/content", response_model=ContentResult)
async def analyse_content(url: str = Query(..., description="URL to analyse")):
    try:
        page = await fetch_page(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    soup = page.soup
    base_url = f"{urlparse(page.response_url).scheme}://{urlparse(page.response_url).netloc}"

    # ---- Text content ----
    text = _extract_text(soup)
    words = [w for w in re.split(r"\s+", text) if w and re.search(r"[a-zA-Z]", w)]
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 10]
    paragraphs = soup.find_all("p")

    word_count = len(words)
    sentence_count = max(len(sentences), 1)
    paragraph_count = len(paragraphs)
    avg_wps = round(word_count / sentence_count, 1)

    flesch = _flesch(words, sentence_count)
    label = _readability_label(flesch)

    html_len = len(page.html)
    text_len = len(text)
    ratio = round(text_len / html_len * 100, 1) if html_len else 0.0

    text_preview = " ".join(words[:60]) + ("…" if len(words) > 60 else "")

    # ---- Links ----
    all_links = soup.find_all("a", href=True)
    internal_hrefs: list[str] = []
    external_count = 0

    for a in all_links:
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        if href.startswith("http://") or href.startswith("https://"):
            parsed = urlparse(href)
            if parsed.netloc == urlparse(base_url).netloc:
                internal_hrefs.append(href)
            else:
                external_count += 1
        elif href.startswith("/"):
            internal_hrefs.append(urljoin(base_url, href))

    # Deduplicate and cap checks at 20
    unique_internal = list(dict.fromkeys(internal_hrefs))
    to_check = unique_internal[:20]

    broken: list[BrokenLink] = []
    if to_check:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; WebsiteAnalyser/1.0)"}
        async with httpx.AsyncClient(headers=headers) as client:
            results = await asyncio.gather(*[_check_link(client, u) for u in to_check])
            broken = [r for r in results if r is not None]

    # ---- Misc ----
    has_favicon = bool(
        soup.find("link", rel=lambda r: r and "icon" in " ".join(r).lower())
        or soup.find("link", rel="shortcut icon")
    )
    viewport = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = viewport is not None

    return ContentResult(
        word_count=word_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        avg_words_per_sentence=avg_wps,
        flesch_reading_ease=flesch,
        readability_label=label,
        content_to_html_ratio=ratio,
        internal_links_total=len(unique_internal),
        internal_links_checked=len(to_check),
        broken_links=broken,
        external_links_total=external_count,
        has_favicon=has_favicon,
        has_meta_viewport=has_viewport,
        text_preview=text_preview,
    )
