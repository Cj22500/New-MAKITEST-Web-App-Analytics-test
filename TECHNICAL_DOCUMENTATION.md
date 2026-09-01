# MAKITEST System & Tech Stack Technical Documentation

## Executive Summary
MAKITEST is a real-time, AI-driven dual gaze tracking and suspicious behavior detection proctoring platform. It monitors exam takers via webcams and browser event hooks to detect unauthorized behavior, off-screen gaze shifts, forbidden hotkeys, and multi-face scenarios during online assessments.

---

## Technical Architecture Overview

```
                      +---------------------------------------+
                      |           Browser / Client            |
                      | - HTML5 Canvas @ 10 FPS Frame Capture |
                      | - JS Keyboard & Blur Listener         |
                      | - Real-time Proctoring UI Panel       |
                      +-------------------+-------------------+
                                          |
                               WebSocket (ws://)
                                          |
                      +-------------------v-------------------+
                      |      Django Channels WebSocket        |
                      |         ProctorConsumer               |
                      +-------------------+-------------------+
                                          |
                                          | Thread Pool (sync_to_async)
                                          v
                      +---------------------------------------+
                      |         GazeSession Pipeline          |
                      | - FaceTrackProcessor (MediaPipe 3D)   |
                      | - EyeTrackProcessor (MediaPipe Eyes)  |
                      | - FaceAxisProcessor (Yaw / Pitch)     |
                      | - EyeScreenPosProcessor (EMA Gaze)    |
                      | - SuspicionScoringProcessor           |
                      | - HeatmapProcessor                    |
                      +-------------------+-------------------+
                                          |
                       +------------------+------------------+
                       |                                     |
                       v                                     v
         Session Storage (`sessions/`)             Database (SQLite / Django ORM)
         - `session_log_<ts>.csv`                  - `StudentExamAttempt`
         - `heatmap_<session_id>.png`              - `ProctoringSessionFiles`
         - `*.mp4` Violation Clips                 - `CustomUser` & `Exam`
                       |
                       +------------------+
                                          |
                                          v
                      +---------------------------------------+
                      |    Teacher / Admin Analytics System   |
                      | - ML Model Inference (`joblib`)       |
                      | - Aggregate Analytics Dashboard       |
                      | - Time-Series Behavioral Logs & Video |
                      +---------------------------------------+
```

---

## Full Technology Stack

### Backend Framework & Application Server
- **Python**: 3.10 / 3.12+
- **Django**: 6.1 web framework for ORM, authentication, view management, and template rendering.
- **Django Channels & Daphne**: 4.x ASGI WebSocket engine for asynchronous real-time frame transmission and communication.
- **SQLite**: Local relational database for persistent models (`StudentExamAttempt`, `Exam`, `CustomUser`, `ProctoringSessionFiles`).

### Computer Vision & ML Core
- **MediaPipe**: `FaceLandmarker` 3D face mesh model (`face_landmarker.task`) for extracting 478 3D facial landmarks and detailed iris/eye geometry.
- **OpenCV (`cv2`)**: Video decoding, frame processing, overlay drawing, and H.264 video evidence writing (`VideoWriter`).
- **NumPy**: Linear algebra, array processing, and distance mapping functions (`polyfit`).
- **Scikit-Learn & Joblib**: ML inference engine for loading `suspicion_model.joblib` (Calibrated Random Forest classifier) and running classification on extracted 79 session features.
- **Pandas**: Feature vector construction and tabular log manipulation.
- **Matplotlib**: Heatmap accumulation and kernel density visualisation.

### Frontend Technologies
- **HTML5 & CSS3**: Custom dark-themed layout and UI (`base.html`).
- **JavaScript (Vanilla ES6)**: MediaDevices API (`getUserMedia`), WebSocket client, dynamic canvas frame encoding, and hotkey monitoring.

---

## Suspicious Behavior Detection Pipeline

1. **Face & Eye Landmark Extraction**:
   - `FaceTrackProcessor`: Runs MediaPipe FaceLandmarker to track facial mesh and gaze ray vectors.
   - `FaceAxisProcessor`: Computes pitch and yaw relative to camera center and maps head orientation to screen coordinates.
   - `EyeTrackProcessor` & `EyeGazeProcessor`: Isolates eyelids and irises to detect iris box positions and blink ratios.
   - `GazeDirectionProcessor`: Fuses head orientation (45%) and eye gaze position (55%) into unified screen pixel coordinates.

2. **Rule-Based Suspicion Scoring (`SuspicionScoringProcessor`)**:
   - **Side Gaze Duration**: > 3.0 seconds triggers violation.
   - **Down Gaze Duration**: > 5.0 seconds triggers violation.
   - **Off-Screen Presence**: > 1.5 seconds face/eyes off-screen triggers violation.
   - **Frantic Eye Movement**: > 6 rapid gaze shifts within 60 seconds triggers violation.
   - **Forbidden Keystrokes**: Hotkeys (`Alt+Tab`, `Ctrl+C/V/X`, `F11`, `PrintScreen`) captured in browser or global hooks instantly trigger violation.

3. **Evidence Recording**:
   - Maintains rolling 30-frame pre-roll buffer (3 seconds at 10 FPS).
   - Upon violation trigger, captures 30 post-roll frames and writes an H.264 `.mp4` video clip asynchronously to `sessions/<session_id>/`.
   - Appends structured event logs to `session_log_<timestamp>.csv`.

4. **Machine Learning Suspicion Classification (`analytics_utils.py`)**:
   - Integrates `suspicion_model.joblib` (Calibrated Random Forest Classifier) and `feature_columns.json`.
   - Extracts 79 session-level statistical features from CSV logs (violation duration ratios, center ratios, gaze shift frequencies, max suspicion scores, etc.).
   - Computes continuous suspicion probabilities and binary classifications ("Suspicious" vs. "Normal").

---

## Analytics & Teacher Dashboard System

### URL Routes & Views (`teacherside`)
- `/teacherside/analytics/` (`analytics_dashboard`):
  - Displays aggregate KPIs (Total Attempts, Suspicious Ratio, Avg Suspicion Score, Total Violations).
  - Displays Risk Level Distribution (High, Medium, Low) and Violation Breakdown charts.
  - Interactive filters by Exam, Risk Level, and Student search query.
- `/teacherside/analytics/attempt/<int:attempt_id>/` (`attempt_analytics_detail`):
  - Student attempt summary, ML suspicion classification results, and feature status.
  - Interactive timeline of behavioral events parsed from CSV log files.
  - Embedded gaze heatmap image viewer.
  - Video evidence player and direct MP4 downloads.
- `/teacherside/analytics/attempt/<int:attempt_id>/run_inference/` (`run_model_inference_ajax`):
  - AJAX endpoint to trigger/re-run ML model inference dynamically.

---

## Deployment & Setup Guide

### Environment Setup
1. Clone repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install scikit-learn joblib pandas
   ```
2. Ensure `face_landmarker.task` is located in the root folder.
3. Place `suspicion_model.joblib` and `feature_columns.json` in root or `models/` folder.
4. Run Django database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run unit tests to verify system integrity:
   ```bash
   python manage.py test teacherside
   ```
6. Launch Daphne ASGI server:
   ```bash
   python manage.py runserver
   ```
