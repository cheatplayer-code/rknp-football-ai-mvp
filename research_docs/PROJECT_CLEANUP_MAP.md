# Project Cleanup Map

This workspace contains many useful prototypes, but they should not all be part of the contest MVP.

Because this folder is not a git repository, nothing was deleted automatically. The safe approach is:

```text
keep the RKNP demo files visible
archive old experiments only after the demo is stable
do not permanently delete research code before making a backup
```

## Keep For RKNP Demo

- `rknp_single_player_demo.py`
- `RKNP_RESEARCH_SUMMARY.md`
- `short_clip_intelligence_mvp.py`
- `SHORT_CLIP_INTELLIGENCE_MVP_README.md`
- `RKNP_2DAY_MVP_PLAN.md`
- `requirements_mvp_runtime.txt`
- `yolov8n.pt`
- `debug\rknp_single_player_*_auto`
- `debug\rknp_video_*_export`

## Optional But Useful Backend Prototypes

These are useful later, but not needed for the one-day contest demo:

- `football_player_mvp_pipeline.py`
- `stage6_player_centered_crop.py`
- `stage7_player_clip_report.py`
- `stage5_segmented_runtime_runner.py`
- `kaggle_filtered_segment_mot_runner.py`

## Archive After Demo

These files/directories are older experiments or heavy bundles. Move them to a `_legacy_archive` folder only after the RKNP demo is working:

- `football_model_single_player_final_integrated_cutie_prtreid.py`
- `football_model_single_player_final_integrated_sam2_prtreid.py`
- `stage5_*.py`
- `STAGE5_*.md`
- `STAGE5_*.json`
- `kaggle_*.py`
- `KAGGLE_*.md`
- `kaggle_training_bundle.zip`
- `segmented_runtime_kaggle_bundle.zip`
- `detector_training`
- `pitch_keypoint_training`
- `kaggle_training_bundle`
- `segmented_runtime_kaggle_bundle`
- `detector_training_pipeline.py`
- `pitch_keypoint_training_pipeline.py`
- `dataset_annotator_web.py`
- `dataset_annotator_web.html`
- `track_dataset_annotator_web.py`
- `track_dataset_annotator_web.html`

## Unrelated To Football MVP

These look unrelated to the football analytics project and should be moved out of the root:

- `evacuation_app.py`
- `evacuation_backend.py`
- `evacuation_web`
- `evacuation_plan.example.json`
- `esp32_evacuation_client_example.ino`
- `mesc-ai-checker-fullstack`

## Recommended Final Contest Folder

Create this structure for the presentation:

```text
rknp_demo_package
  README.md
  rknp_single_player_demo.py
  RKNP_RESEARCH_SUMMARY.md
  sample_outputs
    primary_134136
    backup_134049
```

Do not include giant model experiments in the contest folder. The judge should see a clear MVP, not the whole history of failed prototypes.

