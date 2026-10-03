# Web app setup and validation

## Setup

Use Python 3.12. From the repository root on Windows:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python whatever/manage.py migrate
python whatever/manage.py runserver
```

Open http://localhost:8000/. Camera access requires localhost or HTTPS. The
repository includes the MediaPipe task, classifier and ordered feature list.
NumPy is pinned to 2.2.6 to satisfy the existing SciPy 1.14.1 requirement of
NumPy below 2.3. Python 3.14 is not the supported environment for these pins.

This remains a controlled research prototype: students and teachers can register
themselves, and teachers manage a shared student/class directory. Assign student
classes before creating exams. New exams stay closed until questions are ready;
open them from exam settings. Each teacher can access only their own exams,
attempts, diagnostics and monitoring evidence.

## Student experience

The light academic interface uses consistent spacing, visible focus indicators,
large answer targets, descriptive errors, responsive layouts and clear actions.
Exam taking and calibration are intended for laptops/desktops. General account,
dashboard, results and teacher pages adapt to smaller screens.

Exam preparation checks class, availability, access code and remaining attempts.
Camera permission and calibration occur before an attempt or timer is created.
Students see their webcam preview and technical readiness; model classifications,
flagged events and the three diagnostic dots are available to the owning teacher.
Monitoring signals support human review and do not determine exam scores.

Calibration sets a head baseline, then measures center, top, bottom, left and right
using 60 fresh face-and-eye samples per point. Space advances a completed step;
it does not skip collection or automatically start the exam. The next point has
a two-second countdown. A Continue button provides the same action. The modal
keeps keyboard focus within the setup, ignores held-key repeats, and supports
returning to the camera check. Changing cameras restarts calibration.

The exam shows all questions, a sticky timer, answered count, question links,
clear-answer controls and explicit Unsaved/Saving/Saved states. Answers persist
on the server, including cleared answers. Refresh restores them. A second tab
is read-only until the student explicitly takes over, which marks monitoring
as interrupted and restores the current server answers.

An attempt ends at the earlier of its allotted time or the exam availability
deadline. Leaving or disconnecting does not pause it. The server rejects answers
after expiry and grades saved answers when the student next contacts the server;
the browser submits automatically at expiry. There is no background deadline
scheduler while the student is completely offline. Submission is idempotent,
accepts partial/unanswered work and provides immediate scores and correct answers,
including for exams with retakes. Questions freeze after the first attempt.

MCQ, True/False, numerical and fill-in-the-blank questions can include supporting
images. Image descriptions support screen readers and question images can be
enlarged. Existing standalone IMG questions must be converted before an exam can
open. MCQ editing validates distinct choices and an explicit correct answer.

## Monitoring continuity and research boundaries

Run one Daphne process/worker. The in-process registry serializes each native
tracking pipeline and retains it for 60 seconds after a disconnect. Reconnecting
reuses that pipeline. A restart or longer interruption does not recreate a
previously started exam pipeline or overwrite its evidence; model analysis is
shown as unavailable when monitoring is incomplete. Redis alone will not make
the native pipeline safe across multiple workers. A distributed worker service
would be a separate implementation.

WebSockets require an authenticated student, the correct preparation/attempt,
an active writer lease and an allowed origin. Raw session media paths are blocked;
the owning teacher's endpoints serve logs, heatmaps and clips. A deployment must
preserve this restriction at the reverse proxy/object storage layer too.

The classifier artifact, feature order, rule thresholds, heatmap formulas and
40% head / 60% eye blend are unchanged. Staff diagnostics read the blend weights
and screen dimensions from the pipeline. CSV filenames include microseconds so
setup and exam logs cannot collide within the same second.

The calibration sampler previously counted cached eye measurements when current
face/eye detection failed. It now counts only fresh measurements from a frame
with a face and eyes. This intentional correction and the viewport target layout
can affect calibration distributions. Real hardware and research accuracy must
be revalidated before collecting comparable study data. Automated tests verify
fresh-sample gating and stage controls; they do not establish tracking accuracy.

Before upgrading an existing database, back it up and finish active exams. The
migration preserves the latest duplicate answer (including clears), adds one
answer per attempt/question, backfills legacy timing and marks legacy active
monitoring as interrupted. It does not grant a fresh exam timer.

## Validation

```powershell
python -m pip install -r requirements-dev.txt
python -m pip check
python whatever/manage.py check
python whatever/manage.py makemigrations --check --dry-run
python whatever/manage.py test homepage studentside teacherside camera
```

Browser tests use an isolated Django test database, synthetic camera stream and
simulated tracking WebSocket. They verify real page interactions and HTTP answer
state, not physical camera accuracy. Install Chromium, or use an installed Edge:

```powershell
python -m playwright install chromium
$env:MAKITEST_BROWSER_TESTS='1'
# Optional Windows alternative to downloaded Chromium:
$env:MAKITEST_BROWSER_EXECUTABLE='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
python whatever/manage.py test studentside.browser_tests
```

The browser suite covers autosave, first-option radio answers, clearing, refresh,
tab conflict/takeover, partial submission, timeout without confirmation, Space
calibration, held-key handling and responsive page widths. Screenshots are saved
under ignored `.validation/screenshots/` for visual inspection. Test accounts and
artifacts never enter the normal database.

Validation on Windows/Python 3.12: all 45 backend/authorization/migration/calibration
tests and all four browser scenarios passed. Dependency consistency, Django
system/migration checks and JavaScript syntax checks passed. The real MediaPipe
pipeline initialized, rejected a no-face calibration baseline and finalized;
the existing trained classifier loaded and predicted from synthetic artifacts.
Live student camera calibration, device switching and detection accuracy still
require a hardware trial under representative lighting and seating conditions.
