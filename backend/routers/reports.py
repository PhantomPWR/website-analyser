import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from database import get_db
from services.pdf_builder import build_report_pdf

router = APIRouter()


class ReportSave(BaseModel):
    url: str
    data: dict  # all 6 section results


class ReportMeta(BaseModel):
    id: str
    url: str
    created_at: str


class ReportFull(BaseModel):
    id: str
    url: str
    created_at: str
    data: dict


@router.post("/reports", response_model=ReportMeta, status_code=201)
async def save_report(body: ReportSave):
    report_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    async with get_db() as db:
        await db.execute(
            "INSERT INTO reports (id, url, created_at, data) VALUES (?, ?, ?, ?)",
            (report_id, body.url, created_at, json.dumps(body.data)),
        )
        await db.commit()

    return ReportMeta(id=report_id, url=body.url, created_at=created_at)


@router.get("/reports", response_model=list[ReportMeta])
async def list_reports():
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, url, created_at FROM reports ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
    return [ReportMeta(id=r["id"], url=r["url"], created_at=r["created_at"]) for r in rows]


@router.get("/reports/{report_id}", response_model=ReportFull)
async def get_report(report_id: str):
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, url, created_at, data FROM reports WHERE id = ?", (report_id,)
        )
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return ReportFull(
        id=row["id"],
        url=row["url"],
        created_at=row["created_at"],
        data=json.loads(row["data"]),
    )


@router.delete("/reports/{report_id}", status_code=204)
async def delete_report(report_id: str):
    async with get_db() as db:
        await db.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        await db.commit()


@router.get("/reports/{report_id}/pdf")
async def get_report_pdf(report_id: str):
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT url, created_at, data FROM reports WHERE id = ?",
            (report_id,),
        )
        row = await cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    pdf_bytes = build_report_pdf(
        url=row["url"],
        created_at=row["created_at"],
        data=json.loads(row["data"]),
    )
    filename = f"report-{report_id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
