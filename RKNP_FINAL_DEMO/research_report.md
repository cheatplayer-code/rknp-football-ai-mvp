# RKNP Football AI MVP — Competition Research Report

**Project Title:**  
RKNP Football AI MVP: Short-Clip Image-Space Tracking for Single Player Analysis

---

## 1. Problem Statement

Football video analysis tools are expensive, require full-match tracking, and claim advanced metrics (xG, pass accuracy, real-world speed) that small teams cannot reliably compute from ordinary broadcast footage. Coaches and players need a **low-cost, honest, evidence-based tool** that:

- Works with 15–20 second clips from ordinary video
- Tracks ONE manually selected player
- Produces transparent image-space metrics
- Clearly states limitations and failure modes
- Uses LLM only to explain existing JSON metrics, not to invent computer vision facts

---

## 2. Engineering Goal

Build a competition-ready MVP that demonstrates:

1. **Reliable short-clip tracking** of a single player using YOLO detection + ByteTrack
2. **Quality gate** that marks runs as `demo_suitable` or flags specific failure reasons
3. **Image-space metrics** (visibility %, trusted %, ball-near %, pressure %, body-heights/sec speed)
4. **Honest reports** with clear limitation notices and failure taxonomy
5. **LLM explanation layer** that only narrates existing JSON data

---

## 3. MVP Scope

| In Scope | Out of Scope |
|----------|--------------|
| 15–20 second video clips | Full-match tracking |
| ONE manually selected player | Multi-player tactical analysis |
| Image-space metrics (body-heights/sec) | Real-world speed (km/h) or distance (meters) |
| YOLO ball detection (evidence-only) | Pass accuracy, xG, expected threats |
| Quality gate + failure taxonomy | Heatmaps, tactical network graphs |
| Markdown/JSON reports | Automated talent scouting ratings |
| OpenAI explains JSON metrics only | OpenAI watching video or doing CV |

---

## 4. Architecture Pipeline

```text
Video Input (15–20 sec clip)
    ↓
Player Selection (auto lower-center OR coach-click seed bbox)
    ↓
Detection & Tracking (YOLOv8 + ByteTrack @ 5 FPS sampled)
    ↓
Player Crop & Overlay Videos (target highlighted in green)
    ↓
Metrics Computation (visibility, trusted, ball-near, pressure, speed)
    ↓
Quality Gate (demo_suitable, hard_demo_blockers, failure_taxonomy)
    ↓
JSON + Markdown Report (with limitation banner)
    ↓
LLM Explanation (OpenAI explains JSON only; offline fallback available)
```

**Core Files:**
- `rknp_single_player_demo.py` — Main pipeline
- `rknp_openai_player_analysis.py` — Text layer over JSON
- `rknp_demo_selector.py` — Ranks runs by demo suitability
- `rknp_lk_target_tracker.py` — Fallback optical-flow tracker (evidence-only)

---

## 5. Research Hypotheses

| # | Hypothesis | Status |
|---|------------|--------|
| H1 | Video quality (resolution, blur, camera motion) affects tracking reliability | **Supported** — see failure cases with bbox drift |
| H2 | Manual player selection (coach-click) reduces identity ambiguity vs auto-selection | **Supported** — candidate sheet enables visual confirmation |
| H3 | Color guard (yellow vs blue jerseys) helps but does not solve same-team confusion | **Supported** — yellow/blue case shows both trackable but still has outlier risk |
| H4 | Ball-near metrics are weak when ball is small, blurred, occluded, or not detected by YOLO | **Supported** — ball-near % low (3.5–8.6%) even in active episodes |
| H5 | LLM is useful only as a report explanation layer, not as a CV fact generator | **Supported** — OpenAI mode strictly grounded to JSON with fallback banner |

---

## 6. Metrics Table (From Existing Sample Outputs)

### 6.1 Primary Demo Case (`primary_134136`)

| Metric | Value |
|--------|-------|
| Duration | 16.0 sec |
| Visibility % | 100.0% |
| Trusted % | 100.0% |
| Ball-near % | 7.41% |
| Pressure % | 55.56% |
| Avg Speed (body-heights/sec) | 1.071 |
| P90 Speed | 2.158 |
| Max Speed | 3.97 |
| Speed Outliers | 1 |
| FIFA-style OVR | 84 |
| Demo Suitable | **True** |

**Key Events:**
- 00:13.3 — Run into space (peak speed 3.97 body-heights/sec)
- 00:03.9 — Receiving ball (ball-near detected, outcome not claimed)
- 00:02.7 — Pressing context (nearby players detected)

---

### 6.2 Backup Demo Case (`backup_134049`)

| Metric | Value |
|--------|-------|
| Duration | 11.4 sec |
| Visibility % | 100.0% |
| Trusted % | 96.55% |
| Ball-near % | 8.62% |
| Pressure % | 86.21% |
| Avg Speed (body-heights/sec) | 0.868 |
| P90 Speed | 1.683 |
| Max Speed | 2.208 |
| Speed Outliers | 3 |
| FIFA-style OVR | 82 |
| Demo Suitable | **True** |

**Key Events:**
- 00:11.7 — Run into space (peak speed 2.21 body-heights/sec)
- 00:03.5 — Carrying ball (ball-near detected, outcome not claimed)
- 00:02.7 — Pressing context (nearby players detected)

---

### 6.3 Yellow vs Blue Two-Player Case

| Player | Visibility % | Trusted % | Ball-near % | Pressure % | Avg Speed | P90 Speed | Outliers | OVR |
|--------|--------------|-----------|-------------|------------|-----------|-----------|----------|-----|
| Yellow | 100.00% | 100.00% | 3.53% | 78.82% | 1.653 | 3.161 | 8 | 85 |
| Blue | 100.00% | 100.00% | 5.88% | 84.71% | 1.332 | 2.634 | 7 | 85 |

**Interpretation:**
- Both players visible and trackable in short episode
- Blue had slightly higher ball-near and pressure values
- Yellow had higher average and P90 movement intensity
- Both tracks have speed outliers → must describe as image-space movement, not real-world m/s

---

### 6.4 LK Tracker Evidence Case (`lk_yellow_frame75_clean`)

| Metric | Value |
|--------|-------|
| Method | Lucas-Kanade optical flow |
| Visible % | 100.0% |
| Status | Tracked for 24 sampled frames (≈2.5 sec window) |
| Artifacts | Overlay video, crop sheet, JSON report |

**Note:** LK tracker is a **fallback evidence tool**, not integrated into main quality gate. Useful for showing what happens when detection-based tracking struggles.

---

## 7. Honest Limitations

1. **Short-clip only:** This MVP analyzes 15–20 second episodes, not full matches. Multiple clips are needed for robust player assessment.

2. **Image-space metrics:** Speed is measured in **body-heights per second**, NOT km/h or meters per second. No camera calibration is performed.

3. **Ball detection weakness:** YOLO ball detection is unreliable when the ball is small, blurred, occluded, or in crowded scenes. Ball-near % should be treated as a **lower bound**.

4. **Auto-selection requires confirmation:** The auto-selected player (lower-center heuristic) must be visually confirmed via the candidate sheet before trusting the report.

5. **Same-team jersey confusion:** Color guard helps distinguish yellow vs blue teams, but does not solve identity swaps when multiple players wear similar jerseys.

6. **No tactical claims:** This MVP does NOT compute pass accuracy, xG, expected threats, heatmaps, or tactical network metrics.

7. **LLM does not watch video:** OpenAI/LLM only explains existing JSON metrics. It does NOT perform computer vision or observe the video directly.

---

## 8. Failure Taxonomy

| Failure Type | Description | Detection Signal | Mitigation |
|--------------|-------------|------------------|------------|
| `bbox_drift_or_motion_jump` | Bounding box jumps or drifts due to fast motion or camera shake | Sudden large bbox change between frames | Use LK tracker as evidence; flag run as unsuitable |
| `close_players_or_occlusion_risk` | Target player passes near teammates/opponents, risking ID swap | High nearby_player_count; drop in tracking score | Coach visual confirmation; mark as caution case |
| `ball_not_detected` | Ball is present but YOLO fails to detect it | Low ball_near_pct despite visual evidence | Note limitation; do not claim ball interaction |
| `low_visibility` | Target player not visible in many frames | visibility_pct < 80% | Reject run for demo; select different clip |
| `low_trusted_ratio` | Many frames have low tracking confidence | trusted_pct < 90% | Flag as risky; show as failure-case evidence |
| `speed_outliers` | Implausible speed spikes due to tracking noise | raw_max_speed >> max_speed after filtering | Filter outliers; report cleaned max speed |

---

## 9. Future Work (Post-Competition)

1. **Interactive target confirmation:** Simple GUI or web interface for coach to click and confirm target player before running full pipeline.

2. **Multi-clip aggregation:** Combine metrics from 5–10 short clips to build a more robust player profile.

3. **Improved ball detection:** Train a custom ball detector on football-specific datasets to improve ball-near reliability.

4. **Camera motion compensation:** Estimate global motion to distinguish player movement from camera pan/zoom.

5. **ReID for same-jersey tracking:** Integrate appearance-based re-identification to reduce ID swaps in same-color scenarios.

6. **Export to coaching platforms:** Generate CSV/JSON exports compatible with existing coaching software (Hudl, Sportscode, etc.).

---

## 10. Defense-Ready Explanation

### What This MVP Does Claim

- ✅ Tracks ONE manually selected player in 15–20 second clips
- ✅ Computes image-space metrics (visibility %, trusted %, ball-near %, pressure %, body-heights/sec)
- ✅ Generates overlay videos and contact sheets as visual evidence
- ✅ Applies a quality gate to flag suitable vs risky runs
- ✅ Uses OpenAI/LLM to explain existing JSON metrics in plain language
- ✅ Provides honest limitation notices and failure taxonomy

### What This MVP Does NOT Claim

- ❌ Full-match tracking or analysis
- ❌ Real-world speed (km/h) or distance (meters)
- ❌ Pass accuracy, xG, expected threats, or tactical value
- ❌ Heatmaps, passing networks, or formation analysis
- ❌ Automated talent scouting or recruitment recommendations
- ❌ OpenAI/LLM watching the video or performing computer vision

### Core Defense Statement

> "This MVP demonstrates that **ordinary video can support low-cost, evidence-based individual player review**, but tracking reliability depends on video quality, target selection, occlusion, and jersey similarity. We explicitly limit claims to image-space metrics, clearly mark failure modes, and use LLM only as an explanation layer over verified JSON data."

---

## 11. Appendix: File Reference

| File | Purpose |
|------|---------|
| `rknp_single_player_demo.py` | Main tracking pipeline |
| `rknp_openai_player_analysis.py` | LLM explanation layer |
| `rknp_demo_selector.py` | Ranks runs by demo suitability |
| `rknp_lk_target_tracker.py` | Fallback optical-flow tracker |
| `sample_outputs/primary_134136/` | Best demo case (high reliability) |
| `sample_outputs/backup_134049/` | Secondary demo case (high reliability) |
| `sample_outputs/screenshot_yellow_vs_blue/` | Two-player comparison case |
| `sample_outputs/lk_failure_case/` | LK tracker evidence examples |
| `sample_outputs/demo_selector/` | Demo ranking summary |

---

**Report Generated:** Based on existing JSON reports and sample outputs in `sample_outputs/` directory. No numerical results were invented; all values are from actual pipeline runs.
