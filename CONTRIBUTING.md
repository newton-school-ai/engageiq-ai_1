# Contributing to EngageIQ AI

This document covers branch strategy, PR workflow, pod roles, and coding standards.

---

## Branch Strategy

```
main  (stable - only receives milestone-complete merges from dev)
 |
 +-- dev  (all feature branches merge here)
      |
      +-- feature/issue-N-short-name  (one branch per issue)
```

### Rules

1. Never push to main directly.
2. All PRs target dev.
3. Maintainer merges to main only after full milestone review.
4. One branch per issue. One PR per branch.

### Branch Naming

- Features: `feature/issue-6-mediapipe-facemesh`
- Fixes: `fix/issue-14-blink-filter`
- Docs: `docs/issue-2-db-schema`

### Creating a Branch

```bash
git checkout dev
git pull origin dev
git checkout -b feature/issue-6-mediapipe-facemesh
```

---

## PR Workflow

### Before Opening a PR

1. Your branch is up to date with dev:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout feature/issue-6-mediapipe-facemesh
   git rebase dev
   ```
2. All tests pass: `pytest tests/`
3. Code is formatted: `black src/ tests/` and `isort src/ tests/`
4. No lint errors: `flake8 src/ tests/`

### PR Template

Every PR must use the template in `.github/PULL_REQUEST_TEMPLATE.md`. Fill in:
- Which issue this closes (e.g., "Closes #6")
- What changed and why
- How to test it
- Screenshots or terminal output if applicable

### Review Process

**Competitive PRs (multiple PRs per issue):**
1. Each contributor opens their own PR targeting dev.
2. All other contributors review all competing PRs.
3. Minimum 2 approvals required.
4. Maintainer merges the best implementation after considering votes, quality, and tests.

**Collaborative PRs (one PR per issue):**
1. Team collaborates on one branch, one PR targeting dev.
2. Add all contributors as co-authors in commit message.
3. Minimum 2 approvals from team members who contributed.
4. Maintainer reviews and merges.

---

## Pod Roles

| Role | Permission | Responsibility |
|------|-----------|---------------|
| Faculty | Admin (org owner) | Reviews milestones. Only person who merges dev into main. |
| Maintainer | Maintain | Reviews PRs, merges into dev. Does NOT write code or raise PRs. |
| Contributor | Write | Works on every issue. Raises PRs (individually or collaboratively). Reviews peers' PRs. |

### How Everyone Works on Every Issue

- No issue is assigned to a single contributor. All 4 contributors work on all 35 issues.
- For each issue, the team decides: competitive PRs (each person submits) or collaborative PR (one team submission).
- Every contributor must be able to explain any part of the codebase in Q&A. Faculty will ask at random.
- This ensures full-stack learning. No one leaves the project knowing only "their module."

---

## Coding Standards

### Python

- Python 3.10+ required.
- Formatter: `black` with default settings (line length 88).
- Import sorting: `isort` with black profile.
- Linter: `flake8` with max line length 88.
- Type hints required on all function signatures.
- Docstrings required on all public functions and classes (Google style).

```python
def compute_ear(eye_landmarks: list[tuple[float, float]]) -> float:
    """Compute Eye Aspect Ratio from 6 eye landmarks.

    Args:
        eye_landmarks: List of 6 (x, y) tuples representing eye contour points.

    Returns:
        EAR value as float. Below 0.25 indicates closed eye.
    """
    ...
```

### Naming

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Testing

- Test files mirror source: `src/detection/drowsiness.py` -> `tests/test_drowsiness.py`
- Use pytest. Minimum one test per public function.
- Name tests clearly: `test_ear_below_threshold_returns_drowsy`

### Commits

- Format: `type(scope): description`
- Types: feat, fix, docs, test, refactor, chore
- Examples:
  - `feat(detection): add EAR-based drowsiness detector`
  - `fix(scoring): prevent false state flip on blink`
  - `docs(readme): add quick start section`
  - `test(nudge): add cooldown period tests`

### Frontend (React)

- Functional components with hooks only.
- Tailwind CSS for styling - no separate CSS files.
- Component files: `PascalCase.jsx`
- One component per file.

---

## Environment Setup

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for full setup instructions.

---

NST Engineering - EngageIQ AI | Summer Profile Building Drive 2026
