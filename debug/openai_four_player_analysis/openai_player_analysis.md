# OpenAI Coach Analysis

- created_at_utc: `2026-05-24T11:07:00.474323Z`
- provider_status: `openai_sdk_missing`
- model: `gpt-4.1-mini`

## Coach Summary

OpenAI API недоступен, поэтому создан локальный fallback-отчет по JSON-метрикам. Главный демонстрационный запуск следует выбирать по visual evidence и quality_gate, а не только по рейтингу.

## Player Comparison

### Игрок 1

Видимость 100.0%, trusted tracking 100.0%, ball-near 7.4%, pressure 55.6%, quality=high, demo_suitable=True.

Strengths:
- Трек игрока достаточно стабилен для короткого демонстрационного эпизода.

Development zones:
- По этому клипу недостаточно данных для вывода о владении мячом, передачах или дриблинге.

Training recommendations:
- Можно использовать клип для базовой оценки движения без завышенных выводов о технике.
- Следующий шаг — сравнить этот эпизод с 2-3 другими клипами того же игрока.

Rating interpretation: Рейтинг 8.38 — относительная мотивационная оценка внутри короткого клипа, а не показатель профессионального уровня игрока.

### Игрок 2

Видимость 100.0%, trusted tracking 96.5%, ball-near 8.6%, pressure 86.2%, quality=high, demo_suitable=True.

Strengths:
- Трек игрока достаточно стабилен для короткого демонстрационного эпизода.
- Игрок часто находился рядом с другими игроками, поэтому эпизод полезен для анализа игры под давлением.

Development zones:
- По этому клипу недостаточно данных для вывода о владении мячом, передачах или дриблинге.
- Ограничения запуска: close_players_or_occlusion_risk.

Training recommendations:
- Можно проверить упражнения на открывание под давлением и принятие решений в плотных эпизодах.
- Следующий шаг — сравнить этот эпизод с 2-3 другими клипами того же игрока.

Rating interpretation: Рейтинг 8.22 — относительная мотивационная оценка внутри короткого клипа, а не показатель профессионального уровня игрока.

### Игрок 3

Видимость 100.0%, trusted tracking 100.0%, ball-near 3.5%, pressure 78.8%, quality=medium, demo_suitable=False.

Strengths:
- Игрок часто находился рядом с другими игроками, поэтому эпизод полезен для анализа игры под давлением.

Development zones:
- По этому клипу недостаточно данных для вывода о владении мячом, передачах или дриблинге.
- Нужно визуально проверить contact sheet: возможны скачки bbox, occlusion или нестабильность tracking.
- Ограничения запуска: bbox_drift_or_motion_jump, close_players_or_occlusion_risk.

Training recommendations:
- Можно проверить упражнения на открывание под давлением и принятие решений в плотных эпизодах.
- Следующий шаг — сравнить этот эпизод с 2-3 другими клипами того же игрока.

Rating interpretation: Рейтинг 8.51 — относительная мотивационная оценка внутри короткого клипа, а не показатель профессионального уровня игрока.

### Игрок 4

Видимость 100.0%, trusted tracking 100.0%, ball-near 5.9%, pressure 84.7%, quality=medium, demo_suitable=False.

Strengths:
- Игрок часто находился рядом с другими игроками, поэтому эпизод полезен для анализа игры под давлением.

Development zones:
- По этому клипу недостаточно данных для вывода о владении мячом, передачах или дриблинге.
- Нужно визуально проверить contact sheet: возможны скачки bbox, occlusion или нестабильность tracking.
- Ограничения запуска: bbox_drift_or_motion_jump, close_players_or_occlusion_risk.

Training recommendations:
- Можно проверить упражнения на открывание под давлением и принятие решений в плотных эпизодах.
- Следующий шаг — сравнить этот эпизод с 2-3 другими клипами того же игрока.

Rating interpretation: Рейтинг 8.53 — относительная мотивационная оценка внутри короткого клипа, а не показатель профессионального уровня игрока.

## Best Demo Player

- run: `primary_134136`
- reason: Лучший по demo_suitable=True и tracking_confidence=88.2.

## Research Interpretation

- Короткий выбранный эпизод позволяет получить базовые image-space метрики и evidence-видео.
- Плотные эпизоды, близкие игроки и скачки bbox должны рассматриваться как ограничения tracking, а не скрываться.

## Limitations

- Без калибровки поля нельзя честно заявлять скорость в км/ч или дистанцию в метрах.
- Без надежной детекции мяча нельзя заявлять точные передачи, владение или xG.
- OpenAI/LLM является только текстовым слоем поверх рассчитанных метрик.

## Source Reports

- `primary_134136` rating=`8.38` visibility=`100.0` trusted=`100.0` ball_near=`7.41` pressure=`55.56` quality=`high` suitable=`True`
- `backup_134049` rating=`8.22` visibility=`100.0` trusted=`96.55` ball_near=`8.62` pressure=`86.21` quality=`high` suitable=`True`
- `track_yellow_candidate03_t17` rating=`8.51` visibility=`100.0` trusted=`100.0` ball_near=`3.53` pressure=`78.82` quality=`medium` suitable=`False`
- `track_blue_candidate08_t17` rating=`8.53` visibility=`100.0` trusted=`100.0` ball_near=`5.88` pressure=`84.71` quality=`medium` suitable=`False`
