"""Coverage for portable engagement exports."""

import csv
import io
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.api.middleware.auth import get_current_user
from src.config.settings import EngagementState, UserRole
from src.database import get_db
from src.models import Base, Course, EngagementLog, Session, User


@pytest.fixture
def export_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    db_factory = sessionmaker(bind=engine)
    db = db_factory()
    teacher = User(name="Teacher", email="teacher@example.test", role=UserRole.TEACHER)
    student = User(name="Student", email="student@example.test", role=UserRole.STUDENT)
    db.add_all([teacher, student])
    db.commit()
    course = Course(name="Export course", code="EXP101", teacher_id=teacher.id)
    db.add(course)
    db.commit()
    session = Session(course_id=course.id, status="completed")
    db.add(session)
    db.commit()
    db.add(
        EngagementLog(
            session_id=session.id,
            user_id=student.id,
            timestamp=datetime(2026, 6, 3, 10, 30),
            score=82.5,
            state=EngagementState.ENGAGED,
            gaze='looked "forward", then away',
            drowsiness=0.1,
            expression="focused",
        )
    )
    db.commit()

    def override_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: teacher
    with TestClient(app) as client:
        yield client, session.id, course.id, student.id, db
    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_session_csv_is_rfc4180_and_anonymizes_student(export_client):
    client, session_id, _, student_id, _ = export_client
    response = client.get(f"/api/export/sessions/{session_id}?format=csv")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    rows = list(csv.DictReader(io.StringIO(response.text, newline="")))
    assert list(rows[0]) == [
        "timestamp",
        "anonymized_student_id",
        "engagement_score",
        "state",
        "gaze_state",
        "drowsiness",
        "expression",
    ]
    assert rows[0]["gaze_state"] == 'looked "forward", then away'
    assert rows[0]["anonymized_student_id"] != str(student_id)
    assert rows[0]["anonymized_student_id"].startswith("student_")


def test_course_json_applies_date_and_student_filters(export_client):
    client, _, course_id, student_id, _ = export_client
    response = client.get(
        f"/api/export/courses/{course_id}",
        params={
            "format": "json",
            "start": "2026-06-03",
            "end": "2026-06-03",
            "student_id": student_id,
        },
    )

    assert response.status_code == 200
    records = response.json()
    assert len(records) == 1
    assert records[0]["engagement_score"] == 82.5
    assert records[0]["anonymized_student_id"] != str(student_id)


def test_export_rejects_invalid_format_and_date_range(export_client):
    client, session_id, _, _, _ = export_client

    invalid_format = client.get(f"/api/export/sessions/{session_id}?format=xml")
    invalid_range = client.get(
        f"/api/export/sessions/{session_id}?start=2026-06-04&end=2026-06-03"
    )

    assert invalid_format.status_code == 422
    assert invalid_range.status_code == 422


def test_exports_are_limited_to_teacher_owned_resources(export_client):
    client, _, _, _, db = export_client
    other_teacher = User(
        name="Other teacher",
        email="other-teacher@example.test",
        role=UserRole.TEACHER,
    )
    db.add(other_teacher)
    db.commit()
    other_course = Course(
        name="Private course", code="PRIVATE1", teacher_id=other_teacher.id
    )
    db.add(other_course)
    db.commit()
    other_session = Session(course_id=other_course.id, status="completed")
    db.add(other_session)
    db.commit()

    assert client.get(f"/api/export/sessions/{other_session.id}").status_code == 404
    assert client.get(f"/api/export/courses/{other_course.id}").status_code == 404
