import json
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.fetcher import fetch_page

router = APIRouter()


class SeoResult(BaseModel):
    title: str | None
    description: str | None
    og_tags: dict[str, str]
    canonical: str | None
    robots_meta: str | None
    headings: dict[str, list[str]]
    sitemap_found: bool
    robots_txt_found: bool
    structured_data: list


@router.get("/seo", response_model=SeoResult)
async def analyse_seo(url: str = Query(..., description="URL to analyse")):
    try:
        page = await fetch_page(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    soup = page.soup

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Meta description
    desc_tag = soup.find("meta", attrs={"name": lambda n: n and n.lower() == "description"})
    description = desc_tag.get("content") if desc_tag else None

    # OG tags
    og_tags: dict[str, str] = {}
    for tag in soup.find_all("meta", property=lambda p: p and p.startswith("og:")):
        prop = tag.get("property", "")
        content = tag.get("content", "")
        if prop and content:
            og_tags[prop] = content

    # Canonical
    canonical_tag = soup.find("link", rel=lambda r: r and "canonical" in r)
    canonical = canonical_tag.get("href") if canonical_tag else None

    # Robots meta
    robots_tag = soup.find("meta", attrs={"name": lambda n: n and n.lower() == "robots"})
    robots_meta = robots_tag.get("content") if robots_tag else None

    # Headings
    headings: dict[str, list[str]] = {}
    for level in range(1, 7):
        tag_name = f"h{level}"
        found = [h.get_text(strip=True) for h in soup.find_all(tag_name)]
        if found:
            headings[tag_name] = found

    # Sitemap & robots.txt
    base = f"{urlparse(page.response_url).scheme}://{urlparse(page.response_url).netloc}"
    sitemap_found = await _url_exists(urljoin(base, "/sitemap.xml"))
    robots_txt_found = await _url_exists(urljoin(base, "/robots.txt"))

    # Structured data (JSON-LD)
    structured_data = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            structured_data.append(json.loads(script.string or ""))
        except (json.JSONDecodeError, TypeError):
            pass

    return SeoResult(
        title=title,
        description=description,
        og_tags=og_tags,
        canonical=canonical,
        robots_meta=robots_meta,
        headings=headings,
        sitemap_found=sitemap_found,
        robots_txt_found=robots_txt_found,
        structured_data=structured_data,
    )


async def _url_exists(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            r = await client.head(url)
            return r.status_code < 400
    except Exception:
        return False
