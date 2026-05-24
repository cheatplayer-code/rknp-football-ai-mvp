# Two Player Tracking Summary

Source screenshot:

```text
C:\Users\erbos\OneDrive\Изображения\Снимки экрана\Снимок экрана 2026-05-24 143351.png
```

Matched working clip:

```text
C:\Users\erbos\Videos\2026-05-24 13-41-36.mkv
```

Approximate analyzed window:

```text
1.7s -> 18.5s
```

## Targets

Yellow player:

```text
seed_time_sec = 1.7
seed_bbox_xyxy = 738,231,769,285
output = C:\Users\erbos\Downloads\zhanto_project\debug\target_from_screenshot\track_yellow_candidate03_t17
```

Blue player:

```text
seed_time_sec = 1.7
seed_bbox_xyxy = 815,225,846,281
output = C:\Users\erbos\Downloads\zhanto_project\debug\target_from_screenshot\track_blue_candidate08_t17
```

## Metrics

| player | visibility % | trusted % | ball-near % | pressure % | avg speed | p90 speed | outliers | rating | OVR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| yellow | 100.00 | 100.00 | 3.53 | 78.82 | 1.653 | 3.161 | 8 | 8.51 | 85 |
| blue | 100.00 | 100.00 | 5.88 | 84.71 | 1.332 | 2.634 | 7 | 8.53 | 85 |

## OpenAI Analysis

```text
C:\Users\erbos\Downloads\zhanto_project\debug\target_from_screenshot\openai_yellow_vs_blue\openai_player_analysis.md
```

OpenAI was used only after local JSON metrics were generated. It did not perform tracking or detection.

## Honest Interpretation

- Both selected players were visible and trackable in the short episode.
- Blue had slightly higher ball-near and pressure-context values.
- Yellow had higher average and p90 movement intensity.
- Both tracks have speed outliers, so speed must be described as image-space movement, not real-world meters per second.

