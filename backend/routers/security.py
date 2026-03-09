from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.fetcher import fetch_page

router = APIRouter()

SECURITY_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-embedder-policy",
    "cross-origin-resource-policy",
]


class HeaderCheck(BaseModel):
    present: bool
    value: str | None
    note: str | None


class CookieCheck(BaseModel):
    name: str
    secure: bool
    http_only: bool
    same_site: str | None


class SecurityResult(BaseModel):
    https: bool
    hsts: HeaderCheck
    csp: HeaderCheck
    x_frame_options: HeaderCheck
    x_content_type_options: HeaderCheck
    referrer_policy: HeaderCheck
    permissions_policy: HeaderCheck
    coop: HeaderCheck
    all_security_headers: dict[str, str | None]
    mixed_content_count: int
    mixed_content_urls: list[str]
    cookies: list[CookieCheck]
    server_header: str | None
    x_powered_by: str | None


def _check_header(headers: dict, name: str, note: str | None = None) -> HeaderCheck:
    value = headers.get(name)
    return HeaderCheck(present=value is not None, value=value, note=note)


def _parse_cookies(headers: dict) -> list[CookieCheck]:
    cookies = []
    raw = headers.get("set-cookie", "")
    if not raw:
        return cookies
    # httpx may join multiple set-cookie headers with \n
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(";")]
        name = parts[0].split("=")[0].strip() if parts else "unknown"
        flags = {p.lower().split("=")[0].strip() for p in parts[1:]}
        same_site = next(
            (p.split("=")[1].strip() for p in parts[1:] if p.lower().startswith("samesite=")),
            None,
        )
        cookies.append(CookieCheck(
            name=name,
            secure="secure" in flags,
            http_only="httponly" in flags,
            same_site=same_site,
        ))
    return cookies


def _find_mixed_content(soup, base_url: str) -> list[str]:
    if not base_url.startswith("https://"):
        return []
    mixed = []
    checks = [
        ("img", "src"), ("script", "src"), ("link", "href"),
        ("iframe", "src"), ("audio", "src"), ("video", "src"),
        ("source", "src"),
    ]
    for tag, attr in checks:
        for el in soup.find_all(tag, **{attr: True}):
            val = el.get(attr, "")
            if val.startswith("http://"):
                mixed.append(val)
    return mixed[:20]  # cap at 20


@router.get("/security", response_model=SecurityResult)
async def analyse_security(url: str = Query(..., description="URL to analyse")):
    try:
        page = await fetch_page(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    headers = {k.lower(): v for k, v in page.headers.items()}
    parsed = urlparse(page.response_url)
    https = parsed.scheme == "https"

    hsts = _check_header(headers, "strict-transport-security",
        "Should include max-age≥31536000" if headers.get("strict-transport-security") else None)
    csp = _check_header(headers, "content-security-policy")
    x_frame = _check_header(headers, "x-frame-options",
        "Should be DENY or SAMEORIGIN")
    x_cto = _check_header(headers, "x-content-type-options",
        "Should be nosniff")
    ref_policy = _check_header(headers, "referrer-policy")
    perms = _check_header(headers, "permissions-policy")
    coop = _check_header(headers, "cross-origin-opener-policy")

    all_security_headers = {h: headers.get(h) for h in SECURITY_HEADERS}

    mixed_urls = _find_mixed_content(page.soup, page.response_url)
    cookies = _parse_cookies(headers)

    return SecurityResult(
        https=https,
        hsts=hsts,
        csp=csp,
        x_frame_options=x_frame,
        x_content_type_options=x_cto,
        referrer_policy=ref_policy,
        permissions_policy=perms,
        coop=coop,
        all_security_headers=all_security_headers,
        mixed_content_count=len(mixed_urls),
        mixed_content_urls=mixed_urls,
        cookies=cookies,
        server_header=headers.get("server"),
        x_powered_by=headers.get("x-powered-by"),
    )
