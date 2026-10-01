"""Run the trained session predictor against web-app session artifacts."""

import json
import os
from datetime import datetime, timezone

import joblib
import cv2
import numpy as np
import pandas as pd

import heatmap_feature_extractor as hfe


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "suspicion_model.joblib")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.json")
MODEL_VERSION = os.path.basename(MODEL_PATH)


def predict_session_files(heatmap_path, csv_path, session_directory=None):
    """Predict one web session from its explicitly registered artifact paths."""
    if not heatmap_path or not os.path.isfile(heatmap_path):
        raise FileNotFoundError("Registered session heatmap was not found")
    if not csv_path or not os.path.isfile(csv_path):
        raise FileNotFoundError("Registered exam session CSV was not found")

    with open(FEATURE_COLUMNS_PATH, "r", encoding="utf-8") as feature_file:
        feature_columns = json.load(feature_file)

    features = hfe.extract_session_features(
        os.path.dirname(heatmap_path),
        heatmap_path=heatmap_path,
        csv_path=csv_path,
    )
    if features is None:
        raise ValueError("Session is missing usable heatmap or CSV data")

    ordered_values = pd.DataFrame(
        [[features.get(column, 0.0) for column in feature_columns]],
        columns=feature_columns,
    )
    model = joblib.load(MODEL_PATH)
    predicted_class = model.predict(ordered_values)[0]
    probabilities = model.predict_proba(ordered_values)[0]
    class_probabilities = dict(zip(model.classes_, probabilities))
    probability_non_cheating = float(class_probabilities[0])
    probability_cheating = float(class_probabilities[1])
    label = "cheating" if predicted_class == 1 else "non_cheating"
    confidence = float(class_probabilities[predicted_class])

    result = {
        "predicted_label": label,
        "confidence": confidence,
        "probability_non_cheating": probability_non_cheating,
        "probability_cheating": probability_cheating,
        "model_version": MODEL_VERSION,
        "feature_columns": feature_columns,
        "features": features,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    if session_directory:
        prediction_directory = os.path.join(session_directory, "prediction")
        os.makedirs(prediction_directory, exist_ok=True)

        grid_values = [features.get(f"grid_cell_{index}", 0.0) for index in range(64)]
        grid = np.array(grid_values, dtype=np.float32).reshape(8, 8)
        grid_image = cv2.normalize(grid, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        grid_image = cv2.applyColorMap(grid_image, cv2.COLORMAP_JET)
        grid_artifact_path = os.path.join(prediction_directory, "gaze_grid_8x8.png")
        if not cv2.imwrite(grid_artifact_path, grid_image):
            raise OSError(f"Could not save prediction grid: {grid_artifact_path}")

        result["grid_image_path"] = grid_artifact_path
        result["artifact_path"] = grid_artifact_path
        artifact_path = os.path.join(prediction_directory, "predicted_values.json")
        with open(artifact_path, "w", encoding="utf-8") as artifact_file:
            json.dump(result, artifact_file, indent=2)

    return result