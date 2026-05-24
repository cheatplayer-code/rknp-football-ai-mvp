# RKNP MVP Research Summary

## Project Scope

This project is a contest MVP for youth football academies. The current demo does not try to solve full professional match analytics. It solves one narrow and honest task:

```text
short football clip
-> select one target player
-> track this player in sampled frames
-> export evidence video/crops
-> calculate simple explainable metrics
-> generate a coach/player report
```

The demo is designed for 15-20 second clips. It is a proof of concept for the future mobile app flow where a coach uploads a match clip, chooses a player, and receives an evidence-based player report.

## Current Demo Pipeline

File:

```text
C:\Users\erbos\Downloads\zhanto_project\rknp_single_player_demo.py
```

Pipeline:

```text
input MKV/MP4
-> OpenCV frame sampling at 5 FPS
-> YOLOv8 person/ball detection
-> target player initialization
   - auto strategy: center / lower_center / largest
   - optional manual seed bbox
-> simple target tracking
   - bbox position continuity
   - HSV color histogram similarity
   - size consistency
-> exported target overlay video
-> exported player-centered crop video
-> metrics + FIFA-style motivational card
-> Russian markdown report
```

## What The MVP Measures

- `visibility_pct`: how often the selected player was visible in sampled frames.
- `trusted_pct`: how often the tracker was confident.
- `ball_near_pct`: how often YOLO detected the ball near the selected player.
- `pressure_pct`: how often multiple players were near the selected player.
- `avg_speed_body_heights_per_sec`: approximate image-space movement normalized by player bbox height.
- `p90_speed_body_heights_per_sec`: robust movement intensity, less sensitive to outliers than max speed.
- `speed_outlier_count`: camera motion or tracking-jump warnings.
- `AI Player Rating`: internal explainable MVP rating, not an official player level.
- `FIFA-style card`: motivational visualization of the episode, not an absolute scouting grade.

## What The MVP Does Not Claim

- No xG.
- No exact pass count.
- No heatmaps.
- No full tactical network.
- No exact distance in meters.
- No full-match identity persistence.
- No automatic analysis of all players.

These are intentionally excluded because the input is normal broadcast/screen-recorded video without sensors or calibrated cameras.

## Experiment Setup

Six short football screen-recording clips were tested on May 24, 2026. All runs used the same model and the same script:

```text
YOLO model: yolov8n.pt
sampling: 5 FPS
tracking: bbox + color histogram + size consistency
```

## Results

| run | duration sec | visibility % | trusted % | ball near % | pressure % | avg speed | p90 speed | speed outliers | rating |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `rknp_single_player_133416_auto` | 8.0 | 100.00 | 95.12 | 0.00 | 87.80 | 0.112 | 0.070 | 2 | 7.38 |
| `rknp_single_player_133446_auto` | 13.0 | 100.00 | 96.97 | 9.09 | 33.33 | 1.266 | 2.217 | 11 | 8.40 |
| `rknp_single_player_133535_auto` | 13.0 | 100.00 | 96.97 | 4.55 | 33.33 | 1.338 | 2.341 | 11 | 8.38 |
| `rknp_single_player_134011_auto` | 9.0 | 100.00 | 100.00 | 4.35 | 97.83 | 0.442 | 0.938 | 1 | 7.83 |
| `rknp_single_player_134049_auto` | 11.4 | 100.00 | 96.55 | 8.62 | 86.21 | 0.868 | 1.683 | 3 | 8.22 |
| `rknp_single_player_134136_auto` | 16.0 | 100.00 | 100.00 | 7.41 | 55.56 | 1.071 | 2.158 | 1 | 8.38 |

## Best Demo Runs

Primary demo:

```text
C:\Users\erbos\Downloads\zhanto_project\debug\rknp_single_player_134136_auto
```

Backup demo:

```text
C:\Users\erbos\Downloads\zhanto_project\debug\rknp_single_player_134049_auto
```

These clips show active open-play movement and produce clean evidence artifacts.

## Example Command

```powershell
python C:\Users\erbos\Downloads\zhanto_project\rknp_single_player_demo.py `
  --input_video "C:\Users\erbos\Videos\2026-05-24 13-41-36.mkv" `
  --output_dir "C:\Users\erbos\Downloads\zhanto_project\debug\rknp_single_player_134136_auto" `
  --clip_start_sec 2.5 `
  --clip_end_sec 18.5 `
  --analysis_fps 5 `
  --target_strategy lower_center `
  --target_player_description "Auto-selected player for RKNP demo; coach can replace with a seed bbox."
```

## Output Artifacts

Each run creates:

- `candidate_selection_sheet.jpg`
- `target_tracking_contact_sheet.jpg`
- `target_overlay_sampled.mp4`
- `player_centered_sampled.mp4`
- `rknp_single_player_report.json`
- `rknp_single_player_report.md`

## Scientific Interpretation

The experiment shows that a low-cost pipeline can produce usable evidence from short youth-football clips without sensors. The strongest result is not exact tactical analytics; it is explainable target-player evidence:

- the coach sees which player was analyzed,
- the system shows video proof,
- every metric has a visible reason,
- uncertain measurements are not hidden.

This supports the project goal: reduce subjective evaluation and make simple player feedback accessible to academies with only video.

## Main Limitations

- Screen recordings include UI overlays, pause icons, browser panels and camera motion.
- YOLO ball detection is weak on small broadcast balls.
- Image-space movement is not real-world speed.
- A manual target click/bbox is still better than fully automatic selection.
- Full-match processing requires segmentation, batching and stronger identity recovery.

## Next Engineering Step

For the actual mobile product, the next important feature is not xG or heatmaps. It is a reliable coach flow:

```text
upload video
-> trim clean gameplay window
-> tap target player
-> run single-player analysis
-> show evidence report
```

