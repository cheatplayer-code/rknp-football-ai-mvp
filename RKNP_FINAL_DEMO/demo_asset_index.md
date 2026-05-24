# RKNP Demo Asset Index

Competition-ready asset list for live demo. Do not deviate from these files.

## 1. Main Demo (Primary Case: `primary_134136`)

**Use this sequence for the main presentation.**

| # | Asset Type | File Path | Purpose |
|---|------------|-----------|---------|
| 1 | Overlay Video | `sample_outputs/primary_134136/target_overlay_sampled.mp4` | Show tracking box on original footage |
| 2 | Player Crop | `sample_outputs/primary_134136/player_centered_sampled.mp4` | Show player-centered stabilization |
| 3 | Candidate Sheet | `sample_outputs/primary_134136/candidate_selection_sheet.jpg` | **Crucial:** Show manual target selection (green box) |
| 4 | Contact Sheet | `sample_outputs/primary_134136/target_tracking_contact_sheet.jpg` | Show frame-by-frame consistency |
| 5 | Markdown Report | `sample_outputs/primary_134136/rknp_single_player_report.md` | Show human-readable analysis & limitations |
| 6 | JSON Metrics | `sample_outputs/primary_134136/rknp_single_player_report.json` | Show raw data backing the report |

**Key Metrics to Highlight:**
- `visibility_pct`: 100.0%
- `trusted_pct`: 100.0%
- `speed_outlier_count`: 1
- `demo_suitable`: true

---

## 2. Backup Demo (Secondary Case: `backup_134049`)

**Use only if main demo fails or as a quick secondary example.**

| # | Asset Type | File Path |
|---|------------|-----------|
| 1 | Overlay Video | `sample_outputs/backup_134049/target_overlay_sampled.mp4` |
| 2 | Player Crop | `sample_outputs/backup_134049/player_centered_sampled.mp4` |
| 3 | Candidate Sheet | `sample_outputs/backup_134049/candidate_selection_sheet.jpg` |
| 4 | Contact Sheet | `sample_outputs/backup_134049/target_tracking_contact_sheet.jpg` |
| 5 | Markdown Report | `sample_outputs/backup_134049/rknp_single_player_report.md` |
| 6 | JSON Metrics | `sample_outputs/backup_134049/rknp_single_player_report.json` |

---

## 3. Failure Case (LK Tracker Evidence)

**Use to demonstrate scientific honesty and failure taxonomy.**

| # | Asset Type | File Path | Purpose |
|---|------------|-----------|---------|
| 1 | Overlay Video | `sample_outputs/lk_failure_case/lk_yellow_frame75_clean/lk_target_overlay.mp4` | Show tracker drift/loss |
| 2 | Player Crop | `sample_outputs/lk_failure_case/lk_yellow_frame75_clean/lk_player_centered.mp4` | Show unstable crop |
| 3 | Contact Sheet | `sample_outputs/lk_failure_case/lk_yellow_frame75_clean/lk_crop_sheet.jpg` | Visual proof of failure |
| 4 | JSON Report | `sample_outputs/lk_failure_case/lk_yellow_frame75_clean/lk_tracking_report.json` | Show `failure_taxonomy` flags |

**Talking Point:** "This is why we need a quality gate. We do not hide failures; we label them."

---

## 4. Research Case (Yellow vs Blue)

**Use only if asked about multi-player potential or color guards.**

| # | Asset Type | File Path | Purpose |
|---|------------|-----------|---------|
| 1 | Two Players | `sample_outputs/screenshot_yellow_vs_blue/two_players.png` | Show initial state |
| 2 | Cluster Frame | `sample_outputs/screenshot_yellow_vs_blue/raw_cluster_frame51.jpg` | Show color separation attempt |
| 3 | Summary | `sample_outputs/screenshot_yellow_vs_blue/TWO_PLAYER_TRACKING_SUMMARY.md` | Explain limitations of same-team confusion |

---

## Recommended Demo Order (3-Minute Flow)

1.  **Problem Statement** (No files): "Coaches need objective data, but pro tools are too expensive."
2.  **Candidate Sheet** (`candidate_selection_sheet.jpg"): "Coach manually confirms target (green box)."
3.  **Main Overlay Video** (`target_overlay_sampled.mp4`): "System tracks confirmed target."
4.  **Main Player Crop** (`player_centered_sampled.mp4`): "Stabilized view for detailed review."
5.  **Contact Sheet** (`target_tracking_contact_sheet.jpg`): "Visual proof of consistency across frames."
6.  **Report** (`rknp_single_player_report.md`): "Honest metrics + LLM explanation (no hallucinations)."
7.  **Backup Demo** (Optional): Only if technical issues arise with primary.
8.  **Failure Case** (`lk_failure_case/...`): "Here is what happens when tracking breaks. Quality gate catches it."
9.  **Limitations & Future** (No files): "No km/h, no xG, short clips only. Next: better re-ID."

**Critical Rule:** If asked for speed in km/h or distance in meters, point to the **Limitation Notice** in the Markdown report and explain "image-space only."
