import json
import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict, cross_validate
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEATURES_CSV = os.path.join(BASE_DIR, "features.csv")
MODEL_PATH = os.path.join(BASE_DIR, "suspicion_model.joblib")
FEATURE_COLUMNS_PATH = os.path.join(BASE_DIR, "feature_columns.json")


def get_feature_columns(df, include_grid_cells=True):
    feature_columns = [c for c in df.columns if c not in ("session_id", "label")]
    if not include_grid_cells:
        feature_columns = [c for c in feature_columns if not c.startswith("grid_cell_")]
    return feature_columns


def train_model(include_grid_cells=True, split_counts=(3, 5, 10), model_params=None):
    df = pd.read_csv(FEATURES_CSV)
    feature_columns = get_feature_columns(df, include_grid_cells)
    X = df[feature_columns]
    y = df["label"]

    model_params = model_params or {
        "estimator__n_estimators": 100,
        "estimator__max_depth": 4,
    }
    base_model = RandomForestClassifier(
        n_estimators=model_params["estimator__n_estimators"],
        max_depth=model_params["estimator__max_depth"],
        random_state=42,
    )
    split_counts = tuple(split_counts)
    minimum_class_count = int(y.value_counts().min())
    if not split_counts or any(
        n_splits < 2 or n_splits > minimum_class_count
        for n_splits in split_counts
    ):
        raise ValueError(
            f"split_counts values must be between 2 and {minimum_class_count}."
        )

    for n_splits in split_counts:
        print(f"\n[ModelTrainer] Evaluating {n_splits}-fold stratified CV")
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        calibrated_model = CalibratedClassifierCV(base_model, cv=cv)

        cv_results = cross_validate(calibrated_model, X, y, cv=cv, scoring="accuracy")
        for fold_number, fold_accuracy in enumerate(cv_results["test_score"], start=1):
            print(f"[ModelTrainer] Fold {fold_number} accuracy: {fold_accuracy:.3f}")

        cv_probas = cross_val_predict(
            calibrated_model, X, y, cv=cv, method="predict_proba"
        )[:, 1]
        cv_preds = (cv_probas >= 0.5).astype(int)

        print(
            f"[ModelTrainer] {n_splits}-fold mean accuracy: "
            f"{cv_results['test_score'].mean():.3f} "
            f"(+/- {cv_results['test_score'].std():.3f})"
        )
        print(f"[ModelTrainer] Cross-validated accuracy: {accuracy_score(y, cv_preds):.3f}")
        print(f"[ModelTrainer] Cross-validated ROC-AUC: {roc_auc_score(y, cv_probas):.3f}")
        print(classification_report(y, cv_preds, target_names=["non_cheating", "cheating"]))

    # Refit on the full dataset for the artifact that will be used at inference time.
    final_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    calibrated_model = CalibratedClassifierCV(base_model, cv=final_cv)
    calibrated_model.fit(X, y)
    joblib.dump(calibrated_model, MODEL_PATH)
    with open(FEATURE_COLUMNS_PATH, "w", encoding="utf-8") as f:
        json.dump(feature_columns, f)

    feature_set = "with grid cells" if include_grid_cells else "without grid cells"
    print(f"[ModelTrainer] Saving model parameters: {model_params}")
    print(f"[ModelTrainer] Trained {feature_set}")
    print(f"[ModelTrainer] Saved model to {MODEL_PATH}")
    print(f"[ModelTrainer] Saved feature column order to {FEATURE_COLUMNS_PATH}")


def create_elbow_cv(include_grid_cells=True):
    df = pd.read_csv(FEATURES_CSV)
    feature_columns = get_feature_columns(df, include_grid_cells)
    X = df[feature_columns]
    y = df["label"]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    calibrated_model = CalibratedClassifierCV(
        RandomForestClassifier(random_state=42),
        cv=cv,
    )
    parameter_grid = {
        "estimator__n_estimators": [50, 100, 200, 400, 800],
        "estimator__max_depth": [2, 4, 6, 8, 10, None],
    }
    search = GridSearchCV(
        calibrated_model,
        parameter_grid,
        cv=cv,
        scoring="accuracy",
        n_jobs=-1,
        return_train_score=True,
    )
    search.fit(X, y)

    feature_set = "with grid cells" if include_grid_cells else "without grid cells"
    print(f"[ModelTrainer] Feature set: {feature_set}")
    print(f"[ModelTrainer] Best tested parameters: {search.best_params_}")
    print(f"[ModelTrainer] Best mean CV accuracy: {search.best_score_:.3f}")

    results = pd.DataFrame(search.cv_results_)
    estimator_curve = results[
        results["param_estimator__max_depth"] == 6
    ].sort_values("param_estimator__n_estimators")
    depth_curve = results[
        results["param_estimator__n_estimators"] == 200
    ].copy()
    depth_curve["depth_label"] = depth_curve["param_estimator__max_depth"].map(
        lambda depth: "None" if pd.isna(depth) else str(int(depth))
    )
    depth_curve = depth_curve.sort_values(
        "param_estimator__max_depth", na_position="last"
    )

    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].errorbar(
        estimator_curve["param_estimator__n_estimators"].astype(int),
        estimator_curve["mean_test_score"],
        yerr=estimator_curve["std_test_score"],
        marker="o",
        capsize=4,
    )
    axes[0].set(title="CV accuracy by estimator count (max_depth=6)", xlabel="n_estimators", ylabel="Mean CV accuracy")
    axes[0].grid(True, alpha=0.3)

    axes[1].errorbar(
        depth_curve["depth_label"],
        depth_curve["mean_test_score"],
        yerr=depth_curve["std_test_score"],
        marker="o",
        capsize=4,
    )
    axes[1].set(title="CV accuracy by max depth (n_estimators=200)", xlabel="max_depth", ylabel="Mean CV accuracy")
    axes[1].grid(True, alpha=0.3)

    figure.tight_layout()
    plt.show()
    return search


if __name__ == "__main__":
    search = create_elbow_cv(include_grid_cells=True)
    train_model(
        include_grid_cells=True,
        split_counts=(3, 5, 10),
        model_params=search.best_params_,
    )

