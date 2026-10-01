## MAKITEST : Suspicious Exam Behaviour Detection System

This serves as a guide to the usage, setup, and system framework and architecture of the dual gaze tracking system of MAKITEST. The system monitors exam takers via webcam, tracking head pose and eye gaze to detect and log suspicious behaviours in real time.

---

## End-to-End Process

The project works in two connected phases: it first records and analyses an
exam session, then converts the saved session into data that can be used to
train or apply a machine-learning classifier. The process begins when
`main_trackerprocess.py` opens the webcam and asks whether the session should
be labelled `non_cheating` or `cheating`. Every session is saved in a unique
directory under the corresponding folder in `sessions/`. This directory is
the unit used by the rest of the pipeline.

During each frame, `FrameBufferProcessor` obtains the newest camera image,
while the face and eye processors detect landmarks, estimate head pose, track
iris movement, and calculate eye-based gaze. Calibration establishes the
subject's centre, up, down, left, and right eye measurements. The calibrated
eye position is smoothed and combined with the head-based screen position by
`GazeDirectionProcessor`, producing both an estimated screen coordinate and a
discrete gaze direction such as `Center`, `Left`, or `Down`.

The resulting gaze direction is passed to `SuspicionScoringProcessor`, which
tracks how long the subject looks away, looks down, moves their eyes rapidly,
or leaves the camera view. `KeypressTrackProcessor` supplies suspicious global
keyboard events such as application switching or clipboard shortcuts. When a
rule is triggered, the scorer records an event in
`session_log_<timestamp>.csv` and saves video evidence with a pre-roll and
post-roll. At the same time, `HeatmapProcessor` accumulates screen-position
points. When the session ends, it turns those points into a blurred,
colour-mapped `session_heatmap_<timestamp>.png`.

The two files required by the machine-learning pipeline are therefore the
session heatmap and the suspicion-scoring CSV. `dataset_builder.py` visits
every `session_*` directory in both label folders. For each session it calls
`extract_session_features()`; sessions missing either required file are
skipped. A valid session becomes one row containing numeric heatmap features,
numeric behaviour features, its folder name as `session_id`, and its folder
label (`1` for cheating or `0` for non-cheating). These rows are written to
`features.csv`.

When `heatmap_feature_extractor.py` processes the PNG, it first reconstructs
an approximate intensity map. The heatmap was saved using OpenCV's JET colour
map, so `build_jet_lut()` recreates the 256-colour lookup table and
`recover_intensity_map()` uses a nearest-colour `cKDTree` search to convert
each pixel back to an intensity from 0 to 255. Pure black pixels are treated
as zero density because they represent areas where no gaze points were
recorded.

`extract_heatmap_features()` then describes the spatial distribution of gaze.
It calculates the normalised gaze centroid, horizontal and vertical spread,
the elongation of the distribution, entropy, the concentration of the
strongest 5 percent of pixels (`peak_ratio`), and the proportion of pixels
above intensity 25 (`coverage_ratio`). It also resizes the map to an 8x8 grid
and normalises the 64 cells as probabilities, producing
`grid_cell_0` through `grid_cell_63`. If the recovered map has no density, a
complete set of zero-valued heatmap features is returned instead.

`extract_csv_features()` reads the event log and categorises each violation
label as `frantic_eye_movement`, `forbidden_key`, `off_screen`, `duration`,
or `normal`. It parses each event's timestamps, counts the categories,
counts the total transitions, adds the duration of non-`Center` gaze, and
calculates the non-centre percentage over the session span. It also calculates
`violation_rate` as the number of violation rows divided by the total number
of log rows. The heatmap and CSV dictionaries are combined into the single
feature row used by the dataset builder.

After `features.csv` has been built, `train_model.py` removes `session_id` and
`label` from the input features and trains a calibrated random forest. Five-
fold stratified cross-validation reports accuracy, ROC-AUC, and a
classification report. The final model is then refitted using all available
session rows and saved as `suspicion_model.joblib`; the exact feature order is
saved in `feature_columns.json`.

Finally, `predict_session.py` loads those two model artifacts, extracts the
features from one selected session, rebuilds a one-row pandas DataFrame in the
stored feature order, and obtains probabilities from the classifier. A
cheating probability of at least 0.5 produces the `cheating` label; otherwise
the result is `non_cheating`. The script prints both class probabilities and
the confidence of the selected label.

---

## Step-by-Step Setup

### Prerequisites
- **Python 3.10 or higher** — [Download Python](https://www.python.org/downloads/)
- **A webcam** connected and accessible (index `0` or `1`)
- **Windows OS** recommended (the `keyboard` library requires it for global hotkey hooks)

---

### Step 1 — Clone or Download the Project

Download all project files into a single folder. Ensure the following files are present in the same directory:

```
main_trackerprocess.py          ← entry point (run this)
dataset_builder.py              ← build ML features from saved sessions
train_model.py                  ← train and save the suspicion classifier
predict_session.py              ← classify one saved session
heatmap_feature_extractor.py    ← extract heatmap and behaviour features
face_trackprocessor.py
face_distanceprocessor.py
face_axisprocessor.py
eye_trackprocessor.py
eye_gazeprocessor.py
eye_calibrationprocessor.py
eye_screenposprocessor.py
gaze_directionprocessor.py
suspicion_scoringprocessor.py
heatmap_processor.py
keypress_trackprocessor.py
frame_bufferprocessor.py
face_landmarker.task          ← required MediaPipe model file
requirements.txt
```

> **Important:** The `face_landmarker.task` model file must be present in the same directory as the scripts. Without it, face and eye detection will not function.

---

### Step 2 — Create a Virtual Environment (Recommended)

Open a terminal in the project folder and run:

```bash
python -m venv venv
```

Activate the virtual environment:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

---

### Step 3 — Install Dependencies

With the virtual environment active, install all required packages:

```bash
pip install -r requirements.txt
```

This installs the following libraries:

| Package | Purpose |
|---|---|
| `mediapipe` | Face and eye landmark detection model |
| `opencv-python` / `opencv-contrib-python` | Webcam capture and frame rendering |
| `numpy` | Numerical computation and array operations |
| `matplotlib` | Plotting and heatmap visualisation |
| `keyboard` | Global keyboard hotkey monitoring |
| `sounddevice` | Audio support (reserved for future alerts) |
| `pillow` | Image processing utilities |
| `pandas` | Tabular feature construction and model input |
| `scikit-learn` | Random forest training, calibration, validation, and metrics |
| `scipy` | Efficient heatmap colour-map lookup with `cKDTree` |
| `joblib` | Save and load the trained model |

---

### Step 4 — Verify Webcam Index

Open `main_trackerprocess.py` and locate this line near the top:

```python
cap = cv2.VideoCapture(1)
```

Change the index to match your camera:
- `0` — default built-in webcam
- `1` — secondary or external webcam

---

### Step 5 — Run the Program

Run the main tracker from the terminal:

```bash
python main_trackerprocess.py
```

Before tracking starts, select the session type when prompted:
- `1` — non-cheating session
- `2` — cheating session

Session files are saved in a uniquely named folder under the selected category:

```
sessions/
├── non_cheating/
│   └── session_<id>/
└── cheating/
      └── session_<id>/
```

Two windows will open:
- **Main feed** — shows the live webcam with face/eye landmarks overlaid
- **Screen position debug view** — shows the estimated gaze position on a virtual screen grid

---

### Step 6 — Calibrate the System

Calibration must be performed before gaze tracking is accurate. Follow the on-screen calibration stages:

| Key | Action |
|---|---|
| `{` | Advance to the next calibration stage (look at the indicated target point) |
| `}` | Exit the program |

**Calibration stages (in order):**
1. **Stage 0** — Look straight at the camera (center baseline)
2. **Stage 1** — Look up
3. **Stage 2** — Look down
4. **Stage 3** — Look left
5. **Stage 4** — Look right

At each stage, press `{` while holding your gaze on the target. The system collects 60 frames of samples per stage and saves the result to `calibration_data.json` automatically. On subsequent runs, saved calibration data is loaded from this file.

---

### Step 7 — Review Session Output

After the session ends (`}` to quit), the following output files are generated in the project folder:

| File | Description |
|---|---|
| `session_log_<timestamp>.csv` | Event-based log of all gaze directions, violations, and durations |
| `session_heatmap_<timestamp>.png` | Colour-mapped heatmap of screen gaze positions over the session |
| `<timestamp>_violation_<reason>.mp4` | Video evidence with pre-roll and post-roll around a suspicious event |

Each session is self-contained under its category directory, which allows the
same files to be reviewed manually or used by the machine-learning pipeline.

---

## System Architecture

The system is composed of **13 modules**, each responsible for a distinct processing stage. Data flows from the webcam through detection, tracking, calibration, scoring, and output layers.

```
Webcam → FrameBufferProcessor
           ↓
     FaceTrackProcessor → FaceDistanceProcessor
           ↓                       ↓
     FaceAxisProcessor       EyeTrackProcessor
           ↓                       ↓
     GazeDirectionProcessor ← EyeGazeProcessor
           ↓                       ↓
     EyeScreenPosProcessor ← EyeCalibrationProcessor
           ↓
     SuspicionScoringProcessor → CSV log / Video clips
           ↓
     HeatmapProcessor → Heatmap image
     KeypressTrackProcessor → Suspicious key log
```

---

## Module Reference

### `main_trackerprocess.py` — Main Tracker Process *(entry point)*
The entry point of the application. Initialises OpenCV's camera feed, instantiates every processor module, and runs the main loop that reads frames, calls each processor in sequence, and renders the results. Press `{` to step through calibration and `}` to exit.

---

### `face_trackprocessor.py` — Face Track Processor
Loads the `face_landmarker.task` MediaPipe model and runs face landmark detection on each video frame. Detects up to 1 face and returns the full set of 478 3D facial landmarks. Also tracks a smoothed gaze ray direction by averaging recent face normal vectors, which is fed into the axis and gaze processors.

---

### `face_distanceprocessor.py` — Face Distance Processor
Estimates the physical distance (in centimetres) between the subject and the camera. It uses a second-degree polynomial fitted (`numpy.polyfit`) to a set of manually measured iris-pixel-width vs. distance calibration samples. Given the pixel distance between the left and right iris centers, it returns a centimetre distance estimate.

<img width="720" height="540" alt="image" src="https://github.com/user-attachments/assets/8a1238e4-8496-4b4b-9eac-b3f6588d700e" />
<br><br>

Using the second degree of polynomial gives the process a great balance between efficiency and accuracy. This is implemented by gathering the distance of the irises with their corresponding distance from the camera. The process then uses `polyfit()` to predict the values of input data outside the given samples.

---

### `face_axisprocessor.py` — Face Axis Processor
Computes the **yaw** (left/right rotation) and **pitch** (up/down tilt) of the head in degrees using five key facial landmarks: chin, nose tip, forehead, left cheek, and right cheek. Calibration offsets are applied so that looking straight ahead reads as 0°/0°. The resulting angles are mapped to an estimated screen position using configurable degree limits (default: ±25° yaw, ±12° pitch).

#### Face-Position Anchor Offset
When converting head-pose angles to a screen coordinate, the processor also accounts for where the face sits within the camera frame. Each frame, `update_anchor_from_face_position()` receives the face centre in pixels and the frame dimensions. It normalises the face position to a `[-0.5, 0.5]` range relative to the frame centre, then scales that deviation directly onto screen space (1920×1080):

```
norm_x = (face_center_x / frame_width)  - 0.5
norm_y = (face_center_y / frame_height) - 0.5

anchor_offset_x = norm_x * 1920
anchor_offset_y = norm_y * 1080
```

These offsets are added to the angle-derived screen position inside `get_estimated_screen_position()` before the result is clamped to the screen bounds. A face perfectly centred in the camera frame produces zero offset; a face displaced to the right shifts the estimated gaze position right proportionally, correcting for the parallax-like error that would otherwise occur when the subject is not centred in front of the camera.

---

### `eye_trackprocessor.py` — Eye Track Processor
Uses a second instance of the MediaPipe `FaceLandmarker` model to isolate and track detailed eye geometry. Extracts upper/lower eyelid contours, iris boundary points, and pupil center positions for both eyes. Passes the raw eye geometry to `EyeGazeProcessor` for normalised gaze computation, and draws the eye bounding boxes and landmark points on the frame.

---

### `eye_gazeprocessor.py` — Eye Gaze Processor
Takes the raw eye landmark coordinates from `EyeTrackProcessor` and computes two key measurements per eye:
- **Iris position** — the normalised horizontal position of the iris center within the eye bounding box (0 = far left, 1 = far right)
- **Iris box height** — the pixel distance between the upper and lower eyelid markers, used to infer vertical gaze and detect blinks

These values are returned as `raw_eye_data` which feeds into the calibration and gaze direction processors.

---

### `eye_calibrationprocessor.py` — Eye Calibration Processor
Manages a multi-stage calibration sequence that records baseline eye measurements for center, up, down, left, and right gaze positions. For each stage it collects a rolling window of 60 samples and averages them into threshold values. The calibrated thresholds are stored in a dictionary and saved to `calibration_data.json` so recalibration is not required on every run.

---

### `eye_screenposprocessor.py` — Eye Screen Position Processor
Maps the calibrated iris position values to absolute screen pixel coordinates (default: 1920×1080). Applies exponential moving average (EMA) smoothing with a configurable time constant (`smoothing_tau = 0.18 s`) to eliminate jitter. Also classifies the screen into a 3×3 grid of named regions (e.g. "Up Left", "Center Center", "Down Right") for use by the suspicion scorer.

---

### `gaze_directionprocessor.py` — Gaze Direction Processor
Fuses the face-axis-based screen position and the eye-based screen position into a single weighted estimate. Default weights are 45% face axis and 55% eye gaze. Also classifies the combined gaze into a discrete direction string (`"Up"`, `"Down"`, `"Left"`, `"Right"`, `"Center"`) using calibrated thresholds and dead zones to prevent jitter.

---

### `suspicion_scoringprocessor.py` — Suspicion Scoring Processor
The behavioural analysis engine. Monitors gaze direction and raises suspicion events based on configurable rules:

| Trigger | Default Threshold |
|---|---|
| Looking to the side | > 3.0 seconds |
| Looking down | > 5.0 seconds |
| Face off-screen | > 1.5 seconds |
| Rapid gaze shifts | > 6 shifts / 10 seconds |

When a violation is detected, it:
- Logs the event with timestamps to a CSV file (`session_log_<timestamp>.csv`)
- Saves a video clip (3-second pre-roll + post-roll) to an AVI file
- Tracks and reports suspicious keyboard shortcuts detected by `KeypressTrackProcessor`

---

### `heatmap_processor.py` — Heatmap Processor
Accumulates all gaze screen-position points recorded during the session. On exit, generates a Gaussian-blurred heatmap image showing where the subject looked most frequently. The output is saved as a colour-mapped PNG file (`session_heatmap_<timestamp>.png`).

---

### `keypress_trackprocessor.py` — Keypress Track Processor
Registers global keyboard hooks (using the `keyboard` library) to detect suspicious hotkey combinations without needing focus on the application window. Monitored combos include:

- `Alt+Tab`, `Ctrl+C/V/X` — switching and clipboard
- `Windows`, `Ctrl+Esc` — start menu / app switching
- `Ctrl+T/N/W`, `F11`, `Esc` — browser actions
- `Print Screen`, `Win+Shift+S` — screen capture
- `Alt+F4` — application evasion

Detections are stored in a thread-safe buffer and retrieved each frame by the main loop.

---

### `frame_bufferprocessor.py` — Frame Buffer Processor
Runs a dedicated background thread that continuously reads frames from the OpenCV `VideoCapture` object and stores the latest frame in a thread-safe buffer. This decouples frame acquisition from the processing loop, preventing the main loop from blocking on camera I/O and ensuring the freshest possible frame is always available.

---

## Machine-Learning Pipeline

The repository includes a session-level classifier that combines spatial gaze
patterns from the heatmap with behavioural events from the suspicion-scoring
CSV. Sessions must contain both a `session_heatmap_*.png` file and a
`session_log_*.csv` file to be included.

### Build the feature dataset

After collecting labelled sessions under `sessions/cheating/` and
`sessions/non_cheating/`, run:

```bash
python dataset_builder.py
```

`dataset_builder.py` scans both category folders and writes `features.csv`.
Each row represents one session and contains the extracted features, the
session ID, and the numeric label (`1` for cheating, `0` for non-cheating).
Sessions missing either required artifact are skipped. The output contains
one row per usable session, with 79 extracted numeric features followed by
the session metadata columns.

The current feature dataset contains 186 sessions in 81 columns: 79 numeric
predictors, `session_id`, and `label`. The classes are balanced with 93
non-cheating sessions and 93 cheating sessions. The dataset currently has no
missing values or duplicate session IDs.

### Average gaze-direction duration across all testers

The following summaries use all 93 sessions in each class. `Total Duration`
is the summed duration for a direction, `Normalized Seconds` is that duration
 divided by the total duration for the class, and `Average Duration per Tester` is
the total direction duration divided by the 93 testers in that class. Because
the denominator is the number of testers, this value represents average
seconds spent in a direction per tester, not the duration of an individual
transition run.

#### Non-cheating

| Gaze direction | Total Duration (seconds) | Normalized Seconds based on Total | Average Duration per Tester (seconds) |
|---|---:|---:|---:|
| Center | 9114.97 | 0.5319 | 98.01 |
| Down-Right | 265.09 | 0.0155 | 2.85 |
| Center-Right | 680.70 | 0.0397 | 7.32 |
| Down-Center | 2607.64 | 0.1522 | 28.04 |
| Up-Center | 2836.47 | 0.1655 | 30.50 |
| Up-Right | 372.22 | 0.0217 | 4.00 |
| Up-Left | 677.19 | 0.0395 | 7.28 |
| Center-Left | 424.00 | 0.0247 | 4.56 |
| Down-Left | 158.86 | 0.0093 | 1.71 |
| **Summary standard deviation** |  |  | **31.03** |
| **Summary coefficient of variation** |  |  | **1.52** |

#### Cheating

| Gaze direction | Total Duration (seconds) | Normalized Seconds based on Total | Average Duration per Tester (seconds) |
|---|---:|---:|---:|
| Center | 7481.27 | 0.2777 | 80.44 |
| Down-Right | 1207.28 | 0.0448 | 12.98 |
| Center-Right | 1798.47 | 0.0668 | 19.34 |
| Down-Center | 5042.07 | 0.1872 | 54.22 |
| Up-Center | 2899.42 | 0.1076 | 31.18 |
| Up-Right | 1394.79 | 0.0518 | 15.00 |
| Up-Left | 2800.20 | 0.1039 | 30.11 |
| Center-Left | 3096.81 | 0.1150 | 33.30 |
| Down-Left | 1219.12 | 0.0453 | 13.11 |
| **Summary standard deviation** |  |  | **22.40** |
| **Summary coefficient of variation** |  |  | **0.70** |

### Train the model

```bash
python train_model.py
```

Training uses a calibrated `RandomForestClassifier` with five-fold stratified
cross-validation. It prints cross-validated accuracy, ROC-AUC, and a
classification report, then saves:

| File | Description |
|---|---|
| `suspicion_model.joblib` | Trained calibrated classifier used for inference |
| `feature_columns.json` | Feature names and the order expected by the model |

Run training again whenever `features.csv` changes.

The current trained artifact was produced from the dataset described above.
Its stratified five-fold cross-validation results are:

| Metric | Result |
|---|---:|
| Cross-validated accuracy | 0.909 |
| Cross-validated ROC-AUC | 0.974 |

The per-class precision, recall, and F1-scores are approximately 0.90 to
0.91. These are cross-validated estimates rather than results from an
independent test set, so participant-level or future-session validation is
still required before deployment.

### Predict one session

```bash
python predict_session.py sessions/cheating/session_<id>
```

The predictor loads the saved model and feature-column order, extracts the
session features, supplies them as a named pandas `DataFrame`, and prints the
predicted label and confidence. It returns `(label, confidence)` when called
from Python, or `None` when the session is missing a heatmap or CSV log. After
a successful prediction, it also creates a unique output directory:

```text
predicted_sessions/
└── predicted_session_<uuid>/
      ├── gaze_grid_8x8.png
      └── predicted_values.json
```

`gaze_grid_8x8.png` is a colour-mapped visualisation of the 64 extracted grid
probabilities. `predicted_values.json` stores the source session, predicted
label, confidence, both class probabilities, grid size, all 64 grid values,
and the feature-column order used for prediction. The original return value
of `predict_session()` is unchanged.

## Feature Extraction Reference

The functions in `heatmap_feature_extractor.py` can also be imported directly:

| Function | Purpose |
|---|---|
| `build_jet_lut()` | Build the lookup table for OpenCV's JET colour map |
| `recover_intensity_map(heatmap_img)` | Recover a density surrogate from a saved heatmap image |
| `extract_heatmap_features(intensity_map, grid_size=8)` | Calculate centroid, spread, elongation, entropy, peak, coverage, and grid-cell features |
| `extract_csv_features(csv_path)` | Calculate violation counts, gaze transitions, non-centre time, and violation rate |
| `extract_session_features(session_dir)` | Combine heatmap and CSV features for one session |

The generated heatmap features include normalised centroid coordinates,
normalised spread on both axes, an elongation ratio, entropy, peak ratio,
coverage ratio, and an 8x8 occupancy grid. CSV features include counts for
`frantic_eye_movement`, `forbidden_key`, `off_screen`, and `duration`, plus
transition count, percentage of non-centre gaze time, and violation rate.
The extractor uses the first file returned for each matching heatmap or CSV
pattern; a session should therefore contain one corresponding heatmap and one
corresponding log.

### Heatmap feature calculations

`extract_heatmap_features()` receives a two-dimensional intensity map. Each
pixel is treated as a weighted gaze observation: a brighter pixel contributes
more strongly to the calculations than a darker pixel. The function first
converts the values to `float64` and calculates `total_mass`, the sum of all
pixel intensities. If this value is zero, the function returns a complete set
of zero-valued features because there is no gaze density from which to
calculate a position or distribution.

For a usable map, OpenCV calculates image moments. The zeroth moment, `m00`,
is the total weighted intensity and acts as the denominator for the weighted
averages. The first moments, `m10` and `m01`, give the gaze centroid:

```text
centroid_x = m10 / m00
centroid_y = m01 / m00
```

The centroid is divided by the image width and height to produce
`centroid_x_norm` and `centroid_y_norm`. These values are resolution-
independent: `0` represents the left or top edge, `0.5` is approximately the
middle, and `1` represents the right or bottom edge.

The central moments `mu20` and `mu02` describe the horizontal and vertical
spread around the centroid. Dividing them by `m00` produces weighted
variances:

```text
var_x = mu20 / m00
var_y = mu02 / m00
```

The square roots produce standard deviations, which are then normalised by
the image dimensions to produce `spread_x` and `spread_y`. Small values mean
the gaze is concentrated near the centroid; larger values mean it is spread
across more of the screen. The mixed central moment `mu11` measures whether
horizontal and vertical deviations occur together and is used as the
covariance value `cov_xy`.

The covariance matrix is formed as:

```text
[ var_x   cov_xy ]
[ cov_xy  var_y  ]
```

`np.linalg.eigvalsh()` calculates its two eigenvalues. Each eigenvalue is the
variance along one principal direction of the gaze distribution. The smaller
value represents the narrow direction and the larger value represents the
widest direction. Their ratio becomes `elongation_ratio`:

```text
elongation_ratio = largest_eigenvalue / smallest_eigenvalue
```

A ratio near `1` means the distribution is similarly wide in both directions.
A large ratio means it is stretched along one direction. Eigenvalues are
clipped to a minimum of `1e-9` before division so a highly concentrated map
cannot cause division by zero.

To describe the spatial distribution in a compact and consistent format, the
intensity map is resized to an 8x8 grid using area interpolation. The 64 grid
values are divided by their sum, creating probabilities that represent the
relative gaze activity in each region. They are stored as
`grid_cell_0` through `grid_cell_63`, in row-major order from the top-left
cell to the bottom-right cell.

The grid probabilities are also used to calculate entropy:

```text
entropy = -sum(p * log2(p))
```

Zero-probability cells are ignored because `log2(0)` is undefined. Low entropy
means gaze is concentrated in a few grid regions; high entropy means gaze is
distributed more evenly across the grid.

`peak_ratio` measures hotspot concentration. The intensity pixels are sorted
from brightest to darkest, the brightest 5 percent are selected, and their
intensity is divided by `total_mass`:

```text
peak_ratio = intensity of brightest 5% of pixels / total_mass
```

A high value indicates that much of the gaze density is concentrated in a
small number of hotspots. Finally, `coverage_ratio` counts the pixels whose
intensity is greater than `25` and divides by the total number of pixels. It
therefore measures how much of the image contains meaningful recovered gaze
density.

Together, the eight global heatmap features and 64 grid probabilities produce
72 heatmap features. `extract_csv_features()` adds seven behavioural features,
so each complete session contributes 79 numeric model features.

## Python API Summary

The main callable entry points are:

| Function | Module | Returns |
|---|---|---|
| `build_dataset()` | `dataset_builder.py` | A pandas `DataFrame`, or `None` when no usable sessions are found |
| `train_model()` | `train_model.py` | Saves the trained model and feature-column metadata |
| `predict_session(session_dir)` | `predict_session.py` | `(label, confidence)`, or `None` for incomplete sessions |
| `FaceAxisProcessor.process(avg_direction)` | `face_axisprocessor.py` | Calibrated yaw and pitch |
| `FaceAxisProcessor.get_estimated_screen_position()` | `face_axisprocessor.py` | Clamped `(x, y)` screen coordinates |
| `GazeDirectionProcessor.weighted_screen_position(face, eye)` | `gaze_directionprocessor.py` | Blended screen position and 3x3 grid label |
| `HeatmapProcessor.add_point(screen_pos)` | `heatmap_processor.py` | Adds a bounded gaze point to the session |
| `HeatmapProcessor.generate_heatmap()` | `heatmap_processor.py` | Saved heatmap path, or `None` when no points exist |
| `SuspicionScoringProcessor.update(...)` | `suspicion_scoringprocessor.py` | Current recording and violation state |

