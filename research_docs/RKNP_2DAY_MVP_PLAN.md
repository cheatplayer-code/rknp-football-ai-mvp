# RKNP 2-Day MVP Plan

## Situation

- Low-quality real-match footage is the real domain.
- The current `300` player samples were collected from cleaner, more professional broadcasts.
- That dataset is not enough to justify a new low-quality detector in the remaining time.
- We have about `2` days left.

## Decision

Do **not** spend the final 2 days on:

- collecting a new low-quality detector dataset,
- retraining a football-specific detector,
- full-match end-to-end auto tracking,
- automatic all-player analytics,
- ball tracking or tactical-map claims.

Return to the smallest honest MVP.

## Chosen MVP

### Core promise

Given a short low-quality football clip, the system can:

1. isolate gameplay or a short playable segment,
2. let the operator choose the target player manually,
3. track that chosen player only inside a short usable segment,
4. export:
   - target overlay video,
   - player-centered crop video,
   - simple coverage / visibility metrics,
   - optional short narrative summary.

### What this MVP does **not** promise

- not full-match tracking across all camera cuts,
- not automatic identity persistence through every occlusion,
- not guaranteed target discovery without manual selection,
- not team-wide stats,
- not xG / pass maps / heatmaps / possession,
- not football-role classification reliability on low-quality footage.

## Best Existing Building Blocks

### 1. Segment + manual target selection

- `C:\Users\erbos\Downloads\zhanto_project\stage5_segmented_runtime_runner.py`
- `C:\Users\erbos\Downloads\zhanto_project\kaggle_filtered_segment_mot_runner.py`

Use these to:

- cut video into playable segments,
- generate candidate sheets,
- choose `segment_id` + `target_track_id` or `frame+bbox`,
- export `target_overlay.mp4`,
- export `player_centered.mp4`,
- compute honest visibility metrics.

### 2. Selected-player backend slice

- `C:\Users\erbos\Downloads\zhanto_project\football_player_mvp_pipeline.py`
- `C:\Users\erbos\Downloads\zhanto_project\stage6_player_centered_crop.py`
- `C:\Users\erbos\Downloads\zhanto_project\stage7_player_clip_report.py`

Use these only if time remains and the Stage 5 timeline is already stable enough.

### 3. Judge-friendly short-clip narrative

- `C:\Users\erbos\Downloads\zhanto_project\short_clip_intelligence_mvp.py`

This is presentation-friendly, but optional.
It should not block the core tracking MVP.

## Recommended Detector Policy For The Final 2 Days

For the MVP, favor the detector that gives the most stable **person proposals** on low-quality clips.

That means:

- use a generic person-capable model if it behaves better,
- do not insist on perfect `player / goalkeeper / referee` separation,
- manual target selection is acceptable,
- the output is about one chosen player, not about labeling every actor correctly.

## Deliverables For RKNP

Minimum demo pack:

1. input short video clip,
2. candidate sheet showing target selection,
3. all-tracks overlay,
4. target-only overlay,
5. player-centered clip,
6. JSON metrics:
   - visible frame count,
   - visible coverage percent,
   - active span duration,
7. short README/summary describing scope and limitations.

Optional if stable:

8. simple player clip report,
9. short judge-facing markdown summary.

## 2-Day Execution Plan

### Day 1

Freeze scope and get one clean end-to-end demo working:

1. pick `1-2` short real low-quality clips,
2. run segmented runtime,
3. manually choose target player,
4. export `player_centered.mp4` and `target_overlay.mp4`,
5. verify that the chosen player stays acceptable in the exported usable span,
6. save all artifacts in one demo folder.

Success criterion for Day 1:

- one real low-quality clip works end-to-end.

### Day 2

Polish and package only:

1. run the same flow on one backup clip,
2. produce a small README with limitations,
3. optionally add clip-report or VLM summary if it works without destabilizing the pipeline,
4. prepare the final demo story:
   - choose player,
   - show tracking,
   - show player-centered clip,
   - show metrics.

Success criterion for Day 2:

- reproducible demo on `2` clips,
- no new research branch,
- no new detector-training dependency.

## Hard No List

If a task threatens the deadline, cut it immediately:

- low-quality dataset collection,
- retraining experiments,
- re-identification upgrades,
- new model benchmarking suites,
- automatic all-player dataset generation,
- long-match automation,
- ball-aware analytics.

## Final Product Story

The MVP story is:

"From a low-quality football video, we can manually select one target player, isolate the playable segment, track that player through the usable window, and generate a centered evidence clip plus simple explainable metrics."

That is small, honest, and achievable in 2 days.
