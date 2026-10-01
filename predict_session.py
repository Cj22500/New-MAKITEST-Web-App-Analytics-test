import argparse
import json
import os
import uuid
import joblib
import cv2
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import heatmap_feature_extractor as hfe

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "suspicion_model.joblib")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.json")
PREDICTIONS_ROOT = os.path.join(BASE_DIR, "predicted_sessions")


def save_prediction_outputs(session_dir, features, feature_columns, label, confidence,
                            probability_non_cheating, probability_cheating):
    prediction_dir = os.path.join(
        PREDICTIONS_ROOT,
        f"predicted_session_{uuid.uuid4().hex}",
    )
    os.makedirs(prediction_dir, exist_ok=False)

    grid_values = [features.get(f"grid_cell_{i}", 0.0) for i in range(64)]
    grid = np.array(grid_values, dtype=np.float32).reshape(8, 8)
    grid_image = cv2.normalize(grid, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    grid_image = cv2.applyColorMap(grid_image, cv2.COLORMAP_JET)
    cv2.imwrite(os.path.join(prediction_dir, "gaze_grid_8x8.png"), grid_image)

    prediction_values = {
        "source_session": os.path.abspath(session_dir),
        "predicted_label": label,
        "confidence": float(confidence),
        "probability_non_cheating": float(probability_non_cheating),
        "probability_cheating": float(probability_cheating),
        "grid_size": 8,
        "grid_values": grid_values,
        "feature_columns": feature_columns,
    }
    with open(os.path.join(prediction_dir, "predicted_values.json"), "w", encoding="utf-8") as f:
        json.dump(prediction_values, f, indent=2)

    print(f"[Predictor] Saved prediction outputs to {prediction_dir}")
    return prediction_dir


def predict_session(session_dir):
    model = joblib.load(MODEL_PATH)
    with open(FEATURE_COLUMNS_PATH, "r", encoding="utf-8") as f:
        feature_columns = json.load(f)

    features = hfe.extract_session_features(session_dir)
    if features is None:
        print(f"[Predictor] Session missing heatmap or CSV log: {session_dir}")
        return None

    ordered_values = pd.DataFrame(
        [[features.get(col, 0.0) for col in feature_columns]],
        columns=feature_columns,
    )
    predicted_class = model.predict(ordered_values)[0]
    probabilities = model.predict_proba(ordered_values)[0]
    class_probabilities = dict(zip(model.classes_, probabilities))
    probability_non_cheating = class_probabilities[0]
    probability_cheating = class_probabilities[1]

    label = "cheating" if predicted_class == 1 else "non_cheating"
    confidence = class_probabilities[predicted_class]
    print(
        f"[Predictor] {os.path.basename(session_dir)} -> {label} "
        f"({confidence * 100:.1f}% confidence)"
    )
    print(
        f"[Predictor] Confidence - cheating: {probability_cheating * 100:.1f}%, "
        f"non-cheating: {probability_non_cheating * 100:.1f}%"
    )
    save_prediction_outputs(
        session_dir,
        features,
        feature_columns,
        label,
        confidence,
        probability_non_cheating,
        probability_cheating,
    )
    return label, confidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict cheating/non_cheating for a single session.")
    parser.add_argument(
        "session_dir",
        nargs="?",
        help="Optional path to a session directory containing a heatmap PNG and CSV log.",
    )
    args = parser.parse_args()

    session_dir = args.session_dir
    if session_dir is None:
        root = tk.Tk()
        root.withdraw()
        session_dir = filedialog.askdirectory(
            title="Select a session folder to predict",
            initialdir=os.path.join(BASE_DIR, "sessions"),
        )
        root.destroy()

    if session_dir:
        predict_session(session_dir)
    else:
        print("[Predictor] No session folder selected.")
