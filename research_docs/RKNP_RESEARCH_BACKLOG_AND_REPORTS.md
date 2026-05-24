# RKNP Research Backlog And Reports

## Главная идея исследований

Для защиты важно показывать не только приложение, а инженерное исследование:

```text
какие факторы влияют на качество анализа игрока
-> как мы это измерили
-> какие ограничения нашли
-> какие решения приняли для MVP
```

Ниже список исследований, которые реально связаны с работой модели.

## 1. Исследование качества входного видео

**Вопрос:** как качество записи влияет на detection/tracking?

Что сравнить:

- чистая трансляция vs запись экрана с YouTube/OBS;
- наличие UI-элементов, паузы, кнопок, черных областей;
- дальняя камера vs ближняя камера;
- открытая игра vs штрафная/стандарт.

Метрики:

- количество обнаруженных игроков на кадр;
- `visibility_pct`;
- `trusted_pct`;
- `speed_outlier_count`;
- количество кадров, где мяч найден рядом с игроком.

Вывод для защиты:

> Качество входного видео напрямую влияет на стабильность трекинга. Поэтому в продукте нужен документ-инструкция для тренера: как правильно снимать матч, где стоять, как не закрывать поле, как избегать интерфейсных наложений.

## 2. Исследование выбора target-игрока

**Вопрос:** что лучше: автоматический выбор игрока или ручной tap тренера?

Что сравнить:

- `target_strategy center`;
- `target_strategy lower_center`;
- ручной seed bbox из `candidate_selection.json`;
- два игрока рядом в одном эпизоде.

Метрики:

- `visibility_pct`;
- `trusted_pct`;
- визуальный contact sheet;
- число identity jumps вручную по storyboard.

Вывод:

> Для MVP выбран ручной выбор игрока тренером, потому что это уменьшает риск анализа не того футболиста. Автоматический выбор можно оставить только как helper.

## 3. Исследование detector threshold / model size

**Вопрос:** как `conf`, `imgsz` и YOLO-модель влияют на результат?

Что сравнить:

- `yolov8n.pt` vs `yolov8m.pt`;
- `conf=0.15`, `0.20`, `0.30`;
- `imgsz=640`, `960`, `1280`.

Метрики:

- runtime;
- person detections per sampled frame;
- false positives;
- lost frames;
- `trusted_pct`.

Вывод:

> Для конкурса используем `yolov8n.pt`, потому что он быстрее и достаточно стабилен на коротких клипах. Для production можно тестировать более крупную модель, но она увеличит стоимость.

## 4. Исследование FPS sampling

**Вопрос:** сколько FPS нужно анализировать?

Что сравнить:

- 3 FPS;
- 5 FPS;
- 8 FPS;
- 10 FPS.

Метрики:

- runtime;
- стабильность bbox;
- `speed_outlier_count`;
- потеря коротких действий.

Вывод:

> 5 FPS является разумным MVP-компромиссом: меньше вычислений, но сохраняются основные рывки и перемещения игрока.

## 5. Исследование tracking stability

**Вопрос:** когда трекер теряет игрока или может перепрыгнуть?

Сцены:

- два игрока рядом;
- одинаковая форма;
- overlap/duel;
- игрок выходит из кадра;
- камера резко двигается.

Метрики:

- `trusted_pct`;
- `speed_outlier_count`;
- `nearby_player_count`;
- manual visual QA по `target_tracking_contact_sheet.jpg`.

Вывод:

> В MVP трекер работает как evidence tool, но не как финальный судья. При высоком `speed_outlier_count` отчет должен показывать ограничение качества.

## 6. Исследование ball detection limitation

**Вопрос:** можно ли честно заявлять передачи/удары/дриблинг?

Что проверить:

- обнаруживается ли мяч на дальних кадрах;
- как часто ball-near совпадает с реальным владением;
- исчезает ли мяч из-за компрессии/размытия.

Метрики:

- `ball_near_pct`;
- визуальная проверка кадров с мячом;
- false ball detections.

Вывод:

> На обычной трансляции мяч слишком маленький, поэтому MVP не заявляет точные передачи, удары, xG и владение. Это честное ограничение проекта.

## 7. Исследование rating/card formula

**Вопрос:** как объяснить FIFA-style карточку, чтобы она не выглядела как абсолютный уровень игрока?

Что описать:

- `OVR` не является официальной оценкой;
- `PAC` основан на image-space movement;
- `REL` основан на видимости и доверии к треку;
- `INV` основан на pressure/ball-near context;
- карточка нужна для мотивации игрока.

Вывод:

> Карточка показывает прогресс внутри приложения, а не профессиональный скаутский рейтинг.

## 8. Исследование OpenAI layer

**Вопрос:** где используется OpenAI API?

Архитектура:

```text
OpenCV + YOLO -> JSON metrics -> OpenAI -> coach-friendly explanation
```

Что проверить:

- OpenAI не должен делать CV вместо модели;
- OpenAI не должен выдумывать xG, пасы, удары;
- prompt должен запрещать неподтвержденные выводы;
- результат должен ссылаться только на JSON-метрики.

Вывод:

> OpenAI используется как language layer для объяснения метрик тренеру и игроку, а не как источник компьютерного зрения.

## 9. Исследование двух близких игроков

Текущий пример:

```text
C:\Users\erbos\Downloads\zhanto_project\debug\target_from_screenshot
```

Два target-а:

- `track_yellow_candidate03_t17`
- `track_blue_candidate08_t17`

Результат:

| player | visibility % | trusted % | ball-near % | pressure % | avg speed | p90 speed | outliers | rating |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| yellow | 100.00 | 100.00 | 3.53 | 78.82 | 1.653 | 3.161 | 8 | 8.51 |
| blue | 100.00 | 100.00 | 5.88 | 84.71 | 1.332 | 2.634 | 7 | 8.53 |

Вывод:

> Даже когда два игрока находятся рядом, система может отдельно построить evidence-report для каждого выбранного игрока. Но высокий `speed_outlier_count` показывает, что в плотных сценах нужен осторожный вывод и визуальная проверка.

## Что сделать в первую очередь для РКНП

Минимальный набор исследований на защиту:

1. **6 clips benchmark**: показать таблицу из `RKNP_RESEARCH_SUMMARY.md`.
2. **two-player close scene**: показать yellow vs blue из скриншота.
3. **manual target selection**: объяснить, почему тренер кликает игрока.
4. **limitation study**: почему нет xG/pass/heatmap.
5. **OpenAI grounding**: показать, что OpenAI пишет текст только по JSON-метрикам.

## Какие файлы показывать судьям

Основные:

- `rknp_single_player_demo.py`
- `rknp_openai_player_analysis.py`
- `RKNP_RESEARCH_SUMMARY.md`
- `RKNP_RESEARCH_BACKLOG_AND_REPORTS.md`
- `debug\target_from_screenshot\openai_yellow_vs_blue\openai_player_analysis.md`

Лучшие видео-evidence:

- `debug\target_from_screenshot\track_yellow_candidate03_t17\target_overlay_sampled.mp4`
- `debug\target_from_screenshot\track_blue_candidate08_t17\target_overlay_sampled.mp4`
- `debug\target_from_screenshot\track_yellow_candidate03_t17\player_centered_sampled.mp4`
- `debug\target_from_screenshot\track_blue_candidate08_t17\player_centered_sampled.mp4`

