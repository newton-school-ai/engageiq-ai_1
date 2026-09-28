"""Tests for analytics export API endpoints."""

from datetime import datetime, timedelta
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.config.settings import EngagementState, UserRole
from src.database import get_db
from src.models import Base, Course, EngagementLog, Session as SessionModel, User

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a clean database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """TestClient with overridden database dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_data(db):
    """Populate database with sample teacher, student, course, sessions, and engagement logs."""
    teacher = User(name="Prof. McGonagall", email="mcgonagall@hogwarts.edu", role=UserRole.TEACHER)
    student1 = User(name="Harry Potter", email="harry@hogwarts.edu", role=UserRole.STUDENT)
    student2 = User(name="Hermione Granger", email="hermione@hogwarts.edu", role=UserRole.STUDENT)
    db.add_all([teacher, student1, student2])
    db.commit()

    course = Course(name="Transfiguration", code="MAGIC101", teacher_id=teacher.id)
    db.add(course)
    db.commit()

    session1 = SessionModel(course_id=course.id, status="completed")
    session2 = SessionModel(course_id=course.id, status="active")
    db.add_all([session1, session2])
    db.commit()

    base_time = datetime(2026, 6, 5, 10, 0, 0)

    # Session 1 logs (on 2026-06-05)
    log1 = EngagementLog(
        session_id=session1.id,
        user_id=student1.id,
        timestamp=base_time,
        score=85.0,
        state=EngagementState.ENGAGED,
        gaze="focused",
        drowsiness=0.05,
        expression="happy",
    )
    log2 = EngagementLog(
        session_id=session1.id,
        user_id=student2.id,
        timestamp=base_time + timedelta(minutes=5),
        score=95.0,
        state=EngagementState.ENGAGED,
        gaze="focused",
        drowsiness=0.01,
        expression="focused",
    )

    # Session 2 logs (on 2026-06-15, outside 2026-06-01 to 2026-06-08 range)
    log3 = EngagementLog(
        session_id=session2.id,
        user_id=student1.id,
        timestamp=datetime(2026, 6, 15, 14, 0, 0),
        score=40.0,
        state=EngagementState.DISTRACTED,
        gaze="distracted",
        drowsiness=0.6,
        expression="bored",
    )
    db.add_all([log1, log2, log3])
    db.commit()

    return {
        "teacher": teacher,
        "student1": student1,
        "student2": student2,
        "course": course,
        "session1": session1,
        "session2": session2,
        "log1": log1,
        "log2": log2,
        "log3": log3,
    }


def test_export_session_csv(client, sample_data):
    """Test exporting session engagement logs as CSV."""
    s1_id = sample_data["session1"].id
    res = client.get(f"/api/export/sessions/{s1_id}?format=csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert f'filename="session_{s1_id}_export.csv"' in res.headers["content-disposition"]

    lines = res.text.strip().split("\r\n")
    assert len(lines) == 3  # Header + 2 data rows

    header = lines[0].split(",")
    assert header == [
        "timestamp",
        "anonymized_student_id",
        "engagement_score",
        "state",
        "gaze_state",
        "drowsiness",
        "expression",
    ]

    # Verify anonymized student IDs
    for line in lines[1:]:
        parts = line.split(",")
        anon_id = parts[1]
        assert anon_id.startswith("anon_")
        # Ensure real IDs, names, emails are NOT present
        assert str(sample_data["student1"].id) != anon_id
        assert "harry" not in line.lower()
        assert "hogwarts" not in line.lower()


def test_export_session_json(client, sample_data):
    """Test exporting session engagement logs as JSON."""
    s1_id = sample_data["session1"].id
    res = client.get(f"/api/export/sessions/{s1_id}?format=json")
    assert res.status_code == 200
    assert "application/json" in res.headers["content-type"]
    assert f'filename="session_{s1_id}_export.json"' in res.headers["content-disposition"]

    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 2

    item = data[0]
    expected_keys = {
        "timestamp",
        "anonymized_student_id",
        "engagement_score",
        "state",
        "gaze_state",
        "drowsiness",
        "expression",
    }
    assert set(item.keys()) == expected_keys
    assert item["anonymized_student_id"].startswith("anon_")
    assert item["engagement_score"] == 85.0
    assert item["state"] == "engaged"


def test_export_course_with_date_filter(client, sample_data):
    """Test course export with date range filtering (start & end)."""
    c_id = sample_data["course"].id
    # Date filter: 2026-06-01 to 2026-06-08 (includes session 1, excludes session 2)
    res = client.get(f"/api/export/courses/{c_id}?format=csv&start=2026-06-01&end=2026-06-08")
    assert res.status_code == 200

    lines = res.text.strip().split("\r\n")
    assert len(lines) == 3  # Header + 2 rows from session1 (session2 log on June 15 is excluded)


def test_export_student_id_filter(client, sample_data):
    """Test filtering export by student_id."""
    s1_id = sample_data["session1"].id
    st1_id = sample_data["student1"].id

    res = client.get(f"/api/export/sessions/{s1_id}?format=json&student_id={st1_id}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    # Check that returned ID is still anonymized
    assert data[0]["anonymized_student_id"].startswith("anon_")


def test_export_unsupported_format(client, sample_data):
    """Test that requesting an unsupported format returns 400 Bad Request."""
    s1_id = sample_data["session1"].id
    res = client.get(f"/api/export/sessions/{s1_id}?format=xml")
    assert res.status_code == 400
    assert "Unsupported format" in res.json()["detail"]


def test_export_nonexistent_session(client, db):
    """Test requesting a session that does not exist returns 404 Not Found."""
    res = client.get("/api/export/sessions/99999?format=csv")
    assert res.status_code == 404
    assert "Session with ID 99999 not found" in res.json()["detail"]


def test_export_nonexistent_course(client, db):
    """Test requesting a course that does not exist returns 404 Not Found."""
    res = client.get("/api/export/courses/99999?format=json")
    assert res.status_code == 404
    assert "Course with ID 99999 not found" in res.json()["detail"]


def test_export_invalid_date_range(client, sample_data):
    """Test that start date after end date returns 400 Bad Request."""
    c_id = sample_data["course"].id
    res = client.get(f"/api/export/courses/{c_id}?format=csv&start=2026-06-10&end=2026-06-01")
    assert res.status_code == 400
    assert "'start' date must be before or equal to 'end' date" in res.json()["detail"]


def test_export_large_dataset_streaming(client, db):
    """Test streaming behavior with 1000+ rows."""
    teacher = User(name="Teacher", email="t@school.edu", role=UserRole.TEACHER)
    student = User(name="Student", email="s@school.edu", role=UserRole.STUDENT)
    db.add_all([teacher, student])
    db.commit()

    course = Course(name="Big Data", code="CS999", teacher_id=teacher.id)
    db.add(course)
    db.commit()

    session = SessionModel(course_id=course.id, status="active")
    db.add(session)
    db.commit()

    # Create 1050 engagement logs
    start_time = datetime(2026, 6, 1, 9, 0, 0)
    logs = [
        EngagementLog(
            session_id=session.id,
            user_id=student.id,
            timestamp=start_time + timedelta(seconds=i * 2),
            score=75.0 + (i % 20),
            state=EngagementState.ENGAGED,
            gaze="center",
            drowsiness=0.1,
            expression="neutral",
        )
        for i in range(1050)
    ]
    db.bulk_save_objects(logs)
    db.commit()

    # Test CSV export streaming
    res_csv = client.get(f"/api/export/sessions/{session.id}?format=csv")
    assert res_csv.status_code == 200
    lines = res_csv.text.strip().split("\r\n")
    assert len(lines) == 1051  # 1 header + 1050 data rows

    # Test JSON export streaming
    res_json = client.get(f"/api/export/sessions/{session.id}?format=json")
    assert res_json.status_code == 200
    json_data = json.loads(res_json.text)
    assert len(json_data) == 1050
