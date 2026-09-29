"""Stream engagement data in portable CSV and JSON formats."""

import csv
import hashlib
import hmac
import io
import json
from datetime import date, datetime, timedelta
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.middleware.auth import get_current_user
from src.config.settings import settings
from src.database import get_db
from src.models.course import Course
from src.models.engagement_log import EngagementLog
from src.models.session import Session as ClassSession
from src.models.user import User

router = APIRouter(prefix="/export", tags=["export"])
EXPORT_COLUMNS = (
    "timestamp",
    "anonymized_student_id",
    "engagement_score",
    "state",
    "gaze_state",
    "drowsiness",
    "expression",
)


def _anonymized_student_id(user_id: int) -> str:
    """Return a stable pseudonym without exposing the database student ID."""
    digest = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        str(user_id).encode("ascii"),
        hashlib.sha256,
    ).hexdigest()
    return f"student_{digest[:16]}"


def _row(record) -> dict:
    return {
        "timestamp": record["timestamp"].isoformat() if record["timestamp"] else None,
        "anonymized_student_id": _anonymized_student_id(record["user_id"]),
        "engagement_score": record["score"],
        "state": (
            record["state"].value
            if hasattr(record["state"], "value")
            else record["state"]
        ),
        "gaze_state": record["gaze"],
        "drowsiness": record["drowsiness"],
        "expression": record["expression"],
    }


def _stream_csv(records: Iterator) -> Iterator[str]:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=EXPORT_COLUMNS, lineterminator="\r\n")
    writer.writeheader()
    yield buffer.getvalue()
    buffer.seek(0)
    buffer.truncate(0)
    for record in records:
        writer.writerow(_row(record))
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)


def _stream_json(records: Iterator) -> Iterator[str]:
    yield "["
    first = True
    for record in records:
        if not first:
            yield ","
        yield json.dumps(_row(record), ensure_ascii=False, allow_nan=False)
        first = False
    yield "]"


def _build_export(
    *,
    session_ids: list[int] | None,
    course_id: int | None,
    start: date | None,
    end: date | None,
    student_id: int | None,
    db: Session,
    format: str,
) -> StreamingResponse:
    query = (
        select(
            EngagementLog.timestamp,
            EngagementLog.user_id,
            EngagementLog.score,
            EngagementLog.state,
            EngagementLog.gaze,
            EngagementLog.drowsiness,
            EngagementLog.expression,
        )
        .join(ClassSession, EngagementLog.session_id == ClassSession.id)
        .order_by(EngagementLog.timestamp, EngagementLog.id)
    )
    if session_ids is not None:
        query = query.where(EngagementLog.session_id.in_(session_ids))
    if course_id is not None:
        query = query.where(ClassSession.course_id == course_id)
    if start is not None:
        query = query.where(
            EngagementLog.timestamp >= datetime.combine(start, datetime.min.time())
        )
    if end is not None:
        query = query.where(
            EngagementLog.timestamp
            < datetime.combine(end + timedelta(days=1), datetime.min.time())
        )
    if student_id is not None:
        query = query.where(EngagementLog.user_id == student_id)

    records = db.execute(query.execution_options(yield_per=500)).mappings()
    if format == "csv":
        return StreamingResponse(
            _stream_csv(records),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="engagement-export.csv"'
            },
        )
    return StreamingResponse(
        _stream_json(records),
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="engagement-export.json"'
        },
    )


def _validate_filters(start: date | None, end: date | None) -> None:
    if start is not None and end is not None and start > end:
        raise HTTPException(status_code=422, detail="start must be on or before end")


@router.get("/sessions/{session_id}")
def export_session(
    session_id: int,
    format: str = Query("csv", pattern="^(csv|json)$"),
    start: date | None = None,
    end: date | None = None,
    course_id: int | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export engagement logs for a teacher-owned session."""
    _validate_filters(start, end)
    session = db.scalar(
        select(ClassSession)
        .join(Course, ClassSession.course_id == Course.id)
        .where(ClassSession.id == session_id, Course.teacher_id == current_user.id)
    )
    if current_user.role != "teacher" or session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    session_ids = [session_id]
    if course_id is not None and course_id != session.course_id:
        session_ids = []
    return _build_export(
        session_ids=session_ids,
        course_id=course_id,
        start=start,
        end=end,
        student_id=student_id,
        db=db,
        format=format,
    )


@router.get("/courses/{course_id}")
def export_course(
    course_id: int,
    format: str = Query("csv", pattern="^(csv|json)$"),
    start: date | None = None,
    end: date | None = None,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export engagement logs for every session in a teacher-owned course."""
    _validate_filters(start, end)
    course_exists = db.scalar(
        select(Course.id).where(
            Course.id == course_id, Course.teacher_id == current_user.id
        )
    )
    if current_user.role != "teacher" or course_exists is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return _build_export(
        session_ids=None,
        course_id=course_id,
        start=start,
        end=end,
        student_id=student_id,
        db=db,
        format=format,
    )
