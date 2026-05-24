# RKNP Single Player Demo Report

- input_video: `C:\Users\erbos\Videos\2026-05-24 13-41-36.mkv`
- status: `complete`
- selected_player_mode: `seed_bbox`
- analyzed_duration_sec: `16.8`
- visibility_pct: `100.0`
- AI Player Rating: `8.53`

## FIFA-Style Card

- OVR: `85`
- PAC: `87`
- ACT: `92`
- INV: `60`
- REL: `95`
- DEV: `84`

## Краткий анализ игрока

В коротком эпизоде система удержала выбранного игрока на 100.0% sampled-кадров. По движению игрок показал высокоинтенсивное ускорение и активно менял позицию. Близость мяча к игроку зафиксирована на 5.9% видимых кадров, контекст давления рядом с другими игроками — на 84.7%.

## Сильные стороны

- Игрок достаточно стабильно виден в кадре, поэтому его действия можно использовать как evidence для тренера.
- Есть заметные ускорения: это полезно для оценки рывков, открываний и реакции на эпизод.
- В эпизоде есть признаки вовлечения рядом с мячом, но точный исход действия требует ручной проверки.

## Зоны развития

- Главное ограничение — короткая длительность эпизода; для устойчивой оценки нужны несколько клипов из матча.

## Персональные упражнения

- 3x6 ускорений 10-15 м с изменением направления после визуального сигнала тренера.
- Упражнение 4v2/5v3 на открывание под передачу и быстрое решение после приема.
- Видео-разбор 2-3 эпизодов: где игрок открылся вовремя, где мог дать лучший угол поддержки.
- Прессинг-триггеры: старт давления после плохого приема соперника или передачи назад.

## Action Evidence

- `00:09.3` `run_into_space` / `neutral` / `medium`: Peak movement speed: 3.49 body-heights/sec.
- `00:03.9` `carrying_ball` / `neutral` / `low`: YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed.
- `00:01.9` `pressing` / `neutral` / `low`: Several nearby players were detected around the target; this may indicate pressure/duel context.

## Honest Limitations

- Demo analyzes one short episode, not a full match.
- Exact passes, xG, heatmaps and tactical network maps are not claimed.
- Ball detection is unreliable on broadcast/screen-recorded footage, so ball-related events use low confidence unless evidence is strong.
- Rating is an explainable MVP score for motivation and coaching support, not an official player level.
