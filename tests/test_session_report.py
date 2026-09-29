"""Tests for session engagement report generation."""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

from src.config.settings import EngagementState, PrivacyMode, UserRole
from src.models import Base, Course, EngagementLog, Session, User
from src.reports.session_report import SessionReportGenerator


@pytest.fixture
def report_db() -> Iterator[DatabaseSession]:
    """Provide an isolated in-memory database with all application tables."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)


def make_report_records(db: DatabaseSession) -> int:
    """Insert a small class session with multiple engagement states."""
    teacher = User(
        name="Teacher Name",
        email="teacher@example.com",
        role=UserRole.TEACHER,
        privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
    )
    student_a = User(name="Alice Private", email="a@example.com")
    student_b = User(name="Bob Private", email="b@example.com")
    course = Course(name="Biology", code="BIO101", teacher=teacher)
    start = datetime(2026, 6, 1, 9, 0)
    lecture = Session(
        course=course, start_time=start, end_time=start + timedelta(minutes=3)
    )
    db.add_all([teacher, student_a, student_b, course, lecture])
    db.flush()
    db.add_all(
        [
            EngagementLog(
                session=lecture,
                user=student_a,
                timestamp=start + timedelta(seconds=10),
                score=80,
                state=EngagementState.ENGAGED,
            ),
            EngagementLog(
                session=lecture,
                user=student_b,
                timestamp=start + timedelta(seconds=20),
                score=60,
                state=EngagementState.PASSIVE,
            ),
            EngagementLog(
                session=lecture,
                user=student_a,
                timestamp=start + timedelta(minutes=2),
                score=20,
                state=EngagementState.DISTRACTED,
            ),
        ]
    )
    db.commit()
    return lecture.id


def test_build_report_data_aggregates_session_and_anonymizes_students(
    report_db: DatabaseSession,
) -> None:
    """Aggregate timeline, state counts, dips, and comparison without PII."""
    session_id = make_report_records(report_db)

    report = SessionReportGenerator(report_db).build_report_data(session_id)

    assert report["session"]["course_name"] == "Biology"
    assert report["session"]["student_count"] == 2
    assert report["session"]["log_count"] == 3
    assert report["class_average"] == 53.33
    assert [point["engagement"] for point in report["timeline"]] == [70, 20]
    assert {
        state["state"]: state["count"] for state in report["state_distribution"]
    } == {
        "Distracted": 1,
        "Engaged": 1,
        "Passive": 1,
    }
    assert report["distraction_moments"][0]["timestamp"] == "2026-06-01 09:02"
    assert [row["label"] for row in report["student_comparison"]] == [
        "Student 1",
        "Student 2",
    ]
    assert "Alice Private" not in str(report)
    assert "user_id" not in str(report)


def test_generate_renders_html_and_writes_downloadable_file(
    report_db: DatabaseSession, tmp_path: Path
) -> None:
    """Render the charts and session summary into an HTML file."""
    session_id = make_report_records(report_db)
    output = tmp_path / "report.html"

    html = SessionReportGenerator(report_db).generate(session_id, output)

    assert output.read_text(encoding="utf-8") == html
    assert "Session engagement report" in html
    assert "timelineChart" in html
    assert "stateChart" in html
    assert "comparisonChart" in html
    assert "Student 1" in html
    assert "Alice Private" not in html
    assert "https://cdn.jsdelivr.net/npm/chart.js" in html


def test_missing_session_raises_value_error(report_db: DatabaseSession) -> None:
    """Report generation should clearly reject an unknown session ID."""
    with pytest.raises(ValueError, match="Session 999 was not found"):
        SessionReportGenerator(report_db).build_report_data(999)
