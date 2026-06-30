"""Seed the EngageIQ database with development data."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from random import Random

sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as DbSession

from src.config.settings import PrivacyMode, UserRole, settings
from src.models import (
    Base,
    Course,
    EngagementLog,
    Nudge,
    Report,
    Session,
    SessionStatus,
    User,
)

random = Random(42)


def build_users() -> tuple[list[User], list[User]]:
    """Build teacher and student seed users."""

    teachers = [
        User(
            email="ananya.rao@engageiq.edu",
            name="Ananya Rao",
            role=UserRole.TEACHER,
            privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
        ),
        User(
            email="marcus.chen@engageiq.edu",
            name="Marcus Chen",
            role=UserRole.TEACHER,
            privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
        ),
    ]
    student_names = [
        "Aarav Mehta",
        "Diya Sharma",
        "Kabir Singh",
        "Maya Iyer",
        "Rohan Kapoor",
        "Sara Thomas",
        "Vivaan Nair",
        "Nisha Patel",
        "Arjun Menon",
        "Leah Fernandes",
    ]
    students = [
        User(
            email=f"{name.lower().replace(' ', '.')}@student.engageiq.edu",
            name=name,
            role=UserRole.STUDENT,
            privacy_mode=PrivacyMode.LOCAL_ONLY,
        )
        for name in student_names
    ]
    return teachers, students


def build_courses(teachers: list[User]) -> list[Course]:
    """Build courses assigned to teachers."""

    return [
        Course(
            title="Applied Machine Learning",
            description="Hands-on model training, evaluation, and deployment fundamentals.",
            teacher=teachers[0],
        ),
        Course(
            title="Backend Systems Design",
            description="API architecture, persistence, queues, and reliability patterns.",
            teacher=teachers[1],
        ),
        Course(
            title="Data Storytelling",
            description="Turning analysis into clear decisions through visual narratives.",
            teacher=teachers[0],
        ),
    ]


def build_sessions(courses: list[Course]) -> list[Session]:
    """Build lecture sessions spread across courses."""

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    session_specs = [
        (courses[0], "Feature engineering workshop", 10, SessionStatus.COMPLETED),
        (courses[0], "Model evaluation lab", 8, SessionStatus.COMPLETED),
        (courses[1], "REST API contracts", 6, SessionStatus.COMPLETED),
        (courses[1], "Database migrations", 3, SessionStatus.ACTIVE),
        (courses[2], "Dashboard critique", 1, SessionStatus.PENDING),
    ]

    sessions: list[Session] = []
    for course, title, days_ago, status in session_specs:
        started_at = now - timedelta(days=days_ago, hours=1)
        ended_at = (
            None
            if status == SessionStatus.ACTIVE
            else started_at + timedelta(minutes=75)
        )
        sessions.append(
            Session(
                course=course,
                title=title,
                started_at=started_at,
                ended_at=ended_at,
                status=status,
            )
        )
    return sessions


def build_engagement_logs(
    sessions: list[Session], students: list[User]
) -> list[EngagementLog]:
    """Build engagement logs for each session."""

    states = ["focused", "neutral", "distracted", "drowsy"]
    expressions = ["neutral", "curious", "confused", "smiling", "tired"]
    logs: list[EngagementLog] = []

    for lecture in sessions:
        for index in range(20):
            student = students[index % len(students)]
            score = round(random.uniform(0.35, 0.95), 2)
            state = "focused" if score >= 0.75 else random.choice(states)
            logs.append(
                EngagementLog(
                    session=lecture,
                    student=student,
                    frame_timestamp=lecture.started_at + timedelta(minutes=index * 3),
                    engagement_score=score,
                    engagement_state=state,
                    gaze_score=round(random.uniform(0.4, 1.0), 2),
                    drowsiness_score=round(random.uniform(0.0, 0.45), 2),
                    expression=random.choice(expressions),
                    raw_data={
                        "frame": index,
                        "confidence": round(random.uniform(0.72, 0.99), 2),
                    },
                )
            )
    return logs


def build_nudges(sessions: list[Session], students: list[User]) -> list[Nudge]:
    """Build sample nudges."""

    return [
        Nudge(
            session=sessions[0],
            student=students[2],
            triggered_at=sessions[0].started_at + timedelta(minutes=24),
            nudge_type="attention_reset",
            message="Take a breath and refocus on the current exercise.",
            was_effective=True,
            acknowledged_at=sessions[0].started_at + timedelta(minutes=25),
        ),
        Nudge(
            session=sessions[1],
            student=students[4],
            triggered_at=sessions[1].started_at + timedelta(minutes=36),
            nudge_type="participation_prompt",
            message="Try answering the next checkpoint question.",
            was_effective=False,
        ),
        Nudge(
            session=sessions[3],
            student=students[7],
            triggered_at=sessions[3].started_at + timedelta(minutes=18),
            nudge_type="drowsiness_check",
            message="Sit upright and look back at the shared screen.",
        ),
    ]


def build_reports(sessions: list[Session], teachers: list[User]) -> list[Report]:
    """Build sample reports."""

    generated_at = datetime.now(timezone.utc)
    return [
        Report(
            session=sessions[0],
            generator=teachers[0],
            report_type="session_summary",
            content={
                "average_engagement": 0.78,
                "key_moment": "Strong participation during the coding exercise.",
                "recommended_action": "Add one more applied practice block.",
            },
            file_path="reports/feature-engineering-workshop.pdf",
            generated_at=generated_at,
        ),
        Report(
            session=sessions[2],
            generator=teachers[1],
            report_type="risk_overview",
            content={
                "average_engagement": 0.69,
                "students_needing_followup": 3,
                "recommended_action": "Review API contract examples in the next session.",
            },
            generated_at=generated_at,
        ),
    ]


def main() -> None:
    """Seed the configured database."""

    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)

    with DbSession(engine) as db:
        teachers, students = build_users()
        courses = build_courses(teachers)
        sessions = build_sessions(courses)
        logs = build_engagement_logs(sessions, students)
        nudges = build_nudges(sessions, students)
        reports = build_reports(sessions, teachers)

        db.add_all(
            [*teachers, *students, *courses, *sessions, *logs, *nudges, *reports]
        )
        db.commit()

    print(
        "Seed complete: "
        f"{len(teachers)} teachers, {len(students)} students, {len(courses)} courses, "
        f"{len(sessions)} sessions, {len(logs)} engagement logs, {len(nudges)} nudges, "
        f"{len(reports)} reports."
    )


if __name__ == "__main__":
    main()
