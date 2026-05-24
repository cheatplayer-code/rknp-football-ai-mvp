# RKNP Code Audit And 1-Day Contest Plan

## Executive Summary

The project is not ready to be presented as a full football-intelligence platform. It is ready to be presented as an honest short-clip selected-player MVP:

Coach selects one player, the system tracks that player in a short clip, exports visual evidence, calculates basic image-space metrics, and produces an explainable report.

The strongest scientific angle is:

Ordinary video can support low-cost, evidence-based individual player review, but tracking reliability depends on video quality, target selection, occlusion, and jersey similarity.

## Files That Matter

- `rknp_single_player_demo.py`: main MVP pipeline.
- `rknp_lk_target_tracker.py`: alternative short-span optical-flow tracker.
- `rknp_openai_player_analysis.py`: text/report layer over JSON metrics.
- `rknp_demo_selector.py`: ranks demo/failure runs.
- `research_docs/RKNP_RESEARCH_SUMMARY.md`: experiment summary.
- `research_docs/RKNP_RESEARCH_BACKLOG_AND_REPORTS.md`: research backlog and defense framing.

## What Was Improved In v2

- Added stricter `demo_suitable` logic.
- Runs with high speed outliers or motion-jump risks are no longer treated as main demo candidates.
- OpenAI prompt was rewritten with normal Russian UTF-8 text.
- OpenAI payload now includes `quality_gate`.
- Failure/caution cases are preserved for the scientific defense.

## Main Risks

1. Existing reports can show high trusted tracking even when visual output is unstable.
2. Ball detection is weak on distant or compressed footage.
3. Auto target selection is useful for smoke tests, but the product story should be coach-click/manual seed.
4. FIFA-style card is motivational and episode-relative, not an absolute talent rating.

## 1-Day Plan

1. Show main demo: `sample_outputs/primary_134136`.
2. Keep backup demo: `sample_outputs/backup_134049`.
3. Show limitation demo: `sample_outputs/screenshot_yellow_vs_blue` and `sample_outputs/lk_failure_case`.
4. Run `rknp_demo_selector.py` and show its ranking table.
5. Show JSON/Markdown report.
6. Explain that OpenAI is only a text layer over measured metrics.

## Do Not Claim

- full-match tracking;
- xG;
- pass accuracy;
- exact distance in meters;
- speed in km/h;
- calibrated heatmaps;
- tactical passing networks;
- automatic analysis of all players;
- OpenAI doing computer vision.

## Correct Defense Sentence

MVP анализирует короткий видеофрагмент выбранного игрока, извлекает простые визуальные метрики и формирует объяснимый отчет. Система показывает перспективность подхода, но требует дальнейшего улучшения tracking/re-identification для сложных матчевых условий.
