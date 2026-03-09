import re

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.fetcher import fetch_page

router = APIRouter()


class TechItem(BaseModel):
    name: str
    category: str
    confidence: str  # "high" | "medium" | "low"
    version: str | None = None
    icon: str | None = None


class TechResult(BaseModel):
    technologies: list[TechItem]
    categories: dict[str, list[str]]


# ---------------------------------------------------------------------------
# Fingerprint rules — each entry is (name, category, icon, patterns)
# patterns: list of dicts with keys: type (header/meta/html/script/cookie), key, regex
# ---------------------------------------------------------------------------

FINGERPRINTS: list[dict] = [
    # CMS
    {
        "name": "WordPress", "category": "CMS", "icon": "🔵",
        "rules": [
            {"type": "meta", "attr": "name", "val": "generator", "regex": r"WordPress"},
            {"type": "html", "regex": r"/wp-content/"},
            {"type": "html", "regex": r"/wp-includes/"},
        ],
    },
    {
        "name": "Drupal", "category": "CMS", "icon": "🔵",
        "rules": [
            {"type": "meta", "attr": "name", "val": "generator", "regex": r"Drupal"},
            {"type": "html", "regex": r"/sites/default/files/"},
            {"type": "header", "key": "x-generator", "regex": r"Drupal"},
        ],
    },
    {
        "name": "Joomla", "category": "CMS", "icon": "🔵",
        "rules": [
            {"type": "meta", "attr": "name", "val": "generator", "regex": r"Joomla"},
            {"type": "html", "regex": r"/media/jui/"},
        ],
    },
    {
        "name": "Shopify", "category": "E-commerce", "icon": "🟢",
        "rules": [
            {"type": "html", "regex": r"cdn\.shopify\.com"},
            {"type": "header", "key": "x-shopify-stage", "regex": r".*"},
        ],
    },
    {
        "name": "WooCommerce", "category": "E-commerce", "icon": "🟢",
        "rules": [
            {"type": "html", "regex": r"woocommerce"},
        ],
    },
    {
        "name": "Magento", "category": "E-commerce", "icon": "🟠",
        "rules": [
            {"type": "html", "regex": r"Mage\.Cookies|skin/frontend/"},
            {"type": "cookie", "regex": r"^frontend$"},
        ],
    },
    # JS Frameworks
    {
        "name": "React", "category": "JavaScript Framework", "icon": "⚛️",
        "rules": [
            {"type": "html", "regex": r"react(?:\.min)?\.js|__REACT_DEVTOOLS|_reactFiber|data-reactroot"},
        ],
    },
    {
        "name": "Vue.js", "category": "JavaScript Framework", "icon": "💚",
        "rules": [
            {"type": "html", "regex": r"vue(?:\.min)?\.js|__vue__|data-v-"},
        ],
    },
    {
        "name": "Angular", "category": "JavaScript Framework", "icon": "🔴",
        "rules": [
            {"type": "html", "regex": r"angular(?:\.min)?\.js|ng-version=|ng-app"},
        ],
    },
    {
        "name": "Next.js", "category": "JavaScript Framework", "icon": "⬛",
        "rules": [
            {"type": "html", "regex": r"__NEXT_DATA__|/_next/static/"},
        ],
    },
    {
        "name": "Nuxt.js", "category": "JavaScript Framework", "icon": "💚",
        "rules": [
            {"type": "html", "regex": r"__NUXT__|/_nuxt/"},
        ],
    },
    {
        "name": "Svelte", "category": "JavaScript Framework", "icon": "🟠",
        "rules": [
            {"type": "html", "regex": r"__svelte__|svelte-"},
        ],
    },
    {
        "name": "jQuery", "category": "JavaScript Library", "icon": "🔷",
        "rules": [
            {"type": "html", "regex": r"jquery(?:\.min)?\.js|jQuery\.fn\.jquery"},
        ],
    },
    # Meta-frameworks / SSG
    {
        "name": "Gatsby", "category": "Static Site Generator", "icon": "🟣",
        "rules": [
            {"type": "html", "regex": r"___gatsby|/gatsby-"},
        ],
    },
    {
        "name": "Astro", "category": "Static Site Generator", "icon": "🚀",
        "rules": [
            {"type": "html", "regex": r"astro-island|astro-"},
        ],
    },
    {
        "name": "Hugo", "category": "Static Site Generator", "icon": "🔵",
        "rules": [
            {"type": "meta", "attr": "name", "val": "generator", "regex": r"Hugo"},
        ],
    },
    {
        "name": "Jekyll", "category": "Static Site Generator", "icon": "🔴",
        "rules": [
            {"type": "meta", "attr": "name", "val": "generator", "regex": r"Jekyll"},
        ],
    },
    # Analytics
    {
        "name": "Google Analytics", "category": "Analytics", "icon": "📊",
        "rules": [
            {"type": "html", "regex": r"google-analytics\.com/analytics\.js|gtag\(|UA-\d{4,}-\d+|G-[A-Z0-9]+"},
        ],
    },
    {
        "name": "Google Tag Manager", "category": "Analytics", "icon": "📊",
        "rules": [
            {"type": "html", "regex": r"googletagmanager\.com/gtm\.js|GTM-[A-Z0-9]+"},
        ],
    },
    {
        "name": "Plausible", "category": "Analytics", "icon": "📊",
        "rules": [
            {"type": "html", "regex": r"plausible\.io/js/"},
        ],
    },
    {
        "name": "Hotjar", "category": "Analytics", "icon": "📊",
        "rules": [
            {"type": "html", "regex": r"static\.hotjar\.com|hjid:"},
        ],
    },
    {
        "name": "Matomo", "category": "Analytics", "icon": "📊",
        "rules": [
            {"type": "html", "regex": r"matomo\.js|piwik\.js"},
        ],
    },
    {
        "name": "Segment", "category": "Analytics", "icon": "📊",
        "rules": [
            {"type": "html", "regex": r"cdn\.segment\.com|analytics\.js"},
        ],
    },
    # CDN / Hosting
    {
        "name": "Cloudflare", "category": "CDN", "icon": "🌐",
        "rules": [
            {"type": "header", "key": "cf-ray", "regex": r".*"},
            {"type": "header", "key": "server", "regex": r"cloudflare"},
        ],
    },
    {
        "name": "Fastly", "category": "CDN", "icon": "🌐",
        "rules": [
            {"type": "header", "key": "x-served-by", "regex": r"cache-"},
            {"type": "header", "key": "fastly-restarts", "regex": r".*"},
        ],
    },
    {
        "name": "Vercel", "category": "Hosting", "icon": "▲",
        "rules": [
            {"type": "header", "key": "x-vercel-id", "regex": r".*"},
            {"type": "header", "key": "server", "regex": r"Vercel"},
        ],
    },
    {
        "name": "Netlify", "category": "Hosting", "icon": "🟦",
        "rules": [
            {"type": "header", "key": "x-nf-request-id", "regex": r".*"},
            {"type": "header", "key": "server", "regex": r"Netlify"},
        ],
    },
    # Server / language
    {
        "name": "Nginx", "category": "Web Server", "icon": "🟩",
        "rules": [
            {"type": "header", "key": "server", "regex": r"nginx"},
        ],
    },
    {
        "name": "Apache", "category": "Web Server", "icon": "🪶",
        "rules": [
            {"type": "header", "key": "server", "regex": r"Apache"},
        ],
    },
    {
        "name": "PHP", "category": "Programming Language", "icon": "🐘",
        "rules": [
            {"type": "header", "key": "x-powered-by", "regex": r"PHP"},
            {"type": "cookie", "regex": r"^PHPSESSID$"},
        ],
    },
    {
        "name": "ASP.NET", "category": "Programming Language", "icon": "🟣",
        "rules": [
            {"type": "header", "key": "x-powered-by", "regex": r"ASP\.NET"},
            {"type": "cookie", "regex": r"^ASP\.NET_SessionId$"},
        ],
    },
    # UI libraries
    {
        "name": "Bootstrap", "category": "UI Framework", "icon": "🅱️",
        "rules": [
            {"type": "html", "regex": r"bootstrap(?:\.min)?\.css|bootstrap(?:\.min)?\.js"},
        ],
    },
    {
        "name": "Tailwind CSS", "category": "UI Framework", "icon": "🎨",
        "rules": [
            {"type": "html", "regex": r"tailwindcss|class=\"[^\"]*(?:flex|grid|text-|bg-|p-|m-)[^\"]*\""},
        ],
    },
    # Fonts
    {
        "name": "Google Fonts", "category": "Font Service", "icon": "🔤",
        "rules": [
            {"type": "html", "regex": r"fonts\.googleapis\.com|fonts\.gstatic\.com"},
        ],
    },
]


def _detect(html: str, headers: dict, soup, cookies: list[str]) -> list[TechItem]:
    detected: list[TechItem] = []

    for fp in FINGERPRINTS:
        matched = False
        for rule in fp["rules"]:
            if matched:
                break
            rtype = rule["type"]
            pattern = re.compile(rule["regex"], re.IGNORECASE)

            if rtype == "html" and pattern.search(html):
                matched = True
            elif rtype == "header":
                val = headers.get(rule["key"], "")
                if val and pattern.search(val):
                    matched = True
            elif rtype == "meta":
                tag = soup.find("meta", attrs={rule["attr"]: re.compile(rule["val"], re.IGNORECASE)})
                if tag:
                    content = tag.get("content", "")
                    if pattern.search(content):
                        matched = True
            elif rtype == "cookie":
                if any(pattern.search(c) for c in cookies):
                    matched = True

        if matched:
            detected.append(TechItem(
                name=fp["name"],
                category=fp["category"],
                icon=fp.get("icon"),
                confidence="high",
            ))

    return detected


@router.get("/tech", response_model=TechResult)
async def analyse_tech(url: str = Query(..., description="URL to analyse")):
    try:
        page = await fetch_page(url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=422, detail=f"Failed to fetch URL: {e.response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    headers = {k.lower(): v for k, v in page.headers.items()}

    # Parse cookie names from set-cookie header
    raw_cookies = headers.get("set-cookie", "")
    cookie_names = []
    for line in raw_cookies.split("\n"):
        line = line.strip()
        if line:
            name = line.split("=")[0].strip()
            cookie_names.append(name)

    technologies = _detect(page.html, headers, page.soup, cookie_names)

    # Group by category
    categories: dict[str, list[str]] = {}
    for tech in technologies:
        categories.setdefault(tech.category, []).append(tech.name)

    return TechResult(technologies=technologies, categories=categories)
