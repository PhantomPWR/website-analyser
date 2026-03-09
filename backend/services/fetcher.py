import httpx
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class PageData:
    html: str
    soup: BeautifulSoup
    headers: dict
    response_url: str
    status_code: int


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; WebsiteAnalyser/1.0; +https://github.com/website-analyser)"
    )
}


async def fetch_page(url: str) -> PageData:
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=15.0,
        headers=HEADERS,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "lxml")
        return PageData(
            html=html,
            soup=soup,
            headers=dict(response.headers),
            response_url=str(response.url),
            status_code=response.status_code,
        )
