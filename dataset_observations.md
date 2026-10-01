# Dataset Observations

## Overview

The dataset contains 186 session-level observations and 81 columns. Each row represents one recorded session. The dataset contains 79 potential predictor variables, a `session_id` identifier, and a binary `label`.

The predictor variables consist of:

- Eight gaze-distribution features: normalized gaze centroid, horizontal and vertical spread, elongation ratio, entropy, peak ratio, and coverage ratio.
- Sixty-four spatial heatmap features representing a grid of screen regions.
- Seven behavioral features: frantic eye-movement violations, forbidden-key violations, off-screen violations, duration violations, number of gaze transitions, percentage of time outside the center region, and overall violation rate.

## Class Distribution

The classes are approximately balanced:

- Label 0: 93 sessions, or 50.0% of the dataset.
- Label 1: 93 sessions, or 50.0% of the dataset.

This balance is useful for binary classification because the model is less likely to achieve an apparently high accuracy simply by predicting the majority class.

## Data Quality

No missing values were observed in the dataset. All predictor columns contain numeric values, while `session_id` is a string identifier and `label` is the target variable. No duplicate session IDs were found in the inspected data.

## Captured Session Video Clips Analysis

Each session logs automated `.mp4` video clips whenever a behavioral violation is triggered (e.g., frantic eye movements, forbidden key shortcuts, eyes off-screen, or prolonged directional looks). Across all 186 sessions in the dataset, a total of **3,135 video clips** were captured.

### Overall & Class-Level Clip Counts

| Metric | Cheating (Label 1) | Non-Cheating (Label 0) | Overall Dataset / Difference |
|---|---:|---:|---:|
| **Total Sessions** | 93 | 93 | 186 sessions |
| **Total Captured Clips** | 2,035 | 1,100 | 3,135 clips |
| **Mean Clips / Session** | **21.88** | **11.83** | **+10.05 clips (+84.9%)** |
| **Median Clips / Session** | 20.0 | 11.0 | +9.0 clips |
| **Standard Deviation** | 9.29 | 6.29 | — |
| **Min / Max Range** | 4 to 57 | 1 to 38 | — |

### Key Observations & Comparison

- **Substantial Increase in Captured Evidence**: Cheating sessions captured an overall average of **21.88 clips per session**, compared to **11.83 clips per session** for non-cheating sessions. This represents an average difference of **+10.05 clips per session** (an 84.9% increase in recorded video evidence).
- **Statistical Significance**: A two-sample t-test ($t = 8.44, p = 2.67 \times 10^{-15}$) and Mann-Whitney U test ($U = 7,370.5, p = 1.76 \times 10^{-18}$) confirm that cheating sessions produce significantly more violation clips than non-cheating sessions.
- **Violation Category Breakdown**:
  - **Forbidden-Key Clips**: Cheating sessions averaged **5.47 clips/session** (509 total), whereas non-cheating sessions averaged **0.03 clips/session** (3 total).
  - **Frantic Eye Movement Clips**: Cheating sessions averaged **10.67 clips/session** (992 total) vs. **8.26 clips/session** (768 total) in non-cheating sessions.
  - **Off-Screen Violations**: Cheating sessions averaged **1.42 clips/session** (132 total) vs. **0.41 clips/session** (38 total) in non-cheating sessions.
  - **Duration Gaze Violations**: Cheating sessions averaged **4.32 clips/session** (402 total) vs. **3.13 clips/session** (291 total) in non-cheating sessions.

This difference aligns with expectations, as cheating sessions trigger considerably more hotkey violations, off-screen gaze diversions, and frantic eye patterns, directly resulting in a higher volume of auto-recorded video evidence clips.

## Observed Feature Patterns

Sessions assigned to label 1 generally show more active and dispersed gaze behavior than sessions assigned to label 0. The strongest observed differences include:

- A higher number of gaze transitions. The approximate mean difference between label 1 and label 0 was 260 transitions.
- More forbidden-key violations, with an approximate mean difference of 5.5 violations.
- A substantially higher number of auto-captured video evidence clips, averaging 21.88 clips per session for label 1 versus 11.83 clips for label 0 (a mean difference of +10.05 clips).
- Higher heatmap coverage, indicating that gaze activity is distributed across a larger portion of the screen.
- Higher entropy, indicating a less concentrated gaze distribution.
- A lower peak ratio, indicating that gaze activity is less concentrated in a single dominant region.
- More time spent outside the center region.

These observations suggest that the label-1 sessions are associated with wider screen exploration, more variable gaze behavior, and more recorded behavioral violations. However, these are associations and should not be interpreted as evidence of causation.

## Feature Relationships

Several features are strongly correlated with one another:

- Entropy and coverage ratio have a correlation of approximately 0.94.
- Entropy and peak ratio have a correlation of approximately -0.92.
- Coverage ratio and peak ratio have a correlation of approximately -0.91.

These relationships are expected because all three features describe aspects of the same gaze-distribution pattern. However, the redundancy may reduce the amount of independent information available to the model and can make feature-importance interpretations less reliable.

## Potential Outliers

Some features contain unusually large values relative to the rest of the dataset:

- `elongation_ratio` reaches approximately 39.65, while most observations are substantially lower.
- `num_transitions` reaches approximately 1,547.
- Several violation-count and duration features also contain relatively high values, including up to 16 forbidden-key violations, 30 off-screen violations, and 24 duration violations in a session.

These observations should be inspected to determine whether they represent genuine behavior, unusually long sessions, tracking errors, or data-processing artifacts. Outliers should not be removed automatically, since unusual behavior may be relevant to the classification task.

## Suitability as a Prediction-Model Foundation

The dataset is a suitable starting point for developing and testing a prototype prediction model. It has a clear target variable, a nearly balanced class distribution, consistent session-level features, and multiple feature groups that describe complementary aspects of gaze behavior.

The current training approach is also a reasonable baseline. It uses a Random Forest classifier, stratified five-fold cross-validation, probability calibration, and a saved feature-column order for inference.

Nevertheless, the dataset is small relative to the number of predictors. With 186 sessions and 79 predictors, the model may overfit, and cross-validation results may vary considerably depending on the sampled sessions. Therefore, the current dataset should be treated as an exploratory or proof-of-concept dataset rather than sufficient evidence for deployment.

## Model Trainer Results

The model trainer was executed using the current complete dataset. It trained a calibrated Random Forest classifier using stratified five-fold cross-validation. The reported cross-validated results were:

| Metric | Result |
|---|---:|
| Cross-validated accuracy | 0.909 |
| Cross-validated ROC-AUC | 0.974 |

The classification report was:

| Class | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Non-cheating | 0.90 | 0.91 | 0.91 | 93 |
| Cheating | 0.91 | 0.90 | 0.91 | 93 |
| Macro average | 0.91 | 0.91 | 0.91 | 186 |
| Weighted average | 0.91 | 0.91 | 0.91 | 186 |

The overall cross-validated accuracy was 0.91, with similar precision, recall, and F1-scores for both classes. This indicates that the current feature set separates the two classes reasonably well within the cross-validation procedure. The ROC-AUC of 0.97 indicates strong ranking performance across classification thresholds, although the lower accuracy than the earlier run shows that the estimate is sensitive to the current dataset and should not be treated as deployment evidence.

These results should be interpreted cautiously. They are cross-validated estimates generated from 186 sessions, not results from a completely independent test set. They may therefore be optimistic if sessions from the same participant or recording conditions appear in both training and validation folds, or if any feature is closely related to the labeling procedure. Independent participant-level or future-session testing is still required.

After training, the model artifact was saved as `suspicion_model.joblib`, and the feature order used during training was saved as `feature_columns.json`. These files support consistent feature alignment during session-level prediction.

## Validation Risks and Limitations

The following issues should be addressed before drawing strong conclusions from model performance:

1. If several sessions belong to the same participant, random cross-validation may place sessions from the same participant in both the training and validation folds. This can produce overly optimistic performance estimates. Participant-level splitting should be used when participant identifiers are available.
2. Violation-related features may be closely connected to how the labels were assigned. A separate model trained without violation features should be evaluated to determine whether gaze patterns alone provide predictive value.
3. The labels should represent independently defined ground truth. If the label was assigned because a session was intentionally created as a cheating or non-cheating scenario, the result may measure differences between experimental conditions rather than reliably detecting real-world cheating.
4. The dataset should be tested on new participants and new sessions. Performance on unseen data is more informative than performance on the sessions used to construct the feature dataset.
5. Accuracy should not be used as the only evaluation metric. ROC-AUC, precision, recall, F1-score, PR-AUC, confusion matrices, and calibrated probabilities should also be reported.

## Recommended Future Work

The following steps would strengthen the dataset and the resulting model:

- Collect more sessions from a larger and more diverse participant group.
- Record participant identifiers and use participant-level train/test splits.
- Evaluate models with and without violation features.
- Use repeated cross-validation or bootstrap confidence intervals to quantify uncertainty.
- Test the final model on a separate holdout set collected after model development.
- Investigate the extreme elongation and transition values.
- Standardize recording conditions and document camera position, lighting, calibration quality, session duration, and screen configuration.
- Compare the Random Forest baseline with simpler models such as logistic regression and regularized linear classifiers.
- Examine feature importance using permutation importance or model-agnostic explanations rather than relying only on raw tree importance.

## Summary

The dataset provides a promising foundation for an exploratory gaze-behavior classification model. Label 1 is associated with more dispersed gaze activity, more transitions, higher coverage and entropy, lower peak concentration, more recorded violations, and nearly double the number of auto-captured video evidence clips (21.88 vs 11.83 clips per session). The balanced classes and absence of missing values are positive properties.

However, the limited number of sessions, possible participant dependence, strong feature correlations, outliers, and possible relationship between violation features and labels limit the strength of the conclusions. The increase to 186 sessions improves the sample size, but the dataset is still appropriate primarily for developing a baseline and guiding further data collection. Additional validation is required before the model can be described as reliable for real-world decision-making.
