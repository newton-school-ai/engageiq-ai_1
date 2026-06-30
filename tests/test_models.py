"""Tests for SQLAlchemy models."""

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DbSession

from src.config.settings import PrivacyMode, UserRole
from src.models import Base, Course, EngagementLog, Session, SessionStatus, User


@pytest.fixture()
def db_session():
    """Create an in-memory database session for model tests."""

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with DbSession(engine) as session:
        yield session


def test_model_instantiation() -> None:
    """Models can be instantiated with expected fields."""

    user = User(
        email="teacher@example.com",
        name="Teacher Example",
        role=UserRole.TEACHER,
        privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
    )

    assert user.email == "teacher@example.com"
    assert user.role == UserRole.TEACHER
    assert user.is_active is None


def test_foreign_key_relationships(db_session: DbSession) -> None:
    """Relationships connect sessions to courses and logs to students."""

    teacher = User(
        email="teacher@example.com",
        name="Teacher Example",
        role=UserRole.TEACHER,
        privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
    )
    student = User(
        email="student@example.com",
        name="Student Example",
        role=UserRole.STUDENT,
        privacy_mode=PrivacyMode.LOCAL_ONLY,
    )
    course = Course(
        title="Backend Systems",
        description="Reliable backend design.",
        teacher=teacher,
    )
    lecture = Session(
        course=course,
        title="Schema design",
        started_at=datetime.now(UTC),
        status=SessionStatus.ACTIVE,
    )
    log = EngagementLog(
        session=lecture,
        student=student,
        frame_timestamp=datetime.now(UTC),
        engagement_score=0.82,
        engagement_state="focused",
    )

    db_session.add(log)
    db_session.commit()

    saved_lecture = db_session.query(Session).one()
    saved_log = db_session.query(EngagementLog).one()

    assert saved_lecture.course.title == "Backend Systems"
    assert saved_log.student.email == "student@example.com"


def test_engagement_score_constraint(db_session: DbSession) -> None:
    """Engagement score must remain between zero and one."""

    teacher = User(
        email="teacher@example.com",
        name="Teacher Example",
        role=UserRole.TEACHER,
        privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
    )
    student = User(
        email="student@example.com",
        name="Student Example",
        role=UserRole.STUDENT,
        privacy_mode=PrivacyMode.LOCAL_ONLY,
    )
    course = Course(
        title="Backend Systems",
        description="Reliable backend design.",
        teacher=teacher,
    )
    lecture = Session(
        course=course,
        title="Schema design",
        started_at=datetime.now(UTC),
        status=SessionStatus.ACTIVE,
    )
    invalid_log = EngagementLog(
        session=lecture,
        student=student,
        frame_timestamp=datetime.now(UTC),
        engagement_score=1.25,
        engagement_state="focused",
    )

    db_session.add(invalid_log)

    with pytest.raises(IntegrityError):
        db_session.commit()
