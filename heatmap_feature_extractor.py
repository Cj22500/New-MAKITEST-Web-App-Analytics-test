import cv2
import csv
import glob
import os
import numpy as np
from datetime import datetime
from scipy.spatial import cKDTree

GRID_SIZE = 8  # NxN occupancy grid resolution for heatmap features


def build_jet_lut():
    """Builds the 256-entry BGR lookup table used by cv2.COLORMAP_JET."""
    gradient = np.arange(256, dtype=np.uint8).reshape(1, 256)
    return cv2.applyColorMap(gradient, cv2.COLORMAP_JET)[0]


def recover_intensity_map(heatmap_img):
    """Inverts the JET colormap via nearest-LUT lookup to recover a 0-255 density surrogate."""
    lut = build_jet_lut()
    tree = cKDTree(lut)
    flat = heatmap_img.reshape(-1, 3)
    _, indices = tree.query(flat)
    intensity = indices.astype(np.uint8)
    # Zero-density areas were forced to pure black, not JET's dark-blue zero color.
    black_mask = np.all(flat == 0, axis=1)
    intensity[black_mask] = 0
    return intensity.reshape(heatmap_img.shape[:2])


def extract_heatmap_features(intensity_map, grid_size=GRID_SIZE):
    """Computes spatial distribution features from a recovered intensity map."""
    features = {}
    intensity_f = intensity_map.astype(np.float64)
    total_mass = float(np.sum(intensity_f))

    if total_mass <= 0:
        # No usable density recovered; return a zeroed but complete feature set.
        features.update({
            "centroid_x_norm": 0.0, "centroid_y_norm": 0.0,
            "spread_x": 0.0, "spread_y": 0.0, "elongation_ratio": 0.0,
            "entropy": 0.0, "peak_ratio": 0.0, "coverage_ratio": 0.0,
        })
        for i in range(grid_size * grid_size):
            features[f"grid_cell_{i}"] = 0.0
        return features

    h, w = intensity_map.shape
    moments = cv2.moments(intensity_f)
    centroid_x = moments["m10"] / moments["m00"]
    centroid_y = moments["m01"] / moments["m00"]
    var_x = moments["mu20"] / moments["m00"]
    var_y = moments["mu02"] / moments["m00"]
    cov_xy = moments["mu11"] / moments["m00"]

    cov_matrix = np.array([[var_x, cov_xy], [cov_xy, var_y]])
    eigvals = np.linalg.eigvalsh(cov_matrix)
    eigvals = np.clip(eigvals, a_min=1e-9, a_max=None)
    elongation_ratio = float(eigvals[1] / eigvals[0])

    # Downsample onto a coarse grid for cheap entropy/occupancy features.
    grid = cv2.resize(intensity_f, (grid_size, grid_size), interpolation=cv2.INTER_AREA)
    grid_probs = grid.flatten() / np.sum(grid)
    nonzero_probs = grid_probs[grid_probs > 0]
    entropy = float(-np.sum(nonzero_probs * np.log2(nonzero_probs)))

    flat_sorted = np.sort(intensity_f.flatten())[::-1]
    top_k = max(1, int(0.05 * flat_sorted.size))
    peak_ratio = float(np.sum(flat_sorted[:top_k]) / total_mass)

    coverage_ratio = float(np.count_nonzero(intensity_map > 25) / intensity_map.size)

    features["centroid_x_norm"] = float(centroid_x / w)
    features["centroid_y_norm"] = float(centroid_y / h)
    features["spread_x"] = float(np.sqrt(var_x) / w)
    features["spread_y"] = float(np.sqrt(var_y) / h)
    features["elongation_ratio"] = elongation_ratio
    features["entropy"] = entropy
    features["peak_ratio"] = peak_ratio
    features["coverage_ratio"] = coverage_ratio
    for i, prob in enumerate(grid_probs):
        features[f"grid_cell_{i}"] = float(prob)

    return features


VIOLATION_CATEGORIES = ("frantic_eye_movement", "forbidden_key", "off_screen", "duration")


def _categorize_label(label):
    for category in VIOLATION_CATEGORIES:
        if category in label:
            return category
    return "normal"


def extract_csv_features(csv_path):
    """Computes behavioral features from a session's suspicion-scoring CSV log."""
    rows = []
    with open(csv_path, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    category_counts = {category: 0 for category in VIOLATION_CATEGORIES}
    category_counts["normal"] = 0
    non_center_seconds = 0.0
    total_seconds = 0.0

    if not rows:
        features = {f"violation_count_{c}": 0 for c in VIOLATION_CATEGORIES}
        features.update({"num_transitions": 0, "pct_non_center_time": 0.0, "violation_rate": 0.0})
        return features

    fmt = "%Y-%m-%d %H:%M:%S.%f"
    start_times, finish_times = [], []
    for row in rows:
        label = row["Violation label"]
        category_counts[_categorize_label(label)] += 1

        start_dt = datetime.strptime(row["Timestamp start"], fmt)
        finish_dt = datetime.strptime(row["Timestamp finish"], fmt)
        duration = (finish_dt - start_dt).total_seconds()
        start_times.append(start_dt)
        finish_times.append(finish_dt)
        if row["Gaze direction"] != "Center":
            non_center_seconds += duration

    total_seconds = (max(finish_times) - min(start_times)).total_seconds()
    violation_rows = sum(v for k, v in category_counts.items() if k != "normal")

    features = {f"violation_count_{c}": category_counts[c] for c in VIOLATION_CATEGORIES}
    features["num_transitions"] = len(rows)
    features["pct_non_center_time"] = non_center_seconds / total_seconds if total_seconds > 0 else 0.0
    features["violation_rate"] = violation_rows / len(rows)
    return features


def extract_session_features(session_dir, heatmap_path=None, csv_path=None):
    """Combines heatmap and CSV features for a single session directory."""
    heatmap_matches = [heatmap_path] if heatmap_path else glob.glob(
        os.path.join(session_dir, "heatmap_*.png")
    )
    csv_matches = [csv_path] if csv_path else glob.glob(
        os.path.join(session_dir, "session_log_*.csv")
    )

    if not heatmap_matches or not csv_matches:
        return None

    heatmap_img = cv2.imread(heatmap_matches[0])
    intensity_map = recover_intensity_map(heatmap_img)

    features = extract_heatmap_features(intensity_map)
    features.update(extract_csv_features(csv_matches[0]))
    return features
