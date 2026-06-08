# Pod Guide

Pod structure, collaboration model, sprint timeline, and Q&A rules for EngageIQ AI.

---

## Pod Members

| Role | Name | GitHub Username | Responsibility |
|------|------|----------------|---------------|
| Faculty (Product Manager) | TBD | TBD | Reviews milestone completions. Only person who merges dev into main. |
| Maintainer (Student Leader) | TBD | TBD | Reviews PRs, merges into dev. Does NOT raise PRs or write code. |
| Contributor 1 | TBD | TBD | Works on every issue alongside all other contributors. |
| Contributor 2 | TBD | TBD | Works on every issue alongside all other contributors. |
| Contributor 3 | TBD | TBD | Works on every issue alongside all other contributors. |
| Contributor 4 | TBD | TBD | Works on every issue alongside all other contributors. |

---

## Collaboration Model

Every contributor works on every issue. No one "owns" a module. Everyone learns the full stack.

### How It Works

For each issue, the team picks one of two approaches:

**Option A: Competitive PRs (individual learning)**
1. All 4 contributors independently implement the issue on their own feature branch.
2. Each raises a separate PR targeting dev.
3. Team reviews all PRs together, discusses tradeoffs.
4. Maintainer merges the best implementation.
5. Others learn from the winning PR and review comments.

**Option B: Collaborative PR (team learning)**
1. Contributors discuss the approach together (call, chat, or in-person).
2. They agree on design, split the coding work, and collaborate on one branch.
3. One PR is raised with all contributors as co-authors.
4. Maintainer reviews and merges.

The team decides per-issue which option to use. Some issues are better for competition (straightforward implementations where multiple approaches are interesting), others for collaboration (complex issues where discussion adds more value than individual attempts).

### Branch Naming

**Competitive PRs:**
```
feature/issue-8-facemesh-alice
feature/issue-8-facemesh-bob
feature/issue-8-facemesh-charlie
feature/issue-8-facemesh-diana
```

**Collaborative PR:**
```
feature/issue-8-facemesh
```

### Co-authoring a Collaborative PR

Add co-authors in the commit message:
```
feat(detection): integrate MediaPipe Face Mesh with 468 landmarks

Co-authored-by: Alice <alice@nst.edu>
Co-authored-by: Bob <bob@nst.edu>
Co-authored-by: Charlie <charlie@nst.edu>
Co-authored-by: Diana <diana@nst.edu>
```

---

## Role Definitions

### Faculty (Product Manager)
- Conducts Q&A sessions every 2-3 days per milestone.
- Reviews milestone-complete PRs from dev to main.
- Only person who merges dev into main.
- Does not write code or review individual PRs.

### Maintainer (Student Leader)
- Reviews all PRs targeting dev.
- Merges approved PRs into dev.
- Does NOT write code or raise PRs.
- Ensures code quality, consistency, and that all tests pass.
- Resolves merge conflicts between competing PRs.
- Facilitates team discussions on collaborative issues.
- Tracks sprint progress on the project board.

### Contributors (4 students)
- Work on every issue (no issue is assigned to just one person).
- Raise PRs (individually or collaboratively).
- Review each other's PRs (minimum 2 approvals required).
- Defend their implementations in Q&A sessions.
- Any contributor may be asked to explain any part of the codebase.

---

## Merge Flow

```
Contributors work on feature branches
        |
        v
Raise PR(s) targeting dev
        |
        v
2+ contributors review + approve --> Maintainer merges into dev
        |
        v
After milestone complete, Maintainer raises PR: dev --> main
        |
        v
Faculty reviews + merges into main
```

---

## Sprint Timeline

All 4 contributors work on every milestone together. Timeline is per milestone, not per person.

| Week | Milestone | Issues | Key Deliverable |
|------|-----------|--------|----------------|
| Week 1 | M1: Scaffold + Webcam Pipeline | #1-7 | DB schema, CI, webcam capture, user API |
| Week 2 | M2: Face Detection + Gaze | #8-11 | MediaPipe integration, head pose, gaze, face selector |
| Week 3 | M3: Drowsiness + Expression | #12-15 | EAR drowsiness, yawn, expression classifier, training notebook |
| Week 4 | M4: Engagement Scoring | #16-19 | Multi-signal scorer, state machine, filter, calibration |
| Week 5 | M5: Nudge Agent | #20-23 | Nudge decisions, delivery, effectiveness, preferences UI |
| Week 6 | M6: Teacher Analytics | #24-26 | Class aggregator, at-risk identifier, CSV/JSON export |
| Week 7 | M7: Reports + Interventions | #27-31 | Session/weekly reports, LLM agent, email delivery |
| Week 8 | M8: Dashboard + Demo | #32-35 | React dashboards, PWA, E2E tests, demo video |

---

## Q&A Schedule

Faculty (Product Manager) conducts Q&A sessions every 2-3 days per active milestone.

### Format
1. Any contributor may be called to demo what was built (live or recorded).
2. Faculty asks defense questions from MILESTONES.md to any team member at random.
3. Contributor explains design decisions and tradeoffs.
4. Faculty provides feedback and approves or requests changes.

### Rules
- Every contributor must be able to explain every merged PR, not just the ones they wrote.
- Come prepared. Read the defense questions before Q&A.
- "I don't know" is acceptable once. Come back with the answer next session.
- Code must be pushed to feature branches before Q&A (faculty will check GitHub).
- If blocked, raise it immediately in the pod channel. Do not wait for Q&A.

---

## Review Rules

### For Competitive PRs
- All contributors must review all competing PRs (not just their own).
- Comment on what you like, what you would do differently, and any bugs you spot.
- Vote for the best implementation with a thumbs-up reaction on the PR.
- Maintainer considers votes, code quality, test coverage, and readability before merging.
- After merge, all contributors should read the winning implementation to learn from it.

### For Collaborative PRs
- At least 2 contributors who worked on the PR must review the final code.
- Maintainer checks that all co-authors actually contributed (not just added their name).
- Every co-author must be able to explain the full PR in Q&A.

---

## Daily Standup (Async)

Post in the pod channel daily (2-3 lines):
1. What I did yesterday
2. What I am doing today
3. Am I blocked on anything

---

## How to Get Help

1. Check DEVELOPMENT_GUIDE.md first.
2. Search existing GitHub issues for similar problems.
3. Ask in pod channel with: what you tried, what error you got, relevant code snippet.
4. Discuss with other contributors - they are working on the same issue.
5. If blocked for > 4 hours, escalate to Maintainer.

---

NST Engineering - EngageIQ AI | Summer Profile Building Drive 2026
