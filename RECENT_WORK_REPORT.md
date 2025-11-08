Project: FINAL-YEAR-PROJECT
Report date: 2025-10-27
Author: automated assistant (work summary)

## Summary
This document summarizes the edits and actions performed in the repository during the recent session. It includes code changes, dependency installs, verification steps performed locally, and recommended next actions.

## High-level changes
- Implemented persistence and helper functionality in `attendance_tracker.py`.
  - Added type hints and methods: `to_dict`, `from_dict`, `save_json`, `load_json`, `save_csv`, `load_csv`.
  - Added `percent_present`, `mark_absent`, `clear`, and a concise `__repr__`.
  - Ensured CSV/JSON formats are robust (truthy present values accepted in CSV).

- Reworked and hardened `kiosk_app.py` (kiosk client):
  - Added CLI args and logging (`--api`, `--camera`, `--cooldown`, `--snapshots`, `--verbose`).
  - Camera selection and properties set for better capture.
  - Face detection cascade loading with error checks.
  - Recognition cooldown logic and small retry loop for API calls.
  - Optional face snapshot saving to `./kiosk_snapshots` with timestamps.
  - Key controls in the OpenCV window: `q` (quit), `s` (select session), `r` (refresh sessions), `t` (toggle snapshots).
  - Status overlay text on the video window for recent recognition results.

- Installed missing dependency `requests` into the active Python interpreter and verified import.

- Located backend server entrypoint: `attendance_api.py` (FastAPI app). Confirmed FastAPI endpoints include `/api/attendance/check-in` expected by the kiosk client.

- Maintained and updated an internal todo list to track progress.

## Files created/edited
- Edited: `attendance_tracker.py`
  - Purpose: Core attendance model; now supports persistence (CSV/JSON), helpers and robust I/O.

- Edited: `kiosk_app.py`
  - Purpose: Kiosk client (OpenCV-based) improved with CLI, robustness, saving snapshots and better API handling.

- Created: `RECENT_WORK_REPORT.md` (this file)

- Todo list (in-memory/project tracking) updated via tool; current statuses recorded in workspace metadata.

## Commands run (locally in this workspace)
- Installed `requests` (PowerShell):

```powershell
py -3 -m pip install requests
```

- Verified `requests` import and version:

```powershell
py -3 -c "import requests; print('requests', requests.__version__)"
```

- To run the backend API server (development):

```powershell
py -3 attendance_api.py
# or, with auto-reload
py -3 -m uvicorn attendance_api:app --host 0.0.0.0 --port 8000 --reload
```

- To run the kiosk client (after starting backend):

```powershell
py -3 kiosk_app.py --api http://localhost:8000 --camera 0 --snapshots --verbose
```

## Verification / Testing performed
- Confirmed `requests` installed and importable (version printed).
- Inspected `attendance_api.py` to confirm it runs Uvicorn on `0.0.0.0:8000` when executed, and exposes `/api/attendance/check-in` used by kiosk.
- Basic sanity checks in code (cascade load error handling, frame processing) were added; no full end-to-end runtime tests were executed here (requires webcam + running backend + enrolled students).

## Outstanding items / recommended next steps
1. Add unit tests
   - Add pytest tests for `AttendanceTracker` (happy path + edge cases: empty roster, invalid IDs, CSV/JSON roundtrip).
   - Add integration test (mock `requests`) for `kiosk_app` recognition flow.

2. Add a small CLI demo
   - Create `attendance_cli.py` that demonstrates creating an `AttendanceTracker`, marking students present/absent, and saving/loading CSV/JSON.

3. Add `requests` to `requirements.txt`
   - The project `requirements.txt` currently lists many packages but not `requests`.
   - Add a pinned or minimally constrained version (e.g. `requests>=2.32.5`).

4. Run a manual end-to-end smoke test
   - Start `attendance_api.py`.
   - Enroll at least one test student (use `enroll_students.py` or the `/api/students/enroll` endpoint).
   - Create and start a session (POST `/api/sessions` then `/api/sessions/{id}/start`).
   - Run `kiosk_app.py` and verify the kiosk can check-in the enrolled student.

5. Optional: Improve robustness
   - Add better error handling and retry/backoff for network calls in `kiosk_app.py`.
   - Add logging to `attendance_tracker` operations and tests.

## Quick links (files)
- attendance_tracker.py
- kiosk_app.py
- attendance_api.py
- requirements.txt

## How I verified changes
- Used file reads and edits via the repository tooling.
- Ran `pip install requests` and a small import check using the system Python.
- Searched the repository for API endpoints and key symbols to confirm integration points (grep).

## Notes / assumptions
- I edited `kiosk_app.py` to be self-contained; the kiosk expects the backend at the provided `--api` URL and a running session. The machine running the kiosk should have a webcam accessible by OpenCV.
- I installed `requests` into the active interpreter used by `py -3` on this machine. If you run the project under a different environment (virtualenv), install dependencies there instead.

---
If you want, I can:
- Add `requests>=2.32.5` to `requirements.txt` now.
- Create the `attendance_cli.py` demo and simple pytest tests for `AttendanceTracker` and the kiosk logic (mocking network and camera).
- Run the backend server and a headless kiosk smoke test in this environment (note: webcam access and GUI may not be available in headless CI).

Which of the next steps shall I take now? (add req, add tests, add CLI demo, or run the server+kiosk smoke test)

## Model descriptions
This project uses a conventional face-recognition pipeline made of separate stages. Documenting each component makes evaluation reproducible.

- Face detection
   - Current: OpenCV Haar cascade (haarcascade_frontalface_default.xml) loaded via cv2.
   - Function: detect face bounding boxes in frames.
   - Limitations: sensitive to lighting and pose; may produce false positives in complex backgrounds.

- Face encoding / recognition
   - Current (observed in repository): `face_recognition` (dlib-based) to compute 128-d face encodings and compare using Euclidean distance.
   - Alternative/optional: DeepFace/TensorFlow models that produce embeddings (useful if higher accuracy is required).
   - Key hyperparameters: distance threshold (typ. 0.4–0.7); choosing this threshold affects FAR/FRR trade-off.

- Post-processing
   - Cooldown: a simple time-based suppression (default 3s) to avoid repeated check-ins from rapid frame-to-frame detections.
   - Snapshot saving: optional storage of cropped face images for manual audit.

Include these descriptions with concrete values in the final report (which model/version, threshold used, face alignment/preprocessing steps).

## Evaluation plan & metrics
To properly claim improvements or measure accuracy, follow a reproducible evaluation protocol with these metrics:

- Dataset and splits
   - Enroll set: photos used to register each student (store at least N_enroll images per student, e.g. 5).
   - Test set: independent frames/images used for recognition (N_test per student, captured in different lighting/angles).
   - Use a validation split to tune thresholds (e.g., 70/15/15 or k-fold when dataset is small).

- Metrics to report
   - TP/FP/FN/TN counts and derived measures: Precision, Recall, F1-score.
   - Accuracy (overall), but prefer per-class or per-subject breakdown when classes are imbalanced.
   - FAR (False Acceptance Rate) and FRR (False Rejection Rate). Report EER (Equal Error Rate) when possible.
   - ROC curve and AUC if the model produces continuous similarity scores.
   - Confusion matrix (aggregate or per-subject) to identify common confusions.
   - Latency: mean time per recognition (ms) and throughput (fps).

Define exactly how a prediction maps to TP/FP/FN/TN in this application. For example: a recognition is a positive prediction for student X at time t; compare to ground-truth label for that frame/time.

## Experimental protocol (step-by-step)
1. Prepare dataset
    - Enroll each subject using `enroll_students.py` or API `/api/students/enroll` with several photos.
    - Capture test footage for each subject under representative conditions (lighting, distance, occlusion, multiple people in frame).

2. Create a session and start it (via API or dashboard)
    - Use `/api/sessions` to create and `/api/sessions/{id}/start` to activate.

3. Run the kiosk client and capture logs
    - Start `kiosk_app.py` with `--verbose --snapshots` to record API responses and cropped snapshots.
    - For each test run record: timestamp, detected bounding box, returned student_id (or failure), and similarity/confidence score if available.

4. Ground truth labeling
    - Either label frames manually (recommended for small experiments), or use controlled single-subject captures where ground truth is known by design.

5. Threshold selection
    - Use a validation split to choose a working distance threshold (sweep thresholds and pick where F1 or EER is best).

6. Evaluation
    - Compute metrics listed above and produce plots (ROC, precision-recall).

## Results table template
Below is a suggested markdown table template to put in the report after running experiments.

| Model / Pipeline | Threshold | TP | FP | FN | TN | Precision | Recall | F1 | FAR | FRR | Latency (ms) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| face_recognition (dlib) + Haar | 0.6 | 120 | 5 | 10 | 865 | 0.96 | 0.92 | 0.94 | 0.0056 | 0.076 | 85 |
| face_recognition + CentroidTracker | 0.6 | 125 | 3 | 8 | 864 | 0.98 | 0.94 | 0.96 | 0.0035 | 0.060 | 95 |

Fill this table with real numbers after experiments; the example row above is illustrative only.

## Explanation: cooldown vs. object tracking
- Cooldown (current)
   - Mechanism: after a successful recognition, the kiosk waits a fixed time window (e.g., 3 seconds) before accepting another recognition. This reduces repeated check-ins from the same subject in consecutive frames.
   - Pros: very simple to implement, no additional state storage beyond a timestamp.
   - Cons: coarse control — cannot reliably differentiate different people who appear within the cooldown window; if the same person leaves and returns later the cooldown may block a legitimate re-check.

- Object tracking (recommended)
   - Mechanism: use a lightweight tracker (CentroidTracker, SORT, or Deep SORT) to assign persistent IDs to detected face boxes across frames. Trackers store last_seen timestamps and a per-ID check-in flag.
   - Integration idea: only perform recognition for trackers that are new or not-yet-checked-in; when a tracker is matched to a recognized student, mark that tracker as checked-in and record a timestamp. Optionally still use a cooldown per tracker.
   - Pros: robust against frame-to-frame duplication, supports multiple people simultaneously, reduces false duplicates.
   - Cons: requires matching logic and maintenance of tracker state; more code and (for Deep SORT) extra dependencies.

Recommendation: implement a CentroidTracker first (lightweight) and measure reduction in duplicate check-ins. If occlusion and identity switches are common, upgrade to SORT/Deep SORT.

## Improvements vs prior work (how this project can be stronger)
- Data & preprocessing
   - Face alignment and normalization before encoding (improves embedding stability).
   - Augment enrollment images (flip, slight rotations) to make enrollments more robust.

- Modeling & inference
   - Use ensemble or more modern embedding models (e.g., ArcFace-based backbones) for higher accuracy.
   - Consider score calibration per subject when enrollment set is small.

- System-level
   - Integrate tracking (Centroid/SORT/Deep SORT) to avoid duplicate check-ins and improve multi-person accuracy.
   - Add server-side verification: accept a recognition only if the server-side confidence score and recent tracking history agree.
   - Add logging pipeline and a small dashboard to review false acceptances/false rejections quickly.

## Actionable next steps
1. Update code: add CentroidTracker into `kiosk_app.py` and create a log format for evaluation.
2. Add `tools/evaluate_recognition.py` to compute metrics from the kiosk log (CSV) and generate plots.
3. Run small controlled experiments (5–10 subjects, multiple conditions) and fill the results table above.
4. Iterate: if tracker improves results but occlusion/switches remain, try SORT or Deep SORT.

---
_Report updated to include evaluation plan, metrics, experimental steps, and recommended improvements._