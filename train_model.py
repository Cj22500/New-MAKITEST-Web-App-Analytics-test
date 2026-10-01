import json
import os
import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURES_CSV = os.path.join(BASE_DIR, "features.csv")
MODEL_PATH = os.path.join(BASE_DIR, "suspicion_model.joblib")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.json")


def train_model():
    df = pd.read_csv(FEATURES_CSV)
    feature_columns = [c for c in df.columns if c not in ("session_id", "label")]
    X = df[feature_columns]
    y = df["label"]

    # Small session count -> use k-fold CV instead of a single held-out split.
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    base_model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    calibrated_model = CalibratedClassifierCV(base_model, cv=cv)

    cv_results = cross_validate(calibrated_model, X, y, cv=cv, scoring="accuracy")
    for fold_number, fold_accuracy in enumerate(cv_results["test_score"], start=1):
        print(f"[ModelTrainer] Fold {fold_number} accuracy: {fold_accuracy:.3f}")

    cv_probas = cross_val_predict(calibrated_model, X, y, cv=cv, method="predict_proba")[:, 1]
    cv_preds = (cv_probas >= 0.5).astype(int)

    print(f"[ModelTrainer] Cross-validated accuracy: {accuracy_score(y, cv_preds):.3f}")
    print(f"[ModelTrainer] Cross-validated ROC-AUC: {roc_auc_score(y, cv_probas):.3f}")
    print(classification_report(y, cv_preds, target_names=["non_cheating", "cheating"]))

    # Refit on the full dataset for the artifact that will be used at inference time.
    calibrated_model.fit(X, y)
    joblib.dump(calibrated_model, MODEL_PATH)
    with open(FEATURE_COLUMNS_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_columns, f)

    print(f"[ModelTrainer] Saved model to {MODEL_PATH}")
    print(f"[ModelTrainer] Saved feature column order to {FEATURE_COLUMNS_PATH}")


if __name__ == "__main__":
    train_model()
