# RKNP Football AI - Clean Contest Package v3

This package is the contest-facing version of the short-clip single-player football analytics MVP.

## Honest Scope

The MVP analyzes one selected player in a short 15-20 second clip. It creates visual evidence, simple image-space metrics, a motivational FIFA-style card, and a coach-readable report.

It does not claim:

- xG;
- exact passes;
- full-match tracking;
- real-world speed in km/h;
- distance in meters;
- tactical team networks;
- calibrated field heatmaps;
- automatic analysis of every player.

## Main Files

- `rknp_single_player_demo.py` - YOLO/OpenCV single-player pipeline with stricter quality gate.
- `rknp_lk_target_tracker.py` - Lucas-Kanade short-span fallback and failure-case tracker.
- `rknp_openai_player_analysis.py` - optional OpenAI report layer over JSON metrics only.
- `rknp_demo_selector.py` - ranks report JSON files by demo suitability and failure/caution reasons.

## Existing Outputs To Show

- `sample_outputs/primary_134136` - primary clean demo.
- `sample_outputs/backup_134049` - backup demo, but mention close-player risk.
- `sample_outputs/screenshot_yellow_vs_blue` - caution/failure study with close players.
- `sample_outputs/lk_failure_case` - optical-flow short-span evidence and loss behavior.

## Recommended Commands

```powershell
python .\rknp_demo_selector.py --reports .\sample_outputs --output_dir .\sample_outputs\demo_selector
```

```powershell
python .\rknp_openai_player_analysis.py `
  --reports `
  .\sample_outputs\primary_134136\rknp_single_player_report.json `
  .\sample_outputs\backup_134049\rknp_single_player_report.json `
  --output_dir .\debug\openai_analysis
```

## Quality Gate

New runs from `rknp_single_player_demo.py` include:

- `quality_gate.tracking_confidence`;
- `quality_gate.visual_reliability_label`;
- `quality_gate.demo_suitable`;
- `quality_gate.failure_taxonomy`;
- `quality_gate.hard_demo_blockers`;
- `status_summary.json`.

If `demo_suitable=false`, use that run as a caution/failure case, not as the main demo.


## v3 notes

- Existing sample reports now include post-hoc `quality_gate` fields for presentation and OpenAI grounding.
- Runtime requirements were reduced to the actual MVP dependencies.
- The zip is repacked with normal forward-slash paths for cross-platform extraction.
