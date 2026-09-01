import os
import json
import logging
import csv
import collections
from datetime import datetime
import numpy as np
import pandas as pd
from django.conf import settings

logger = logging.getLogger(__name__)

# Try importing joblib
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logger.warning("joblib is not installed. ML model inference will use fallback heuristic mode.")

# File paths for suspicion model
MODEL_DIR = getattr(settings, 'SUSPICION_MODEL_DIR', os.path.join(settings.BASE_DIR, 'models'))
MODEL_FILE_PATH = os.path.join(MODEL_DIR, 'suspicion_model.joblib')
FEATURE_COLS_PATH = os.path.join(MODEL_DIR, 'feature_columns.json')

# Also check root directory as fallback
ROOT_MODEL_FILE_PATH = os.path.join(settings.BASE_DIR, 'suspicion_model.joblib')
ROOT_FEATURE_COLS_PATH = os.path.join(settings.BASE_DIR, 'feature_columns.json')


def get_model_and_features():
    """
    Loads suspicion_model.joblib and feature_columns.json if available.
    Returns (model, feature_columns) or (None, None).
    """
    model_path = MODEL_FILE_PATH if os.path.exists(MODEL_FILE_PATH) else (
        ROOT_MODEL_FILE_PATH if os.path.exists(ROOT_MODEL_FILE_PATH) else None
    )
    feature_path = FEATURE_COLS_PATH if os.path.exists(FEATURE_COLS_PATH) else (
        ROOT_FEATURE_COLS_PATH if os.path.exists(ROOT_FEATURE_COLS_PATH) else None
    )

    if not JOBLIB_AVAILABLE or not model_path or not feature_path:
        return None, None

    try:
        model = joblib.load(model_path)
        with open(feature_path, 'r', encoding='utf-8') as f:
            feature_columns = json.load(f)
        return model, feature_columns
    except Exception as e:
        logger.exception("Failed to load suspicion ML model or feature columns: %s", e)
        return None, None


def parse_session_csv(csv_path):
    """
    Parses a session log CSV file.
    Columns: Gaze direction, Timestamp start, Timestamp finish, Violation label, Numerical behavioural score, Video Evidence File
    Returns list of dict entries with calculated duration.
    """
    events = []
    if not csv_path or not os.path.exists(csv_path):
        return events

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                direction = row.get("Gaze direction", "Center")
                start_str = row.get("Timestamp start", "")
                finish_str = row.get("Timestamp finish", "")
                label = row.get("Violation label", "normal")
                try:
                    score = float(row.get("Numerical behavioural score", 0))
                except (ValueError, TypeError):
                    score = 0.0
                video_file = row.get("Video Evidence File", "")

                # Compute duration in seconds
                duration_s = 0.0
                if start_str and finish_str:
                    try:
                        t_start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S.%f')
                        t_finish = datetime.strptime(finish_str, '%Y-%m-%d %H:%M:%S.%f')
                        duration_s = max(0.0, (t_finish - t_start).total_seconds())
                    except ValueError:
                        try:
                            t_start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
                            t_finish = datetime.strptime(finish_str, '%Y-%m-%d %H:%M:%S')
                            duration_s = max(0.0, (t_finish - t_start).total_seconds())
                        except ValueError:
                            duration_s = 0.0

                events.append({
                    'direction': direction,
                    'start_time': start_str,
                    'finish_time': finish_str,
                    'duration_s': duration_s,
                    'violation_label': label,
                    'score': score,
                    'video_file': video_file,
                })
    except Exception as e:
        logger.exception("Error parsing CSV %s: %s", csv_path, e)

    return events


def extract_features_from_events(events, feature_columns=None):
    """
    Extracts statistical features from parsed CSV events to align with feature_columns.
    Returns pandas DataFrame with 1 row and matching columns.
    """
    total_events = len(events)
    total_duration = sum(e['duration_s'] for e in events) or 1.0

    violations = [e for e in events if e['violation_label'] and e['violation_label'] != 'normal']
    violation_count = len(violations)
    violation_duration = sum(e['duration_s'] for e in violations)

    gaze_directions = [e['direction'] for e in events]
    center_count = sum(1 for d in gaze_directions if d == 'Center')
    off_center_count = total_events - center_count

    durations = [e['duration_s'] for e in events]
    scores = [e['score'] for e in events]

    feature_dict = {
        'total_events': total_events,
        'total_duration': total_duration,
        'violation_count': violation_count,
        'violation_duration': violation_duration,
        'violation_ratio': violation_duration / total_duration,
        'center_ratio': (sum(e['duration_s'] for e in events if e['direction'] == 'Center')) / total_duration,
        'off_center_ratio': 1.0 - ((sum(e['duration_s'] for e in events if e['direction'] == 'Center')) / total_duration),
        'avg_event_duration': np.mean(durations) if durations else 0.0,
        'max_event_duration': np.max(durations) if durations else 0.0,
        'std_event_duration': np.std(durations) if len(durations) > 1 else 0.0,
        'mean_suspicion_score': np.mean(scores) if scores else 0.0,
        'max_suspicion_score': np.max(scores) if scores else 0.0,
        'shift_frequency': total_events / (total_duration / 60.0) if total_duration > 0 else 0.0,
    }

    # Count violation types
    violation_types = ['looking_off_screen', 'face_off_screen', 'eyes_off_screen', 'frantic_eye_movement', 'forbidden_key']
    for vtype in violation_types:
        feature_dict[f'vtype_{vtype}_count'] = sum(1 for e in violations if vtype in e['violation_label'])

    # Build DataFrame
    if feature_columns:
        # Fill missing features required by feature_columns with 0.0 or calculated default
        df_dict = {}
        for col in feature_columns:
            if col in feature_dict:
                df_dict[col] = feature_dict[col]
            else:
                # Default unknown/extra features to 0.0
                df_dict[col] = 0.0
        df = pd.DataFrame([df_dict], columns=feature_columns)
    else:
        df = pd.DataFrame([feature_dict])

    return df


def predict_suspicion_for_attempt(exam_attempt, session_files=None):
    """
    Runs ML model inference (or heuristic fallback) on a student exam attempt's session log CSV files.
    Returns dict with probability, prediction_label, features, and model_status.
    """
    model, feature_cols = get_model_and_features()

    events = []
    csv_paths = []
    if session_files:
        csv_paths = session_files.get_all_csv_paths()
        # Parse exam session CSV (usually the second CSV or last CSV)
        for csv_p in csv_paths:
            if csv_p and os.path.exists(csv_p):
                parsed = parse_session_csv(csv_p)
                events.extend(parsed)

    if not events:
        # Return fallback/default response if no events available
        base_suspicion = exam_attempt.suspicion_score if exam_attempt else 0.0
        prob = min(1.0, max(0.0, base_suspicion / 100.0 if base_suspicion > 1.0 else base_suspicion))
        return {
            'probability': prob,
            'prediction_label': 'Suspicious' if prob >= 0.5 else 'Normal',
            'is_suspicious': prob >= 0.5,
            'model_used': False,
            'model_status': 'No log events found. Using rule-based fallback.',
            'event_count': 0,
            'features': {},
        }

    if model and feature_cols:
        try:
            df_feat = extract_features_from_events(events, feature_columns=feature_cols)
            if hasattr(model, 'predict_proba'):
                prob_array = model.predict_proba(df_feat)
                # Assume binary classification where index 1 is suspicious class
                prob = float(prob_array[0][1]) if prob_array.shape[1] > 1 else float(prob_array[0][0])
            else:
                pred = model.predict(df_feat)
                prob = float(pred[0])

            is_suspicious = prob >= 0.5
            label = "Suspicious" if is_suspicious else "Normal"
            return {
                'probability': prob,
                'prediction_label': label,
                'is_suspicious': is_suspicious,
                'model_used': True,
                'model_status': 'Calibrated Random Forest model inference complete.',
                'event_count': len(events),
                'features': df_feat.iloc[0].to_dict(),
            }
        except Exception as e:
            logger.exception("Error running ML model inference: %s", e)

    # Heuristic fallback if model not loaded or error occurred
    total_dur = sum(e['duration_s'] for e in events) or 1.0
    viol_dur = sum(e['duration_s'] for e in events if e['violation_label'] != 'normal')
    viol_count = sum(1 for e in events if e['violation_label'] != 'normal')
    max_score = max((e['score'] for e in events), default=0.0)

    # Heuristic score calculation
    heuristic_score = min(1.0, (viol_dur / total_dur) * 0.5 + (viol_count * 0.1) + (max_score / 200.0))
    if exam_attempt and exam_attempt.suspicion_score > 0:
        heuristic_score = max(heuristic_score, min(1.0, exam_attempt.suspicion_score / 100.0))

    return {
        'probability': heuristic_score,
        'prediction_label': 'Suspicious' if heuristic_score >= 0.5 else 'Normal',
        'is_suspicious': heuristic_score >= 0.5,
        'model_used': False,
        'model_status': 'ML model file missing/unavailable. Used rule-based heuristic analysis.',
        'event_count': len(events),
        'features': extract_features_from_events(events).iloc[0].to_dict(),
    }


def compute_aggregate_analytics(attempts, session_files_map):
    """
    Computes aggregate metrics, violation breakdowns, gaze direction distributions,
    and risk levels across a collection of StudentExamAttempt queryset / items.
    """
    total_attempts = len(attempts)
    if total_attempts == 0:
        return {
            'total_attempts': 0,
            'suspicious_attempts_count': 0,
            'suspicious_ratio': 0.0,
            'avg_suspicion_score': 0.0,
            'total_violations_count': 0,
            'violation_breakdown': {},
            'gaze_distribution': {},
            'risk_distribution': {'High': 0, 'Medium': 0, 'Low': 0},
            'recent_violations': [],
        }

    suspicious_count = 0
    total_suspicion_sum = 0.0
    total_violations_count = 0

    violation_breakdown = collections.defaultdict(int)
    gaze_distribution = collections.defaultdict(float)
    risk_distribution = {'High': 0, 'Medium': 0, 'Low': 0}
    recent_violations = []

    for attempt in attempts:
        score = attempt.suspicion_score or 0.0
        total_suspicion_sum += score
        total_violations_count += (attempt.violation_count or 0)

        # Categorize risk level
        if score >= 50.0 or attempt.violation_count >= 5:
            risk_level = 'High'
            suspicious_count += 1
        elif score >= 20.0 or attempt.violation_count >= 2:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        risk_distribution[risk_level] += 1

        # Process session files & CSV log entries if available
        sfiles = session_files_map.get(attempt.proctoring_session_id)
        if sfiles:
            csv_paths = sfiles.get_all_csv_paths()
            for csv_p in csv_paths:
                if csv_p and os.path.exists(csv_p):
                    events = parse_session_csv(csv_p)
                    for ev in events:
                        gaze_distribution[ev['direction']] += ev['duration_s']
                        label = ev['violation_label']
                        if label and label != 'normal':
                            violation_breakdown[label] += 1
                            if len(recent_violations) < 20:
                                recent_violations.append({
                                    'student': attempt.student.get_full_name() or attempt.student.username,
                                    'exam': attempt.exam.title,
                                    'session_id': attempt.proctoring_session_id,
                                    'violation': label,
                                    'direction': ev['direction'],
                                    'duration_s': round(ev['duration_s'], 2),
                                    'video_file': ev['video_file'],
                                    'timestamp': ev['start_time'],
                                    'attempt_id': attempt.id,
                                })

    # Convert gaze distribution to percentages
    total_gaze_time = sum(gaze_distribution.values()) or 1.0
    gaze_percentages = {
        k: round((v / total_gaze_time) * 100, 1) for k, v in gaze_distribution.items()
    }

    return {
        'total_attempts': total_attempts,
        'suspicious_attempts_count': suspicious_count,
        'suspicious_ratio': round((suspicious_count / total_attempts) * 100, 1),
        'avg_suspicion_score': round(total_suspicion_sum / total_attempts, 2),
        'total_violations_count': total_violations_count,
        'violation_breakdown': dict(violation_breakdown),
        'gaze_distribution': gaze_percentages,
        'risk_distribution': risk_distribution,
        'recent_violations': recent_violations,
    }
