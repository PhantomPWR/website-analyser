from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import (
    accessibility, content, performance, reports, security, seo, tech,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Website Analyser API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.include_router(seo.router, prefix="/analyse", tags=["seo"])
app.include_router(performance.router, prefix="/analyse", tags=["performance"])
app.include_router(security.router, prefix="/analyse", tags=["security"])
app.include_router(tech.router, prefix="/analyse", tags=["tech"])
app.include_router(accessibility.router, prefix="/analyse", tags=["accessibility"])
app.include_router(content.router, prefix="/analyse", tags=["content"])
app.include_router(reports.router, tags=["reports"])


@app.get("/health")
async def health():
    return {"status": "ok"}
