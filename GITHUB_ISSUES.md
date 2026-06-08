# EngageIQ AI - GitHub Issues (Full Descriptions)

Use this file as reference when creating issues on GitHub. Copy each issue's content into the GitHub issue body.

---

## Issue #1: Initialize repo scaffold, CI config, Docker setup

**Labels:** `m1`, `infra`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

Before anyone writes a single line of detection code, the project needs a clean, consistent structure that every contributor can clone and immediately start working in. Without this, four people will create four different directory layouts, import paths will break across branches, and merging becomes a nightmare.

A well-structured scaffold is not busywork - it is the foundation that makes parallel development possible. When all four contributors are working on the same issue simultaneously (competitive PRs), they need identical starting points. The scaffold gives them that.

Docker is included here because the development environment must be reproducible. "It works on my machine" is not acceptable when five people are contributing to the same codebase.

### What needs to be built

Create the full directory tree with all Python packages, verify all imports work, and ensure Docker builds cleanly.

### Files to create or update

- All `__init__.py` files in `src/` subdirectories
- `Dockerfile` - verify it builds with all CV dependencies (OpenCV, MediaPipe)
- `docker-compose.yml` - backend + PostgreSQL + frontend services
- Verify `requirements.txt` installs without errors
- Verify `.gitignore` covers all generated files

### How this affects overall development

This is issue #1 for a reason. Every other issue depends on this. If the scaffold is wrong, every contributor's work is built on a broken foundation. Get this right, and 34 issues flow smoothly. Get this wrong, and every PR has merge conflicts in import paths.

### How to test locally

```bash
# Clone and verify structure
git clone https://github.com/newton-school-ai/engageiq-ai.git
cd engageiq-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify all packages are importable
python -c "from src.agents import supervisor; print('agents OK')"
python -c "from src.detection import face_mesh; print('detection OK')"
python -c "from src.scoring import engagement_score; print('scoring OK')"
python -c "from src.nudge import nudge_decision; print('nudge OK')"
python -c "from src.analytics import class_aggregator; print('analytics OK')"
python -c "from src.api.main import app; print('API OK')"

# Verify Docker builds
docker-compose build
docker-compose up -d
curl http://localhost:8000/health  # should return {"status": "ok"}
docker-compose down
```

### Acceptance Criteria

- All `src/` packages are importable without errors
- `pip install -r requirements.txt` completes without dependency conflicts
- `docker-compose build` completes without errors
- `docker-compose up` starts backend and PostgreSQL successfully
- `/health` endpoint returns 200
- `.gitignore` excludes `.env`, `__pycache__/`, `models/weights/`, `data/sample_recordings/*.mp4`

### Branch

`feature/issue-1-scaffold`

### Depends on

None (first issue)

---

## Issue #2: Set up GitHub Actions CI (lint + test on every PR)

**Labels:** `m1`, `infra`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

Without automated CI, broken code slips into dev unnoticed. A contributor pushes code with a syntax error, the maintainer merges it, and suddenly three other contributors are debugging someone else's mistake. CI catches this before any human has to look at it.

This is especially critical in the competitive PR model. When four contributors submit four different implementations for the same issue, the maintainer needs an automated first pass. If a PR fails CI, it does not get reviewed - period. This saves the maintainer hours of review time and forces contributors to test their own code before submitting.

Linting (black, isort, flake8) ensures consistent code style across all contributors. When everyone's code looks the same, reviews focus on logic, not formatting.

### What needs to be built

Create a GitHub Actions workflow that runs on every PR targeting dev or main. It should lint (black, isort, flake8) and run pytest.

### Files to create or update

- `.github/workflows/ci.yml`

### How this affects overall development

Every PR from this point forward gets automatic quality checks. The maintainer can trust that any PR with a green checkmark at least passes basic quality gates. This changes the review workflow from "check everything manually" to "focus on logic and design."

### How to test locally

```bash
# Run the same checks CI will run
black --check src/ tests/
isort --check src/ tests/ --profile black
flake8 src/ tests/ --max-line-length 88
pytest tests/ -v

# To test the workflow file syntax
# Push a branch with a deliberate lint error
# Verify CI fails on the PR
# Fix the error, push again
# Verify CI passes
```

### Acceptance Criteria

- CI triggers automatically on every PR to dev and main
- Runs black --check, isort --check, flake8, and pytest
- PR shows green checkmark when all pass, red X when any fail
- Workflow completes in under 3 minutes
- CI uses Python 3.10 to match development environment

### Branch

`feature/issue-2-ci-workflow`

### Depends on

Closes #1

---

## Issue #3: Design database schema

**Labels:** `m1`, `infra`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

The database schema is the contract between every module in the system. When the detection pipeline produces an engagement score, it needs to know exactly where and how to store it. When the analytics module generates a report, it needs to know exactly where to read from. The schema defines these relationships.

Getting the schema wrong early is expensive. Adding a column is easy. Changing a foreign key relationship after five modules depend on it means rewriting queries, updating tests, and fixing bugs across the entire codebase. Thinking carefully about the schema now prevents weeks of rework later.

For EngageIQ, the core entities are: Users (students and teachers), Courses, Sessions (one per lecture), EngagementLogs (per-frame scores), Nudges (sent to students), and Reports (generated summaries). Every module in the system reads from or writes to these tables.

### What needs to be built

Create SQLAlchemy models for all 6 core entities with correct relationships, types, constraints, and indexes.

### Files to create or update

- `src/models/user.py` - User model (name, email, role, privacy_mode)
- `src/models/course.py` - Course model (name, code, teacher_id)
- `src/models/session.py` - Session model (course_id, start_time, end_time, status)
- `src/models/engagement_log.py` - EngagementLog (session_id, user_id, timestamp, score, state, gaze, drowsiness, expression)
- `src/models/nudge.py` - Nudge model (session_id, user_id, nudge_type, trigger_state, effectiveness_delta)
- `src/models/report.py` - Report model (session_id, report_type, content_json, created_at)
- `src/models/base.py` - SQLAlchemy declarative base

### How this affects overall development

Every module depends on this schema. The detection pipeline writes EngagementLogs. The nudge agent reads EngagementLogs and writes Nudges. The analytics module reads everything. The report generator reads everything and writes Reports. If the schema is wrong, every downstream module is wrong.

### How to test locally

```bash
# Run model tests
pytest tests/test_models.py -v

# Test that models can be instantiated
python -c "
from src.models.user import User
from src.models.course import Course
from src.models.session import Session
u = User(name='Test', email='test@nst.edu', role='student', privacy_mode='local_only')
print(f'User: {u.name}, role: {u.role}')
print('All models importable')
"
```

### Acceptance Criteria

- All 6 models defined with correct column types (String, Integer, Float, DateTime, Enum, JSON)
- Foreign key relationships: Course belongs to User (teacher), Session belongs to Course, EngagementLog belongs to Session and User, Nudge belongs to Session and User, Report belongs to Session
- Enum types for UserRole (student/teacher), PrivacyMode (local_only/share_with_teacher), EngagementState, NudgeType
- Created_at and updated_at timestamps on all models
- Indexes on frequently queried columns (session_id + user_id on EngagementLog, session_id on Nudge)
- At least 1 test per model verifying instantiation and relationships

### Branch

`feature/issue-3-db-schema`

### Depends on

Closes #1

---

## Issue #4: Alembic initial migration + seed data script

**Labels:** `m1`, `infra`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

SQLAlchemy models define what the schema should look like. Alembic makes it actually happen in the database. Without Alembic, you are running raw SQL to create tables, which means every developer's local database is slightly different, and deploying to production involves manual table creation that someone will inevitably forget a step of.

The seed data script is equally important. When a contributor clones the repo and sets up their database, they need test data to work with immediately. Without it, every developer writes their own test data, which leads to inconsistent testing and "it works with my data" bugs.

Seed data also enables the competitive PR workflow. When four contributors test their implementations against the same seed data, their results are directly comparable. The maintainer can evaluate competing PRs fairly.

### What needs to be built

Initialize Alembic, create the first migration from SQLAlchemy models, and write a seed script that populates test data.

### Files to create or update

- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Alembic environment setup
- `alembic/versions/001_initial_schema.py` - First migration
- `scripts/seed_data.py` - Seed script with test users, courses, sessions

### How this affects overall development

After this issue, every contributor can run two commands (`alembic upgrade head` and `python scripts/seed_data.py`) to have a fully populated database. This eliminates "how do I set up the database" questions and ensures everyone tests against identical data.

### How to test locally

```bash
# Create fresh database
createdb engageiq_dev

# Run migration
alembic upgrade head

# Verify tables exist
psql engageiq_dev -c "\dt"
# Should show: users, courses, sessions, engagement_logs, nudges, reports

# Run seed script
python scripts/seed_data.py

# Verify seed data
psql engageiq_dev -c "SELECT count(*) FROM users;"      # should be 7 (2 teachers + 5 students)
psql engageiq_dev -c "SELECT count(*) FROM courses;"     # should be 2
psql engageiq_dev -c "SELECT count(*) FROM sessions;"    # should be 3

# Verify downgrade works
alembic downgrade base
psql engageiq_dev -c "\dt"  # should show no tables
```

### Acceptance Criteria

- `alembic upgrade head` creates all 6 tables with correct columns and constraints
- `alembic downgrade base` cleanly removes all tables
- Seed script inserts: 2 teachers, 5 students, 2 courses, 3 sample sessions
- Seed script is idempotent (running twice does not create duplicates)
- Seed script prints what it created (e.g., "Created 7 users, 2 courses, 3 sessions")
- Migration file has descriptive docstring explaining what it creates

### Branch

`feature/issue-4-alembic-seed`

### Depends on

Closes #3

---

## Issue #5: Build webcam capture pipeline

**Labels:** `m1`, `cv`, `detection`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

The webcam capture pipeline is the entry point for the entire system. Without frames from a camera, there is nothing to detect, nothing to score, nothing to nudge about. Every CV model downstream receives its input from this pipeline.

This issue is also where you learn about video I/O in OpenCV, frame rates, and the difference between synchronous and asynchronous frame capture. In production, the webcam runs in the browser and sends frames to the backend via WebSocket. For development and testing, OpenCV's VideoCapture reads directly from the laptop webcam or a video file. Both paths must work.

The video file input is critical for testing. Contributors cannot run real webcam sessions every time they test their code. Pre-recorded clips let them test detection, scoring, and nudging without sitting in front of a camera.

### What needs to be built

A webcam capture service supporting multiple input sources (webcam, video file) with configurable FPS and graceful shutdown.

### Files to create or update

- `src/ingestion/webcam_capture.py` - Core capture logic (OpenCV VideoCapture)
- `src/ingestion/stream_handler.py` - WebSocket handler for browser frame streaming
- `src/api/routes/stream.py` - WebSocket endpoint

### How this affects overall development

Every detection module (#8 through #15) depends on this pipeline for input frames. If the pipeline drops frames, delivers them out of order, or fails to maintain target FPS, every downstream module inherits those problems. The pipeline must be rock-solid.

### How to test locally

```bash
# Test webcam capture
python -m src.ingestion.webcam_capture --source webcam --fps 15 --duration 10
# Should display 10 seconds of webcam feed with FPS counter overlay

# Test video file capture
python -m src.ingestion.webcam_capture --source data/sample_recordings/test_clip.mp4 --fps 15
# Should play the video file at 15 FPS with counter

# Test graceful shutdown
# Run webcam capture, press Ctrl+C
# Should exit cleanly without error traceback

# Test FPS accuracy
python -c "
from src.ingestion.webcam_capture import WebcamCapture
cap = WebcamCapture(source=0, fps=15)
frames = cap.capture(duration=5)
print(f'Captured {len(frames)} frames in 5 seconds')
print(f'Effective FPS: {len(frames) / 5:.1f}')  # should be ~15
"
```

### Acceptance Criteria

- Captures frames from laptop webcam at configurable FPS (5 to 30)
- Captures frames from video file at configurable FPS
- WebSocket endpoint accepts base64-encoded frames from browser
- FPS counter displayed in demo mode
- Graceful shutdown on KeyboardInterrupt (releases camera, closes connections)
- Returns frames as numpy arrays (BGR, uint8) compatible with OpenCV and MediaPipe
- Logs actual FPS vs target FPS for debugging

### Branch

`feature/issue-5-webcam-capture`

### Depends on

Closes #1

---

## Issue #6: Create frame preprocessing service

**Labels:** `m1`, `cv`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

Raw webcam frames are 640x480 (or higher) resolution images of someone's entire room. CV models do not need the bookshelf behind you or the wall to your left. They need a tightly cropped, normalized face region at a specific resolution.

Preprocessing is the bridge between raw video and CV inference. Every model downstream - face mesh, expression classifier, object detector - expects a specific input format. If this preprocessing step is wrong, every model receives garbage input and produces garbage output. The "garbage in, garbage out" principle is especially ruthless in computer vision.

FPS control is also handled here. Running MediaPipe at 30 FPS is overkill for engagement detection (engagement changes over seconds, not milliseconds). Running at 10-15 FPS saves CPU and battery, which matters when students run this on their laptops for hour-long lectures.

### What needs to be built

A preprocessing pipeline that detects the face region, crops it, resizes to model input dimensions, normalizes pixel values, and controls output FPS.

### Files to create or update

- `src/ingestion/frame_extractor.py` - Preprocessing pipeline
- `src/utils/image_utils.py` - Image manipulation utilities (crop, resize, normalize)

### How this affects overall development

This is the last piece of the ingestion pipeline. After this, detection modules receive clean, consistent face crops. If preprocessing is inconsistent (different crops, different normalization), the same face produces different detection results on different runs. Consistency here means reliability everywhere.

### How to test locally

```bash
# Test with video file
python -m src.ingestion.frame_extractor --input data/sample_recordings/test_clip.mp4 --output-fps 10
# Should display preprocessed face crops at 10 FPS

# Test normalization
python -c "
from src.ingestion.frame_extractor import FrameExtractor
from src.ingestion.webcam_capture import WebcamCapture
import numpy as np

cap = WebcamCapture(source=0, fps=15)
frame = cap.capture_one()
extractor = FrameExtractor(target_size=(224, 224))
face_crop = extractor.process(frame)

print(f'Input shape: {frame.shape}')       # e.g., (480, 640, 3)
print(f'Output shape: {face_crop.shape}')   # (224, 224, 3)
print(f'Value range: {face_crop.min():.2f} to {face_crop.max():.2f}')  # 0.0 to 1.0
"
```

### Acceptance Criteria

- Detects face bounding box from full frame (using MediaPipe or Haar cascade for quick detection)
- Crops face with 20% padding around bounding box (so forehead and chin are not cut off)
- Resizes crop to configurable dimensions (default 224x224)
- Normalizes pixel values to 0.0-1.0 float range
- Drops excess frames to maintain target output FPS
- Returns None when no face detected (does not crash)
- Processing time under 10ms per frame on laptop CPU

### Branch

`feature/issue-6-frame-preprocessing`

### Depends on

Closes #5

---

## Issue #7: Build user auth with Google OAuth, JWT sessions, and onboarding API

**Labels:** `m1`, `infra`, `frontend`
**Milestone:** M1: Project Scaffold and Webcam Pipeline

### Why

EngageIQ has two types of users with fundamentally different needs. Students want personal engagement data and smart nudges. Teachers want class-level analytics and intervention suggestions. The system must know who is who from the moment they sign up.

Google OAuth is the primary login method because the target users are college students and teachers, almost all of them have a Google account (university email or personal Gmail). One-click Google login reduces signup friction to near zero.

The flow: user clicks "Sign in with Google" -> Google consent screen -> backend receives auth code -> exchanges for Google profile (name, email, avatar) -> creates or finds user in database -> issues a JWT token for session management. On first login, the user is directed to an onboarding screen where they select their role (student/teacher) and privacy preferences.

Privacy preferences are captured at onboarding, not as an afterthought. When a student registers, they choose "local_only" (data stays on their device) or "share_with_teacher" (anonymized scores visible to teacher). This cannot be a default that users forget to change, it must be an explicit choice during signup.

The course enrollment API is how students connect to their teacher's class. Without it, the system cannot aggregate individual engagement into class-level analytics for the teacher.

### What needs to be built

Google OAuth integration, JWT token issuance/validation, protected route middleware, user onboarding (role + privacy), course CRUD, course enrollment, frontend login UI.

### Files to create or update

- `src/api/routes/auth.py` - Google OAuth callback, token issuance, token refresh
- `src/api/routes/users.py` - User profile, onboarding (role + privacy selection)
- `src/api/routes/courses.py` - Course CRUD and enrollment endpoints
- `src/api/middleware/auth.py` - JWT verification middleware, role-based access (student vs teacher)
- `src/api/schemas/user.py` - Pydantic schemas (UserCreate, UserResponse, TokenResponse)
- `src/api/schemas/course.py` - Pydantic schemas for course operations
- `src/models/user.py` - Add google_id, avatar_url, auth_provider fields
- `frontend/src/components/GoogleLoginButton.jsx` - Google sign-in button
- `frontend/src/contexts/AuthContext.jsx` - Auth state management, token storage, auto-refresh
- `.env.example` - Add GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, JWT_SECRET_KEY

### How this affects overall development

User identity gates session history, engagement data, nudge preferences, and teacher dashboards. Protected routes ensure only authenticated users can start webcam sessions or view analytics. Privacy preferences set here determine data flow for the entire system. The course enrollment API is how students connect to their teacher's class for aggregated analytics.

### How to test locally

```bash
# 1. Set up Google OAuth credentials at console.cloud.google.com
#    - Create OAuth 2.0 Client ID (Web application)
#    - Add http://localhost:5173 to Authorized JavaScript origins
#    - Add http://localhost:8000/api/auth/google/callback to Authorized redirect URIs
#    - Copy Client ID and Client Secret to .env

# 2. Start backend
uvicorn src.api.main:app --reload --port 8000

# 3. Start frontend
cd frontend && npm run dev

# 4. Click "Sign in with Google" -> consent screen -> redirected back -> logged in
# 5. First-time users see onboarding: select role (student/teacher) + privacy preference

# 6. Verify JWT works
TOKEN="<jwt_from_login_response>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/users/me

# 7. Test protected route without token
curl http://localhost:8000/api/users/me
# Should return 401 Unauthorized

# 8. Create a course (teacher only)
curl -X POST http://localhost:8000/api/courses \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Data Structures", "code": "CS201"}'

# 9. Enroll student in course
curl -X POST http://localhost:8000/api/courses/1/enroll \
  -H "Authorization: Bearer $TOKEN"

# 10. Verify enrollment
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/courses/1/students
```

### Acceptance Criteria

- [ ] Google OAuth login flow works end-to-end (click -> consent -> JWT -> logged in)
- [ ] Backend exchanges Google auth code for user profile (name, email, avatar)
- [ ] New users directed to onboarding screen on first login (select role + privacy)
- [ ] JWT issued on login, expires in 24 hours, refresh token for 7 days
- [ ] JWT middleware protects routes: webcam session, engagement data, analytics
- [ ] Role-based access: teacher-only routes (class analytics, intervention) check role
- [ ] Privacy mode required for students (no default, must explicitly choose local_only or share_with_teacher)
- [ ] Frontend shows Google login button, user avatar + name after login, logout button
- [ ] Auth state persists across page refresh (token stored in memory, refresh on expiry)
- [ ] POST /api/courses creates a course linked to authenticated teacher
- [ ] POST /api/courses/{id}/enroll enrolls authenticated student in a course
- [ ] GET /api/courses/{id}/students returns enrolled students
- [ ] Input validation with clear error messages (e.g., "email already registered", "invalid role")
- [ ] At least 5 tests: Google login mock, JWT validation, protected route 401, role check, course enrollment

### Branch

`feature/issue-7-user-api`

### Depends on

Closes #4

---

## Issue #8: Integrate MediaPipe Face Mesh

**Labels:** `m2`, `cv`, `detection`
**Milestone:** M2: Face Detection and Gaze Estimation

### Why

MediaPipe Face Mesh is the foundation of the entire detection pipeline. It provides 468 facial landmarks - precise (x, y, z) coordinates for every part of the face including eyes, eyebrows, nose, lips, jaw, and forehead. Every other detection module in EngageIQ depends on these landmarks.

Head pose estimation (#9) uses 6 of these landmarks. Drowsiness detection (#12) uses the 12 eye landmarks. Yawn detection (#13) uses the lip landmarks. Expression classification (#14) uses the cropped face region that Face Mesh identifies. Without Face Mesh, none of these modules can function.

MediaPipe was chosen over alternatives (dlib, OpenCV Haar cascades) for three reasons. First, it provides 468 landmarks versus dlib's 68 - far more detail for fine-grained analysis. Second, it runs at 30+ FPS on laptop CPU without a GPU. Third, it has a WebAssembly version that can run entirely in the browser, which is critical for EngageIQ's privacy-first design where no video leaves the student's device.

### What needs to be built

A Face Mesh detector class that wraps MediaPipe, handles initialization, processes frames, extracts landmarks, and provides a demo visualization mode.

### Files to create or update

- `src/detection/face_mesh.py` - FaceMeshDetector class

### How this affects overall development

This is the most critical detection module. Issues #9, #10, #11, #12, #13, and #14 all depend on Face Mesh output. If landmarks are inaccurate, every downstream calculation (EAR, MAR, head pose, gaze) inherits that inaccuracy. The FPS benchmark set here determines the maximum throughput of the entire pipeline.

### How to test locally

```bash
# Demo mode - visualizes landmarks on webcam feed
python -m src.detection.face_mesh --demo
# Should open webcam window with:
# - Green dots on all 468 landmarks
# - FPS counter in top-left corner
# - "No face detected" message when you step away

# Benchmark mode
python -c "
from src.detection.face_mesh import FaceMeshDetector
from src.ingestion.webcam_capture import WebcamCapture
import time

detector = FaceMeshDetector()
cap = WebcamCapture(source=0, fps=30)

start = time.time()
count = 0
for frame in cap.stream(duration=10):
    landmarks = detector.detect(frame)
    if landmarks is not None:
        count += 1
elapsed = time.time() - start
print(f'Processed {count} faces in {elapsed:.1f}s')
print(f'FPS: {count / elapsed:.1f}')  # should be 25+
print(f'Landmarks shape: {landmarks.shape}')  # should be (468, 3)
"
```

### Acceptance Criteria

- Detects face and returns 468 landmarks as numpy array of shape (468, 3)
- Each landmark is (x, y, z) where x, y are normalized 0-1 coordinates and z is depth
- Runs at 25+ FPS on laptop CPU (benchmark with 10-second capture)
- Returns None gracefully when no face is detected (no exception)
- Handles varying lighting conditions (desk lamp, window light, dim room)
- Demo mode visualizes all 468 landmarks overlaid on the webcam feed
- FPS counter displayed in demo mode
- Properly releases MediaPipe resources on close

### Branch

`feature/issue-8-facemesh`

### Depends on

Closes #6

---

## Issue #9: Implement head pose estimation

**Labels:** `m2`, `cv`, `detection`
**Milestone:** M2: Face Detection and Gaze Estimation

### Why

A student's head direction is one of the strongest engagement signals. If someone is facing their screen, they are probably paying attention. If they are looking down at their phone, turned to talk to a roommate, or slumped forward asleep - the head pose tells you exactly that.

Head pose estimation converts raw facial landmarks into three angles: pitch (nodding up/down), yaw (turning left/right), and roll (tilting head sideways). These angles are the input to the gaze classifier (#10) and contribute 20% of the overall engagement score (#16).

The algorithm uses OpenCV's solvePnP function, which takes six 2D landmark points from the face (nose tip, chin, left eye corner, right eye corner, left mouth corner, right mouth corner), compares them against a 3D reference model of a human face, and computes the rotation angles. This is the same technique used in AR face filters and driver drowsiness systems.

### What needs to be built

A head pose estimator that takes Face Mesh landmarks and returns pitch, yaw, roll angles in degrees.

### Files to create or update

- `src/detection/head_pose.py` - HeadPoseEstimator class with solvePnP implementation

### How this affects overall development

Head pose feeds directly into the gaze classifier (#10) which determines if the student is looking at the screen. It also feeds into the engagement scorer (#16) as a 20% weight. Inaccurate head pose means inaccurate gaze classification and engagement scores for every student in every session.

### How to test locally

```bash
# Demo mode - visualizes 3 axes on face
python -m src.detection.head_pose --demo
# Should open webcam with 3 colored axes drawn from nose tip:
# Red axis = yaw (left/right turn)
# Green axis = pitch (up/down nod)
# Blue axis = roll (sideways tilt)
#
# Test by:
# - Looking straight: pitch ~0, yaw ~0, roll ~0
# - Looking left: yaw increases to +30
# - Looking right: yaw decreases to -30
# - Looking down: pitch decreases to -20
# - Tilting head: roll changes

# Accuracy test
python -c "
from src.detection.face_mesh import FaceMeshDetector
from src.detection.head_pose import estimate_head_pose
from src.ingestion.webcam_capture import WebcamCapture

detector = FaceMeshDetector()
cap = WebcamCapture(source=0, fps=15)

print('Look straight at the screen...')
frame = cap.capture_one()
landmarks = detector.detect(frame)
pitch, yaw, roll = estimate_head_pose(landmarks, frame.shape)
print(f'Pitch: {pitch:.1f}, Yaw: {yaw:.1f}, Roll: {roll:.1f}')
# Expected: all near 0 when looking straight
"
```

### Acceptance Criteria

- Returns (pitch, yaw, roll) as floats in degrees
- Accuracy within 5 degrees for frontal pose (looking straight at camera)
- Accuracy within 10 degrees for up to 30-degree head rotation
- Works with the 6 standard landmark points from MediaPipe Face Mesh
- Demo mode draws 3-axis gizmo (RGB = XYZ) from nose tip
- Shows live pitch, yaw, roll values on screen in demo mode
- Does not crash on partial face occlusion (returns last known pose or None)
- Processing time under 2ms per frame (solvePnP is fast)

### Branch

`feature/issue-9-head-pose`

### Depends on

Closes #8

---

## Issue #10: Build gaze direction classifier

**Labels:** `m2`, `cv`, `detection`
**Milestone:** M2: Face Detection and Gaze Estimation

### Why

Raw pitch, yaw, and roll angles are continuous numbers that the engagement scorer cannot directly use. The gaze classifier converts these angles into discrete, meaningful states: is the student looking at the screen, looking away, looking down, or have their eyes closed?

This classification is what makes the system actionable. "Yaw is 35 degrees" means nothing to a nudge agent. "Student is looking away to the left for 15 seconds" means it is time to send a gentle reminder.

The classifier also introduces the concept of configurable thresholds. What counts as "looking away"? Is it 20 degrees of yaw or 30 degrees? Different webcam positions, screen sizes, and sitting distances affect this. Making thresholds configurable means the system can adapt to each student's setup rather than forcing everyone into a one-size-fits-all model.

### What needs to be built

A gaze classifier that maps head pose angles and eye state (open/closed) to discrete gaze states with confidence scores.

### Files to create or update

- `src/detection/gaze_classifier.py` - GazeClassifier class with configurable thresholds

### How this affects overall development

The gaze state is the single largest contributor to the engagement score (30% weight in #16). It is also the primary trigger for nudges (#20) - if a student is looking away for too long, that is the most common disengagement signal. Getting this right means accurate engagement scoring and well-timed nudges.

### How to test locally

```bash
# Demo mode
python -m src.detection.gaze_classifier --demo
# Should show webcam with current gaze state label:
# Look straight -> "AT_SCREEN" (green label)
# Turn left -> "AWAY_LEFT" (yellow label)
# Turn right -> "AWAY_RIGHT" (yellow label)
# Look down -> "LOOKING_DOWN" (orange label)
# Close eyes -> "EYES_CLOSED" (red label)

# Test threshold configurability
python -c "
from src.detection.gaze_classifier import GazeClassifier, GazeState

# Default thresholds
clf = GazeClassifier()
state, conf = clf.classify(pitch=0, yaw=5, ear=0.3)
print(f'Straight ahead: {state}, confidence: {conf:.2f}')  # AT_SCREEN

state, conf = clf.classify(pitch=0, yaw=35, ear=0.3)
print(f'Turned right: {state}, confidence: {conf:.2f}')  # AWAY_RIGHT

state, conf = clf.classify(pitch=-20, yaw=0, ear=0.3)
print(f'Looking down: {state}, confidence: {conf:.2f}')  # LOOKING_DOWN

state, conf = clf.classify(pitch=0, yaw=0, ear=0.15)
print(f'Eyes closed: {state}, confidence: {conf:.2f}')  # EYES_CLOSED
"
```

### Acceptance Criteria

- Classifies into 5 states: AT_SCREEN, AWAY_LEFT, AWAY_RIGHT, LOOKING_DOWN, EYES_CLOSED
- Returns confidence score (0.0 to 1.0) for each classification
- Thresholds configurable: yaw_threshold (default 25 degrees), pitch_threshold (default 15 degrees), ear_threshold (default 0.25)
- Accuracy > 85% on manual testing (test each state 20 times)
- No rapid flipping between states on borderline angles (add 5-degree hysteresis buffer)
- Demo mode shows live state label with color coding

### Branch

`feature/issue-10-gaze-classifier`

### Depends on

Closes #9

---

## Issue #11: Multi-face handling and face selection logic

**Labels:** `m2`, `cv`, `detection`
**Milestone:** M2: Face Detection and Gaze Estimation

### Why

Indian students often study in shared rooms, hostels, or living rooms where family members walk behind them. If your roommate passes behind you during a lecture, the system should not suddenly start tracking their face instead of yours. If your sibling sits next to you, the system should not average both your engagement scores.

Multi-face handling is a real-world robustness issue. In a controlled lab, face detection is easy - there is one face in frame. In a student's hostel room, there might be three. The system must reliably lock onto the primary user and ignore everyone else, even when the primary user briefly looks away or covers part of their face.

This issue also introduces object tracking across frames. Rather than independently detecting faces in each frame (which can jump between faces), tracking maintains identity across frames so the system knows "this is the same person I have been tracking for the last 30 minutes."

### What needs to be built

A face selection module that scores multiple detected faces and consistently selects the primary user across frames.

### Files to create or update

- `src/detection/face_selector.py` - FaceSelector class with scoring and tracking

### How this affects overall development

Without this, every detection module from #12 to #15 will occasionally process the wrong face, producing incorrect engagement scores. This is especially problematic for the calibration system (#19) which stores per-student baselines - if the calibration captures your roommate's baseline instead of yours, all subsequent detection is wrong.

### How to test locally

```bash
# Demo mode - have someone walk behind you
python -m src.detection.face_selector --demo
# Should show:
# Green box around primary face (you)
# Gray box around secondary faces (others)
# Label showing face score: "Primary (score: 0.92)"
# Primary face should NOT change when someone walks behind you

# Test with two people on screen
# Sit side by side with a friend
# Primary face should be the one closest to camera center
# If friend leans in closer, primary should NOT switch (temporal consistency)

# Stability test
python -c "
from src.detection.face_selector import FaceSelector
from src.detection.face_mesh import FaceMeshDetector
from src.ingestion.webcam_capture import WebcamCapture

selector = FaceSelector()
detector = FaceMeshDetector(max_faces=3)
cap = WebcamCapture(source=0, fps=15)

switches = 0
last_primary = None
for frame in cap.stream(duration=30):
    faces = detector.detect_all(frame)
    primary = selector.select(faces, frame.shape)
    if last_primary is not None and primary != last_primary:
        switches += 1
    last_primary = primary

print(f'Primary face switches in 30 seconds: {switches}')
# Should be 0 if only you are in frame
"
```

### Acceptance Criteria

- Correctly selects primary face when 2-3 faces are in frame
- Selection scoring uses: face area (40%), center proximity (30%), temporal consistency (30%)
- Primary face does not switch when a secondary face briefly appears and disappears
- Primary face does not switch when secondary face is larger (e.g., someone leans in closer temporarily)
- Temporal consistency window is configurable (default 30 frames = 2 seconds)
- Falls back gracefully to single-face mode when only one face detected
- Green/gray bounding box visualization in demo mode
- Zero primary face switches during 30-second single-person test

### Branch

`feature/issue-11-face-selector`

### Depends on

Closes #8

---

## Issue #12: Implement EAR-based drowsiness detection

**Labels:** `m3`, `cv`, `detection`
**Milestone:** M3: Drowsiness and Expression Detection

### Why

Drowsiness is the clearest signal that a student has completely disengaged. A distracted student might re-engage on their own. A drowsy student will not. Detecting drowsiness early and sending a gentle nudge can save an entire lecture's worth of learning.

The Eye Aspect Ratio (EAR) is a simple, elegant measure invented by Soukupova and Cech in 2016. It computes the ratio of vertical eye distances to horizontal eye distance using six landmarks per eye. When the eye is open, EAR is around 0.3. When the eye is closed, EAR drops below 0.2. A blink is a brief dip (under 0.3 seconds). Drowsiness is a sustained dip (over 1.5 seconds).

The beauty of EAR is that it requires zero training. It is a pure geometric computation on landmarks that MediaPipe already provides. No dataset, no model, no GPU. Just math. This makes it reliable, fast, and interpretable - you can explain exactly why the system flagged a student as drowsy.

### What needs to be built

An EAR computation function and a drowsiness detector that distinguishes blinks from drowsiness using temporal tracking.

### Files to create or update

- `src/detection/drowsiness.py` - DrowsinessDetector class with EAR computation
- `src/utils/landmark_utils.py` - Utility functions for extracting specific landmark subsets

### How this affects overall development

Drowsiness contributes 25% to the engagement score via the alertness component (#16). It is also a direct trigger for high-priority nudges (#20) - a drowsy student gets a nudge faster than a distracted one. The EAR threshold calibration issue (#19) depends on getting the baseline EAR computation right here first.

### How to test locally

```bash
# Demo mode
python -m src.detection.drowsiness --demo
# Blink normally -> brief "BLINK" label appears and disappears
# Close eyes for 2+ seconds -> "DROWSY" warning appears in red
# EAR value displayed live in corner

# Accuracy test
python -c "
from src.detection.drowsiness import compute_ear, DrowsinessDetector
import numpy as np

# Test EAR formula with known points
# Open eye (equilateral-ish shape)
open_eye = [(0.0, 0.3), (0.1, 0.4), (0.2, 0.4), (0.3, 0.3), (0.2, 0.2), (0.1, 0.2)]
ear_open = compute_ear(open_eye)
print(f'Open eye EAR: {ear_open:.3f}')  # should be ~0.33

# Closed eye (flat shape)
closed_eye = [(0.0, 0.3), (0.1, 0.31), (0.2, 0.31), (0.3, 0.3), (0.2, 0.29), (0.1, 0.29)]
ear_closed = compute_ear(closed_eye)
print(f'Closed eye EAR: {ear_closed:.3f}')  # should be ~0.07
"

# False positive test - sit attentively for 60 seconds
python -c "
from src.detection.drowsiness import DrowsinessDetector
from src.detection.face_mesh import FaceMeshDetector
from src.ingestion.webcam_capture import WebcamCapture
import time

detector = FaceMeshDetector()
drowsiness = DrowsinessDetector()
cap = WebcamCapture(source=0, fps=15)

false_positives = 0
for frame in cap.stream(duration=60):
    landmarks = detector.detect(frame)
    if landmarks is not None:
        is_drowsy = drowsiness.update(landmarks, time.time())
        if is_drowsy:
            false_positives += 1

print(f'False positives in 60 seconds of attentive behavior: {false_positives}')
# Should be 0
"
```

### Acceptance Criteria

- EAR computed correctly from 6 eye landmarks per eye (indices from MediaPipe Face Mesh)
- Returns EAR for left eye, right eye, and average
- Blinks (EAR < threshold for < 0.3 seconds) are labeled as blinks, not drowsiness
- Drowsiness (EAR < threshold for > 1.5 seconds continuously) triggers drowsy state
- Default EAR threshold: 0.25 (configurable)
- Default drowsy duration: 1.5 seconds (configurable)
- False positive rate < 5% during 60 seconds of normal attentive behavior
- Blink counter tracks blinks per minute (useful for fatigue trend)
- Demo mode shows live EAR value, blink count, and drowsiness state

### Branch

`feature/issue-12-ear-drowsiness`

### Depends on

Closes #8

---

## Issue #13: Build yawn detection

**Labels:** `m3`, `cv`, `detection`
**Milestone:** M3: Drowsiness and Expression Detection

### Why

Yawning is a fatigue signal that EAR-based drowsiness detection misses. A student can yawn with their eyes wide open. Frequent yawning (3 or more in 5 minutes) is a strong indicator that the student needs a break, even if their eyes are not closing.

The Mouth Aspect Ratio (MAR) is the mouth equivalent of EAR. It computes the ratio of vertical lip distances to horizontal lip distance. When the mouth is closed, MAR is near 0. When the mouth opens wide for a yawn, MAR exceeds 0.6. The key challenge is distinguishing yawns from speech - talking also opens the mouth, but in shorter, more varied patterns. A yawn is sustained (over 1.5 seconds) and typically accompanied by a wider opening than speech.

Combining yawn detection with EAR-based drowsiness gives a robust fatigue assessment. A student who is blinking slowly AND yawning frequently is definitely tired. Either signal alone might be a false positive; together, they are reliable.

### What needs to be built

A MAR computation function and a yawn detector with frequency tracking.

### Files to create or update

- `src/detection/yawn.py` - YawnDetector class with MAR computation and frequency tracking

### How this affects overall development

Yawn frequency feeds into the alertness score, which is 25% of overall engagement (#16). The fatigue signal (3+ yawns in 5 minutes) is used by the nudge agent (#20) to suggest a break. It also contributes to the weekly trend report (#28) - teachers can see if students are consistently fatigued in specific time slots.

### How to test locally

```bash
# Demo mode
python -m src.detection.yawn --demo
# Open mouth wide for 2 seconds -> "YAWN" label appears
# Talk normally -> should NOT trigger yawn detection
# MAR value displayed live
# Yawn count displayed: "Yawns: 0"

# Speech false positive test
python -c "
from src.detection.yawn import YawnDetector
from src.detection.face_mesh import FaceMeshDetector
from src.ingestion.webcam_capture import WebcamCapture
import time

detector = FaceMeshDetector()
yawn_det = YawnDetector()
cap = WebcamCapture(source=0, fps=15)

print('Talk normally for 30 seconds...')
yawns = 0
for frame in cap.stream(duration=30):
    landmarks = detector.detect(frame)
    if landmarks is not None:
        is_yawn = yawn_det.update(landmarks, time.time())
        if is_yawn:
            yawns += 1

print(f'False yawns during 30 seconds of talking: {yawns}')
# Should be 0
"
```

### Acceptance Criteria

- MAR computed correctly from lip landmarks (MediaPipe Face Mesh indices)
- Yawn detected when MAR > 0.6 sustained for > 1.5 seconds
- Normal speech (MAR 0.2-0.5, duration < 0.5s per syllable) does not trigger false yawns
- Yawn frequency tracked: count per rolling 5-minute window
- `is_fatigued()` returns True when 3+ yawns in 5 minutes
- Default thresholds configurable: MAR threshold (0.6), duration (1.5s), fatigue count (3), fatigue window (300s)
- Demo mode shows live MAR value, yawn count, and fatigue status
- Zero false yawns during 30-second speech test

### Branch

`feature/issue-13-yawn-detection`

### Depends on

Closes #8

---

## Issue #14: Train or integrate expression classifier

**Labels:** `m3`, `cv`, `detection`
**Milestone:** M3: Drowsiness and Expression Detection

### Why

A student looking at the screen with their eyes open is not necessarily engaged. They might be confused, staring blankly because they do not understand the material. They might be bored, watching the lecture on autopilot while thinking about lunch. EAR tells you if eyes are open. Gaze tells you where they are looking. But only expression classification tells you what they are feeling.

This is where the system moves from mechanical detection ("are eyes open?") to emotional understanding ("is the student confused?"). A confused student needs the teacher to slow down and explain differently. A bored student needs the teacher to add an activity or change pace. Without expression classification, the system cannot distinguish these two very different states.

The FER2013 dataset (Facial Expression Recognition 2013) provides 35,000 grayscale 48x48 face images labeled with 7 emotions. EngageIQ uses 4 of these: engaged (approximated by "happy" + "surprise"), confused (approximated by "fear" + "disgust"), bored (approximated by "sad"), and neutral. This mapping is deliberate - the standard 7-class FER labels do not map perfectly to engagement states, so remapping is necessary.

### What needs to be built

An expression classifier that takes a cropped face image and returns one of 4 engagement-relevant expressions with a confidence score.

### Files to create or update

- `src/detection/expression.py` - ExpressionClassifier class

### How this affects overall development

Expression contributes 25% to the engagement score (#16). It is also the primary signal for the "Confused" state in the state machine (#17), which triggers different nudges and different intervention suggestions than the "Distracted" or "Drowsy" states. Getting expression classification right means the system responds appropriately to different kinds of disengagement.

### How to test locally

```bash
# Demo mode
python -m src.detection.expression --demo
# Should show webcam with predicted expression label and confidence bar
# Try each expression:
# - Attentive/alert face -> "ENGAGED" 
# - Furrowed brow, squinting -> "CONFUSED"
# - Flat affect, slack face -> "BORED"
# - Relaxed, no strong expression -> "NEUTRAL"

# Benchmark
python -c "
from src.detection.expression import ExpressionClassifier
from src.ingestion.webcam_capture import WebcamCapture
import time

clf = ExpressionClassifier()
cap = WebcamCapture(source=0, fps=15)

frame = cap.capture_one()
start = time.time()
for _ in range(100):
    expr, conf = clf.predict(frame)
elapsed = time.time() - start

print(f'Expression: {expr}, confidence: {conf:.2f}')
print(f'Avg inference time: {elapsed/100*1000:.1f}ms')  # should be < 30ms
"
```

### Acceptance Criteria

- Classifies into 4 states: ENGAGED, CONFUSED, BORED, NEUTRAL
- Returns class label and confidence score (0.0 to 1.0)
- Uses FER library (pre-trained) or custom CNN as backend (configurable)
- Accuracy > 70% on FER2013 test set (mapped to 4 classes)
- Inference time < 30ms per frame on laptop CPU
- Handles varying lighting conditions without significant accuracy drop
- Demo mode shows live expression label with confidence bar
- Input: cropped face image as numpy array (any size - internally resized)

### Branch

`feature/issue-14-expression-classifier`

### Depends on

Closes #8

---

## Issue #15: Expression model training notebook with FER2013 benchmarking

**Labels:** `m3`, `cv`
**Milestone:** M3: Drowsiness and Expression Detection

### Why

Using a pre-trained library is practical, but it is not learning. This notebook exists so every contributor understands what is happening inside the expression classifier - not just how to call it, but how it works.

The Build, Understand, Defend framework means every contributor must be able to answer: "How does the expression classifier work?" The answer is not "I imported the FER library." The answer is: "It is a convolutional neural network with 3 conv layers and 2 fully connected layers, trained on FER2013 with 35,887 images across 7 classes which we remapped to 4. The confusion matrix shows it confuses bored and neutral 18% of the time because the facial differences are subtle. Our custom model achieves 72% accuracy versus the FER library's 68% on our 4-class mapping."

This notebook is also where contributors learn data exploration, model training, evaluation metrics (confusion matrix, per-class accuracy), and the concept of transfer learning. These are skills that go on resumes and come up in interviews.

### What needs to be built

A Jupyter notebook that downloads FER2013, explores the data, trains a lightweight CNN, evaluates it, and compares against the FER library baseline.

### Files to create or update

- `notebooks/expression_training.ipynb` - Full training notebook
- `notebooks/README.md` - Instructions to run the notebook

### How this affects overall development

This notebook can produce a custom model that replaces or supplements the FER library used in #14. If the custom model outperforms FER on the 4-class mapping, it should be used as the default. The notebook also serves as documentation - anyone reviewing the project can see exactly how the model was trained and evaluated.

### How to test locally

```bash
# Install Jupyter if not already
pip install jupyter

# Run notebook
jupyter notebook notebooks/expression_training.ipynb
# Run all cells top to bottom
# Should complete without errors
# Final cell prints accuracy comparison

# Verify saved model
ls models/weights/expression_custom.pth  # should exist after training
python -c "
import torch
model = torch.load('models/weights/expression_custom.pth', map_location='cpu')
print('Model loaded successfully')
print(f'Parameters: {sum(p.numel() for p in model.parameters()):,}')
"
```

### Acceptance Criteria

- Notebook downloads FER2013 automatically (from Kaggle or alternative mirror)
- Data exploration section: class distribution, sample images per class, train/test split sizes
- Preprocessing: grayscale to RGB conversion, normalization, data augmentation (horizontal flip, slight rotation)
- Model architecture: 3 conv blocks (conv + batchnorm + relu + maxpool) + 2 FC layers + dropout
- Training: 20 epochs, Adam optimizer, learning rate scheduler, train/val loss curves plotted
- Evaluation: confusion matrix, per-class precision/recall/F1, overall accuracy
- 7-class to 4-class remapping clearly documented with rationale
- Comparison table: custom model vs FER library on same test set
- Saves best model weights to models/weights/
- Markdown cells explain each step in plain language (Build, Understand, Defend)
- Training completes in under 30 minutes on CPU

### Branch

`feature/issue-15-expression-notebook`

### Depends on

Closes #14

---

## Issue #16: Design multi-signal engagement scoring

**Labels:** `m4`, `agent`, `cv`
**Milestone:** M4: Engagement Scoring Agent

### Why

Individual CV signals are noisy and incomplete on their own. Gaze alone cannot tell you if a student is drowsy. Expression alone cannot tell you if they are looking at the screen. Drowsiness alone does not capture confusion. The engagement scorer fuses all four signals into a single, reliable 0-100 score that downstream modules (nudge agent, analytics, reports) can act on.

The weighted average approach was chosen over a trained ML model for three reasons. First, it is interpretable - when a student asks "why did I get a low engagement score at minute 14?", you can answer "your gaze was away (30% weight) and your expression was confused (25% weight)." Second, it is configurable per course type - a coding lab needs higher gaze weight than a discussion seminar. Third, it requires zero training data - you do not need labeled engagement examples to start scoring.

This is also where the system transitions from perception (seeing what the student is doing) to reasoning (interpreting what it means). The scorer is the first "agentic" component - it makes a judgment call, not just a measurement.

### What needs to be built

A weighted scorer that fuses gaze, pose, expression, and alertness signals into a 0-100 engagement score with configurable weights.

### Files to create or update

- `src/scoring/engagement_score.py` - Engagement scorer with weighted fusion
- `src/config/scoring_weights.py` - Weight profiles per course type

### How this affects overall development

The engagement score is the single number that the entire downstream system depends on. The state machine (#17) maps it to discrete states. The nudge agent (#20) triggers based on it. The analytics (#24) aggregate it. The reports (#27, #28) visualize it. If the score is unreliable, every downstream module produces unreliable results.

### How to test locally

```bash
pytest tests/test_engagement_score.py -v

# Manual signal fusion test
python -c "
from src.scoring.engagement_score import compute_engagement_score

# Fully engaged student
score = compute_engagement_score(gaze_score=100, pose_score=95, expression_score=90, alertness_score=100)
print(f'Fully engaged: {score:.1f}')  # should be > 95

# Looking away but alert
score = compute_engagement_score(gaze_score=0, pose_score=30, expression_score=60, alertness_score=100)
print(f'Looking away: {score:.1f}')  # should be ~40-50

# Drowsy
score = compute_engagement_score(gaze_score=50, pose_score=40, expression_score=30, alertness_score=0)
print(f'Drowsy: {score:.1f}')  # should be < 30

# Missing signal (expression model failed)
score = compute_engagement_score(gaze_score=90, pose_score=85, expression_score=None, alertness_score=95)
print(f'Missing expression: {score:.1f}')  # should redistribute weights, still ~90
"
```

### Acceptance Criteria

- Score range 0-100 with clear interpretation (0 = fully disengaged, 100 = fully engaged)
- Default weights: gaze 30%, pose 20%, expression 25%, alertness 25%
- Weights configurable per course type (theory, lab, seminar, discussion profiles)
- Handles missing signals gracefully: redistributes weight proportionally among remaining signals
- At least 8 test cases covering: all high, all low, mixed, missing signals, edge cases
- Score is a float, not an integer (enables fine-grained temporal smoothing)
- Function is pure (no side effects, no state) - easy to test and reason about

### Branch

`feature/issue-16-engagement-score`

### Depends on

Closes #10, Closes #12, Closes #14

---

## Issue #17: Build engagement state machine

**Labels:** `m4`, `agent`
**Milestone:** M4: Engagement Scoring Agent

### Why

A continuous score of 47.3 is hard for a nudge agent to act on. Should it nudge at 47? At 40? At 30? The state machine converts the continuous score into discrete, actionable states: Engaged, Passive, Distracted, Drowsy, Confused. Each state has clear meaning and triggers specific responses.

Hysteresis is the critical feature. Without it, a student hovering at the boundary between Engaged (70+) and Passive (40-69) would flip back and forth every few seconds as their score fluctuates around 68-72. Hysteresis adds a duration requirement: you must stay below 70 for at least 30 seconds before transitioning from Engaged to Passive. Brief dips are ignored. This prevents the system from being jumpy and annoying.

The state machine also provides the event system that downstream modules subscribe to. When the state transitions from Engaged to Distracted, that event triggers the nudge agent to consider sending a reminder. Without a clean event system, every module would be polling the score and independently deciding what to do, leading to inconsistent behavior.

### What needs to be built

A finite state machine with 5 states, configurable score ranges, duration thresholds for transitions, and an event system for state changes.

### Files to create or update

- `src/scoring/state_machine.py` - EngagementStateMachine class

### How this affects overall development

The state machine is the interface between scoring and action. The nudge agent (#20) subscribes to state transition events. The analytics (#24) log state durations. The reports (#27, #28) summarize time spent in each state. If the state machine is noisy (frequent false transitions), every downstream module inherits that noise.

### How to test locally

```bash
pytest tests/test_state_machine.py -v

# Hysteresis test
python -c "
from src.scoring.state_machine import EngagementStateMachine
import time

sm = EngagementStateMachine()

# Feed high scores for 5 seconds
for i in range(75):  # 75 frames at 15 FPS = 5 seconds
    state = sm.update(score=85, is_drowsy=False, is_confused=False, timestamp=i/15)
print(f'After 5s of score 85: {state}')  # ENGAGED

# Brief dip for 1 second (should NOT transition)
for i in range(75, 90):
    state = sm.update(score=35, is_drowsy=False, is_confused=False, timestamp=i/15)
print(f'After 1s dip to 35: {state}')  # Still ENGAGED (hysteresis)

# Sustained drop for 20 seconds (should transition)
for i in range(90, 390):
    state = sm.update(score=35, is_drowsy=False, is_confused=False, timestamp=i/15)
print(f'After 20s at 35: {state}')  # DISTRACTED
"
```

### Acceptance Criteria

- 5 states: ENGAGED (70-100), PASSIVE (40-69), DISTRACTED (15-39), DROWSY (0-30 + drowsy signal), CONFUSED (any score + confused expression)
- Duration thresholds: ENGAGED (immediate), PASSIVE (30s), DISTRACTED (15s), DROWSY (10s), CONFUSED (20s)
- Hysteresis prevents transitions from brief fluctuations
- State history logged with timestamps (list of (state, start_time, end_time) tuples)
- Transition events emittable (callback function or event list)
- Score ranges and duration thresholds configurable
- At least 6 test cases: sustained high, sustained low, brief dip, gradual decline, drowsy override, confused override

### Branch

`feature/issue-17-state-machine`

### Depends on

Closes #16

---

## Issue #18: Implement temporal smoothing and anomaly filtering

**Labels:** `m4`, `cv`
**Milestone:** M4: Engagement Scoring Agent

### Why

Human behavior is noisy. A student scratches their nose, and for two frames their hand covers their face - the face detector returns None, and the engagement score drops to zero. They sneeze, and for one second their eyes close and mouth opens wide - drowsiness and yawn detection both fire. They glance at their phone to check the time (2 seconds), and the gaze classifier reports them as distracted.

None of these are real disengagement. They are normal human behavior that happens dozens of times per hour. Without temporal filtering, the engagement score looks like a seismograph during an earthquake - constantly spiking and dropping, making it useless for any downstream analysis.

The temporal filter applies a sliding window average over the last 2 seconds of scores, which smooths out single-frame anomalies while still detecting sustained changes within a reasonable response time. It is the difference between a useful signal and noise.

### What needs to be built

A temporal filter with configurable sliding window that smooths engagement scores and filters single-frame anomalies.

### Files to create or update

- `src/scoring/temporal_filter.py` - TemporalFilter class with sliding window

### How this affects overall development

The filtered score is what every downstream module actually uses. The raw score from #16 is too noisy for direct use. The state machine (#17) operates on filtered scores. The nudge agent (#20) responds to filtered states. Without this filter, the system produces constant false alerts.

### How to test locally

```bash
pytest tests/test_temporal_filter.py -v

# Anomaly filtering test
python -c "
from src.scoring.temporal_filter import TemporalFilter

tf = TemporalFilter(window_size=30)  # 2 seconds at 15 FPS

# Feed stable high scores
for _ in range(30):
    smoothed = tf.smooth(85.0)
print(f'Stable at 85: smoothed = {smoothed:.1f}')  # ~85

# Inject single anomaly
smoothed = tf.smooth(10.0)  # nose scratch, face occluded
print(f'After single anomaly: smoothed = {smoothed:.1f}')  # should still be ~82, not 10

# Sustained drop
for _ in range(45):  # 3 seconds of low scores
    smoothed = tf.smooth(25.0)
print(f'After 3s sustained drop: smoothed = {smoothed:.1f}')  # should be ~25-30
"
```

### Acceptance Criteria

- Sliding window of configurable size (default 30 frames = 2 seconds at 15 FPS)
- Single-frame anomalies (1-2 frames of zero score) do not drop the smoothed output by more than 5 points
- Sustained changes (15+ seconds) are fully reflected in smoothed output within 3 seconds
- Latency introduced is at most 1 second (half the window size)
- Handles empty window gracefully (returns raw score when buffer not yet full)
- Memory usage bounded (uses deque, not growing list)
- At least 4 test cases: stable input, single anomaly, sustained change, ramp up/down

### Branch

`feature/issue-18-temporal-filter`

### Depends on

Closes #16

---

## Issue #19: Per-student calibration system

**Labels:** `m4`, `cv`, `agent`
**Milestone:** M4: Engagement Scoring Agent

### Why

Not every face is the same. Students of East Asian descent typically have a lower resting EAR (Eye Aspect Ratio) than students of European descent due to differences in eyelid structure. A student wearing glasses has different landmark positions than one without. A student with a naturally flat affect shows less facial expressiveness than an animated person. Using the same thresholds for everyone is not just inaccurate - it is unfair.

The calibration system captures each student's personal baseline during a 30-second setup. It measures their resting EAR (so drowsiness detection uses a personalized threshold), their natural head pose (so gaze detection accounts for their webcam position), and their baseline expression distribution (so the system knows what "neutral" looks like for them).

This is also a UX feature. The 30-second calibration is the student's first interaction with the system. It should feel smooth, guided, and confidence-building. "Look at the screen naturally for 30 seconds" is simple and non-threatening.

### What needs to be built

A calibration module that captures personal baselines and adjusts detection thresholds per student.

### Files to create or update

- `src/scoring/calibration.py` - CalibrationManager class
- `src/api/routes/calibration.py` - Calibration API endpoint

### How this affects overall development

Calibration improves accuracy for every student, which means more accurate engagement scores, fewer false nudges, and more trustworthy analytics. Without it, students with naturally low EAR get flagged as drowsy when they are perfectly alert, and students with flat affect get scored as bored when they are focused.

### How to test locally

```bash
# Demo calibration
python -m src.scoring.calibration --demo
# Prompts: "Look at the screen naturally for 30 seconds"
# Shows live EAR, head pose, and expression during calibration
# After 30 seconds, prints calibrated thresholds:
# "Your baseline EAR: 0.27 (drowsiness threshold set to 0.21)"
# "Your baseline head pose: pitch -2, yaw 3 (gaze thresholds adjusted)"
# "Your baseline expression: 60% neutral, 30% engaged, 10% other"

# Threshold comparison test
python -c "
from src.scoring.calibration import CalibrationManager

# Student with naturally low EAR (e.g., East Asian)
cm = CalibrationManager()
cm.calibrate_ear(resting_ear=0.22)
print(f'Low EAR student - drowsiness threshold: {cm.ear_threshold:.3f}')  # should be ~0.17, not 0.25

# Student with naturally high EAR
cm2 = CalibrationManager()
cm2.calibrate_ear(resting_ear=0.35)
print(f'High EAR student - drowsiness threshold: {cm2.ear_threshold:.3f}')  # should be ~0.28
"
```

### Acceptance Criteria

- 30-second calibration captures: resting EAR (averaged over 450 frames), natural head pose (pitch, yaw, roll baselines), expression distribution
- EAR drowsiness threshold set to (resting_ear * 0.8) instead of fixed 0.25
- Gaze thresholds adjusted relative to natural head pose (if student's natural yaw is 5 degrees right, that becomes their center)
- Calibration data persisted per student in database
- Student can re-calibrate anytime
- Skippable with clear warning ("using default thresholds - may be less accurate for you")
- API endpoint: POST /api/calibrate/{user_id} starts calibration, GET /api/calibrate/{user_id} returns stored baselines
- Calibration completes in exactly 30 seconds (with progress indicator)

### Branch

`feature/issue-19-calibration`

### Depends on

Closes #12, Closes #16

---

## Issue #20: Build nudge decision agent

**Labels:** `m5`, `agent`, `nudge`
**Milestone:** M5: Nudge Agent and Delivery System

### Why

Knowing a student is distracted is only half the problem. The other half is deciding what to do about it. Nudge too early and you annoy a student who was about to re-engage on their own. Nudge too late and the student has already missed 10 minutes of material. Nudge too often and the student disables the system entirely.

The nudge decision agent is the first truly agentic component in EngageIQ. It does not follow a simple rule ("if distracted, nudge"). It considers multiple factors: How long has the student been distracted? When was the last nudge sent? Has the student responded well to nudges before? How many nudges have already been sent this session? What type of nudge worked best for this student?

This is where LangGraph enters the picture. The agent is implemented as a LangGraph state machine with nodes for: evaluating the current engagement state, checking nudge history, deciding whether to nudge, selecting the nudge type, and recording the decision for future learning.

### What needs to be built

A LangGraph-based nudge decision agent that evaluates when and how to nudge based on engagement state, nudge history, and effectiveness data.

### Files to create or update

- `src/nudge/nudge_decision.py` - Nudge decision logic
- `src/agents/nudge_agent.py` - LangGraph agent implementation

### How this affects overall development

This agent determines the student experience of EngageIQ. Too many nudges and students hate the system. Too few and it has no impact. The nudge effectiveness tracker (#22) feeds data back to this agent to improve its decisions over time. The preferences UI (#23) lets students override the agent's defaults.

### How to test locally

```bash
pytest tests/test_nudge_decision.py -v

# Scenario test
python -c "
from src.nudge.nudge_decision import NudgeDecisionEngine

engine = NudgeDecisionEngine(cooldown_seconds=300, max_nudges=5)

# Student just became distracted
decision = engine.should_nudge(
    current_state='distracted',
    state_duration=35,  # distracted for 35 seconds
    last_nudge_time=None,  # no nudges yet
    session_nudge_count=0,
    effectiveness_history=[]
)
print(f'First distraction: nudge={decision.should_nudge}, type={decision.nudge_type}')
# should_nudge=True

# Student distracted again, but nudged 2 minutes ago
decision = engine.should_nudge(
    current_state='distracted',
    state_duration=35,
    last_nudge_time=120,  # 2 minutes ago
    session_nudge_count=1,
    effectiveness_history=[{'type': 'notification', 'effective': True}]
)
print(f'After cooldown: nudge={decision.should_nudge}')
# should_nudge=False (cooldown not expired)

# Max nudges reached
decision = engine.should_nudge(
    current_state='distracted',
    state_duration=35,
    last_nudge_time=600,  # 10 minutes ago
    session_nudge_count=5,
    effectiveness_history=[]
)
print(f'Max reached: nudge={decision.should_nudge}')
# should_nudge=False
"
```

### Acceptance Criteria

- Nudge triggers only after configurable sustained disengagement (default: 30 seconds)
- Cooldown period between nudges: default 5 minutes, configurable
- Maximum nudges per session: default 5, configurable
- Agent considers past nudge effectiveness when selecting nudge type
- Returns NudgeDecision object with: should_nudge (bool), nudge_type (str), reason (str)
- LangGraph implementation with clear state graph (evaluate -> check_history -> decide -> record)
- At least 6 test cases: first nudge, cooldown active, cooldown expired, max reached, drowsy (faster trigger), effectiveness-based type selection

### Branch

`feature/issue-20-nudge-decision`

### Depends on

Closes #17

---

## Issue #21: Implement nudge delivery system

**Labels:** `m5`, `nudge`, `frontend`
**Milestone:** M5: Nudge Agent and Delivery System

### Why

A decision to nudge is useless without a way to deliver it. The delivery system must reach the student without being intrusive or disruptive. Three channels offer different levels of interruption: a browser notification (mild), a visual overlay (subtle), and an audio chime (assertive).

The visual overlay is the most nuanced. It cannot be a popup that blocks the lecture video. It should be a gentle glow on the screen edge that the student notices peripherally. Think of it as the digital equivalent of a teacher making eye contact with a distracted student - noticeable but not embarrassing.

The audio chime must be gentle enough that it does not startle the student or disturb their roommates, but noticeable enough to break the distraction loop. A soft bell or water drop sound, played once at low volume, is ideal.

### What needs to be built

Three nudge delivery channels with configurable messages and intensity.

### Files to create or update

- `src/nudge/nudge_delivery.py` - Multi-channel delivery system
- `frontend/src/components/NudgeOverlay.jsx` - Visual overlay component

### How this affects overall development

The delivery system is the user-facing output of the nudge pipeline. It directly affects student satisfaction with the system. If nudges are too intrusive, students disable the system. If they are too subtle, students do not notice them. The effectiveness tracker (#22) measures whether the delivery actually works.

### How to test locally

```bash
# Test each delivery channel
python -m src.nudge.nudge_delivery --type notification --message "Time to refocus!"
# Should show browser notification

python -m src.nudge.nudge_delivery --type overlay --message "You seem distracted"
# Should show gentle screen-edge glow via WebSocket to frontend

python -m src.nudge.nudge_delivery --type audio
# Should play gentle chime sound

# Test via API
curl -X POST http://localhost:8000/api/nudge/test \
  -H "Content-Type: application/json" \
  -d '{"type": "notification", "message": "Test nudge", "user_id": 1}'
```

### Acceptance Criteria

- Browser notification: shows with custom message, auto-dismisses after 5 seconds
- Visual overlay: subtle screen-edge glow (not a popup), fades in/out over 2 seconds, non-blocking
- Audio chime: gentle sound, under 2 seconds, low volume, plays once
- Each channel can be triggered independently
- Nudge type and timestamp logged to database (for effectiveness tracking)
- Student can disable any channel via API (preferences stored per user)
- Delivery is async (does not block the detection pipeline)

### Branch

`feature/issue-21-nudge-delivery`

### Depends on

Closes #20

---

## Issue #22: Add nudge effectiveness tracker

**Labels:** `m5`, `nudge`, `analytics`
**Milestone:** M5: Nudge Agent and Delivery System

### Why

Sending nudges without measuring their impact is like prescribing medicine without checking if the patient gets better. The effectiveness tracker closes the feedback loop: after every nudge, it measures whether the student's engagement actually improved.

This data transforms the nudge agent from a rule-based system into a learning system. If notification nudges improve engagement 60% of the time but audio nudges only work 30% of the time for a specific student, the agent should prefer notifications for that student. Over multiple sessions, the agent personalizes its nudge strategy per student.

Effectiveness data also provides valuable analytics for teachers. If nudges are consistently ineffective for a particular lecture topic, that suggests the content itself needs improvement - no amount of nudging will make a confusing explanation clear.

### What needs to be built

A tracker that measures engagement change after nudges, computes per-nudge-type effectiveness, and feeds results back to the decision agent.

### Files to create or update

- `src/nudge/effectiveness_tracker.py` - EffectivenessTracker class

### How this affects overall development

This is the learning component that makes the nudge system intelligent over time. Without it, the nudge agent uses the same strategy forever, even if it is not working. The effectiveness data also appears in session reports (#27) and weekly reports (#28) - teachers can see whether nudges are helping.

### How to test locally

```bash
pytest tests/test_effectiveness_tracker.py -v

python -c "
from src.nudge.effectiveness_tracker import EffectivenessTracker

tracker = EffectivenessTracker(measurement_window=60)

# Simulate nudge -> engagement improves
tracker.record_nudge(nudge_type='notification', timestamp=0, pre_score=35)
tracker.record_post_score(timestamp=30, score=55)
tracker.record_post_score(timestamp=60, score=65)
result = tracker.evaluate_last_nudge()
print(f'Notification: effective={result.effective}, delta={result.delta:+.1f}')
# effective=True, delta=+30.0

# Simulate nudge -> no improvement
tracker.record_nudge(nudge_type='audio', timestamp=120, pre_score=30)
tracker.record_post_score(timestamp=150, score=32)
tracker.record_post_score(timestamp=180, score=28)
result = tracker.evaluate_last_nudge()
print(f'Audio: effective={result.effective}, delta={result.delta:+.1f}')
# effective=False, delta=-2.0

# Check per-type stats
stats = tracker.get_stats()
print(f'Notification success rate: {stats[\"notification\"].success_rate:.0%}')
print(f'Audio success rate: {stats[\"audio\"].success_rate:.0%}')
"
```

### Acceptance Criteria

- Measures engagement score delta in 60-second post-nudge window
- Nudge is "effective" if average post-nudge score improves by 10+ points
- Tracks success rate per nudge type (notification, overlay, audio)
- Feeds effectiveness data to nudge decision agent via API or direct reference
- Persists effectiveness history per student across sessions in database
- Handles edge cases: nudge at end of session (incomplete window), multiple nudges in quick succession
- At least 4 test cases: effective nudge, ineffective nudge, per-type stats, cross-session persistence

### Branch

`feature/issue-22-nudge-effectiveness`

### Depends on

Closes #21

---

## Issue #23: Nudge preferences UI

**Labels:** `m5`, `nudge`, `frontend`
**Milestone:** M5: Nudge Agent and Delivery System

### Why

Nudging is only effective if the student is willing to receive nudges. A system that forces a specific nudge style on every student will be disabled by students who find it annoying. The preferences UI gives students control over their experience.

Quiet hours matter because Indian students study at all hours. A student reviewing lecture recordings at midnight does not want an audio chime waking up their roommates. Channel toggles matter because some students find browser notifications useful but screen overlays distracting (or vice versa). Sensitivity control matters because some students want frequent check-ins while others prefer to be left alone unless they are clearly struggling.

This is also a privacy and autonomy feature. Students should feel in control of the system, not surveilled by it. The preferences UI makes the system feel like a helpful tool rather than a monitoring device.

### What needs to be built

A student-facing preferences panel with channel toggles, quiet hours, and sensitivity control.

### Files to create or update

- `frontend/src/components/NudgePreferences.jsx` - Preferences panel component
- `src/api/routes/preferences.py` - Preferences API endpoints
- `src/api/schemas/preferences.py` - Pydantic schemas for preferences

### How this affects overall development

The nudge decision agent (#20) must respect these preferences. If a student disables audio nudges, the agent must never send one. If quiet hours are active, no audio nudges during that window. The preferences are stored per student and loaded at session start.

### How to test locally

```bash
# Start frontend and navigate to /student/settings/nudge
# Should show:
# - Toggle switches for: Notifications, Visual Overlay, Audio Chime
# - Quiet hours: Start time picker, End time picker
# - Sensitivity slider: Less / Normal / More

# Test via API
curl -X PUT http://localhost:8000/api/preferences/2 \
  -H "Content-Type: application/json" \
  -d '{"notification_enabled": true, "overlay_enabled": true, "audio_enabled": false, "quiet_hours_start": "22:00", "quiet_hours_end": "08:00", "sensitivity": "less"}'

# Verify preferences are respected
curl http://localhost:8000/api/preferences/2
# Should return saved preferences

# Verify nudge agent respects preferences
# Trigger a nudge during quiet hours -> should NOT send audio
# Disable overlay -> trigger nudge -> should NOT show overlay
```

### Acceptance Criteria

- Toggle each nudge channel independently (notification, overlay, audio)
- Quiet hours with start and end time (24-hour format)
- Sensitivity options: less (10-minute cooldown), normal (5-minute), more (3-minute)
- Preferences persist across sessions in database
- Changes take effect immediately (no restart needed)
- API validates input (quiet hours must be valid times, sensitivity must be one of three values)
- Default preferences: all channels enabled, no quiet hours, normal sensitivity
- Responsive design (works on phone)

### Branch

`feature/issue-23-nudge-preferences`

### Depends on

Closes #21

---

## Issue #24: Build class-level engagement aggregator

**Labels:** `m6`, `analytics`
**Milestone:** M6: Teacher Analytics and Insights

### Why

A teacher with 60 students cannot look at 60 individual engagement timelines. They need one view that shows the pulse of the entire class: is the class engaged right now? Did engagement drop during the recursion explanation? Are Monday morning lectures consistently worse than Wednesday afternoon?

The aggregator is also where individual privacy meets collective analytics. Each student's data is anonymized before aggregation. The teacher sees "65% of the class was engaged during minute 14" - not "Rahul scored 45 at minute 14." This is the architectural enforcement of the privacy principle.

Class-level engagement dip detection is especially valuable. When 40% of the class simultaneously loses engagement at minute 23, that is almost certainly a content problem, not a student problem. Flagging these moments gives teachers concrete, actionable feedback on their teaching.

### What needs to be built

An aggregation engine that computes class-wide engagement metrics from individual student data, with engagement dip detection.

### Files to create or update

- `src/analytics/class_aggregator.py` - ClassAggregator class

### How this affects overall development

This is the foundation of the teacher experience. The teacher dashboard (#33) displays these aggregated metrics. The intervention agent (#29) analyzes these aggregates to suggest teaching improvements. The weekly report (#28) summarizes weekly aggregation trends. If aggregation is wrong, the entire teacher-facing side of the system is wrong.

### How to test locally

```bash
pytest tests/test_class_aggregator.py -v

python -c "
from src.analytics.class_aggregator import ClassAggregator

agg = ClassAggregator()

# Simulate 10 students' scores at minute 14
scores = [80, 70, 90, 60, 85, 75, 65, 80, 70, 90]
stats = agg.aggregate(scores)
print(f'Class average: {stats.average:.1f}')     # 76.5
print(f'Class median: {stats.median:.1f}')        # 77.5
print(f'Std deviation: {stats.std_dev:.1f}')      # 9.7
print(f'Engaged (>70): {stats.engaged_pct:.0%}')  # 70%

# Detect engagement dip
timeline = {
    10: 78, 11: 80, 12: 75, 13: 72,
    14: 52,  # 33% drop!
    15: 48, 16: 55, 17: 60, 18: 70
}
dips = agg.detect_dips(timeline, threshold=0.15)
print(f'Dips detected at minutes: {[d.minute for d in dips]}')  # [14]
"
```

### Acceptance Criteria

- Computes: mean, median, standard deviation, min, max, engaged percentage (score > 70)
- Generates minute-by-minute engagement timeline for the class
- Detects engagement dips: moments where class average drops > 15% from session average
- All student IDs are anonymized in output (hashed or replaced with sequential IDs)
- Handles missing data: if a student disconnects mid-session, they are excluded from that minute's average
- Real-time capable: can process incoming scores via WebSocket and update aggregates live
- At least 4 test cases: normal class, class with dip, class with outlier, class with missing students

### Branch

`feature/issue-24-class-aggregator`

### Depends on

Closes #17

---

## Issue #25: Implement at-risk student identifier

**Labels:** `m6`, `analytics`
**Milestone:** M6: Teacher Analytics and Insights

### Why

A single low-engagement session can happen to anyone - a bad night's sleep, a personal issue, a topic that just did not click. But three consecutive low-engagement sessions is a pattern. It means the student is struggling in a sustained way that session-level nudges cannot fix. They need help from the teacher.

The at-risk identifier bridges the gap between automated nudges and human intervention. The system cannot tutor a struggling student or understand their personal challenges. But it can flag them early, before they have fallen so far behind that catching up is overwhelming.

Declining trend detection adds nuance. A student whose engagement drops from 80 to 70 to 60 over three weeks has not crossed the "at-risk" threshold yet, but they are heading there. Early detection of declining trends gives teachers time to intervene before it becomes a crisis.

### What needs to be built

A risk identification engine that flags students with consistently low or declining engagement across multiple sessions.

### Files to create or update

- `src/analytics/risk_identifier.py` - RiskIdentifier class
- `src/analytics/trend_analyzer.py` - TrendAnalyzer for rolling averages

### How this affects overall development

The teacher dashboard (#33) highlights at-risk students. The intervention agent (#29) uses this data to suggest broader interventions ("3 students have been consistently disengaged during recursion topics - consider adding more examples"). The weekly report (#28) includes an at-risk summary.

### How to test locally

```bash
pytest tests/test_risk_identifier.py -v

python -c "
from src.analytics.risk_identifier import RiskIdentifier

ri = RiskIdentifier(threshold=50, consecutive_sessions=3)

# At-risk: 3 sessions below threshold
result = ri.evaluate(student_id='anon_42', session_scores=[40, 35, 30])
print(f'Low 3 sessions: at_risk={result.at_risk}, reason={result.reason}')
# at_risk=True, reason='below_threshold_3_sessions'

# Not at-risk: inconsistent
result = ri.evaluate(student_id='anon_43', session_scores=[50, 80, 70])
print(f'Inconsistent: at_risk={result.at_risk}')
# at_risk=False

# Declining trend
result = ri.evaluate(student_id='anon_44', session_scores=[80, 75, 70, 65, 60])
print(f'Declining: declining_trend={result.declining_trend}')
# declining_trend=True (week-over-week drop > 10%)
"
```

### Acceptance Criteria

- Flags students with average engagement below threshold for 3+ consecutive sessions
- Threshold and consecutive session count configurable
- Detects declining trend: current week average < previous week average by > 10%
- Supports rolling 7-day and 30-day analysis windows
- At-risk list uses anonymized student IDs (teacher cannot identify students by default)
- Students can opt in to be identified to the teacher for targeted help
- At least 5 test cases: at-risk, not at-risk, declining, recovering, edge cases

### Branch

`feature/issue-25-risk-identifier`

### Depends on

Closes #24

---

## Issue #26: Export analytics as CSV/JSON

**Labels:** `m6`, `analytics`, `infra`
**Milestone:** M6: Teacher Analytics and Insights

### Why

Not every teacher uses EngageIQ's dashboard. Some prefer Excel for their own analysis. Some need to submit engagement data to their department for NAAC accreditation. Some want to load the data into Google Sheets or their institution's LMS. Raw data export makes this possible.

This is also about data ownership. The teacher's engagement data should not be locked inside EngageIQ. They should be able to extract it in standard formats and use it however they want. This builds trust in the system and reduces vendor lock-in concerns.

CSV is for spreadsheet users. JSON is for developers and LMS integrations. Both should support the same filters so the export is consistent regardless of format.

### What needs to be built

API endpoints and a dashboard button for exporting engagement data in CSV and JSON formats with filters.

### Files to create or update

- `src/api/routes/export.py` - Export API endpoints
- `frontend/src/components/ExportButton.jsx` - Export button component

### How this affects overall development

This is the data portability layer. It does not affect other modules directly, but it significantly increases the system's utility for teachers. It also enables external analysis and visualization that the EngageIQ dashboard may not support.

### How to test locally

```bash
# Export session data as CSV
curl "http://localhost:8000/api/export/sessions/1?format=csv" > session_1.csv
cat session_1.csv | head -5
# Should show: timestamp,anonymized_student_id,engagement_score,state

# Export as JSON
curl "http://localhost:8000/api/export/sessions/1?format=json" > session_1.json
python -c "import json; data = json.load(open('session_1.json')); print(f'Records: {len(data)}')"

# Export with date filter
curl "http://localhost:8000/api/export/courses/1?format=csv&start=2026-06-01&end=2026-06-08" > week.csv

# Large export test
curl "http://localhost:8000/api/export/courses/1?format=csv" --max-time 10
# Should complete within 10 seconds even for 1000+ rows
```

### Acceptance Criteria

- GET /api/export/sessions/{id}?format=csv returns CSV with headers
- GET /api/export/sessions/{id}?format=json returns JSON array
- Columns: timestamp, anonymized_student_id, engagement_score, state, gaze_state, drowsiness_level, expression
- Filter by: date range (start, end), course_id, anonymized_student_id
- Large exports (1000+ rows) stream via chunked response without timeout
- CSV is RFC 4180 compliant (proper quoting, escaping)
- Frontend export button triggers download with filename: engageiq_session_{id}_{date}.csv
- Student IDs are always anonymized in exports (even if teacher has opt-in access)

### Branch

`feature/issue-26-export-analytics`

### Depends on

Closes #24

---

## Issue #27: Build session engagement report

**Labels:** `m7`, `analytics`
**Milestone:** M7: Report Generator and Intervention Agent

### Why

After a lecture ends, both the teacher and students want a quick summary. The teacher wants to know: How engaged was the class? When did I lose them? What should I do differently next time? The student wants to know: How focused was I? When did I drift? How do I compare to the class average?

The session report turns raw engagement data into a narrative. Rather than showing a wall of numbers, it highlights the key moments: "Class engagement dropped 25% at minute 14 during the recursion explanation" and "Your top distraction period was minutes 22-28." These highlights are what make the data actionable.

This is also where the system proves its value. A teacher who sees a well-formatted report with clear insights after their first lecture will keep using the system. A teacher who sees a confusing data dump will not.

### What needs to be built

A report generator that produces per-session engagement summaries with timeline charts, key moments, and class comparison.

### Files to create or update

- `src/reports/session_report.py` - SessionReportGenerator class
- `src/templates/session_report.html` - Jinja2 HTML template

### How this affects overall development

Session reports are displayed in the student dashboard (#32) and teacher dashboard (#33). The weekly report (#28) aggregates multiple session reports. The email delivery system (#31) sends these reports automatically. The intervention agent (#29) analyzes session report data to generate suggestions.

### How to test locally

```bash
# Generate report for a session
python -m src.reports.session_report --session-id 1 --output report.html
open report.html

# Should display:
# - Session summary (date, duration, overall engagement score)
# - Engagement timeline chart (minute-by-minute line graph)
# - Top 3 distraction moments with timestamps
# - Class average comparison (if share_with_teacher enabled)
# - State distribution pie chart (% time in each state)
```

### Acceptance Criteria

- Report includes: session metadata, engagement timeline chart, state distribution, top distraction moments
- Highlights top 3 engagement dip moments with timestamps and duration
- Shows overall session score and class average comparison (anonymized)
- State distribution: percentage of time spent in each engagement state
- Renders as clean HTML viewable in any browser
- HTML is self-contained (inline CSS, inline chart via Chart.js CDN)
- Can be sent as email body or downloaded as file
- Generates in under 5 seconds for a 1-hour session

### Branch

`feature/issue-27-session-report`

### Depends on

Closes #24

---

## Issue #28: Build weekly trend report

**Labels:** `m7`, `analytics`
**Milestone:** M7: Report Generator and Intervention Agent

### Why

Session reports show what happened in one lecture. Weekly reports show patterns across lectures. "Monday 8am consistently has 20% lower engagement than Wednesday 2pm" is information a teacher cannot see from individual session reports but can see in a weekly trend.

Weekly reports are also how students track their own improvement. A student who sees their average engagement increase from 55 to 72 over four weeks has concrete proof that their focus strategies are working. This positive reinforcement encourages continued use of the system.

For institutional use, weekly reports provide the evidence that NEP 2020's outcome-based education requires. UGC and NAAC accreditation processes increasingly ask for learning analytics - weekly engagement trends are exactly that.

### What needs to be built

A weekly report generator with engagement curves, day/time patterns, and week-over-week comparison.

### Files to create or update

- `src/reports/weekly_report.py` - WeeklyReportGenerator class
- `src/templates/weekly_report.html` - Jinja2 HTML template

### How this affects overall development

The weekly report is the primary recurring output that keeps teachers engaged with the system. The email delivery system (#31) sends it every Monday. The teacher dashboard (#33) displays it in the analytics section.

### How to test locally

```bash
python -m src.reports.weekly_report --course-id 1 --week 2026-W24 --output weekly.html
open weekly.html

# Should display:
# - Week summary (number of sessions, overall average engagement)
# - Engagement curve per lecture (overlaid line chart)
# - Day-of-week pattern (bar chart: Mon-Fri average engagement)
# - Week-over-week delta (this week vs last week)
# - At-risk student count (anonymized)
# - Top 3 difficult segments across all lectures
```

### Acceptance Criteria

- Shows engagement trends across all lectures in the week
- Day-of-week pattern chart (which days have lowest/highest engagement)
- Time-of-day pattern (morning vs afternoon vs evening)
- Week-over-week comparison with delta indicators (up/down arrows, percentage change)
- At-risk student count (anonymized)
- Top difficult segments ranked across all lectures
- Exportable as HTML and PDF (via WeasyPrint)
- Generates in under 10 seconds for a week with 5 sessions and 60 students

### Branch

`feature/issue-28-weekly-report`

### Depends on

Closes #27

---

## Issue #29: Implement LLM-powered intervention agent

**Labels:** `m7`, `agent`
**Milestone:** M7: Report Generator and Intervention Agent

### Why

Data without recommendations is just numbers. A teacher who sees "engagement dropped 25% at minute 14" thinks "ok, what should I do about it?" The intervention agent answers that question by analyzing engagement patterns and generating specific, actionable teaching suggestions.

This is the most sophisticated agent in the system. It takes engagement data (dips, patterns, state distributions) and produces natural language advice: "Students lost focus during the recursion explanation at minute 14. Consider adding a live coding example to make the concept tangible. Your Q&A segments consistently have the highest engagement - try adding 2-minute discussion breaks every 15 minutes."

The key is specificity. "Make your lecture more engaging" is useless. "Add a coding exercise after slide 14 where students implement a recursive fibonacci function" is actionable. The LLM (Groq by default) provides the language generation capability, while the engagement data provides the grounding that prevents hallucination.

### What needs to be built

A LangGraph agent that analyzes engagement data and generates actionable teaching intervention suggestions.

### Files to create or update

- `src/agents/intervention_agent.py` - InterventionAgent class with LangGraph

### How this affects overall development

Intervention suggestions appear in the teacher dashboard (#33) and in the session report (#27). They are the primary value-add for teachers. Without good suggestions, the system is just a fancy chart viewer. With good suggestions, it is a teaching assistant.

### How to test locally

```bash
python -m src.agents.intervention_agent --session-id 1

# Should output 3+ specific suggestions, for example:
# 1. "Engagement dropped 25% at minute 14 (recursion topic). Consider replacing 
#     the slide-based explanation with a live coding walkthrough. Students show 
#     40% higher engagement during interactive segments."
# 2. "Students show signs of fatigue between minutes 35-45. Consider adding a 
#     2-minute stretch break at the 35-minute mark."
# 3. "Q&A segments consistently produce the highest engagement. Current Q&A is 
#     only at the end. Try adding 2-minute Q&A breaks every 15 minutes."

# Verify no generic advice
python -c "
from src.agents.intervention_agent import InterventionAgent

agent = InterventionAgent()
suggestions = agent.generate(session_id=1)
for s in suggestions:
    assert 'minute' in s.text or 'slide' in s.text or 'topic' in s.text, \
        f'Suggestion too generic: {s.text}'
    print(f'- {s.text}')
print(f'\nAll {len(suggestions)} suggestions are specific')
"
```

### Acceptance Criteria

- Generates 3+ actionable suggestions per session
- Every suggestion references specific data: timestamps, engagement percentages, patterns
- No generic advice: "make it more engaging", "be more interactive", "improve your teaching" are failures
- Uses Groq (free tier) by default, configurable to other LLM providers
- Prompt includes engagement data as structured context (not just "analyze this session")
- Suggestions are categorized: content (change material), delivery (change pace/style), structure (change schedule)
- Generates in under 10 seconds (single LLM call with structured output)
- Handles empty sessions gracefully ("Insufficient data - need at least 10 minutes of engagement data")

### Branch

`feature/issue-29-intervention-agent`

### Depends on

Closes #24, Closes #27

---

## Issue #30: Add content difficulty correlator

**Labels:** `m7`, `analytics`
**Milestone:** M7: Report Generator and Intervention Agent

### Why

When engagement dips at the same point in two different lectures on the same topic, that is a signal about the content, not the students. If "recursion" causes a 30% engagement drop in every section that covers it, the problem is with how recursion is being taught - not with the students in any particular section.

The difficulty correlator identifies these content-level patterns. It maps engagement dips to specific time segments within lectures and tracks whether the same segments are problematic across multiple sessions. This gives teachers evidence-based insight into which topics need pedagogical redesign.

This works even without access to slide content or lecture recordings. It uses timing only: "engagement consistently drops between minutes 12-18 in lectures for CS201." The teacher knows what they teach at minute 12 - they do not need the system to tell them.

### What needs to be built

An analytics module that maps engagement dips to lecture segments and tracks cross-session patterns.

### Files to create or update

- `src/analytics/difficulty_correlator.py` - DifficultyCorrelator class

### How this affects overall development

The difficulty correlator provides data to the intervention agent (#29) for more specific suggestions. It also appears in the weekly report (#28) as a "consistently difficult topics" section. Over time, it builds a map of content difficulty across the entire course.

### How to test locally

```bash
pytest tests/test_difficulty_correlator.py -v

python -c "
from src.analytics.difficulty_correlator import DifficultyCorrelator

dc = DifficultyCorrelator()

# Session 1: dip at minute 14
dc.add_session(session_id=1, timeline={10: 78, 11: 80, 12: 75, 13: 72, 14: 52, 15: 48, 16: 55, 17: 60, 18: 70, 19: 75})

# Session 2 (different section, same course): dip at minute 14 again
dc.add_session(session_id=2, timeline={10: 82, 11: 79, 12: 77, 13: 70, 14: 48, 15: 45, 16: 50, 17: 58, 18: 72, 19: 78})

# Find consistently difficult segments
difficult = dc.find_difficult_segments(min_sessions=2)
for seg in difficult:
    print(f'Minute {seg.minute}: avg drop {seg.avg_drop:.0f}%, occurred in {seg.session_count} sessions')
# Minute 14: avg drop 30%, occurred in 2 sessions
"
```

### Acceptance Criteria

- Identifies segments where engagement drops > 15% from session average
- Tracks per-segment difficulty across multiple sessions for the same course
- Ranks segments by severity: frequency x magnitude of drop
- Outputs: minute, average drop percentage, number of sessions affected
- Works with timing data only (no slide content or recording needed)
- Handles varying lecture lengths (normalizes to percentage of lecture rather than absolute minutes for comparison)
- At least 3 test cases: single session dip, cross-session pattern, no difficult segments

### Branch

`feature/issue-30-difficulty-correlator`

### Depends on

Closes #24

---

## Issue #31: Email delivery integration for automated reports

**Labels:** `m7`, `infra`
**Milestone:** M7: Report Generator and Intervention Agent

### Why

Teachers are busy. Asking them to log into a dashboard after every lecture to check engagement data will work for the first week and then stop. Automated email delivery puts the data in front of them without any effort on their part.

The session report email is sent within 5 minutes of a lecture ending - while the teaching experience is still fresh in the teacher's mind. The weekly report is sent Monday morning - in time to adjust the week's teaching plan. This timing is deliberate: reports are most useful when they arrive at the moment the teacher can act on them.

Email rendering is its own challenge. HTML emails look different in Gmail, Outlook, Apple Mail, and mobile clients. The templates must use table-based layouts (not flexbox/grid) and inline styles (not CSS classes) because email clients strip external stylesheets. This is a real-world constraint that every web developer encounters.

### What needs to be built

Email delivery integration using SendGrid (or Resend) for automated session and weekly report distribution.

### Files to create or update

- `src/reports/email_sender.py` - EmailSender class
- `src/templates/email_session.html` - Session report email template
- `src/templates/email_weekly.html` - Weekly report email template

### How this affects overall development

This is the delivery mechanism for reports from #27 and #28. Without email delivery, teachers must manually check the dashboard. Automated delivery is what makes the system "set and forget" for teachers - they get insights without effort.

### How to test locally

```bash
# Send test session report email
python -m src.reports.email_sender --to test@nst.edu --report session --session-id 1
# Check inbox for formatted session report

# Send test weekly report email
python -m src.reports.email_sender --to test@nst.edu --report weekly --course-id 1 --week 2026-W24

# Verify HTML renders correctly
python -c "
from src.reports.email_sender import EmailSender
sender = EmailSender()

# Without SendGrid key, should log warning and save HTML to file instead
sender.send_session_report(session_id=1, to='test@nst.edu')
# Output: 'SendGrid not configured. Report saved to reports_output/session_1.html'
"
```

### Acceptance Criteria

- Sends session report email within 5 minutes of session end (configurable)
- Sends weekly report email every Monday at 8am (configurable via cron-like schedule)
- HTML email renders correctly in Gmail, Outlook, and mobile (table-based layout, inline styles)
- Teacher can opt out of email reports via preferences
- Falls back gracefully when SendGrid API key is not configured: saves HTML to file, logs warning, does not crash
- SendGrid/Resend provider configurable in .env
- Email subject includes course name and date: "EngageIQ: CS201 Session Report - June 8, 2026"
- Rate limiting: max 10 emails per minute to avoid SendGrid throttling

### Branch

`feature/issue-31-email-delivery`

### Depends on

Closes #27, Closes #28

---

## Issue #32: Build student dashboard

**Labels:** `m8`, `frontend`
**Milestone:** M8: Dashboard, Integration and Demo

### Why

The student dashboard is where everything comes together for the student. It is the answer to "Is this system actually helping me?" If a student can see their engagement improving week over week, they stay motivated. If they can see which lectures they struggled in and get tips for improvement, they adjust their behavior.

The focus streak feature gamifies engagement. "You have been focused for 5 consecutive sessions" is a simple but powerful motivator. It taps into the same psychology as streak counters in Duolingo or GitHub contribution graphs - people do not want to break their streak.

Self-improvement tips are personalized based on the student's data. If a student consistently loses focus after 25 minutes, the tip is "Try the Pomodoro technique - focus for 25 minutes, then take a 5-minute break." If they are most distracted during morning lectures, the tip is "Your engagement is 30% higher in afternoon sessions - consider scheduling study time accordingly."

### What needs to be built

A React dashboard with engagement history, focus streaks, session comparison, and personalized tips.

### Files to create or update

- `frontend/src/pages/StudentDashboard.jsx` - Main dashboard page
- `frontend/src/components/EngagementChart.jsx` - Interactive engagement chart
- `frontend/src/components/FocusStreak.jsx` - Focus streak counter
- `frontend/src/components/SessionHistory.jsx` - Session list with scores
- `frontend/src/components/ImprovementTips.jsx` - Personalized tips panel

### How this affects overall development

This is the primary student-facing interface. All the detection, scoring, nudging, and analytics work from M1-M7 culminates in this dashboard. If the dashboard is clunky or confusing, all that backend work is wasted. The mobile-responsive version (#34) extends this to phone screens.

### How to test locally

```bash
cd frontend
npm install
npm run dev
# Navigate to http://localhost:5173/student/dashboard

# Should display:
# - Engagement chart: last 7 sessions, interactive (hover for details)
# - Focus streak: "5 sessions" with flame icon
# - Session history: list of recent sessions with date, duration, score
# - Improvement tips: 2-3 personalized suggestions based on data
# - Current session (if active): live engagement score

# Test with seed data
# Login as student from seed data
# Dashboard should populate with sample session data
```

### Acceptance Criteria

- Engagement chart shows last 7 sessions with scores (Recharts line chart)
- Chart is interactive: hover shows exact score and date
- Focus streak counter: increments for consecutive sessions with avg engagement > 70
- Session history: scrollable list with date, course name, duration, overall score, state distribution
- Improvement tips: at least 2 personalized tips based on student data patterns
- Loading states: skeleton loaders while data fetches
- Empty state: clear message when no session data exists yet ("Complete your first session to see your engagement data")
- Responsive: usable on both laptop (1024px+) and tablet (768px) screens
- Fetches data from backend API (not hardcoded)

### Branch

`feature/issue-32-student-dashboard`

### Depends on

Closes #27

---

## Issue #33: Build teacher dashboard

**Labels:** `m8`, `frontend`
**Milestone:** M8: Dashboard, Integration and Demo

### Why

The teacher dashboard is where every analytics feature meets its audience. A teacher who can see their class's real-time engagement, review session reports, identify struggling students, and read AI-generated teaching suggestions - all in one place - has a powerful tool for improving their teaching.

Real-time engagement during a live lecture is the most compelling feature. The teacher glances at a side monitor (or their phone) and sees a live class engagement graph updating every few seconds. If engagement suddenly drops, they can adjust on the fly - crack a joke, ask a question, start a discussion. This immediate feedback loop is something no LMS provides.

The intervention panel is where EngageIQ's agentic capabilities are most visible. The teacher finishes a lecture, opens the dashboard, and sees: "Engagement dropped 25% during the recursion explanation at minute 14. Here are 3 specific suggestions to improve next time." This is not a chart. This is an AI teaching assistant.

### What needs to be built

A React dashboard with class overview, live engagement monitoring (WebSocket), historical analytics, and intervention suggestions.

### Files to create or update

- `frontend/src/pages/TeacherDashboard.jsx` - Main dashboard page
- `frontend/src/components/ClassOverview.jsx` - Class engagement summary
- `frontend/src/components/LiveEngagement.jsx` - Real-time engagement graph
- `frontend/src/components/InterventionPanel.jsx` - AI suggestions panel
- `frontend/src/components/AtRiskPanel.jsx` - At-risk student list

### How this affects overall development

This is the most complex frontend component. It combines real-time WebSocket data (#5), aggregated analytics (#24), at-risk identification (#25), session reports (#27), and intervention suggestions (#29) into a single coherent interface. It is the integration test for the entire backend.

### How to test locally

```bash
cd frontend
npm install
npm run dev
# Navigate to http://localhost:5173/teacher/dashboard

# Should display:
# - Class overview: course selector, total students, average engagement
# - Live engagement (if session active): real-time line graph updating via WebSocket
# - Session history: list of past sessions with engagement summaries
# - Intervention panel: AI-generated suggestions for selected session
# - At-risk panel: list of students with declining engagement (anonymized)

# Test real-time updates
# Start a mock session with 3 simulated students
python scripts/simulate_session.py --students 3 --duration 60
# Teacher dashboard should show live engagement graph updating every 2 seconds
```

### Acceptance Criteria

- Class overview: course selector dropdown, total enrolled students, current/last session average engagement
- Live engagement: real-time line graph via WebSocket, updates every 2 seconds, shows class average
- Session history: selectable list, clicking a session shows its report
- Intervention panel: displays 3+ suggestions from intervention agent for selected session
- At-risk panel: shows anonymized students with low/declining engagement, trend arrows
- WebSocket connection handles disconnects gracefully (reconnects automatically)
- Loading states and empty states for all panels
- Responsive: usable on laptop (1024px+) and tablet (768px)

### Branch

`feature/issue-33-teacher-dashboard`

### Depends on

Closes #25, Closes #29, Closes #32

---

## Issue #34: Mobile-responsive dashboard + PWA setup

**Labels:** `m8`, `frontend`
**Milestone:** M8: Dashboard, Integration and Demo

### Why

Indian college students use their phones for everything. If the student dashboard only works on a laptop, you lose the students who want to check their engagement stats on the bus, between classes, or in the canteen. A phone-accessible dashboard means students interact with their data more frequently, which means they care about it more.

The PWA (Progressive Web App) setup lets students "install" EngageIQ on their phone's home screen without going through an app store. They tap "Add to Home Screen" in Chrome, and it appears as an app icon. It opens full-screen, loads fast (service worker caching), and feels native. This is significantly easier than building a separate Android/iOS app and achieves 90% of the same experience.

Mobile-responsive design is not just shrinking the desktop layout. Charts need different aspect ratios. Navigation becomes a hamburger menu. Touch targets must be 44px minimum. Tables become card lists. The entire information hierarchy changes on a small screen.

### What needs to be built

Make both dashboards fully responsive for mobile screens. Add PWA manifest and service worker for home screen installation.

### Files to create or update

- `frontend/public/manifest.json` - PWA manifest
- `frontend/public/service-worker.js` - Service worker for offline caching
- `frontend/public/icons/` - App icons (192x192, 512x512)
- Update all dashboard components with responsive Tailwind classes

### How this affects overall development

This extends the reach of the system from laptop-only to any device with a browser. The PWA features (offline caching, home screen icon) make the system feel professional and permanent rather than a web page students have to remember to bookmark.

### How to test locally

```bash
cd frontend
npm run dev

# Test responsive layout
# Open Chrome DevTools -> Toggle device toolbar
# Test at: 375px (iPhone SE), 390px (iPhone 14), 414px (iPhone Plus), 768px (iPad)

# Verify for each breakpoint:
# - Navigation is a hamburger menu (not full sidebar)
# - Charts resize and remain readable
# - All buttons/links are at least 44px touch targets
# - No horizontal scrolling
# - Text is readable without zooming

# Test PWA
npm run build
npx serve dist/

# On Android Chrome:
# - Visit the URL
# - Should see "Add to Home Screen" banner
# - After adding, app opens full-screen with EngageIQ icon
```

### Acceptance Criteria

- Dashboard fully usable on 375px-width screens (no horizontal scroll, no overlapping elements)
- Navigation: hamburger menu on mobile, sidebar on desktop
- Charts: responsive aspect ratio, readable labels, touch-friendly tooltips
- Cards: single column on mobile, grid on desktop
- All interactive elements have minimum 44px touch targets
- PWA manifest: app name, icons (192x192, 512x512), theme color, start URL
- Service worker caches static assets for fast loading
- "Add to Home Screen" prompt appears on Android Chrome
- Lighthouse PWA audit score > 80

### Branch

`feature/issue-34-mobile-pwa`

### Depends on

Closes #32, Closes #33

---

## Issue #35: E2E testing, demo video, deployment guide

**Labels:** `m8`, `infra`
**Milestone:** M8: Dashboard, Integration and Demo

### Why

A project that only runs on your laptop is not a product - it is a demo. Deployment means EngageIQ runs on a real server, accessible via a public URL, without anyone needing to install Python or run terminal commands. This is the difference between something you show in a screen recording and something you can hand someone a link to.

End-to-end testing proves the system works as a whole, not just in isolated units. A bug that only appears when the detection pipeline feeds into the scorer which feeds into the nudge agent which feeds into the dashboard - that bug does not show up in unit tests. E2E testing catches it.

The demo video is the portfolio artifact. It is what goes on LinkedIn, what you share with recruiters, and what faculty uses to evaluate the project. A 3-5 minute video showing the complete flow - student joins, engagement tracked in real-time, nudge delivered, teacher sees analytics - tells the story of EngageIQ better than any README.

This is the final issue. When this is merged to main, EngageIQ is live.

### What needs to be built

E2E tests using pre-recorded webcam sessions, deployment to Railway or Render, and a demo video showing the complete system.

### Files to create or update

- `tests/test_e2e.py` - End-to-end test suite
- `docs/deployment_guide.md` - Deployment steps, environment variables, live URL
- `docs/architecture.md` - System architecture diagram and module descriptions
- `docs/demo_script.md` - Demo video script and talking points

### How this affects overall development

This is the capstone. Every issue from 1 to 34 contributed a piece. This issue assembles them into a running system that anyone can access. The demo video is what goes on LinkedIn. The live URL is what you share with recruiters. The architecture doc is what you reference in interviews when someone asks "walk me through how EngageIQ works."

### How to test locally

```bash
# Run E2E test with pre-recorded webcam session
pytest tests/test_e2e.py -v
# Should process a 10-minute recorded session through:
# frame extraction -> face detection -> drowsiness/expression -> 
# engagement scoring -> state machine -> nudge decision -> 
# analytics aggregation -> report generation

# Build and run with Docker
docker-compose up --build
curl http://localhost:8000/health           # API health check
curl http://localhost:8000/docs             # API documentation
open http://localhost:5173                  # Frontend dashboard

# Deploy to Railway
npm install -g @railway/cli
railway login
railway init
railway up

# Set environment variables on Railway dashboard
# Verify live deployment
curl https://your-app.up.railway.app/health
open https://your-app.up.railway.app

# Smoke test against live URL
python -c "
import httpx
base = 'https://your-app.up.railway.app'
r = httpx.get(f'{base}/health')
print(f'Health: {r.status_code}')  # 200
r = httpx.get(f'{base}/docs')
print(f'Docs: {r.status_code}')    # 200
"
```

### Acceptance Criteria

- E2E test processes a 10-minute pre-recorded session through the full pipeline without errors
- `docker-compose up --build` starts API, frontend, and PostgreSQL without errors
- All environment variables from .env.example correctly passed to containers
- Application deployed to Railway or Render with a live public URL
- Live URL accessible without VPN, local setup, or any installation
- Frontend loads correctly on the live URL
- WebSocket connection works on the live URL (real-time engagement updates)
- `docs/deployment_guide.md` documents: live URL, how to redeploy, environment variables needed
- `docs/architecture.md` includes: system diagram showing all modules and data flow, tech stack table
- Demo video recorded (3-5 minutes): student onboarding, calibration, live engagement tracking, nudge delivery, teacher dashboard with analytics and intervention suggestions
- All existing tests pass

### Branch

`feature/issue-35-deployment`

### Depends on

Closes #32, Closes #33, Closes #34

---

**REMINDER (BOLD): Update HireFlow AI project with the same pod restructuring - all contributors work on every issue, competitive/collaborative PRs, maintainer only merges.**

---

NST Engineering - EngageIQ AI | Summer Profile Building Drive 2026
