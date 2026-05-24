# RKNP Single Player Demo Report

- input_video: `C:\Users\erbos\Videos\2026-05-24 13-40-49.mkv`
- status: `complete`
- selected_player_mode: `auto_lower_center`
- analyzed_duration_sec: `11.4`
- visibility_pct: `100.0`
- AI Player Rating: `8.22`

## FIFA-Style Card

- OVR: `82`
- PAC: `76`
- ACT: `80`
- INV: `59`
- REL: `95`
- DEV: `78`

## Краткий анализ игрока

В коротком эпизоде система удержала выбранного игрока на 100.0% sampled-кадров. По движению игрок активно перемещался и поддерживал эпизод. Близость мяча к игроку зафиксирована на 8.6% видимых кадров, контекст давления рядом с другими игроками — на 86.2%.

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

- `00:11.7` `run_into_space` / `neutral` / `medium`: Peak movement speed: 2.21 body-heights/sec.
- `00:03.5` `carrying_ball` / `neutral` / `low`: YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed.
- `00:02.7` `pressing` / `neutral` / `low`: Several nearby players were detected around the target; this may indicate pressure/duel context.

## Honest Limitations

- Demo analyzes one short episode, not a full match.
- Exact passes, xG, heatmaps and tactical network maps are not claimed.
- Ball detection is unreliable on broadcast/screen-recorded footage, so ball-related events use low confidence unless evidence is strong.
- Rating is an explainable MVP score for motivation and coaching support, not an official player level.
