# RKNP Demo Selector Summary

This file ranks existing `rknp_single_player_report.json` runs for a contest demo.
Use top suitable runs as main demo clips and use risky runs as failure-case evidence.

## Top Demo Candidates

| rank | run | suitable | reliability | confidence | visibility | trusted | outliers | score |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 1 | `primary_134136` | True | high | 88.2 | 100.0 | 100.0 | 1 | 94.4 |
| 2 | `backup_134049` | True | high | 83.39 | 100.0 | 96.55 | 3 | 85.783 |
| 3 | `track_blue_candidate08_t17` | True | medium | 77.4 | 100.0 | 100.0 | 7 | 72.8 |
| 4 | `track_yellow_candidate03_t17` | True | medium | 75.6 | 100.0 | 100.0 | 8 | 69.2 |

## Failure / Caution Cases

| run | suitable | reliability | reasons |
|---|---:|---|---|
| `backup_134049` | True | high | close_players_or_occlusion_risk |
| `track_blue_candidate08_t17` | True | medium | bbox_drift_or_motion_jump, close_players_or_occlusion_risk |
| `track_yellow_candidate03_t17` | True | medium | bbox_drift_or_motion_jump, close_players_or_occlusion_risk |
