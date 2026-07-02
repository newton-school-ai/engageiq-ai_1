"""Tests for SQLAlchemy ORM models — instantiation and relationships."""

from datetime import datetime, timezone

from src.models.course import Course
from src.models.engagement_log import EngagementLog, EngagementState
from src.models.nudge import Nudge, NudgeType
from src.models.report import Report, ReportType
from src.models.session import Session, SessionStatus
from src.models.user import PrivacyMode, User, UserRole

# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class TestUser:
    def test_instantiation(self):
        user = User(
            name="Alice",
            email="alice@nst.edu",
            role=UserRole.STUDENT,
            privacy_mode=PrivacyMode.LOCAL_ONLY,
        )
        assert user.name == "Alice"
        assert user.email == "alice@nst.edu"
        assert user.role == UserRole.STUDENT
        assert user.privacy_mode == PrivacyMode.LOCAL_ONLY

    def test_teacher_role(self):
        teacher = User(
            name="Prof. Smith",
            email="smith@nst.edu",
            role=UserRole.TEACHER,
            privacy_mode=PrivacyMode.SHARE_WITH_TEACHER,
        )
        assert teacher.role == UserRole.TEACHER

    def test_repr(self):
        user = User(name="Bob", email="bob@nst.edu", role=UserRole.STUDENT)
        assert "bob@nst.edu" in repr(user)

    def test_default_collections(self):
        user = User(name="Carol", email="carol@nst.edu", role=UserRole.STUDENT)
        # Relationships are lazy — just verify the attribute exists
        assert hasattr(user, "courses_taught")
        assert hasattr(user, "engagement_logs")
        assert hasattr(user, "nudges")

    def test_userrole_enum_values(self):
        assert UserRole.STUDENT.value == "student"
        assert UserRole.TEACHER.value == "teacher"

    def test_privacymode_enum_values(self):
        assert PrivacyMode.LOCAL_ONLY.value == "local_only"
        assert PrivacyMode.SHARE_WITH_TEACHER.value == "share_with_teacher"


# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------


class TestCourse:
    def test_instantiation(self):
        course = Course(name="Machine Learning", code="ML101", teacher_id=1)
        assert course.name == "Machine Learning"
        assert course.code == "ML101"
        assert course.teacher_id == 1

    def test_repr(self):
        course = Course(name="Deep Learning", code="DL202", teacher_id=2)
        assert "DL202" in repr(course)

    def test_has_sessions_relationship(self):
        course = Course(name="NLP", code="NLP303", teacher_id=1)
        assert hasattr(course, "sessions")


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


class TestSession:
    def test_instantiation(self):
        now = datetime.now(timezone.utc)
        session = Session(
            course_id=1,
            start_time=now,
            status=SessionStatus.ACTIVE,
        )
        assert session.course_id == 1
        assert session.start_time == now
        assert session.status == SessionStatus.ACTIVE

    def test_default_status(self):
        session = Session(
            course_id=1,
            start_time=datetime.now(timezone.utc),
        )
        assert session.status == SessionStatus.SCHEDULED

    def test_optional_end_time(self):
        session = Session(course_id=1, start_time=datetime.now(timezone.utc))
        assert session.end_time is None

    def test_repr(self):
        session = Session(course_id=3, start_time=datetime.now(timezone.utc))
        assert "course_id=3" in repr(session)

    def test_session_status_enum_values(self):
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.COMPLETED.value == "completed"

    def test_has_all_relationships(self):
        session = Session(course_id=1, start_time=datetime.now(timezone.utc))
        assert hasattr(session, "engagement_logs")
        assert hasattr(session, "nudges")
        assert hasattr(session, "reports")


# ---------------------------------------------------------------------------
# EngagementLog
# ---------------------------------------------------------------------------


class TestEngagementLog:
    def test_instantiation(self):
        log = EngagementLog(
            session_id=1,
            user_id=1,
            timestamp=datetime.now(timezone.utc),
            score=72.5,
            state=EngagementState.ENGAGED,
        )
        assert log.session_id == 1
        assert log.user_id == 1
        assert log.score == 72.5
        assert log.state == EngagementState.ENGAGED

    def test_optional_signal_scores(self):
        log = EngagementLog(
            session_id=1,
            user_id=1,
            timestamp=datetime.now(timezone.utc),
            score=50.0,
            state=EngagementState.PASSIVE,
        )
        assert log.gaze_score is None
        assert log.pose_score is None
        assert log.expression_score is None
        assert log.alertness_score is None

    def test_full_signal_scores(self):
        log = EngagementLog(
            session_id=2,
            user_id=3,
            timestamp=datetime.now(timezone.utc),
            score=85.0,
            state=EngagementState.ENGAGED,
            gaze_score=90.0,
            pose_score=80.0,
            expression_score=85.0,
            alertness_score=88.0,
            is_drowsy=False,
            is_yawning=False,
            phone_detected=False,
        )
        assert log.gaze_score == 90.0
        assert log.is_drowsy is False

    def test_drowsy_state(self):
        log = EngagementLog(
            session_id=1,
            user_id=1,
            timestamp=datetime.now(timezone.utc),
            score=20.0,
            state=EngagementState.DROWSY,
            is_drowsy=True,
        )
        assert log.state == EngagementState.DROWSY
        assert log.is_drowsy is True

    def test_repr(self):
        log = EngagementLog(
            session_id=1,
            user_id=2,
            timestamp=datetime.now(timezone.utc),
            score=60.0,
            state=EngagementState.PASSIVE,
        )
        assert "score=60.0" in repr(log)

    def test_engagement_state_enum_values(self):
        assert EngagementState.ENGAGED.value == "engaged"
        assert EngagementState.DISTRACTED.value == "distracted"
        assert EngagementState.DROWSY.value == "drowsy"
        assert EngagementState.CONFUSED.value == "confused"


# ---------------------------------------------------------------------------
# Nudge
# ---------------------------------------------------------------------------


class TestNudge:
    def test_instantiation(self):
        nudge = Nudge(
            session_id=1,
            user_id=2,
            nudge_type=NudgeType.FOCUS_REMINDER,
            trigger_state="distracted",
        )
        assert nudge.session_id == 1
        assert nudge.user_id == 2
        assert nudge.nudge_type == NudgeType.FOCUS_REMINDER
        assert nudge.trigger_state == "distracted"

    def test_default_acknowledged(self):
        nudge = Nudge(
            session_id=1,
            user_id=1,
            nudge_type=NudgeType.BREAK_SUGGESTION,
            trigger_state="drowsy",
        )
        assert nudge.acknowledged is False

    def test_effectiveness_delta(self):
        nudge = Nudge(
            session_id=1,
            user_id=1,
            nudge_type=NudgeType.ENCOURAGEMENT,
            trigger_state="passive",
            pre_nudge_score=40.0,
            effectiveness_delta=15.5,
        )
        assert nudge.effectiveness_delta == 15.5

    def test_repr(self):
        nudge = Nudge(
            session_id=3,
            user_id=4,
            nudge_type=NudgeType.DROWSINESS_ALERT,
            trigger_state="drowsy",
        )
        assert "session=3" in repr(nudge)

    def test_nudge_type_enum_values(self):
        assert NudgeType.FOCUS_REMINDER.value == "focus_reminder"
        assert NudgeType.DROWSINESS_ALERT.value == "drowsiness_alert"
        assert NudgeType.BREAK_SUGGESTION.value == "break_suggestion"


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


class TestReport:
    def test_instantiation(self):
        report = Report(
            session_id=1,
            report_type=ReportType.SESSION_SUMMARY,
        )
        assert report.session_id == 1
        assert report.report_type == ReportType.SESSION_SUMMARY

    def test_content_json(self):
        data = {"mean_score": 72.3, "at_risk_count": 2, "total_students": 30}
        report = Report(
            session_id=1,
            report_type=ReportType.SESSION_SUMMARY,
            content_json=data,
        )
        assert report.content_json["mean_score"] == 72.3

    def test_optional_rendered_path(self):
        report = Report(session_id=1, report_type=ReportType.WEEKLY_TREND)
        assert report.rendered_path is None

    def test_repr(self):
        report = Report(session_id=5, report_type=ReportType.AT_RISK_STUDENTS)
        assert "session=5" in repr(report)

    def test_report_type_enum_values(self):
        assert ReportType.SESSION_SUMMARY.value == "session_summary"
        assert ReportType.WEEKLY_TREND.value == "weekly_trend"
        assert ReportType.INTERVENTION_SUGGESTIONS.value == "intervention_suggestions"


# ---------------------------------------------------------------------------
# Cross-model relationship wiring
# ---------------------------------------------------------------------------


class TestRelationships:
    def test_course_belongs_to_user(self):
        teacher = User(name="Dr. Lee", email="lee@nst.edu", role=UserRole.TEACHER)
        course = Course(name="CV", code="CV101", teacher_id=1)
        course.teacher = teacher
        assert course.teacher.role == UserRole.TEACHER

    def test_session_belongs_to_course(self):
        course = Course(name="NLP", code="NLP101", teacher_id=1)
        session = Session(course_id=1, start_time=datetime.now(timezone.utc))
        session.course = course
        assert session.course.code == "NLP101"

    def test_engagement_log_belongs_to_session_and_user(self):
        log = EngagementLog(
            session_id=1,
            user_id=1,
            timestamp=datetime.now(timezone.utc),
            score=65.0,
            state=EngagementState.PASSIVE,
        )
        assert log.session_id == 1
        assert log.user_id == 1

    def test_nudge_belongs_to_session_and_user(self):
        nudge = Nudge(
            session_id=2,
            user_id=3,
            nudge_type=NudgeType.TOPIC_REVIEW,
            trigger_state="confused",
        )
        assert nudge.session_id == 2
        assert nudge.user_id == 3

    def test_report_belongs_to_session(self):
        report = Report(
            session_id=4,
            report_type=ReportType.SESSION_SUMMARY,
            content_json={"score": 80},
        )
        assert report.session_id == 4
