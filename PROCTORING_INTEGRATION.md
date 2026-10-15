# Proctoring and Prediction Integration

## Components

| Component | Responsibility |
|---|---|
| `whatever/camera/templates/camera/home.html` | Camera selection, calibration UI, browser frame capture |
| `whatever/studentside/templates/studentside/exam_session.html` | Exam questions and exam-time monitor |
| `whatever/camera/consumers.py` | Django Channels WebSocket protocol |
| `gaze_session.py` | Per-connection tracking and artifact finalization |
| `whatever/studentside/models.py` | Attempts, thresholds, and registered artifacts |
| `web_session_predict.py` | Web-app classifier inference |
| `heatmap_feature_extractor.py` | Heatmap and CSV feature construction |

## Lifecycle

The ID created by `exam_details` is reused across two WebSocket connections. Each connection has its own in-memory `GazeSession`, but both write to the same session directory.

```text
exam_details
  -> temporary request.session['proctoring_session_id']
  -> camera WebSocket: calibration
  -> StudentExamAttempt is created by exam_session
  -> exam WebSocket: monitoring
  -> GazeSession.finalize()
  -> ProctoringSessionFiles.create_or_update_from_session()
  -> web_session_predict.predict_session_files()
```

## WebSocket Protocol

Client messages:

| Message | Meaning |
|---|---|
| JPEG binary data | Process one camera frame |
| `{"type":"calibrate_next"}` | Advance calibration |
| `{"type":"keystrokes","keys":[...]}` | Report browser events |
| `{"type":"ping"}` | Keepalive |

Server messages include `ready`, `frame_result`, `calibration`, `calibration_complete`, `pong`, `session_closed`, and `error`.

## Stored Data

`StudentExamAttempt` stores the student, exam, attempt number, score, timestamps, WebSocket session ID, live suspicion fields, and final prediction fields:

- `prediction_label`
- `prediction_confidence`
- `probability_cheating`
- `probability_non_cheating`
- `prediction_status`
- `prediction_error`
- `prediction_model_version`
- `prediction_completed_at`
- `prediction_artifact`

Prediction statuses are `pending`, `running`, `completed`, `failed`, or `unavailable`.

`ProctoringSessionFiles` records relative paths below `MEDIA_ROOT/sessions/<session_id>/` for calibration JSON, the heatmap, session logs, and violation videos.

The first CSV is the calibration log. The final CSV is treated as the exam log by `get_exam_csv_path()`. Prediction never falls back to the calibration CSV.

## Prediction Flow

`submit_exam` registers artifacts and invokes `_predict_exam_attempt`. The helper gets the registered heatmap and final exam CSV, marks the attempt `running`, calls `predict_session_files`, then saves probabilities, label, confidence, model version, completion time, and artifact path. Missing artifacts or inference errors produce `unavailable` or `failed` without blocking answer submission.

The prediction artifact is stored at:

```text
media/sessions/<session_id>/prediction/predicted_values.json
```

## Required Setup

```powershell
pip install -r requirements.txt
python whatever/manage.py migrate
python whatever/manage.py check
python whatever/manage.py runserver
```

The model contract must be present at the repository root:

```text
suspicion_model.joblib
feature_columns.json
```

## Current Limitations

- Prediction is synchronous during submission.
- The submission path depends on final session artifacts being present when the file scan runs.
- Live `suspicion_score` and `violation_count` are separate from final classifier probabilities.
- Teacher review displays prediction status and result; the prediction JSON is currently stored as a session artifact.
