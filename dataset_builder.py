import glob
import os
import pandas as pd
import heatmap_feature_extractor as hfe

SESSIONS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
LABEL_DIRS = {"cheating": 1, "non_cheating": 0}
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "features.csv")


def build_dataset():
    rows = []
    for label_dir, label_value in LABEL_DIRS.items():
        session_dirs = glob.glob(os.path.join(SESSIONS_ROOT, label_dir, "session_*"))
        for session_dir in session_dirs:
            features = hfe.extract_session_features(session_dir)
            if features is None:
                print(f"[DatasetBuilder] Skipping {session_dir}: missing heatmap or CSV log.")
                continue
            features["session_id"] = os.path.basename(session_dir)
            features["label"] = label_value
            rows.append(features)

    if not rows:
        print("[DatasetBuilder] No sessions found with usable data.")
        return None

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"[DatasetBuilder] Wrote {len(df)} session rows to {OUTPUT_CSV}")
    return df


if __name__ == "__main__":
    build_dataset()
