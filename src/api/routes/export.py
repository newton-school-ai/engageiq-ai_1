"""Analytics export routes for sessions and courses."""

import csv
from datetime import datetime
import io
import json
from typing import Generator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from src.analytics.class_aggregator import ClassAggregator
from src.database import get_db
from src.models.course import Course
from src.models.engagement_log import EngagementLog
from src.models.session import Session as SessionModel

router = APIRouter(prefix="/export", tags=["export"])


def parse_date_param(val: Optional[str], is_end: bool = False) -> Optional[datetime]:
    """Parse string date/datetime parameter into datetime object."""
    if not val:
        return None
    val = val.strip()
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        pass
    try:
        d = datetime.strptime(val, "%Y-%m-%d")
        if is_end:
            return datetime(d.year, d.month, d.day, 23, 59, 59, 999999)
        return datetime(d.year, d.month, d.day, 0, 0, 0)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: '{val}'. Expected YYYY-MM-DD or ISO 8601 format.",
        )


def anonymize_id(user_id: int) -> str:
    """Return deterministic anonymized student ID."""
    return ClassAggregator.anonymize_student_ids([user_id])[user_id]


def stream_csv(query) -> Generator[str, None, None]:
    """Generator function that yields RFC 4180 compliant CSV chunk by chunk."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "timestamp",
        "anonymized_student_id",
        "engagement_score",
        "state",
        "gaze_state",
        "drowsiness",
        "expression",
    ])
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    for log in query.yield_per(500):
        state_val = log.state.value if hasattr(log.state, "value") else str(log.state)
        anon_id = anonymize_id(log.user_id)
        writer.writerow([
            log.timestamp.isoformat() if log.timestamp else "",
            anon_id,
            log.score,
            state_val,
            log.gaze or "",
            log.drowsiness if log.drowsiness is not None else "",
            log.expression or "",
        ])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)


def stream_json(query) -> Generator[str, None, None]:
    """Generator function that yields JSON array elements chunk by chunk."""
    yield "[\n"
    first = True
    for log in query.yield_per(500):
        if not first:
            yield ",\n"
        else:
            first = False
        state_val = log.state.value if hasattr(log.state, "value") else str(log.state)
        anon_id = anonymize_id(log.user_id)
        item = {
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "anonymized_student_id": anon_id,
            "engagement_score": log.score,
            "state": state_val,
            "gaze_state": log.gaze,
            "drowsiness": log.drowsiness,
            "expression": log.expression,
        }
        yield json.dumps(item)
    yield "\n]"


@router.get("/sessions/{id}")
def export_session(
    id: int,
    format: str = Query("csv", description="Export format: 'csv' or 'json'"),
    start: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD or ISO)"),
    end: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD or ISO)"),
    student_id: Optional[int] = Query(None, description="Student ID filter"),
    db: DBSession = Depends(get_db),
):
    """Export session engagement logs in CSV or JSON format."""
    fmt = format.lower() if format else "csv"
    if fmt not in ("csv", "json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: '{format}'. Format must be 'csv' or 'json'.",
        )

    session_obj = db.query(SessionModel).filter(SessionModel.id == id).first()
    if not session_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID {id} not found",
        )

    start_dt = parse_date_param(start, is_end=False)
    end_dt = parse_date_param(end, is_end=True)
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'start' date must be before or equal to 'end' date.",
        )

    query = db.query(EngagementLog).filter(EngagementLog.session_id == id)
    if start_dt:
        query = query.filter(EngagementLog.timestamp >= start_dt)
    if end_dt:
        query = query.filter(EngagementLog.timestamp <= end_dt)
    if student_id is not None:
        query = query.filter(EngagementLog.user_id == student_id)

    query = query.order_by(EngagementLog.timestamp.asc())

    if fmt == "csv":
        headers = {"Content-Disposition": f'attachment; filename="session_{id}_export.csv"'}
        return StreamingResponse(
            stream_csv(query),
            media_type="text/csv",
            headers=headers,
        )
    else:
        headers = {"Content-Disposition": f'attachment; filename="session_{id}_export.json"'}
        return StreamingResponse(
            stream_json(query),
            media_type="application/json",
            headers=headers,
        )


@router.get("/courses/{id}")
def export_course(
    id: int,
    format: str = Query("csv", description="Export format: 'csv' or 'json'"),
    start: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD or ISO)"),
    end: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD or ISO)"),
    student_id: Optional[int] = Query(None, description="Student ID filter"),
    course_id: Optional[int] = Query(None, description="Optional course_id query filter"),
    db: DBSession = Depends(get_db),
):
    """Export course engagement logs in CSV or JSON format."""
    fmt = format.lower() if format else "csv"
    if fmt not in ("csv", "json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format: '{format}'. Format must be 'csv' or 'json'.",
        )

    target_course_id = course_id if course_id is not None else id

    course_obj = db.query(Course).filter(Course.id == target_course_id).first()
    if not course_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {target_course_id} not found",
        )

    start_dt = parse_date_param(start, is_end=False)
    end_dt = parse_date_param(end, is_end=True)
    if start_dt and end_dt and start_dt > end_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'start' date must be before or equal to 'end' date.",
        )

    query = (
        db.query(EngagementLog)
        .join(SessionModel, EngagementLog.session_id == SessionModel.id)
        .filter(SessionModel.course_id == target_course_id)
    )
    if start_dt:
        query = query.filter(EngagementLog.timestamp >= start_dt)
    if end_dt:
        query = query.filter(EngagementLog.timestamp <= end_dt)
    if student_id is not None:
        query = query.filter(EngagementLog.user_id == student_id)

    query = query.order_by(EngagementLog.timestamp.asc())

    if fmt == "csv":
        headers = {
            "Content-Disposition": f'attachment; filename="course_{target_course_id}_export.csv"'
        }
        return StreamingResponse(
            stream_csv(query),
            media_type="text/csv",
            headers=headers,
        )
    else:
        headers = {
            "Content-Disposition": f'attachment; filename="course_{target_course_id}_export.json"'
        }
        return StreamingResponse(
            stream_json(query),
            media_type="application/json",
            headers=headers,
        )
