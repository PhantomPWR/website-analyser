import os
from urllib.parse import urljoin, urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.fetcher import fetch_page

router = APIRouter()

PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PAGESPEED_KEY = os.getenv("PAGESPEED_API_KEY", "")


class WebVital(BaseModel):
    value: float | None
    display: str | None
    score: float | None  # 0-1 from PageSpeed


class ResourceSummary(BaseModel):
    scripts: int
    stylesheets: int
    images: int
    total_resources: int
    html_size_kb: float


class PerformanceResult(BaseModel):
    performance_score: int | None
    fcp: WebVital
    lcp: WebVital
    cls: WebVital
    ttfb: WebVital
    inp: WebVital
    speed_index: WebVital
    resources: ResourceSummary
    pagespeed_available: bool
    pagespeed_error: str | None


def _extract_vital(audits: dict, key: str) -> WebVital:
    audit = audits.get(key, {})
    numeric = audit.get("numericValue")
    display = audit.get("displayValue")
    score = audit.get("score")
    return WebVital(value=numeric, display=display, score=score)


@router.get("/performance", response_model=PerformanceResult)
async def analyse_performance(url: str = Query(..., description="URL to analyse")):
    # Fetch the page for resource analysis
    try:
        page = await fetch_page(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    soup = page.soup

    # Resource counts from HTML
    scripts = len(soup.find_all("script", src=True))
    stylesheets = len(soup.find_all("link", rel=lambda r: r and "stylesheet" in r))
    images = len(soup.find_all("img"))
    html_size_kb = round(len(page.html.encode("utf-8")) / 1024, 1)

    resources = ResourceSummary(
        scripts=scripts,
        stylesheets=stylesheets,
        images=images,
        total_resources=scripts + stylesheets + images,
        html_size_kb=html_size_kb,
    )

    # PageSpeed Insights
    pagespeed_available = False
    performance_score = None
    empty_vital = WebVital(value=None, display=None, score=None)
    fcp = lcp = cls = ttfb = inp = speed_index = empty_vital

    try:
        params = {"url": url, "strategy": "mobile", "category": "performance"}
        if PAGESPEED_KEY:
            params["key"] = PAGESPEED_KEY

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.get(PAGESPEED_API, params=params)
            resp.raise_for_status()
            data = resp.json()

        categories = data.get("lighthouseResult", {}).get("categories", {})
        audits = data.get("lighthouseResult", {}).get("audits", {})

        perf = categories.get("performance", {})
        raw_score = perf.get("score")
        performance_score = round(raw_score * 100) if raw_score is not None else None

        fcp = _extract_vital(audits, "first-contentful-paint")
        lcp = _extract_vital(audits, "largest-contentful-paint")
        cls = _extract_vital(audits, "cumulative-layout-shift")
        ttfb = _extract_vital(audits, "server-response-time")
        inp = _extract_vital(audits, "interaction-to-next-paint")
        speed_index = _extract_vital(audits, "speed-index")

        pagespeed_available = True

    except httpx.HTTPStatusError as e:
        pagespeed_available = False
        pagespeed_error = f"PageSpeed API returned {e.response.status_code}: {e.response.text[:300]}"
    except Exception as e:
        pagespeed_available = False
        pagespeed_error = str(e) or f"{type(e).__name__} (no message)"
    else:
        pagespeed_error = None

    return PerformanceResult(
        performance_score=performance_score,
        fcp=fcp,
        lcp=lcp,
        cls=cls,
        ttfb=ttfb,
        inp=inp,
        speed_index=speed_index,
        resources=resources,
        pagespeed_available=pagespeed_available,
        pagespeed_error=pagespeed_error,
    )
