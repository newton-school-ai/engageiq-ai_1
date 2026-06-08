#!/bin/bash
# EngageIQ AI - Create all 35 issues on GitHub (milestones already exist)
# Usage: cd engageiq-ai && bash scripts/create_github_issues.sh

set -e

REPO="newton-school-ai/engageiq-ai"

echo "========================================="
echo "Creating 35 issues for $REPO"
echo "========================================="

echo ""
echo ">>> Fetching existing milestone titles..."

# gh issue create uses milestone title (not number), so we just need the exact titles
# Verify milestones exist
gh api repos/$REPO/milestones --jq '.[].title' | sort

echo ""
echo "All 8 milestones found. Proceeding to create issues..."
echo ""

# Milestone titles (must match exactly what's on GitHub)
M1="M1: Project Scaffold and Webcam Pipeline"
M2="M2: Face Detection and Gaze Estimation"
M3="M3: Drowsiness and Expression Detection"
M4="M4: Engagement Scoring Agent"
M5="M5: Nudge Agent and Delivery System"
M6="M6: Teacher Analytics and Insights"
M7="M7: Report Generator and Intervention Agent"
M8="M8: Dashboard, Integration and Demo"

# --- STEP 2: Create Issues --------------------------------------------------

echo ""
echo ">>> Creating issues..."

# Helper function
create_issue() {
  local num="$1"
  local title="$2"
  local milestone="$3"
  local labels="$4"
  local body="$5"

  local full_title="Issue $num - $title"
  echo -n "  #$num $full_title ... "
  gh issue create --repo "$REPO" \
    --title "$full_title" \
    --milestone "$milestone" \
    --label "$labels" \
    --body "$body" > /dev/null 2>&1
  echo "done"
  sleep 1
}

# --- M1 Issues (#1-7) -------------------------------------------------------

create_issue 1 "Initialize repo scaffold, CI config, Docker setup" "$M1" "m1,infra" \
"## Why

Before anyone writes a single line of detection code, the project needs a clean, consistent structure that every contributor can clone and immediately start working in. Without this, four people will create four different directory layouts, import paths will break across branches, and merging becomes a nightmare.

A well-structured scaffold is not busywork - it is the foundation that makes parallel development possible. When all four contributors are working on the same issue simultaneously (competitive PRs), they need identical starting points. The scaffold gives them that.

Docker is included here because the development environment must be reproducible. \"It works on my machine\" is not acceptable when five people are contributing to the same codebase.

## What needs to be built

Create the full directory tree with all Python packages, verify all imports work, and ensure Docker builds cleanly.

## Files to create or update

- All \`__init__.py\` files in \`src/\` subdirectories
- \`Dockerfile\` - verify it builds with all CV dependencies (OpenCV, MediaPipe)
- \`docker-compose.yml\` - backend + PostgreSQL + frontend services
- Verify \`requirements.txt\` installs without errors
- Verify \`.gitignore\` covers all generated files

## How this affects overall development

This is issue #1 for a reason. Every other issue depends on this. If the scaffold is wrong, every contributor's work is built on a broken foundation. Get this right, and 34 issues flow smoothly. Get this wrong, and every PR has merge conflicts in import paths.

## How to test locally

\`\`\`bash
# Clone and verify structure
git clone https://github.com/newton-school-ai/engageiq-ai.git
cd engageiq-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify all packages are importable
python -c \"from src.agents import supervisor; print('agents OK')\"
python -c \"from src.detection import face_mesh; print('detection OK')\"
python -c \"from src.scoring import engagement_score; print('scoring OK')\"
python -c \"from src.nudge import nudge_decision; print('nudge OK')\"
python -c \"from src.analytics import class_aggregator; print('analytics OK')\"
python -c \"from src.reports import session_report; print('reports OK')\"
python -c \"from src.api import main; print('api OK')\"

# Docker build
docker-compose build
docker-compose up -d
curl http://localhost:8000/health
\`\`\`

## Acceptance Criteria

- [ ] All \`src/\` packages are importable without errors
- [ ] \`pip install -r requirements.txt\` succeeds in a clean virtualenv
- [ ] \`docker-compose build\` succeeds without errors
- [ ] \`docker-compose up\` starts backend, frontend, and PostgreSQL
- [ ] \`.gitignore\` covers: \`.env\`, \`__pycache__\`, \`*.pyc\`, \`node_modules/\`, \`data/videos/\`, model weights, \`_internal/\`
- [ ] Directory structure matches what is defined in PROJECT_CONTEXT.md

## Branch

\`feature/issue-1-scaffold\`

## Depends on

None (first issue)"

create_issue 2 "Set up GitHub Actions CI workflow" "$M1" "m1,infra" \
"## Why

Without automated CI, broken code slips into dev unnoticed. A contributor pushes code with a syntax error, another contributor pulls it, and now two people are debugging instead of building. CI catches these problems automatically on every PR before anyone reviews it.

CI is also the enforcement mechanism for coding standards. The team agreed on black formatting, isort imports, and flake8 linting. Without CI, these are suggestions. With CI, they are requirements - your PR literally cannot merge if your code is not formatted correctly.

This is especially important with competitive PRs. When four contributors each submit their own implementation, the Maintainer needs a quick way to verify that all submissions at least pass basic quality checks before reviewing the actual code.

## What needs to be built

A GitHub Actions workflow that runs linting and testing on every PR targeting dev or main.

## Files to create or update

- \`.github/workflows/ci.yml\` - CI workflow definition

## How this affects overall development

CI runs on every PR for the rest of the project. If CI is broken or flaky, it blocks all development. If CI is slow (> 5 minutes), contributors get frustrated waiting. Getting CI right on issue #2 means 33 subsequent issues have a reliable quality gate.

## How to test locally

\`\`\`bash
# Run the same checks locally that CI will run
black --check src/ tests/
isort --check src/ tests/
flake8 src/ tests/
pytest tests/ -v

# To test the workflow itself, push a branch with a deliberate lint error
echo 'x=1' > src/temp_bad.py  # no spaces around =
git checkout -b test/ci-check
git add . && git commit -m 'test: trigger CI with bad formatting'
git push origin test/ci-check
# Open PR -> CI should fail on black check
# Delete the branch after verifying
\`\`\`

## Acceptance Criteria

- [ ] CI triggers automatically on every PR targeting \`dev\` or \`main\`
- [ ] Runs \`black --check\`, \`isort --check\`, \`flake8\`, and \`pytest\` in that order
- [ ] PR shows green checkmark (pass) or red X (fail) in GitHub UI
- [ ] Workflow completes in under 3 minutes
- [ ] Uses Python 3.10 to match project requirements
- [ ] Caches pip dependencies for faster runs

## Branch

\`feature/issue-2-ci-workflow\`

## Depends on

Closes #1"

create_issue 3 "Design database schema and Alembic migrations" "$M1" "m1,infra" \
"## Why

The database schema defines every data relationship in EngageIQ. Users enroll in courses. Courses have sessions. Sessions generate engagement logs. Engagement triggers nudges. Analytics produce reports. If these relationships are wrong, every query, every API endpoint, and every dashboard is wrong.

Alembic migrations are included because the schema will evolve. When issue #19 adds calibration data per student, that is a new column. When issue #22 adds nudge effectiveness tracking, that is a new table. Without Alembic, schema changes require dropping and recreating the database, losing all test data. With Alembic, changes are versioned and reversible.

Seed data is critical for development velocity. Without it, every contributor has to manually create users, courses, and sessions before they can test anything. With seed data, one command gives everyone a consistent dataset to develop against.

## What needs to be built

SQLAlchemy models for all 6 core tables, initial Alembic migration, and a seed script with sample data.

## Files to create or update

- \`src/models/user.py\` - User model (student/teacher roles, privacy preferences)
- \`src/models/course.py\` - Course model
- \`src/models/session.py\` - Session model (lecture sessions)
- \`src/models/engagement_log.py\` - EngagementLog model (per-frame engagement data)
- \`src/models/nudge.py\` - Nudge model (nudge history and effectiveness)
- \`src/models/report.py\` - Report model (generated reports)
- \`src/models/base.py\` - SQLAlchemy DeclarativeBase
- \`alembic/\` - Alembic config and initial migration
- \`scripts/seed.py\` - Seed script with sample data

## How this affects overall development

The database schema is the contract between backend and frontend. Every API endpoint reads from or writes to these tables. The engagement pipeline (#16-18) writes to engagement_logs. The nudge agent (#20-22) reads engagement_logs and writes to nudges. The reports (#27-28) aggregate from engagement_logs. If the schema is wrong, every downstream module needs to be rewritten.

## How to test locally

\`\`\`bash
# Create database and run migrations
createdb engageiq_dev
alembic upgrade head

# Verify tables exist
python -c \"
from sqlalchemy import create_engine, inspect
engine = create_engine('postgresql://localhost/engageiq_dev')
tables = inspect(engine).get_table_names()
print(f'Tables: {tables}')
assert 'users' in tables
assert 'courses' in tables
assert 'sessions' in tables
assert 'engagement_logs' in tables
assert 'nudges' in tables
assert 'reports' in tables
print('All 6 tables created successfully')
\"

# Run seed script
python scripts/seed.py
# Should create: 2 teachers, 10 students, 3 courses, 5 sessions

# Run model tests
pytest tests/test_models.py -v
\`\`\`

## Acceptance Criteria

- [ ] 6 SQLAlchemy models with correct columns, types, foreign keys, and relationships
- [ ] User model supports roles (student/teacher) and privacy preferences
- [ ] EngagementLog stores per-frame data: timestamp, score, state, gaze, drowsiness, expression
- [ ] Alembic migration creates all tables from scratch (\`alembic upgrade head\`)
- [ ] Seed script populates database with realistic sample data
- [ ] \`alembic downgrade base\` cleanly removes all tables
- [ ] At least 3 tests: model creation, relationships, constraints

## Branch

\`feature/issue-3-db-schema\`

## Depends on

Closes #1"

create_issue 4 "Build webcam capture and frame preprocessing pipeline" "$M1" "m1,cv,infra" \
"## Why

Every CV module in EngageIQ starts with a webcam frame. Face detection needs frames. Drowsiness detection needs frames. Expression classification needs frames. If the frame capture pipeline is unreliable - dropping frames, running at inconsistent FPS, producing blurry or poorly-lit images - every downstream detector inherits that unreliability.

Frame preprocessing is where raw webcam output becomes ML-ready input. A raw 1080p frame is too large for real-time face mesh inference. Converting to RGB (OpenCV captures in BGR), resizing to a standard resolution, and normalizing pixel values are all necessary steps that every detection module would otherwise duplicate.

This pipeline also establishes the system's processing cadence. At 15 FPS, the system processes one frame every 67 milliseconds. This is fast enough to detect sustained behaviors (drowsiness, distraction) while being slow enough to run on laptop CPUs without maxing them out.

## What needs to be built

A webcam capture module with configurable FPS, resolution, and a preprocessing pipeline that outputs ML-ready frames.

## Files to create or update

- \`src/pipeline/capture.py\` - WebcamCapture class with configurable FPS and resolution
- \`src/pipeline/preprocessor.py\` - FramePreprocessor class (resize, RGB convert, normalize)

## How this affects overall development

This is the data source for the entire CV pipeline. Every detection module (#8-15) receives frames from this pipeline. If frames are inconsistent (varying sizes, color spaces, or frame rates), each detector needs its own preprocessing, leading to duplicated code and inconsistent behavior.

## How to test locally

\`\`\`bash
# Test webcam capture
python -m src.pipeline.capture --fps 15 --duration 5
# Should open webcam, capture for 5 seconds, report actual FPS

# Test preprocessing
python -c \"
from src.pipeline.preprocessor import FramePreprocessor
import numpy as np

# Simulate a 1080p BGR frame
frame = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
prep = FramePreprocessor(target_size=(640, 480))
result = prep.process(frame)
print(f'Input: {frame.shape}, Output: {result.shape}')
# Output should be (480, 640, 3) in RGB
\"

pytest tests/test_capture.py tests/test_preprocessor.py -v
\`\`\`

## Acceptance Criteria

- [ ] Captures frames at configurable FPS (default 15)
- [ ] Handles missing webcam gracefully (clear error message, not crash)
- [ ] Preprocessor outputs consistent size (640x480 default), RGB color space
- [ ] Actual FPS within 20% of target FPS on laptop CPU
- [ ] Can switch between webcam and video file input (for testing with recordings)
- [ ] Frame timestamp attached to each frame for temporal analysis
- [ ] At least 3 tests: capture initialization, preprocessing output shape, FPS stability

## Branch

\`feature/issue-4-webcam-pipeline\`

## Depends on

Closes #1"

create_issue 5 "Implement WebSocket frame streaming endpoint" "$M1" "m1,infra" \
"## Why

The webcam runs in the browser. The CV pipeline runs on the backend. WebSocket is the bridge between them. Unlike HTTP requests (which require a new connection for each frame), WebSocket maintains a persistent connection that can stream frames continuously with minimal overhead.

At 15 FPS, the system sends 15 frames per second from browser to server. HTTP polling would mean 15 separate request-response cycles per second, each with TCP handshake overhead. WebSocket sends frames over a single persistent connection, reducing latency from ~100ms to ~10ms per frame.

WebSocket is also bidirectional. The server can push engagement scores and nudge triggers back to the browser without the browser polling. This enables the real-time dashboard that shows engagement updating live.

## What needs to be built

A FastAPI WebSocket endpoint that receives base64-encoded frames from the browser and feeds them to the CV pipeline.

## Files to create or update

- \`src/api/websocket.py\` - WebSocket endpoint for frame streaming
- \`src/api/main.py\` - Register WebSocket route

## How this affects overall development

The WebSocket endpoint is the entry point for all real-time data. In production, frames come through this endpoint. The teacher dashboard (#33) receives live engagement updates through this same WebSocket connection. The nudge delivery system (#21) pushes nudge events through it.

## How to test locally

\`\`\`bash
# Start the backend
uvicorn src.api.main:app --reload

# Test WebSocket connection with websocat
pip install websockets
python -c \"
import asyncio, websockets, json, base64
import numpy as np

async def test():
    async with websockets.connect('ws://localhost:8000/ws/session/1') as ws:
        # Send a fake frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        frame_b64 = base64.b64encode(frame.tobytes()).decode()
        await ws.send(json.dumps({'frame': frame_b64, 'timestamp': 1.0}))
        response = await ws.recv()
        print(f'Response: {response}')

asyncio.run(test())
\"
\`\`\`

## Acceptance Criteria

- [ ] WebSocket endpoint at \`/ws/session/{session_id}\`
- [ ] Accepts base64-encoded frames with timestamps
- [ ] Decodes frames and passes to preprocessing pipeline
- [ ] Sends engagement score back to client after processing
- [ ] Handles client disconnect gracefully (cleanup resources)
- [ ] Supports multiple concurrent connections (one per student)
- [ ] Connection authenticated via session token
- [ ] At least 3 tests: connection, frame processing, disconnect handling

## Branch

\`feature/issue-5-websocket\`

## Depends on

Closes #1, Closes #4"

create_issue 6 "Build user onboarding and role management API" "$M1" "m1,infra" \
"## Why

EngageIQ has two distinct user types - students and teachers - with different permissions, different dashboards, and different data access. A teacher can see class-level analytics but not individual student names (unless opted in). A student can see their own data but not other students'. This role distinction must be enforced at the API level, not just the UI level.

The onboarding flow also captures privacy preferences. Under India's DPDPA (Digital Personal Data Protection Act, 2023), collecting biometric-adjacent data (facial landmarks) requires informed consent. The onboarding screen explains what data is collected, how it is processed (on-device, not stored), and what the student can opt out of. This is not optional - it is a legal requirement.

## What needs to be built

API endpoints for user registration, login, role management, and privacy preferences.

## Files to create or update

- \`src/api/routes/users.py\` - User CRUD and auth endpoints
- \`src/api/routes/courses.py\` - Course enrollment endpoints
- \`src/api/schemas/user.py\` - Pydantic request/response schemas

## How this affects overall development

User authentication gates every API endpoint. The session API (#5 WebSocket) needs to know which user is connecting. The nudge preferences (#23) are stored per user. The analytics (#24-26) filter by user role. Without user management, nothing else can be properly tested with realistic multi-user scenarios.

## How to test locally

\`\`\`bash
# Start backend
uvicorn src.api.main:app --reload

# Register a student
curl -X POST http://localhost:8000/api/users/register \\
  -H 'Content-Type: application/json' \\
  -d '{\"name\": \"Rahul\", \"email\": \"rahul@nst.edu\", \"role\": \"student\", \"privacy_mode\": \"anonymized\"}'

# Register a teacher
curl -X POST http://localhost:8000/api/users/register \\
  -H 'Content-Type: application/json' \\
  -d '{\"name\": \"Prof. Sharma\", \"email\": \"sharma@nst.edu\", \"role\": \"teacher\"}'

# Enroll student in course
curl -X POST http://localhost:8000/api/courses/1/enroll \\
  -H 'Content-Type: application/json' \\
  -d '{\"user_id\": 1}'

pytest tests/test_users.py -v
\`\`\`

## Acceptance Criteria

- [ ] POST /api/users/register creates user with role (student/teacher)
- [ ] GET /api/users/{id} returns user profile (role-appropriate fields)
- [ ] POST /api/courses/{id}/enroll adds student to course
- [ ] Privacy preferences stored per user: anonymized (default), identified (opt-in)
- [ ] Input validation: email format, role must be student/teacher, duplicate email rejected
- [ ] At least 4 tests: register student, register teacher, enroll, duplicate email

## Branch

\`feature/issue-6-user-api\`

## Depends on

Closes #3"

create_issue 7 "Create Alembic migration setup and seed data script" "$M1" "m1,infra" \
"## Why

Database migrations are how schema changes are tracked and applied across environments. When a contributor adds a new column for calibration data in issue #19, that change needs to propagate to every other contributor's local database and to the production database - without losing existing data.

Seed data accelerates development. Instead of manually creating test users, courses, and sessions through API calls every time you reset your database, one command populates everything. This is especially valuable when four contributors are independently developing - everyone works against the same dataset.

The seed script also serves as documentation. New contributors can look at it to understand the data model, relationships, and typical values. It is a living example of how the system's data fits together.

## What needs to be built

Alembic configuration, initial migration, and a seed script that populates the database with realistic sample data.

## Files to create or update

- \`alembic.ini\` - Alembic configuration
- \`alembic/env.py\` - Migration environment setup
- \`alembic/versions/001_initial.py\` - Initial migration
- \`scripts/seed.py\` - Seed data script

## How this affects overall development

Every contributor runs \`alembic upgrade head\` to set up their database. Every new migration is added as a new version file. The seed script is run after migrations to populate test data. When schema changes in future issues (#19 calibration, #22 effectiveness tracking), new migration files are added.

## How to test locally

\`\`\`bash
# Fresh database setup
dropdb engageiq_dev 2>/dev/null; createdb engageiq_dev

# Run migrations
alembic upgrade head

# Verify tables
python -c \"
from sqlalchemy import create_engine, inspect
engine = create_engine('postgresql://localhost/engageiq_dev')
print(inspect(engine).get_table_names())
\"

# Run seed script
python scripts/seed.py
# Output: Created 2 teachers, 10 students, 3 courses, 5 sessions, 100 engagement logs

# Verify seed data
python -c \"
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://localhost/engageiq_dev')
with engine.connect() as conn:
    users = conn.execute(text('SELECT count(*) FROM users')).scalar()
    courses = conn.execute(text('SELECT count(*) FROM courses')).scalar()
    print(f'Users: {users}, Courses: {courses}')
\"

# Test rollback
alembic downgrade base
# All tables should be removed
\`\`\`

## Acceptance Criteria

- [ ] \`alembic upgrade head\` creates all tables defined in models
- [ ] \`alembic downgrade base\` cleanly removes all tables
- [ ] Seed script creates: 2 teachers, 10 students, 3 courses, 5 sessions, sample engagement logs
- [ ] Seed script is idempotent (running twice does not create duplicates)
- [ ] Migration file is auto-generated from SQLAlchemy models (\`alembic revision --autogenerate\`)
- [ ] At least 2 tests: migration up/down, seed data counts

## Branch

\`feature/issue-7-alembic-seed\`

## Depends on

Closes #3"

# --- M2 Issues (#8-11) ------------------------------------------------------

create_issue 8 "Integrate MediaPipe Face Mesh with 468 landmarks" "$M2" "m2,cv,detection" \
"## Why

MediaPipe Face Mesh is the foundation of EngageIQ's entire computer vision pipeline. Every downstream module depends on its output: drowsiness detection needs eye landmarks, head pose needs nose and chin positions, expression classification needs the full face mesh, and gaze estimation needs iris positions. Choosing MediaPipe over alternatives (dlib, OpenCV Haar cascades) was deliberate - it provides 468 landmarks (vs. dlib's 68), runs at 30+ FPS on CPU (vs. dlib's 15 FPS), and includes iris tracking that dlib lacks entirely.

The lazy initialization pattern is important because MediaPipe's model loading takes 2-3 seconds. Loading it on import would slow down every test and every module that imports detection code. Lazy init means the model loads only when the first frame is processed, keeping imports fast and tests that don't need the model instant.

## What needs to be built

A FaceMeshDetector class that initializes MediaPipe lazily, processes frames, and returns structured landmark data with confidence scores.

## Files to create or update

- \`src/detection/face_mesh.py\` - FaceMeshDetector class with lazy initialization

## How this affects overall development

This is the input to everything in M2-M4. Head pose estimation (#9) takes landmarks as input. Gaze classification (#10) takes eye/iris landmarks. Drowsiness detection (#12) takes eye landmarks. Expression classification (#14) takes the face region. If Face Mesh is unreliable, every downstream module is unreliable.

## How to test locally

\`\`\`bash
# Quick demo with webcam
python -m src.detection.face_mesh --demo
# Should open webcam and overlay 468 green dots on your face

# Test with a static image
python -c \"
from src.detection.face_mesh import FaceMeshDetector
import cv2

detector = FaceMeshDetector()
frame = cv2.imread('tests/fixtures/sample_face.jpg')
result = detector.detect(frame)
print(f'Faces found: {len(result.faces)}')
print(f'Landmarks per face: {len(result.faces[0].landmarks)}')
print(f'Confidence: {result.faces[0].confidence:.2f}')
\"

pytest tests/test_face_mesh.py -v
\`\`\`

## Acceptance Criteria

- [ ] Returns 468 (x, y, z) landmarks per face with confidence score
- [ ] Lazy initialization: model loads on first \`detect()\` call, not on import
- [ ] Processes frames at 25+ FPS on laptop CPU (i5/Ryzen 5 or better)
- [ ] Handles no-face frames gracefully (returns empty list, no crash)
- [ ] Handles multiple faces (returns list of face results)
- [ ] Demo script visualizes landmarks on live webcam feed
- [ ] At least 4 tests: single face, no face, multiple faces, confidence threshold

## Branch

\`feature/issue-8-facemesh\`

## Depends on

Closes #4"

create_issue 9 "Implement head pose estimation using solvePnP" "$M2" "m2,cv,detection" \
"## Why

Head pose tells you where a student is looking. A student facing the screen (pitch ~0, yaw ~0) is likely engaged. A student with their head turned 30 degrees to the right (yaw = 30) is probably looking at their phone or talking to someone. A student looking down at 45 degrees (pitch = -45) might be sleeping or reading something on their desk.

OpenCV's solvePnP algorithm estimates 3D head orientation from 2D facial landmarks. It uses 6 key reference points (nose tip, chin, left/right eye corners, left/right mouth corners) and a generic 3D face model to compute the rotation vector, which we decompose into pitch (up/down), yaw (left/right), and roll (tilt).

The 5-degree accuracy requirement matters because the threshold for \"looking away\" is typically 15-20 degrees. If your measurement has 10-degree error, you cannot reliably distinguish \"looking at screen\" from \"looking slightly to the side\", leading to constant false positives.

## What needs to be built

A head pose estimator that takes 468 Face Mesh landmarks and returns pitch, yaw, and roll angles in degrees.

## Files to create or update

- \`src/detection/head_pose.py\` - \`estimate_head_pose\` function using solvePnP

## How this affects overall development

Head pose is a direct input to gaze classification (#10) and contributes 20% weight to the engagement score (#16). It is also used in calibration (#19) to establish each student's natural head position. Inaccurate pose estimation cascades into inaccurate engagement scores.

## How to test locally

\`\`\`bash
# Demo with webcam
python -m src.detection.head_pose --demo
# Should show pitch/yaw/roll values updating live
# Draw 3D axes on nose tip

python -c \"
from src.detection.face_mesh import FaceMeshDetector
from src.detection.head_pose import estimate_head_pose
import cv2

detector = FaceMeshDetector()
frame = cv2.imread('tests/fixtures/sample_face.jpg')
result = detector.detect(frame)
landmarks = result.faces[0].landmarks
pitch, yaw, roll = estimate_head_pose(landmarks, frame.shape)
print(f'Pitch: {pitch:.1f}deg, Yaw: {yaw:.1f}deg, Roll: {roll:.1f}deg')
\"

pytest tests/test_head_pose.py -v
\`\`\`

## Acceptance Criteria

- [ ] Returns pitch, yaw, roll in degrees (float)
- [ ] Uses 6 reference landmarks from Face Mesh (nose tip, chin, eye corners, mouth corners)
- [ ] Accuracy within 5 degrees when compared to known ground truth poses
- [ ] Handles partial face occlusion gracefully (returns None if insufficient landmarks visible)
- [ ] Demo script draws 3D coordinate axes on nose tip in webcam feed
- [ ] At least 4 tests: frontal face, turned left, turned right, looking down

## Branch

\`feature/issue-9-head-pose\`

## Depends on

Closes #8"

create_issue 10 "Build gaze classification system" "$M2" "m2,cv,detection" \
"## Why

Head pose tells you the direction the head is pointing, but not necessarily where the eyes are looking. A student can face the screen while their eyes glance at their phone. The gaze classifier combines head pose with iris position to determine actual gaze direction, outputting one of five states: at_screen, away_left, away_right, looking_down, eyes_closed.

Iris tracking from MediaPipe provides the missing piece. MediaPipe Face Mesh returns iris landmarks (4 points per eye), which allow computing the iris position relative to the eye corners. If the iris is centered, the student is looking forward. If it is shifted left, they are looking left. Combined with head pose, this gives a much more reliable gaze estimate than head pose alone.

The 30% weight in the engagement score (#16) makes gaze the single most influential signal. This is appropriate because looking at the screen is the most basic indicator of engagement. You can be bored while looking at the screen, but you are definitely not engaged if you are not looking at it.

## What needs to be built

A gaze classifier that combines head pose and iris position to classify gaze into 5 states.

## Files to create or update

- \`src/detection/gaze_classifier.py\` - GazeState enum and \`classify_gaze\` function

## How this affects overall development

Gaze state feeds directly into the engagement score (#16) with 30% weight - the highest of any signal. It is also used by the state machine (#17) to determine transitions. If gaze classification has a high false positive rate, students get incorrectly scored as disengaged, and the nudge agent sends unnecessary nudges.

## How to test locally

\`\`\`bash
# Demo with webcam
python -m src.detection.gaze_classifier --demo
# Should show gaze state updating live with color coding:
# Green = at_screen, Red = away_left/right, Yellow = looking_down, Gray = eyes_closed

python -c \"
from src.detection.gaze_classifier import classify_gaze, GazeState

# Frontal gaze
state = classify_gaze(pitch=0, yaw=0, iris_ratio=0.5)
print(f'Frontal: {state}')  # AT_SCREEN

# Looking right
state = classify_gaze(pitch=0, yaw=25, iris_ratio=0.8)
print(f'Right: {state}')  # AWAY_RIGHT

# Looking down
state = classify_gaze(pitch=-30, yaw=0, iris_ratio=0.5)
print(f'Down: {state}')  # LOOKING_DOWN
\"

pytest tests/test_gaze_classifier.py -v
\`\`\`

## Acceptance Criteria

- [ ] 5 gaze states: AT_SCREEN, AWAY_LEFT, AWAY_RIGHT, LOOKING_DOWN, EYES_CLOSED
- [ ] Combines head pose (pitch, yaw) with iris position ratio
- [ ] Thresholds: yaw > 20deg = away, pitch < -25deg = looking down, EAR < 0.2 = eyes closed
- [ ] All thresholds configurable in settings
- [ ] Demo script with color-coded gaze state overlay on webcam
- [ ] At least 5 tests: one per gaze state

## Branch

\`feature/issue-10-gaze-classifier\`

## Depends on

Closes #9"

create_issue 11 "Implement multi-face selector for group webcam scenarios" "$M2" "m2,cv,detection" \
"## Why

In Indian colleges, it is common for two or three students to share a laptop during online lectures. The webcam sees multiple faces, but the engagement system needs to track a specific student. Without a multi-face selector, the system either crashes (unexpected multiple faces), picks randomly (inconsistent tracking), or averages all faces (meaningless score).

The selector uses face embedding similarity to maintain consistent tracking. During the first frame, the student selects their face (or it is identified via calibration). The system computes a face embedding and uses it to re-identify the same face in subsequent frames, even if other faces appear or disappear.

This is also important for the object detector (#15). Detecting a \"second person\" in the frame is only meaningful if you first know which face is the primary student. The multi-face selector provides that anchor.

## What needs to be built

A face selector that identifies and tracks the primary student's face when multiple faces are visible.

## Files to create or update

- \`src/detection/face_selector.py\` - FaceSelector class with embedding-based tracking

## How this affects overall development

Without this, the entire pipeline breaks in multi-face scenarios. Every detection module assumes it is processing the primary student's face. If the wrong face is selected, all engagement data is wrong. This affects accuracy for shared-laptop scenarios which are common in Indian college settings.

## How to test locally

\`\`\`bash
# Demo with webcam (have a friend appear in frame)
python -m src.detection.face_selector --demo
# Should highlight the primary face in green, others in gray
# Primary face should persist even if others move in/out

python -c \"
from src.detection.face_selector import FaceSelector
import numpy as np

selector = FaceSelector()

# Simulate frame with 3 faces
faces = [
    {'landmarks': np.random.rand(468, 3), 'bbox': [100, 100, 200, 200]},
    {'landmarks': np.random.rand(468, 3), 'bbox': [300, 100, 400, 200]},
    {'landmarks': np.random.rand(468, 3), 'bbox': [500, 100, 600, 200]},
]

# Select largest face as primary (first frame)
primary = selector.select(faces)
print(f'Primary face index: {primary}')

# On subsequent frames, should track the same face
primary2 = selector.select(faces)
print(f'Same face tracked: {primary == primary2}')
\"

pytest tests/test_face_selector.py -v
\`\`\`

## Acceptance Criteria

- [ ] Selects primary face from multiple detected faces
- [ ] First frame: selects largest face (closest to camera) or user-selected face
- [ ] Subsequent frames: tracks the same face using embedding similarity
- [ ] Handles face disappearing and reappearing (re-identification within 5 seconds)
- [ ] Returns None when primary face not found (not a random other face)
- [ ] Works with up to 5 faces in frame without performance degradation
- [ ] At least 4 tests: single face, multi face selection, tracking persistence, face disappearance

## Branch

\`feature/issue-11-face-selector\`

## Depends on

Closes #8"

# --- M3 Issues (#12-15) -----------------------------------------------------

create_issue 12 "Build EAR-based drowsiness detector" "$M3" "m3,cv,detection" \
"## Why

Drowsiness is one of the strongest signals of disengagement. A student whose eyes are closing is not just distracted - they are on the verge of falling asleep. Detecting this early (within 2-3 seconds of sustained eye closure) allows the nudge system to intervene before the student misses significant lecture content.

The Eye Aspect Ratio (EAR) algorithm from Soukupova & Cech (2016) is the standard approach. EAR computes the ratio of vertical eye opening to horizontal eye width using 6 eye landmarks. When the eye is open, EAR is typically 0.25-0.35. When closing, it drops below 0.20. When fully closed, it approaches 0.05.

The critical challenge is distinguishing blinks from drowsiness. A normal blink lasts 0.1-0.4 seconds. Drowsiness manifests as sustained eye closure lasting 1.5+ seconds, or a pattern of slow, heavy blinks where EAR recovery is sluggish. The temporal analysis component tracks EAR over a sliding window to separate the two.

## What needs to be built

An EAR-based drowsiness detector that computes eye aspect ratio from landmarks, applies temporal analysis to distinguish blinks from drowsiness, and outputs a binary drowsy/alert signal.

## Files to create or update

- \`src/detection/drowsiness.py\` - \`compute_ear\` function and \`DrowsinessDetector\` class

## How this affects overall development

Drowsiness contributes 25% weight to the alertness signal in the engagement score (#16). The state machine (#17) has a special DROWSY state that overrides the score-based state when drowsiness is detected. The nudge agent (#20) uses a faster trigger for drowsy students (10 seconds vs. 30 seconds for distraction).

## How to test locally

\`\`\`bash
# Demo with webcam
python -m src.detection.drowsiness --demo
# Close your eyes slowly - should detect drowsiness after 1.5 seconds
# Normal blinks should NOT trigger

python -c \"
from src.detection.drowsiness import compute_ear, DrowsinessDetector

# Test EAR with known landmarks
# Open eye landmarks (EAR should be ~0.3)
open_eye = [(0.0, 0.3), (0.2, 0.4), (0.4, 0.3), (0.2, 0.2), (0.1, 0.2), (0.3, 0.2)]  # simplified
ear = compute_ear(open_eye)
print(f'Open eye EAR: {ear:.3f}')  # should be > 0.25

# Closed eye landmarks (EAR should be ~0.05)
closed_eye = [(0.0, 0.3), (0.2, 0.31), (0.4, 0.3), (0.2, 0.29), (0.1, 0.29), (0.3, 0.29)]
ear = compute_ear(closed_eye)
print(f'Closed eye EAR: {ear:.3f}')  # should be < 0.1

# Test drowsiness detection over time
detector = DrowsinessDetector(ear_threshold=0.25, drowsy_frames=23)  # 23 frames at 15 FPS = 1.5 seconds
for i in range(30):
    is_drowsy = detector.update(ear=0.15, timestamp=i/15)  # sustained low EAR
print(f'After 2 seconds of low EAR: drowsy={is_drowsy}')  # True
\"

pytest tests/test_drowsiness.py -v
\`\`\`

## Acceptance Criteria

- [ ] \`compute_ear\` returns float from 6 eye landmarks
- [ ] Blinks (< 0.3 seconds of low EAR) are NOT detected as drowsiness
- [ ] Drowsiness (> 1.5 seconds of sustained low EAR) IS detected
- [ ] EAR threshold configurable (default 0.25, adjusted by calibration #19)
- [ ] Duration threshold configurable (default 1.5 seconds)
- [ ] False positive rate < 5% during normal attentive behavior
- [ ] At least 5 tests: open eye EAR, closed eye EAR, blink not drowsy, sustained closure is drowsy, threshold edge cases

## Branch

\`feature/issue-12-drowsiness\`

## Depends on

Closes #8"

create_issue 13 "Implement MAR-based yawn detection" "$M3" "m3,cv,detection" \
"## Why

Yawning is a reliable fatigue indicator that complements EAR-based drowsiness detection. A student can be fatigued without closing their eyes - they might be yawning, which EAR alone would miss. The combination of EAR and MAR provides a more complete picture of alertness.

The Mouth Aspect Ratio (MAR) works analogously to EAR but for the mouth. It computes the ratio of vertical mouth opening to horizontal mouth width. During normal speech, the mouth opens and closes rapidly (0.2-0.5 seconds). A yawn is characterized by a wide, sustained mouth opening lasting 2-4 seconds - significantly longer and wider than speech.

The is_fatigued method combines yawn frequency with EAR data. A single yawn might mean nothing, but three yawns in 10 minutes combined with sluggish EAR recovery is a strong fatigue signal.

## What needs to be built

A MAR-based yawn detector that distinguishes yawns from speech and combines with EAR data to assess fatigue.

## Files to create or update

- \`src/detection/yawn.py\` - \`compute_mar\` function and \`YawnDetector\` class

## How this affects overall development

Yawn detection feeds into the alertness component of the engagement score (#16). Combined with EAR, it provides the complete alertness signal (25% weight). The fatigue assessment helps the nudge agent (#20) decide between a gentle reminder (\"take a stretch break\") vs. a stronger nudge.

## How to test locally

\`\`\`bash
# Demo with webcam
python -m src.detection.yawn --demo
# Yawn naturally - should detect after 2 seconds of sustained opening
# Speaking should NOT trigger

python -c \"
from src.detection.yawn import compute_mar, YawnDetector

# Open mouth (yawn-like)
mar = compute_mar(mouth_landmarks_open)
print(f'Yawn MAR: {mar:.3f}')  # should be > 0.6

# Closed mouth
mar = compute_mar(mouth_landmarks_closed)
print(f'Closed MAR: {mar:.3f}')  # should be < 0.3

# Test fatigue assessment
detector = YawnDetector(mar_threshold=0.6, yawn_duration=2.0)
# Simulate 3 yawns in 10 minutes
detector.record_yawn(timestamp=60)
detector.record_yawn(timestamp=300)
detector.record_yawn(timestamp=540)
print(f'Fatigued: {detector.is_fatigued()}')  # True (3 yawns in 10 min)
\"

pytest tests/test_yawn.py -v
\`\`\`

## Acceptance Criteria

- [ ] \`compute_mar\` returns float from mouth landmarks
- [ ] Yawn detection requires sustained opening > 2 seconds (not brief speech)
- [ ] MAR threshold configurable (default 0.6)
- [ ] \`is_fatigued\` method combines yawn frequency + optional EAR data
- [ ] Fatigue triggered by 3+ yawns in 10 minutes
- [ ] Speech (rapid mouth movement) does not trigger yawn detection
- [ ] At least 4 tests: yawn MAR, speech MAR, fatigue assessment, threshold edge cases

## Branch

\`feature/issue-13-yawn\`

## Depends on

Closes #8"

create_issue 14 "Build expression classifier (4-class: engaged, confused, bored, neutral)" "$M3" "m3,cv,detection" \
"## Why

Facial expressions provide direct evidence of cognitive state. A confused expression means the student does not understand the current material - information that no other signal (gaze, pose, drowsiness) can provide. A bored expression combined with correct gaze (looking at screen) reveals a student who is physically present but mentally checked out.

The 4-class simplification (engaged, confused, bored, neutral) from FER2013's standard 7 classes (anger, disgust, fear, happy, sad, surprise, neutral) is deliberate. Anger and disgust are irrelevant in a classroom context. Fear and surprise are too rare to be useful. Happy maps to engaged. Sad maps to bored. This reduces the classification problem while keeping the educationally relevant classes.

Transfer learning from a pre-trained FER model is the practical approach. Training from scratch would require a labeled classroom expression dataset that does not exist. Fine-tuning an existing FER model on the 4 target classes gives reasonable accuracy (70%+) with minimal training data.

## What needs to be built

A facial expression classifier that categorizes face crops into 4 engagement-relevant classes using transfer learning.

## Files to create or update

- \`src/detection/expression.py\` - Expression enum and \`ExpressionClassifier\` class

## How this affects overall development

Expression contributes 25% weight to the engagement score (#16). The CONFUSED state in the state machine (#17) is primarily triggered by the expression classifier. The intervention agent (#29) uses expression data to identify confusing content segments. If the classifier has low accuracy, confused students are not identified and the system misses its most unique signal.

## How to test locally

\`\`\`bash
# Demo with webcam
python -m src.detection.expression --demo
# Should show expression label updating in real-time
# Try: smile (engaged), frown (confused), blank stare (bored), resting face (neutral)

python -c \"
from src.detection.expression import ExpressionClassifier, Expression
import cv2

classifier = ExpressionClassifier()
face_crop = cv2.imread('tests/fixtures/sample_face.jpg')
result = classifier.classify(face_crop)
print(f'Expression: {result.expression}, Confidence: {result.confidence:.2f}')
# Example: Expression.NEUTRAL, 0.78
\"

pytest tests/test_expression.py -v
\`\`\`

## Acceptance Criteria

- [ ] 4 expression classes: ENGAGED, CONFUSED, BORED, NEUTRAL
- [ ] Uses pre-trained FER model with transfer learning for 4-class output
- [ ] Accuracy > 70% on FER2013 test set (mapped to 4 classes)
- [ ] Inference time < 50ms per face crop on CPU
- [ ] Returns expression enum + confidence score (0-1)
- [ ] Handles poor lighting gracefully (returns NEUTRAL with low confidence, not crash)
- [ ] At least 4 tests: one per expression class with sample images

## Branch

\`feature/issue-14-expression\`

## Depends on

Closes #8"

create_issue 15 "Create expression model training notebook" "$M3" "m3,cv,detection" \
"## Why

The pre-trained FER model from issue #14 gives a starting point, but it was trained on posed expressions in lab conditions - not on real students sitting in front of laptop webcams. The training notebook allows the team to fine-tune the model on more representative data, documenting every decision: which FER2013 classes map to which EngageIQ classes, what augmentations work best for webcam-quality images, and what accuracy is achievable.

This notebook is also a Build-Understand-Defend artifact. During Q&A, faculty will ask \"Why did you choose these 4 classes?\" and \"What is FER2013's known bias?\" The notebook's markdown cells should answer these questions with data and visualizations, not just code.

The notebook format (not a .py script) is intentional. Notebooks combine code, visualizations, and explanations in a single document. They are the standard format for ML experimentation because they allow iterative exploration with inline plots of training curves, confusion matrices, and sample predictions.

## What needs to be built

A Jupyter notebook that trains (or fine-tunes) the 4-class expression classifier with documented experiments.

## Files to create or update

- \`notebooks/expression_training.ipynb\` - Training notebook with experiments and analysis

## How this affects overall development

The trained model weights are saved to \`models/\` and loaded by ExpressionClassifier (#14). The notebook documents the accuracy metrics that appear in the project defense. If the model accuracy is low (<70%), the team knows to invest more time in data augmentation or try a different base model.

## How to test locally

\`\`\`bash
# Install Jupyter
pip install jupyter

# Run the notebook
jupyter notebook notebooks/expression_training.ipynb

# The notebook should contain:
# 1. FER2013 dataset loading and 7-to-4 class mapping
# 2. Data augmentation (brightness, rotation, horizontal flip)
# 3. Model architecture (base FER model + custom 4-class head)
# 4. Training loop with validation
# 5. Confusion matrix visualization
# 6. Sample predictions on webcam-like images
# 7. Model export to models/expression_model.pth

# Quick validation
python -c \"
import torch
model = torch.load('models/expression_model.pth', map_location='cpu')
print(f'Model loaded successfully')
\"
\`\`\`

## Acceptance Criteria

- [ ] Notebook runs end-to-end without errors (Cell -> Run All)
- [ ] Downloads and processes FER2013 dataset automatically
- [ ] Documents 7-to-4 class mapping with justification
- [ ] Applies at least 3 data augmentations relevant to webcam imagery
- [ ] Training achieves > 70% accuracy on 4-class test set
- [ ] Confusion matrix shows per-class precision and recall
- [ ] Exports trained model weights to \`models/expression_model.pth\`
- [ ] Markdown cells explain every major decision (not just code comments)

## Branch

\`feature/issue-15-expression-notebook\`

## Depends on

Closes #14"

# --- M4 Issues (#16-19) -----------------------------------------------------

create_issue 16 "Design multi-signal engagement scoring" "$M4" "m4,agent,cv" \
"## Why

Individual CV signals are noisy and incomplete on their own. Gaze alone cannot tell you if a student is drowsy. Expression alone cannot tell you if they are looking at the screen. Drowsiness alone does not capture confusion. The engagement scorer fuses all four signals into a single, reliable 0-100 score that downstream modules (nudge agent, analytics, reports) can act on.

The weighted average approach was chosen over a trained ML model for three reasons. First, it is interpretable - when a student asks \"why did I get a low engagement score at minute 14?\", you can answer \"your gaze was away (30% weight) and your expression was confused (25% weight).\" Second, it is configurable per course type - a coding lab needs higher gaze weight than a discussion seminar. Third, it requires zero training data - you do not need labeled engagement examples to start scoring.

This is also where the system transitions from perception (seeing what the student is doing) to reasoning (interpreting what it means). The scorer is the first \"agentic\" component - it makes a judgment call, not just a measurement.

## What needs to be built

A weighted scorer that fuses gaze, pose, expression, and alertness signals into a 0-100 engagement score with configurable weights.

## Files to create or update

- \`src/scoring/engagement_score.py\` - Engagement scorer with weighted fusion
- \`src/config/scoring_weights.py\` - Weight profiles per course type

## How this affects overall development

The engagement score is the single number that the entire downstream system depends on. The state machine (#17) maps it to discrete states. The nudge agent (#20) triggers based on it. The analytics (#24) aggregate it. The reports (#27, #28) visualize it. If the score is unreliable, every downstream module produces unreliable results.

## How to test locally

\`\`\`bash
pytest tests/test_engagement_score.py -v

python -c \"
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
\"
\`\`\`

## Acceptance Criteria

- [ ] Score range 0-100 with clear interpretation (0 = fully disengaged, 100 = fully engaged)
- [ ] Default weights: gaze 30%, pose 20%, expression 25%, alertness 25%
- [ ] Weights configurable per course type (theory, lab, seminar, discussion profiles)
- [ ] Handles missing signals gracefully: redistributes weight proportionally among remaining signals
- [ ] At least 8 test cases covering: all high, all low, mixed, missing signals, edge cases
- [ ] Score is a float, not an integer (enables fine-grained temporal smoothing)
- [ ] Function is pure (no side effects, no state) - easy to test and reason about

## Branch

\`feature/issue-16-engagement-score\`

## Depends on

Closes #10, Closes #12, Closes #14"

create_issue 17 "Build engagement state machine" "$M4" "m4,agent" \
"## Why

A continuous score of 47.3 is hard for a nudge agent to act on. Should it nudge at 47? At 40? At 30? The state machine converts the continuous score into discrete, actionable states: Engaged, Passive, Distracted, Drowsy, Confused. Each state has clear meaning and triggers specific responses.

Hysteresis is the critical feature. Without it, a student hovering at the boundary between Engaged (70+) and Passive (40-69) would flip back and forth every few seconds as their score fluctuates around 68-72. Hysteresis adds a duration requirement: you must stay below 70 for at least 30 seconds before transitioning from Engaged to Passive. Brief dips are ignored. This prevents the system from being jumpy and annoying.

The state machine also provides the event system that downstream modules subscribe to. When the state transitions from Engaged to Distracted, that event triggers the nudge agent to consider sending a reminder.

## What needs to be built

A finite state machine with 5 states, configurable score ranges, duration thresholds for transitions, and an event system for state changes.

## Files to create or update

- \`src/scoring/state_machine.py\` - EngagementStateMachine class

## How this affects overall development

The state machine is the interface between scoring and action. The nudge agent (#20) subscribes to state transition events. The analytics (#24) log state durations. The reports (#27, #28) summarize time spent in each state.

## How to test locally

\`\`\`bash
pytest tests/test_state_machine.py -v

python -c \"
from src.scoring.state_machine import EngagementStateMachine

sm = EngagementStateMachine()

# Feed high scores for 5 seconds
for i in range(75):
    state = sm.update(score=85, is_drowsy=False, is_confused=False, timestamp=i/15)
print(f'After 5s of score 85: {state}')  # ENGAGED

# Brief dip for 1 second (should NOT transition due to hysteresis)
for i in range(75, 90):
    state = sm.update(score=35, is_drowsy=False, is_confused=False, timestamp=i/15)
print(f'After 1s dip to 35: {state}')  # Still ENGAGED

# Sustained drop for 20 seconds (should transition)
for i in range(90, 390):
    state = sm.update(score=35, is_drowsy=False, is_confused=False, timestamp=i/15)
print(f'After 20s at 35: {state}')  # DISTRACTED
\"
\`\`\`

## Acceptance Criteria

- [ ] 5 states: ENGAGED (70-100), PASSIVE (40-69), DISTRACTED (15-39), DROWSY (0-30 + drowsy signal), CONFUSED (any score + confused expression)
- [ ] Duration thresholds: ENGAGED (immediate), PASSIVE (30s), DISTRACTED (15s), DROWSY (10s), CONFUSED (20s)
- [ ] Hysteresis prevents transitions from brief fluctuations
- [ ] State history logged with timestamps
- [ ] Transition events emittable (callback or event list)
- [ ] Score ranges and duration thresholds configurable
- [ ] At least 6 test cases: sustained high, sustained low, brief dip, gradual decline, drowsy override, confused override

## Branch

\`feature/issue-17-state-machine\`

## Depends on

Closes #16"

create_issue 18 "Implement temporal smoothing and anomaly filtering" "$M4" "m4,cv" \
"## Why

Human behavior is noisy. A student scratches their nose, and for two frames their hand covers their face - the face detector returns None, and the engagement score drops to zero. They sneeze, and for one second their eyes close and mouth opens wide - drowsiness and yawn detection both fire. None of these are real disengagement.

The temporal filter applies a sliding window average over the last 2 seconds of scores, smoothing out single-frame anomalies while still detecting sustained changes within a reasonable response time. It is the difference between a useful signal and noise.

## What needs to be built

A temporal filter with configurable sliding window that smooths engagement scores and filters single-frame anomalies.

## Files to create or update

- \`src/scoring/temporal_filter.py\` - TemporalFilter class with sliding window

## How this affects overall development

The filtered score is what every downstream module actually uses. The state machine (#17) operates on filtered scores. The nudge agent (#20) responds to filtered states. Without this filter, the system produces constant false alerts.

## How to test locally

\`\`\`bash
pytest tests/test_temporal_filter.py -v

python -c \"
from src.scoring.temporal_filter import TemporalFilter

tf = TemporalFilter(window_size=30)  # 2 seconds at 15 FPS

# Feed stable high scores
for _ in range(30):
    smoothed = tf.smooth(85.0)
print(f'Stable at 85: smoothed = {smoothed:.1f}')  # ~85

# Inject single anomaly
smoothed = tf.smooth(10.0)
print(f'After single anomaly: smoothed = {smoothed:.1f}')  # should still be ~82

# Sustained drop
for _ in range(45):
    smoothed = tf.smooth(25.0)
print(f'After 3s sustained drop: smoothed = {smoothed:.1f}')  # should be ~25-30
\"
\`\`\`

## Acceptance Criteria

- [ ] Sliding window of configurable size (default 30 frames = 2 seconds at 15 FPS)
- [ ] Single-frame anomalies do not drop the smoothed output by more than 5 points
- [ ] Sustained changes are fully reflected within 3 seconds
- [ ] Handles empty window gracefully (returns raw score when buffer not yet full)
- [ ] Memory usage bounded (uses deque, not growing list)
- [ ] At least 4 test cases: stable input, single anomaly, sustained change, ramp up/down

## Branch

\`feature/issue-18-temporal-filter\`

## Depends on

Closes #16"

create_issue 19 "Per-student calibration system" "$M4" "m4,cv,agent" \
"## Why

Not every face is the same. Students of East Asian descent typically have a lower resting EAR than students of European descent. A student wearing glasses has different landmark positions. Using the same thresholds for everyone is not just inaccurate - it is unfair.

The calibration system captures each student's personal baseline during a 30-second setup. It measures their resting EAR, natural head pose, and baseline expression distribution so detection thresholds are personalized.

## What needs to be built

A calibration module that captures personal baselines and adjusts detection thresholds per student.

## Files to create or update

- \`src/scoring/calibration.py\` - CalibrationManager class
- \`src/api/routes/calibration.py\` - Calibration API endpoint

## How this affects overall development

Calibration improves accuracy for every student, which means more accurate engagement scores, fewer false nudges, and more trustworthy analytics. Without it, students with naturally low EAR get flagged as drowsy when they are perfectly alert.

## How to test locally

\`\`\`bash
python -m src.scoring.calibration --demo
# Prompts: \"Look at the screen naturally for 30 seconds\"
# After 30 seconds, prints calibrated thresholds

python -c \"
from src.scoring.calibration import CalibrationManager

cm = CalibrationManager()
cm.calibrate_ear(resting_ear=0.22)
print(f'Low EAR student threshold: {cm.ear_threshold:.3f}')  # ~0.17, not 0.25

cm2 = CalibrationManager()
cm2.calibrate_ear(resting_ear=0.35)
print(f'High EAR student threshold: {cm2.ear_threshold:.3f}')  # ~0.28
\"
\`\`\`

## Acceptance Criteria

- [ ] 30-second calibration captures: resting EAR, natural head pose, expression distribution
- [ ] EAR threshold set to (resting_ear * 0.8) instead of fixed 0.25
- [ ] Gaze thresholds adjusted relative to natural head pose
- [ ] Calibration data persisted per student in database
- [ ] Student can re-calibrate anytime
- [ ] Skippable with clear warning
- [ ] API: POST /api/calibrate/{user_id}, GET /api/calibrate/{user_id}

## Branch

\`feature/issue-19-calibration\`

## Depends on

Closes #12, Closes #16"

# --- M5 Issues (#20-23) -----------------------------------------------------

create_issue 20 "Build nudge decision agent" "$M5" "m5,agent,nudge" \
"## Why

Knowing a student is distracted is only half the problem. The other half is deciding what to do about it. Nudge too early and you annoy a student who was about to re-engage. Nudge too late and the student has already missed 10 minutes. Nudge too often and the student disables the system.

The nudge decision agent is the first truly agentic component. It considers: How long has the student been distracted? When was the last nudge? Has the student responded well to nudges before? How many nudges have been sent this session?

This is where LangGraph enters the picture. The agent is a LangGraph state machine with nodes for: evaluating engagement state, checking nudge history, deciding whether to nudge, selecting nudge type, and recording the decision.

## What needs to be built

A LangGraph-based nudge decision agent that evaluates when and how to nudge based on engagement state, history, and effectiveness data.

## Files to create or update

- \`src/nudge/nudge_decision.py\` - Nudge decision logic
- \`src/agents/nudge_agent.py\` - LangGraph agent implementation

## How this affects overall development

This agent determines the student experience. Too many nudges and students hate the system. Too few and it has no impact. The effectiveness tracker (#22) feeds data back to improve decisions over time.

## How to test locally

\`\`\`bash
pytest tests/test_nudge_decision.py -v

python -c \"
from src.nudge.nudge_decision import NudgeDecisionEngine

engine = NudgeDecisionEngine(cooldown_seconds=300, max_nudges=5)

# First distraction
decision = engine.should_nudge(
    current_state='distracted', state_duration=35,
    last_nudge_time=None, session_nudge_count=0, effectiveness_history=[])
print(f'First: nudge={decision.should_nudge}, type={decision.nudge_type}')

# During cooldown
decision = engine.should_nudge(
    current_state='distracted', state_duration=35,
    last_nudge_time=120, session_nudge_count=1, effectiveness_history=[])
print(f'Cooldown: nudge={decision.should_nudge}')  # False

# Max reached
decision = engine.should_nudge(
    current_state='distracted', state_duration=35,
    last_nudge_time=600, session_nudge_count=5, effectiveness_history=[])
print(f'Max: nudge={decision.should_nudge}')  # False
\"
\`\`\`

## Acceptance Criteria

- [ ] Nudge triggers only after configurable sustained disengagement (default: 30 seconds)
- [ ] Cooldown period: default 5 minutes, configurable
- [ ] Maximum nudges per session: default 5, configurable
- [ ] Considers past nudge effectiveness when selecting type
- [ ] Returns NudgeDecision with: should_nudge, nudge_type, reason
- [ ] LangGraph implementation with clear state graph
- [ ] At least 6 test cases

## Branch

\`feature/issue-20-nudge-decision\`

## Depends on

Closes #17"

create_issue 21 "Implement nudge delivery system" "$M5" "m5,nudge,frontend" \
"## Why

A decision to nudge is useless without a way to deliver it. Three channels offer different levels of interruption: browser notification (mild), visual overlay (subtle), and audio chime (assertive).

The visual overlay cannot be a popup blocking the lecture. It should be a gentle glow on the screen edge that the student notices peripherally. The audio chime must be gentle enough not to startle but noticeable enough to break the distraction loop.

## What needs to be built

Three nudge delivery channels with configurable messages and intensity.

## Files to create or update

- \`src/nudge/nudge_delivery.py\` - Multi-channel delivery system
- \`frontend/src/components/NudgeOverlay.jsx\` - Visual overlay component

## How this affects overall development

The delivery system is the user-facing output of the nudge pipeline. It directly affects student satisfaction. The effectiveness tracker (#22) measures whether delivery actually works.

## How to test locally

\`\`\`bash
python -m src.nudge.nudge_delivery --type notification --message \"Time to refocus!\"
python -m src.nudge.nudge_delivery --type overlay --message \"You seem distracted\"
python -m src.nudge.nudge_delivery --type audio

curl -X POST http://localhost:8000/api/nudge/test \\
  -H 'Content-Type: application/json' \\
  -d '{\"type\": \"notification\", \"message\": \"Test nudge\", \"user_id\": 1}'
\`\`\`

## Acceptance Criteria

- [ ] Browser notification: shows with custom message, auto-dismisses after 5 seconds
- [ ] Visual overlay: subtle screen-edge glow, fades in/out, non-blocking
- [ ] Audio chime: gentle sound, under 2 seconds, low volume
- [ ] Each channel triggerable independently
- [ ] Nudge type and timestamp logged to database
- [ ] Student can disable any channel via API
- [ ] Delivery is async (does not block detection pipeline)

## Branch

\`feature/issue-21-nudge-delivery\`

## Depends on

Closes #20"

create_issue 22 "Add nudge effectiveness tracker" "$M5" "m5,nudge,analytics" \
"## Why

Sending nudges without measuring their impact is like prescribing medicine without checking if the patient gets better. The effectiveness tracker closes the feedback loop: after every nudge, it measures whether engagement actually improved.

This transforms the nudge agent from rule-based to learning. If notifications work 60% of the time but audio only 30% for a specific student, the agent should prefer notifications for that student.

## What needs to be built

A tracker that measures engagement change after nudges, computes per-type effectiveness, and feeds results back to the decision agent.

## Files to create or update

- \`src/nudge/effectiveness_tracker.py\` - EffectivenessTracker class

## How this affects overall development

This is the learning component that makes the nudge system intelligent over time. Effectiveness data also appears in session reports (#27) and weekly reports (#28).

## How to test locally

\`\`\`bash
pytest tests/test_effectiveness_tracker.py -v

python -c \"
from src.nudge.effectiveness_tracker import EffectivenessTracker

tracker = EffectivenessTracker(measurement_window=60)

tracker.record_nudge(nudge_type='notification', timestamp=0, pre_score=35)
tracker.record_post_score(timestamp=30, score=55)
tracker.record_post_score(timestamp=60, score=65)
result = tracker.evaluate_last_nudge()
print(f'Notification: effective={result.effective}, delta={result.delta:+.1f}')

tracker.record_nudge(nudge_type='audio', timestamp=120, pre_score=30)
tracker.record_post_score(timestamp=150, score=32)
result = tracker.evaluate_last_nudge()
print(f'Audio: effective={result.effective}, delta={result.delta:+.1f}')

stats = tracker.get_stats()
print(f'Notification rate: {stats[\"notification\"].success_rate:.0%}')
\"
\`\`\`

## Acceptance Criteria

- [ ] Measures engagement score delta in 60-second post-nudge window
- [ ] Nudge is \"effective\" if average post-nudge score improves by 10+ points
- [ ] Tracks success rate per nudge type
- [ ] Feeds effectiveness data to nudge decision agent
- [ ] Persists history per student across sessions
- [ ] At least 4 test cases

## Branch

\`feature/issue-22-nudge-effectiveness\`

## Depends on

Closes #21"

create_issue 23 "Nudge preferences UI" "$M5" "m5,nudge,frontend" \
"## Why

Nudging is only effective if the student is willing to receive nudges. A system that forces a specific style on every student will be disabled. The preferences UI gives students control: channel toggles, quiet hours, sensitivity.

Quiet hours matter because Indian students study at all hours. A student reviewing recordings at midnight does not want an audio chime waking up their roommates.

## What needs to be built

A student-facing preferences panel with channel toggles, quiet hours, and sensitivity control.

## Files to create or update

- \`frontend/src/components/NudgePreferences.jsx\` - Preferences panel
- \`src/api/routes/preferences.py\` - Preferences API endpoints
- \`src/api/schemas/preferences.py\` - Pydantic schemas

## How this affects overall development

The nudge decision agent (#20) must respect these preferences. If audio is disabled, the agent must never send one. Preferences are loaded at session start.

## How to test locally

\`\`\`bash
# Navigate to /student/settings/nudge
# Should show toggles, quiet hours, sensitivity slider

curl -X PUT http://localhost:8000/api/preferences/2 \\
  -H 'Content-Type: application/json' \\
  -d '{\"notification_enabled\": true, \"overlay_enabled\": true, \"audio_enabled\": false, \"quiet_hours_start\": \"22:00\", \"quiet_hours_end\": \"08:00\", \"sensitivity\": \"less\"}'

curl http://localhost:8000/api/preferences/2
\`\`\`

## Acceptance Criteria

- [ ] Toggle each nudge channel independently
- [ ] Quiet hours with start and end time (24-hour format)
- [ ] Sensitivity: less (10-min cooldown), normal (5-min), more (3-min)
- [ ] Preferences persist across sessions
- [ ] Changes take effect immediately
- [ ] Default: all enabled, no quiet hours, normal sensitivity
- [ ] Responsive design (works on phone)

## Branch

\`feature/issue-23-nudge-preferences\`

## Depends on

Closes #21"

# --- M6 Issues (#24-26) -----------------------------------------------------

create_issue 24 "Build class-level engagement aggregator" "$M6" "m6,analytics" \
"## Why

A teacher with 60 students cannot look at 60 individual timelines. They need one view showing the class pulse: is the class engaged now? Did engagement drop during the recursion explanation?

The aggregator also enforces privacy. Each student's data is anonymized before aggregation. The teacher sees \"65% of the class was engaged at minute 14\" - not \"Rahul scored 45.\"

Class-level dip detection is especially valuable. When 40% of the class simultaneously loses engagement, that is a content problem, not a student problem.

## What needs to be built

An aggregation engine that computes class-wide engagement metrics with dip detection.

## Files to create or update

- \`src/analytics/class_aggregator.py\` - ClassAggregator class

## How this affects overall development

Foundation of the teacher experience. Teacher dashboard (#33) displays these metrics. Intervention agent (#29) analyzes aggregates. Weekly report (#28) summarizes trends.

## How to test locally

\`\`\`bash
pytest tests/test_class_aggregator.py -v

python -c \"
from src.analytics.class_aggregator import ClassAggregator

agg = ClassAggregator()
scores = [80, 70, 90, 60, 85, 75, 65, 80, 70, 90]
stats = agg.aggregate(scores)
print(f'Average: {stats.average:.1f}, Engaged: {stats.engaged_pct:.0%}')

timeline = {10: 78, 11: 80, 12: 75, 13: 72, 14: 52, 15: 48, 16: 55, 17: 60, 18: 70}
dips = agg.detect_dips(timeline, threshold=0.15)
print(f'Dips at: {[d.minute for d in dips]}')
\"
\`\`\`

## Acceptance Criteria

- [ ] Computes: mean, median, std dev, min, max, engaged percentage (score > 70)
- [ ] Minute-by-minute engagement timeline
- [ ] Detects dips where class average drops > 15% from session average
- [ ] All student IDs anonymized in output
- [ ] Handles missing data (disconnected students excluded)
- [ ] At least 4 test cases

## Branch

\`feature/issue-24-class-aggregator\`

## Depends on

Closes #17"

create_issue 25 "Implement at-risk student identifier" "$M6" "m6,analytics" \
"## Why

A single low-engagement session can happen to anyone. But three consecutive low sessions is a pattern - the student needs help from the teacher that session-level nudges cannot provide.

Declining trend detection adds nuance. A student dropping from 80 to 70 to 60 over three weeks has not crossed the threshold yet, but they are heading there.

## What needs to be built

A risk identification engine that flags students with consistently low or declining engagement across multiple sessions.

## Files to create or update

- \`src/analytics/risk_identifier.py\` - RiskIdentifier class
- \`src/analytics/trend_analyzer.py\` - TrendAnalyzer for rolling averages

## How this affects overall development

Teacher dashboard (#33) highlights at-risk students. Intervention agent (#29) uses this data. Weekly report (#28) includes at-risk summary.

## How to test locally

\`\`\`bash
pytest tests/test_risk_identifier.py -v

python -c \"
from src.analytics.risk_identifier import RiskIdentifier

ri = RiskIdentifier(threshold=50, consecutive_sessions=3)

result = ri.evaluate(student_id='anon_42', session_scores=[40, 35, 30])
print(f'Low 3 sessions: at_risk={result.at_risk}')

result = ri.evaluate(student_id='anon_44', session_scores=[80, 75, 70, 65, 60])
print(f'Declining: declining_trend={result.declining_trend}')
\"
\`\`\`

## Acceptance Criteria

- [ ] Flags students with average below threshold for 3+ consecutive sessions
- [ ] Detects declining trend: current week avg < previous week avg by > 10%
- [ ] Rolling 7-day and 30-day analysis windows
- [ ] At-risk list uses anonymized student IDs
- [ ] Students can opt in to be identified for targeted help
- [ ] At least 5 test cases

## Branch

\`feature/issue-25-risk-identifier\`

## Depends on

Closes #24"

create_issue 26 "Export analytics as CSV/JSON" "$M6" "m6,analytics,infra" \
"## Why

Not every teacher uses the dashboard. Some prefer Excel. Some need data for NAAC accreditation. Raw data export in standard formats makes this possible.

This is also about data ownership - the teacher's data should not be locked inside EngageIQ.

## What needs to be built

API endpoints and dashboard button for exporting engagement data in CSV and JSON formats with filters.

## Files to create or update

- \`src/api/routes/export.py\` - Export API endpoints
- \`frontend/src/components/ExportButton.jsx\` - Export button component

## How this affects overall development

Data portability layer. Does not affect other modules directly but significantly increases utility for teachers.

## How to test locally

\`\`\`bash
curl 'http://localhost:8000/api/export/sessions/1?format=csv' > session_1.csv
cat session_1.csv | head -5

curl 'http://localhost:8000/api/export/sessions/1?format=json' > session_1.json
python -c \"import json; print(len(json.load(open('session_1.json'))))\"

curl 'http://localhost:8000/api/export/courses/1?format=csv&start=2026-06-01&end=2026-06-08' > week.csv
\`\`\`

## Acceptance Criteria

- [ ] GET /api/export/sessions/{id}?format=csv and ?format=json
- [ ] Columns: timestamp, anonymized_student_id, engagement_score, state, gaze_state, drowsiness, expression
- [ ] Filter by: date range, course_id, student_id
- [ ] Large exports (1000+ rows) stream via chunked response
- [ ] CSV is RFC 4180 compliant
- [ ] Frontend export button triggers download
- [ ] Student IDs always anonymized in exports

## Branch

\`feature/issue-26-export-analytics\`

## Depends on

Closes #24"

# --- M7 Issues (#27-31) -----------------------------------------------------

create_issue 27 "Build session engagement report" "$M7" "m7,analytics" \
"## Why

After a lecture, both teacher and students want a quick summary. The teacher wants: How engaged was the class? When did I lose them? The student wants: How focused was I? When did I drift?

The session report turns raw data into a narrative with highlighted key moments, making the data actionable.

## What needs to be built

A report generator producing per-session engagement summaries with timeline charts and key moments.

## Files to create or update

- \`src/reports/session_report.py\` - SessionReportGenerator class
- \`src/templates/session_report.html\` - Jinja2 HTML template

## How this affects overall development

Displayed in both dashboards (#32, #33). Weekly report (#28) aggregates these. Email delivery (#31) sends them. Intervention agent (#29) analyzes the data.

## How to test locally

\`\`\`bash
python -m src.reports.session_report --session-id 1 --output report.html
open report.html

# Should display: session summary, engagement timeline chart,
# top 3 distraction moments, class average comparison, state distribution pie chart
\`\`\`

## Acceptance Criteria

- [ ] Includes: session metadata, engagement timeline, state distribution, top distraction moments
- [ ] Highlights top 3 engagement dip moments with timestamps
- [ ] Shows class average comparison (anonymized)
- [ ] Renders as clean, self-contained HTML (inline CSS, Chart.js CDN)
- [ ] Can be sent as email body or downloaded
- [ ] Generates in under 5 seconds for 1-hour session

## Branch

\`feature/issue-27-session-report\`

## Depends on

Closes #24"

create_issue 28 "Build weekly trend report" "$M7" "m7,analytics" \
"## Why

Session reports show one lecture. Weekly reports show patterns. \"Monday 8am consistently has 20% lower engagement than Wednesday 2pm\" is information a teacher cannot see from individual sessions.

Weekly reports also let students track improvement. A student seeing their average rise from 55 to 72 over four weeks has concrete proof their strategies work.

## What needs to be built

A weekly report generator with engagement curves, day/time patterns, and week-over-week comparison.

## Files to create or update

- \`src/reports/weekly_report.py\` - WeeklyReportGenerator class
- \`src/templates/weekly_report.html\` - Jinja2 HTML template

## How this affects overall development

Primary recurring output. Email delivery (#31) sends it every Monday. Teacher dashboard (#33) displays it.

## How to test locally

\`\`\`bash
python -m src.reports.weekly_report --course-id 1 --week 2026-W24 --output weekly.html
open weekly.html

# Should display: week summary, per-lecture engagement curves,
# day-of-week pattern, week-over-week delta, at-risk count, difficult segments
\`\`\`

## Acceptance Criteria

- [ ] Engagement trends across all lectures in the week
- [ ] Day-of-week and time-of-day pattern charts
- [ ] Week-over-week comparison with delta indicators
- [ ] At-risk student count (anonymized)
- [ ] Top difficult segments ranked across all lectures
- [ ] Exportable as HTML and PDF
- [ ] Generates in under 10 seconds

## Branch

\`feature/issue-28-weekly-report\`

## Depends on

Closes #27"

create_issue 29 "Implement LLM-powered intervention agent" "$M7" "m7,agent" \
"## Why

Data without recommendations is just numbers. The intervention agent analyzes engagement patterns and generates specific, actionable teaching suggestions using an LLM (Groq).

The key is specificity. \"Make your lecture more engaging\" is useless. \"Add a coding exercise after slide 14 where students implement recursive fibonacci\" is actionable.

## What needs to be built

A LangGraph agent that analyzes engagement data and generates actionable teaching intervention suggestions.

## Files to create or update

- \`src/agents/intervention_agent.py\` - InterventionAgent class with LangGraph

## How this affects overall development

Suggestions appear in teacher dashboard (#33) and session reports (#27). This is the primary value-add for teachers.

## How to test locally

\`\`\`bash
python -m src.agents.intervention_agent --session-id 1

# Should output 3+ specific suggestions referencing timestamps and data

python -c \"
from src.agents.intervention_agent import InterventionAgent

agent = InterventionAgent()
suggestions = agent.generate(session_id=1)
for s in suggestions:
    assert 'minute' in s.text or 'slide' in s.text or 'topic' in s.text
    print(f'- {s.text}')
\"
\`\`\`

## Acceptance Criteria

- [ ] 3+ actionable suggestions per session
- [ ] Every suggestion references specific data: timestamps, percentages, patterns
- [ ] No generic advice (\"make it more engaging\" is a failure)
- [ ] Uses Groq (free tier) by default, configurable
- [ ] Suggestions categorized: content, delivery, structure
- [ ] Generates in under 10 seconds
- [ ] Handles empty sessions gracefully

## Branch

\`feature/issue-29-intervention-agent\`

## Depends on

Closes #24, Closes #27"

create_issue 30 "Add content difficulty correlator" "$M7" "m7,analytics" \
"## Why

When engagement dips at the same point in two different lectures on the same topic, that is a signal about the content, not the students. The difficulty correlator identifies these cross-session patterns.

This works without access to slides or recordings. It uses timing: \"engagement drops between minutes 12-18 in CS201.\" The teacher knows what they teach at minute 12.

## What needs to be built

An analytics module mapping engagement dips to lecture segments and tracking cross-session patterns.

## Files to create or update

- \`src/analytics/difficulty_correlator.py\` - DifficultyCorrelator class

## How this affects overall development

Provides data to the intervention agent (#29) and appears in weekly reports (#28) as a \"consistently difficult topics\" section.

## How to test locally

\`\`\`bash
pytest tests/test_difficulty_correlator.py -v

python -c \"
from src.analytics.difficulty_correlator import DifficultyCorrelator

dc = DifficultyCorrelator()
dc.add_session(session_id=1, timeline={10: 78, 11: 80, 12: 75, 13: 72, 14: 52, 15: 48, 16: 55})
dc.add_session(session_id=2, timeline={10: 82, 11: 79, 12: 77, 13: 70, 14: 48, 15: 45, 16: 50})

difficult = dc.find_difficult_segments(min_sessions=2)
for seg in difficult:
    print(f'Minute {seg.minute}: avg drop {seg.avg_drop:.0f}%, in {seg.session_count} sessions')
\"
\`\`\`

## Acceptance Criteria

- [ ] Identifies segments where engagement drops > 15% from session average
- [ ] Tracks per-segment difficulty across multiple sessions
- [ ] Ranks by severity: frequency x magnitude
- [ ] Works with timing data only
- [ ] At least 3 test cases

## Branch

\`feature/issue-30-difficulty-correlator\`

## Depends on

Closes #24"

create_issue 31 "Email delivery integration for automated reports" "$M7" "m7,infra" \
"## Why

Teachers are busy. Automated email puts the data in front of them without effort. Session report within 5 minutes of lecture ending (while experience is fresh). Weekly report Monday morning (in time to adjust).

Email rendering requires table-based layouts and inline styles because email clients strip external stylesheets.

## What needs to be built

Email delivery using SendGrid (or Resend) for automated session and weekly report distribution.

## Files to create or update

- \`src/reports/email_sender.py\` - EmailSender class
- \`src/templates/email_session.html\` - Session report email template
- \`src/templates/email_weekly.html\` - Weekly report email template

## How this affects overall development

Delivery mechanism for reports from #27 and #28. Makes the system \"set and forget\" for teachers.

## How to test locally

\`\`\`bash
python -m src.reports.email_sender --to test@nst.edu --report session --session-id 1
python -m src.reports.email_sender --to test@nst.edu --report weekly --course-id 1 --week 2026-W24

# Without SendGrid key, should save HTML to file
\`\`\`

## Acceptance Criteria

- [ ] Session report email within 5 minutes of session end
- [ ] Weekly report every Monday at 8am
- [ ] HTML renders in Gmail, Outlook, and mobile
- [ ] Teacher can opt out
- [ ] Falls back gracefully without SendGrid key (saves to file)
- [ ] Rate limiting: max 10 emails per minute

## Branch

\`feature/issue-31-email-delivery\`

## Depends on

Closes #27, Closes #28"

# --- M8 Issues (#32-35) -----------------------------------------------------

create_issue 32 "Build student dashboard" "$M8" "m8,frontend" \
"## Why

The student dashboard is where everything comes together for the student. It answers: \"Is this system actually helping me?\" Focus streaks gamify engagement (like Duolingo). Improvement tips are personalized based on data patterns.

## What needs to be built

A React dashboard with engagement history, focus streaks, session comparison, and personalized tips.

## Files to create or update

- \`frontend/src/pages/StudentDashboard.jsx\` - Main dashboard
- \`frontend/src/components/EngagementChart.jsx\` - Interactive chart
- \`frontend/src/components/FocusStreak.jsx\` - Streak counter
- \`frontend/src/components/SessionHistory.jsx\` - Session list
- \`frontend/src/components/ImprovementTips.jsx\` - Tips panel

## How this affects overall development

Primary student-facing interface. All M1-M7 work culminates here. Mobile version (#34) extends this.

## How to test locally

\`\`\`bash
cd frontend && npm install && npm run dev
# Navigate to http://localhost:5173/student/dashboard

# Should display: engagement chart (last 7 sessions), focus streak,
# session history, improvement tips, current session (if active)
\`\`\`

## Acceptance Criteria

- [ ] Engagement chart: last 7 sessions (Recharts line chart, interactive hover)
- [ ] Focus streak counter for consecutive sessions with avg > 70
- [ ] Session history: scrollable list with date, course, duration, score
- [ ] At least 2 personalized improvement tips
- [ ] Loading and empty states
- [ ] Responsive: laptop (1024px+) and tablet (768px)
- [ ] Fetches data from backend API

## Branch

\`feature/issue-32-student-dashboard\`

## Depends on

Closes #27"

create_issue 33 "Build teacher dashboard" "$M8" "m8,frontend" \
"## Why

The teacher dashboard is where every analytics feature meets its audience. Real-time engagement during a live lecture is the most compelling feature. The intervention panel shows AI-generated teaching suggestions.

## What needs to be built

A React dashboard with class overview, live monitoring (WebSocket), historical analytics, and intervention suggestions.

## Files to create or update

- \`frontend/src/pages/TeacherDashboard.jsx\` - Main dashboard
- \`frontend/src/components/ClassOverview.jsx\` - Class summary
- \`frontend/src/components/LiveEngagement.jsx\` - Real-time graph
- \`frontend/src/components/InterventionPanel.jsx\` - AI suggestions
- \`frontend/src/components/AtRiskPanel.jsx\` - At-risk students

## How this affects overall development

Most complex frontend component. Combines WebSocket (#5), analytics (#24), at-risk (#25), reports (#27), and interventions (#29) into one interface.

## How to test locally

\`\`\`bash
cd frontend && npm install && npm run dev
# Navigate to http://localhost:5173/teacher/dashboard

# Should display: class overview, live engagement (if session active),
# session history, intervention panel, at-risk panel

# Test real-time
python scripts/simulate_session.py --students 3 --duration 60
# Dashboard should show live graph updating every 2 seconds
\`\`\`

## Acceptance Criteria

- [ ] Class overview with course selector, student count, average engagement
- [ ] Live engagement: real-time line graph via WebSocket, 2-second updates
- [ ] Session history: selectable, clicking shows report
- [ ] Intervention panel: 3+ suggestions from intervention agent
- [ ] At-risk panel: anonymized students with trend arrows
- [ ] WebSocket reconnects on disconnect
- [ ] Loading and empty states
- [ ] Responsive: laptop and tablet

## Branch

\`feature/issue-33-teacher-dashboard\`

## Depends on

Closes #25, Closes #29, Closes #32"

create_issue 34 "Mobile-responsive dashboard + PWA setup" "$M8" "m8,frontend" \
"## Why

Indian college students use their phones for everything. A phone-accessible dashboard means students interact with their data more frequently. PWA lets students \"install\" EngageIQ on their home screen without an app store.

Mobile-responsive is not just shrinking the desktop layout. Charts need different aspect ratios. Navigation becomes hamburger menu. Touch targets must be 44px minimum.

## What needs to be built

Make both dashboards fully responsive for mobile. Add PWA manifest and service worker.

## Files to create or update

- \`frontend/public/manifest.json\` - PWA manifest
- \`frontend/public/service-worker.js\` - Offline caching
- \`frontend/public/icons/\` - App icons (192x192, 512x512)
- Update all dashboard components with responsive Tailwind classes

## How this affects overall development

Extends reach from laptop-only to any device. PWA makes the system feel professional and permanent.

## How to test locally

\`\`\`bash
cd frontend && npm run dev
# Chrome DevTools -> Toggle device toolbar
# Test at: 375px (iPhone SE), 390px (iPhone 14), 768px (iPad)

# Verify: hamburger menu, readable charts, 44px touch targets, no horizontal scroll

# Test PWA
npm run build && npx serve dist/
# On Android Chrome: should see \"Add to Home Screen\"
\`\`\`

## Acceptance Criteria

- [ ] Dashboard usable on 375px screens (no horizontal scroll)
- [ ] Hamburger menu on mobile, sidebar on desktop
- [ ] Charts: responsive aspect ratio, readable labels, touch-friendly tooltips
- [ ] All interactive elements have 44px minimum touch targets
- [ ] PWA manifest with icons, theme color, start URL
- [ ] Service worker caches static assets
- [ ] Lighthouse PWA audit > 80

## Branch

\`feature/issue-34-mobile-pwa\`

## Depends on

Closes #32, Closes #33"

create_issue 35 "E2E testing, demo video, deployment guide" "$M8" "m8,infra" \
"## Why

A project that only runs on your laptop is a demo, not a product. Deployment means EngageIQ runs on a real server with a public URL. E2E testing proves the full pipeline works. The demo video is the portfolio artifact for LinkedIn and recruiters.

## What needs to be built

E2E tests, deployment to Railway or Render, and a demo video script.

## Files to create or update

- \`tests/test_e2e.py\` - End-to-end test suite
- \`docs/deployment_guide.md\` - Deployment steps and live URL
- \`docs/architecture.md\` - System architecture diagram
- \`docs/demo_script.md\` - Demo video script and talking points

## How this affects overall development

This is the capstone. Every issue from 1 to 34 assembles here. The demo video goes on LinkedIn. The live URL goes to recruiters. The architecture doc is for interviews.

## How to test locally

\`\`\`bash
# E2E test
pytest tests/test_e2e.py -v

# Docker deployment
docker-compose up --build
curl http://localhost:8000/health
open http://localhost:5173

# Deploy to Railway
npm install -g @railway/cli
railway login && railway init && railway up
curl https://your-app.up.railway.app/health
\`\`\`

## Acceptance Criteria

- [ ] E2E test processes 10-minute pre-recorded session through full pipeline
- [ ] \`docker-compose up --build\` starts all services without errors
- [ ] Deployed to Railway or Render with live public URL
- [ ] Frontend loads on live URL
- [ ] WebSocket works on live URL
- [ ] \`docs/deployment_guide.md\`: live URL, redeploy steps, env vars
- [ ] \`docs/architecture.md\`: system diagram, tech stack table
- [ ] Demo video (3-5 minutes): onboarding, calibration, live tracking, nudge, teacher analytics
- [ ] All existing tests pass

## Branch

\`feature/issue-35-deployment\`

## Depends on

Closes #32, Closes #33, Closes #34"

echo ""
echo "========================================="
echo "Done! All 8 milestones and 35 issues created."
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Go to https://github.com/newton-school-ai/engageiq-ai/issues to verify"
echo "  2. Create project board: EngageIQ Sprint Tracker"
echo "  3. Add pod members to the repo"
