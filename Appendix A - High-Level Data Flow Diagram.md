# Appendix A
## High-Level Data Flow Diagram of the MAKITEST System

### A.1 Purpose and scope

This appendix presents the high-level data flow of the MAKITEST Suspicious Exam Behavior Detection System (SEBDS). It describes how information moves among students, teachers and administrators, the browser-based application, its database, session-artifact storage, and the machine-learning prediction component.

The diagram represents the integrated Django web application. In this workflow, the student uses a standard web browser to access exams and, when monitoring is active, to provide camera frames and browser-reported events. The application processes those inputs to produce session artifacts and a classifier result for review. The separate desktop tracker and offline dataset-training workflow are not part of the web-session flow shown here.

The DFD is an implementation-level overview rather than a deployment topology. It shows logical processes and stores, not individual Django views, model fields, network infrastructure, or every validation rule.

### A.2 High-level DFD

```mermaid
%%{init: {"themeVariables": {"fontSize": "24px"}, "flowchart": {"nodeSpacing": 35, "rankSpacing": 45, "curve": "linear"}}}%%
flowchart TB
    Student[Student]
    Staff[Teacher / Administrator]

    subgraph MAKITEST["MAKITEST web application"]
        direction TB
        P1(["1. Authenticate"])
        P2(["2. Manage exams"])
        P3(["3. Deliver exam"])
        P4(["4. Monitor session"])
        P5(["5. Predict session"])
        P6(["6. Review attempt"])

        P1 --> P3
        P2 --> P3
        P3 --> P4
        P3 --> P5
        P5 --> P6
    end

    D1[("D1: Application database")]
    D2[("D2: Session files")]
    D3[("D3: Model and feature schema")]

    Student -->|"Credentials"| P1
    P1 -->|"Role-based access"| Student
    Staff -->|"Exam and question changes"| P2
    P2 -->|"Management results"| Staff

    Student -->|"Answers and submission"| P3
    P3 -->|"Questions, status and score"| Student

    Student -->|"Camera frames and browser events"| P4
    P4 -->|"Calibration and live feedback"| Student

    P1 <-->|"Accounts and roles"| D1
    P2 <-->|"Exams and questions"| D1
    P3 <-->|"Attempts, answers and scores"| D1
    P4 -->|"Calibration and monitoring metadata"| D1
    P4 -->|"Logs, heatmap and event clips"| D2

    D2 -->|"Exam log and heatmap"| P5
    D3 -->|"Classifier and feature order"| P5
    P5 -->|"Prediction artifact"| D2
    P5 -->|"Label, probabilities and status"| D1

    Staff -->|"Review request"| P6
    D1 -->|"Attempt and prediction data"| P6
    D2 -->|"Available session evidence"| P6
    P6 -->|"Review details"| Staff
```

### A.3 Description of entities, processes, and stores

#### External entities

**Student.** The student authenticates through the web application, views eligible exams, completes and submits answers, and participates in the browser-based calibration and monitoring flow. Subject to browser permission and the active session, the client sends camera frames and browser-reported monitoring events to the application. The browser is the source of those inputs; the diagram does not imply that the system captures operating-system-wide activity.

**Teacher or administrator.** Teaching staff create and manage exams and questions, configure exam access, and review submitted attempts. Review information can include scores, prediction status, and available monitoring artifacts. Administrative operations are grouped with teacher-facing management in this high-level view.

#### Application processes

**1. Authenticate and route users.** The application verifies account credentials and uses account roles to direct users to the relevant student, teacher, or administrative pages. Account records and web-session state are maintained through the application database and Django session facilities.

**2. Prepare and manage exams.** Teachers create or update exams and their questions, including access and class-related settings. The process stores exam content in the database and makes eligible exam information available to students.

**3. Deliver exam and record answers.** The application presents exam questions, tracks an attempt, accepts saved answers, and finalizes the attempt when submitted or otherwise completed. It calculates the score from the recorded answers and exam key. Attempt and answer records, along with prediction fields, are stored in the database.

**4. Calibrate and monitor session.** Before monitored exam activity, the browser guides the student through calibration. During the exam, browser-captured camera frames are sent to the monitoring service over a WebSocket connection. The server-side gaze pipeline processes frames for face and eye landmarks, gaze position or direction, head pose, heatmap accumulation, and rule-based event scoring. Browser-reported events, such as selected key combinations or loss of page focus, may also be received. Calibration thresholds and monitoring status are associated with the student or attempt; generated logs and other session evidence are written to session storage.

**5. Register artifacts and predict.** At the end of a monitored attempt, the application registers the session’s files and uses the final exam-session CSV and heatmap as prediction inputs. The prediction component combines extracted session features with the configured feature order and trained classifier. It records prediction status and result fields against the attempt and writes a prediction JSON artifact when produced. If required inputs or inference are unavailable, the attempt can retain an unavailable or failed prediction status rather than treating the absence of a result as a positive prediction.

**6. Review attempts and evidence.** Teachers request a student-attempt review. The application retrieves attempt, score, and prediction information from the database and obtains the registered session artifacts from file storage when available. It presents these materials as review information to support staff judgment; a classifier result is not, by itself, a determination of misconduct.

#### Data stores

**D1: Application database.** In the current project configuration, Django uses SQLite. The database contains user and role data, exam and question records, student answers, attempt and score information, calibration-related records, and registered artifact paths and prediction fields. The diagram groups these logical records into one store for readability.

**D2: Session and media files.** The application writes uploaded or generated media under its media directory. A proctoring session may contain calibration data, timestamped CSV logs, a heatmap image, violation video clips, and a prediction JSON artifact. The database keeps references to registered files; the files themselves are not represented as database rows containing their full contents.

**D3: Classifier and feature schema.** The prediction process reads the trained model (`suspicion_model.joblib`) and the expected input-column order (`feature_columns.json`) from application files. These are inputs to inference, not per-student session records.

### A.4 Principal data-flow sequence

The flow begins when a student authenticates and requests an exam. The application checks the relevant account, role, and exam information, then returns exam content for an eligible attempt. As the student answers questions, answer and attempt state is persisted. On submission, the application grades the stored answers and finalizes the attempt.

For monitored activity, the application establishes a session identifier and uses it to associate the calibration and exam-monitoring phases with the same session directory. The browser sends camera frames and supported browser events to the monitoring process. Calibration data and exam monitoring outputs are written as session files; attempt and calibration metadata are stored in the database. At finalization, the application registers available artifacts and requests session prediction using the exam log and heatmap—not the calibration log—as session evidence. The resulting status and prediction values are associated with the attempt, after which a teacher can review the attempt and its available evidence.

### A.5 Interpretation and system boundary

The diagram distinguishes **observations**, **derived artifacts**, and **application records**. Camera frames and browser events are inputs; gaze estimates, rule-triggered events, heatmaps, and session logs are derived outputs; answers, scores, attempt state, and prediction fields are persisted application records. This separation is important because an observed gaze direction or a model-generated label is an indicator for review, not proof that a student engaged in misconduct.

The implemented monitoring path is browser-based and focuses on face and eye landmark tracking, gaze estimation, head-pose analysis, heatmaps, rule-based event scoring, and browser-reported events. It does not represent facial recognition, liveness detection, object or hand detection, audio analysis, or a global keyboard hook as implemented components. Data retention, production hosting, and multi-worker deployment are outside the scope of this logical DFD.

# Appendix B
## Development Timeline of the MAKITEST System

### B.1 Basis of the timeline

This timeline synthesizes the dated Git commit histories of the current repository and the two related repositories, [Setup-and-Testing](https://github.com/pfftbuh/Setup-and-Testing) and [DjangoCEASARWebApp](https://github.com/pfftbuh/DjangoCEASARWebApp), together with the current project structure. It groups related commits into system-development workstreams rather than listing every commit individually. The dates indicate when a notable implementation or documentation change is recorded in a repository; they should not be interpreted as the exact start and finish dates of all work.

Across the three histories, the chart covers November 24, 2025, through October 12, 2026. To avoid displaying empty intervals, a workstream with no subsequent notable update is extended to the next relevant milestone or the end of its observed history. These extensions are a presentation convention and do not imply continuous development on every intervening day. Parallel workstreams may overlap.

### B.2 Gantt chart

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}, "themeCSS": ".sectionTitle { font-size: 14px !important; } .tick text { font-size: 18px !important; }", "gantt": {"barHeight": 28, "barGap": 8, "leftPadding": 250, "rightPadding": 24, "topPadding": 42, "fontSize": 18, "sectionFontSize": 14, "taskFontSize": 16}}}%%
gantt
    title MAKITEST development across the three repository histories
    dateFormat YYYY-MM-DD
    axisFormat %b %Y

    section Standalone: Setup-and-Testing
    Initial tracker and eye-tracking experiments :s1, 2025-11-24, 2025-12-01
    Tracking, calibration and data-capture foundation :s2, 2025-12-01, 2026-07-03
    Camera and exam-session recording; CSV and heatmap outputs :s3, 2026-07-03, 2026-08-10

    section Earlier web app: DjangoCEASARWebApp
    Face and eye tracking; gaze estimation and calibration :w1, 2026-03-24, 2026-04-28
    Screen-position mapping, event scoring and video evidence :w2, 2026-04-28, 2026-08-24
    Session organization, heatmaps, feature extraction and model prediction :w3, 2026-08-24, 2026-09-25
    Dataset evaluation, prediction refinements and heatmap overlay :w4, 2026-09-25, 2026-10-12

    section Current web app: New-MAKITEST-Web-App
    Webcam, face and eye tracking; calibration pipeline :a1, 2026-08-12, 2026-08-17

    section Web application
    Django project structure, authentication and student flow :a2, 2026-08-13, 2026-08-17
    Teacher exam authoring, questions and access management :a3, 2026-08-14, 2026-08-18
    Exam attempts, answer submission and results :a4, 2026-08-17, 2026-08-23

    section Proctoring and prediction
    Browser calibration and live monitoring integration :a5, 2026-08-17, 2026-08-23
    Session artifacts, teacher review and prediction integration :a6, 2026-08-18, 2026-09-12
    Feature extraction, model training and evaluation :a7, 2026-09-12, 2026-10-03

    section User experience and reliability
    Student scores, guided calibration and durable exam flow :a8, 2026-10-01, 2026-10-05
    Teacher authorization and camera setup refinements :a9, 2026-10-05, 2026-10-12

    section Research documentation
    Dataset, heatmap, evaluation and video-analysis write-up :a10, 2026-09-12, 2026-10-03
    System architecture, data model and findings revisions :a11, 2026-10-03, 2026-10-12
```

### B.3 Interpretation of development phases

**Standalone prototype — [Setup-and-Testing](https://github.com/pfftbuh/Setup-and-Testing) (November 24, 2025–August 10, 2026).** The earliest recorded work covers the first tracker and iris-tracking experiments, followed by calibration, gaze tracking, and data-capture changes. Later commits record camera and exam-session handling and the addition of CSV and heatmap outputs. The December-to-July bar carries the earlier tracking and data-capture work forward to the next notable recorded update, as requested; it does not claim that development occurred continuously during that interval.

**Earlier web-app lineage — [DjangoCEASARWebApp](https://github.com/pfftbuh/DjangoCEASARWebApp) (March 24–October 12, 2026).** The available commit history records face and eye tracking, gaze estimation, calibration, and data collection from March onward. Subsequent milestones add screen-position mapping, event-based suspicion scoring, and video evidence. August commits organize session output and introduce heatmap feature extraction, model training, and prediction; later commits revise dataset observations and prediction outputs and add heatmap-overlay work.

**Current web application — [New-MAKITEST-Web-App](https://github.com/pfftbuh/New-MAKITEST-Web-App) (August 12–October 12, 2026).** The repository history records the Django web application foundation, user authentication, student and teacher workflows, exam authoring, attempts, answers, grading, and results. Monitoring is integrated with calibration and browser-based exam sessions; the application subsequently registers session artifacts, supports teacher evidence review, and connects session data to prediction.

**Feature engineering and model evaluation (August 27–October 3, 2026).** Commits across the earlier web-app and current project histories record heatmap-derived features, Random Forest training and evaluation, prediction output, configurable evaluation procedures, and dataset documentation. These changes connect session-level evidence to structured features and classifier output.

**User experience, authorization, and reliability (October 1–12, 2026).** Work recorded in the current web-app history includes a student scores page, faster camera capture settings, guided calibration and exam-flow improvements, consistent interface labels, teacher authorization checks, and clearer camera setup instructions.

**Research documentation (September 12–October 12, 2026).** Manuscript updates document video evidence, gaze and heatmap analysis, model evaluation, dataset fields, system architecture, data modeling, and later interpretation of results. This is shown separately from software implementation because manuscript changes form a parallel research-documentation stream.

### B.4 Reading the chart

The chart is a high-level reconstruction from the three linked Git histories and the current project structure, not a project-management schedule. Related workstreams overlap because the repositories represent the standalone prototype, an earlier web-app lineage, and the current integrated web application. Some histories also contain merges or mirrored development; overlapping bars therefore indicate related recorded milestones, not necessarily independent work. Where a bar bridges a period without a notable commit, the extension follows the convention stated in B.1 and should not be read as evidence of continuous work, exact feature-completion dates, effort, or deployment readiness.

# Appendix C
## Use-Case Model of the MAKITEST System

### C.1 Purpose and scope

This appendix presents the principal user goals supported by the MAKITEST web-application prototype. The use cases reflect the implemented Django applications and the study's focus on browser-based exam delivery and proctor assistance. “Teacher / Proctor” refers to the authorized teacher role in the application; the system supports staff review of monitoring indicators but does not automatically determine that misconduct occurred.

The model covers account access, teacher authorization, exam and question management, student exam preparation and completion, session monitoring, and review of submitted attempts. The standalone desktop tracker, offline model-training workflow, operating-system-wide keyboard capture, facial recognition, liveness detection, object detection, and hand tracking are outside this web-application boundary.

### C.2 Use-case diagram

```mermaid
%%{init: {"themeVariables": {"fontSize": "18px"}, "flowchart": {"nodeSpacing": 24, "rankSpacing": 32, "curve": "linear"}}}%%
flowchart LR
    Student[Student]
    Teacher[Teacher / Proctor]
    Admin[Administrator]

    subgraph System["MAKITEST web application"]
        direction TB
        UC1([Create account, sign in, and sign out])
        UC2([View eligible exams])
        UC3([Prepare exam and calibrate camera])
        UC4([Take exam and save answers])
        UC5([Submit exam and view results])
        UC6([View personal score history])
        UC7([Create and manage exams and questions])
        UC8([Configure exam access and class])
        UC9([Manage student class assignments])
        UC10([Review attempts and monitoring evidence])
        UC11([Authorize teacher accounts])
        UC12([Process session data and generate indicators])
    end

    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5
    Student --> UC6

    Teacher --> UC1
    Teacher --> UC7
    Teacher --> UC8
    Teacher --> UC9
    Teacher --> UC10

    Admin --> UC1
    Admin --> UC11

    UC3 --> UC4
    UC4 --> UC12
    UC5 --> UC12
    UC12 --> UC10
```

### C.3 Actors

| Actor | Role in the system |
|---|---|
| **Student** | Uses a student account to view exams assigned to the student's class, complete camera setup when required, take eligible exams, submit answers, and view personal results and scores. |
| **Teacher / Proctor** | Uses an authorized teacher account to manage their exams and questions, maintain student class assignments, and review exam attempts and available monitoring evidence. |
| **Administrator** | Uses an administrator account to authorize or revoke authorization for teacher accounts. |
| **MAKITEST web application** | Performs internal operations such as checking exam eligibility, saving answers and scores, processing session data, and producing monitoring artifacts and prediction indicators. These are system responsibilities, not additional human actors. |

### C.4 Use-case descriptions

| ID and use case | Actor(s) and preconditions | Main flow | Exceptions and constraints |
|---|---|---|---|
| **UC-01 — Account access** | Student, Teacher / Proctor, Administrator; user is signed out. | Register if needed → sign in → system routes by role → sign out. | Invalid credentials or registration data are rejected; unauthorized teachers cannot access teacher features. |
| **UC-02 — View eligible exams** | Student; signed in. | Open dashboard → view class-matched exams, availability and attempts → select an exam. | No class or matching exam means no exam is listed; closed, expired, or attempt-limited exams cannot be started. |
| **UC-03 — Prepare exam and calibrate camera** | Student; has selected an eligible exam. | Enter configured access code → create preparation session → grant camera permission and complete guided calibration → save calibration/session data. | Wrong code or incomplete setup prevents starting; camera availability and browser permission are required for calibration. |
| **UC-04 — Take exam and save answers** | Student; signed in, eligible, prepared and calibrated. | Start or resume attempt → answer questions while time is tracked and answers saved → browser sends available camera frames/events → system records processed monitoring indicators and evidence. | Expired attempts are finalized. Missing monitoring or prediction inputs do not prevent scoring; prediction status may be unavailable or failed. |
| **UC-05 — Submit exam and view results** | Student; has an active or completed attempt. | Submit or reach time limit → system finalizes and grades saved answers → associate available artifacts → display result and save to attempt history. | Repeated submission does not complete the same attempt twice; prediction may remain pending or be unavailable/failed when the score is ready. |
| **UC-06 — View personal score history** | Student; signed in. | Open scores → view own attempts and scores → select an attempt for available result details. | Students can access only their own attempt and score information. |
| **UC-07 — Create and manage exams and questions** | Authorized Teacher / Proctor; signed in. | Create exam with title, description, class, deadline, time/attempt limits and optional code → add/edit questions and answer keys → save validated changes. | New exams remain closed during preparation; incomplete or unsupported questions prevent opening. Teachers can manage only their own exams. |
| **UC-08 — Configure exam access and class** | Authorized Teacher / Proctor; signed in and owns the exam. | Set class, deadline, time/attempt limits and optional code → open or close exam → system applies settings to student eligibility. | Incomplete or unsupported questions prevent opening; class and availability rules restrict student access. |
| **UC-09 — Manage student class assignments** | Authorized Teacher / Proctor; signed in. | Search or browse student list → update class designation → system saves it for exam matching. | Only student class designation is managed through this workflow. |
| **UC-10 — Review attempts and monitoring evidence** | Authorized Teacher / Proctor; signed in; attempt belongs to an exam they own. | Open exam/student attempts → review answers, scores, prediction status and indicators → view/download registered CSVs, heatmaps, clips or session archive → make a human assessment. | Artifacts are shown only when registered. Gaze, event, rule-score and model outputs are review indicators, not proof or automatic misconduct decisions. |
| **UC-11 — Authorize teacher accounts** | Administrator; signed in. | Open authorization page → inspect teacher states → authorize or revoke a teacher → system saves the decision. | Unauthorized teachers cannot sign in to teacher features. |

### C.5 Scope notes and assumptions

- Role-specific web pages enforce student, authorized-teacher, and administrator access. A student can access only their own exam attempts and scores; teachers can manage only their own exams and review associated attempts.
- Exam availability is constrained by class designation, open/closed state, deadline, attempt limit, and any configured access code.
- The web monitoring flow uses browser-provided camera frames and browser-reported events. It does not imply unrestricted keyboard or operating-system monitoring, and the system does not automatically determine cheating.
- Camera WebSocket authentication is configurable in the current prototype; it may allow anonymous connections unless `GAZE_REQUIRE_AUTH` is enabled. This use-case model therefore describes the intended student workflow and does not claim that every deployment enforces authenticated WebSocket connections.
- The custom administrator workflow documented here covers teacher-account authorization. The broader user/exam database CRUD functions described as a role capability in the manuscript are not represented as custom use cases unless provided through separately configured Django administration.
