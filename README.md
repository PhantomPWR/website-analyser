# Website Analyser

A full-stack website auditing tool. Enter any URL and get a detailed breakdown across six analysis dimensions — results are automatically persisted as a report you can revisit or export as a PDF.

---

## Features

| Section | What it checks |
| --- | --- |
| **SEO** | Title, meta description, canonical, robots meta, sitemap, robots.txt, Open Graph tags, JSON-LD structured data |
| **Performance** | PageSpeed Insights score, Core Web Vitals (FCP, LCP, CLS, TTFB, INP, Speed Index), resource counts & HTML size |
| **Security** | HTTPS, HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP, mixed content, server disclosure, cookie flags |
| **Technology** | 35+ fingerprints across CMS, JS frameworks, UI libraries, analytics, CDN, hosting and more |
| **Accessibility** | Language attribute, image alt text, form labels, heading hierarchy, ARIA landmarks, skip links, positive tabindex |
| **Content** | Flesch Reading Ease, word/sentence/paragraph counts, content-to-HTML ratio, internal/external links, broken link detection |

---

## Stack

**Frontend** — Nuxt 4 + Vue 3, Nuxt UI (Tailwind CSS v4), TypeScript, pnpm, Node 22

**Backend** — FastAPI + Python 3.12, uv, httpx, BeautifulSoup4, aiosqlite, fpdf2

**Infrastructure** — Docker Compose; Nuxt route rules proxy API requests from the frontend container to the backend, eliminating CORS concerns in production.

---

## Getting started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A [PageSpeed Insights API key](https://developers.google.com/speed/docs/insights/v5/get-started) *(optional — omitting it skips Core Web Vitals but everything else still works)*

### Run with Docker

```bash
git clone <repo-url>
cd website-analyser

# Optional — add your PageSpeed API key
echo "PAGESPEED_API_KEY=AIza..." > .env

docker compose up --build -d
```

Open <http://localhost:3007>.

### Run locally

#### Backend

```bash
cd backend
uv pip install --system -r pyproject.toml
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
# from project root
pnpm install
pnpm dev
```

Frontend runs on <http://localhost:3000>. Set `NUXT_PUBLIC_API_BASE=http://localhost:8000` in a `.env` file when running outside of Docker.

---

## Environment variables

| Variable | Service | Description |
| --- | --- | --- |
| `PAGESPEED_API_KEY` | Backend | Google PageSpeed Insights API key (`AIza…`). Optional. |
| `NUXT_PUBLIC_API_BASE` | Frontend | Backend base URL. Leave empty in Docker — the route rules proxy handles it. |
| `DB_PATH` | Backend | SQLite database path. Defaults to `/data/reports.db`. |

---

## Project structure

```text
website-analyser/
├── app/
│   ├── app.vue                        # App shell (navbar + page outlet)
│   ├── pages/
│   │   ├── index.vue                  # URL input + tabbed analysis results
│   │   └── reports/
│   │       ├── index.vue              # Saved reports list
│   │       └── [id].vue               # Individual report view + PDF download
│   ├── composables/
│   │   └── useAnalyser.ts             # Fetch logic, state, auto-persist
│   └── components/sections/
│       ├── SeoSection.vue
│       ├── PerformanceSection.vue
│       ├── SecuritySection.vue
│       ├── TechSection.vue
│       ├── AccessibilitySection.vue
│       └── ContentSection.vue
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── database.py                    # SQLite init + async connection helper
│   ├── services/
│   │   ├── fetcher.py                 # Shared async page fetch (httpx + BS4)
│   │   └── pdf_builder.py             # PDF report generation (fpdf2)
│   └── routers/
│       ├── seo.py
│       ├── performance.py
│       ├── security.py
│       ├── tech.py
│       ├── accessibility.py
│       ├── content.py
│       └── reports.py                 # CRUD + PDF export
├── Dockerfile                         # Nuxt frontend (multi-stage)
├── Dockerfile.backend                 # FastAPI backend
└── docker-compose.yml
```

---

## API reference

All `/analyse/*` endpoints accept a `?url=<url>` query parameter.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/analyse/seo` | SEO analysis |
| `GET` | `/analyse/performance` | Performance + PageSpeed Insights |
| `GET` | `/analyse/security` | Security headers & cookies |
| `GET` | `/analyse/tech` | Technology detection |
| `GET` | `/analyse/accessibility` | Accessibility audit |
| `GET` | `/analyse/content` | Content & readability |
| `POST` | `/reports` | Save a report |
| `GET` | `/reports` | List all saved reports |
| `GET` | `/reports/{id}` | Get a full report |
| `DELETE` | `/reports/{id}` | Delete a report |
| `GET` | `/reports/{id}/pdf` | Download report as PDF |
