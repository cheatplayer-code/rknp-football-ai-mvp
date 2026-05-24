Ты помогаешь подготовить научный проект для конкурса РКНП.

Контекст проекта:
Мобильное приложение для детских и юношеских футбольных академий: тренер загружает видео, выбирает одного игрока, система возвращает evidence-метрики, краткий анализ, FIFA-style карточку и персональные упражнения. Цель - снизить субъективность и сделать базовую аналитику доступной.

Ниже JSON-метрики нескольких игроков из одного короткого футбольного эпизода.
Это не профессиональная полная аналитика матча. Это MVP:
- один выбранный игрок;
- короткий клип;
- YOLO/OpenCV evidence;
- bbox tracking;
- простые метрики видимости, движения, pressure context и ball-near;
- FIFA-style карточка как мотивационная визуализация.

Запрещено выдумывать:
- xG;
- точные передачи;
- удары;
- heatmap;
- дистанцию в метрах;
- владение мячом;
- полноценную тактическую карту.

Сделай честный тренерский вывод на русском языке.

Верни строго JSON:
{
  "coach_summary": "2-4 предложения",
  "player_comparison": [
    {
      "run_name": "...",
      "short_label": "Игрок A/B/C",
      "episode_profile": "краткий профиль по метрикам",
      "strengths": ["..."],
      "development_zones": ["..."],
      "training_recommendations": ["..."],
      "rating_interpretation": "как читать рейтинг без завышенных обещаний"
    }
  ],
  "best_demo_player": {
    "run_name": "...",
    "reason": "почему этот игрок лучше всего подходит для демонстрации"
  },
  "research_interpretation": [
    "какой научный вывод можно защитить по этим метрикам",
    "какое ограничение надо честно сказать судьям"
  ],
  "limitations": ["..."]
}

JSON-метрики:
[
  {
    "run_name": "rknp_single_player_134136_auto",
    "report_path": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_auto\\rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-41-36.mkv",
    "selected_player": {
      "mode": "auto_lower_center",
      "time_sec": 2.5,
      "bbox_xyxy": {
        "x1": 784,
        "y1": 368,
        "x2": 836,
        "y2": 464
      },
      "description": "Auto-selected player for RKNP demo; coach can replace with a seed bbox."
    },
    "metrics": {
      "sample_count": 81,
      "duration_sec": 16.0,
      "visible_sample_count": 81,
      "trusted_sample_count": 81,
      "visibility_pct": 100.0,
      "trusted_pct": 100.0,
      "ball_near_sample_count": 6,
      "ball_near_pct": 7.41,
      "pressure_sample_count": 45,
      "pressure_pct": 55.56,
      "avg_speed_body_heights_per_sec": 1.071,
      "p90_speed_body_heights_per_sec": 2.158,
      "max_speed_body_heights_per_sec": 3.97,
      "raw_max_speed_body_heights_per_sec": 10.807,
      "speed_outlier_count": 1,
      "high_intensity_sample_count": 20
    },
    "events": [
      {
        "time_sec": 13.3,
        "time_label": "00:13.3",
        "action": "run_into_space",
        "outcome": "neutral",
        "confidence": "medium",
        "evidence": "Peak movement speed: 3.97 body-heights/sec."
      },
      {
        "time_sec": 3.9,
        "time_label": "00:03.9",
        "action": "receiving_ball",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed."
      },
      {
        "time_sec": 2.7,
        "time_label": "00:02.7",
        "action": "pressing",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "Several nearby players were detected around the target; this may indicate pressure/duel context."
      }
    ],
    "rating": {
      "ai_player_rating": 8.38,
      "fifa_style_card": {
        "OVR": 84,
        "PAC": 86,
        "ACT": 87,
        "INV": 55,
        "REL": 95,
        "DEV": 81
      }
    },
    "artifacts": {
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_auto\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_auto\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_auto\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_auto\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  },
  {
    "run_name": "rknp_single_player_134136_candidate02",
    "report_path": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate02\\rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-41-36.mkv",
    "selected_player": {
      "mode": "seed_bbox",
      "time_sec": 2.5,
      "bbox_xyxy": {
        "x1": 675,
        "y1": 230,
        "x2": 704,
        "y2": 283
      },
      "description": "Manual target candidate 02 from candidate_selection.json."
    },
    "metrics": {
      "sample_count": 81,
      "duration_sec": 16.0,
      "visible_sample_count": 81,
      "trusted_sample_count": 81,
      "visibility_pct": 100.0,
      "trusted_pct": 100.0,
      "ball_near_sample_count": 3,
      "ball_near_pct": 3.7,
      "pressure_sample_count": 63,
      "pressure_pct": 77.78,
      "avg_speed_body_heights_per_sec": 1.66,
      "p90_speed_body_heights_per_sec": 3.161,
      "max_speed_body_heights_per_sec": 3.984,
      "raw_max_speed_body_heights_per_sec": 6.296,
      "speed_outlier_count": 8,
      "high_intensity_sample_count": 33
    },
    "events": [
      {
        "time_sec": 3.1,
        "time_label": "00:03.1",
        "action": "run_into_space",
        "outcome": "neutral",
        "confidence": "medium",
        "evidence": "Peak movement speed: 3.98 body-heights/sec."
      },
      {
        "time_sec": 17.7,
        "time_label": "00:17.7",
        "action": "carrying_ball",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed."
      },
      {
        "time_sec": 2.7,
        "time_label": "00:02.7",
        "action": "pressing",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "Several nearby players were detected around the target; this may indicate pressure/duel context."
      }
    ],
    "rating": {
      "ai_player_rating": 8.51,
      "fifa_style_card": {
        "OVR": 85,
        "PAC": 87,
        "ACT": 92,
        "INV": 58,
        "REL": 95,
        "DEV": 83
      }
    },
    "artifacts": {
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate02\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate02\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate02\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate02\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  },
  {
    "run_name": "rknp_single_player_134136_candidate03",
    "report_path": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate03\\rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-41-36.mkv",
    "selected_player": {
      "mode": "seed_bbox",
      "time_sec": 2.5,
      "bbox_xyxy": {
        "x1": 793,
        "y1": 244,
        "x2": 834,
        "y2": 307
      },
      "description": "Manual target candidate 03 from candidate_selection.json."
    },
    "metrics": {
      "sample_count": 81,
      "duration_sec": 16.0,
      "visible_sample_count": 81,
      "trusted_sample_count": 81,
      "visibility_pct": 100.0,
      "trusted_pct": 100.0,
      "ball_near_sample_count": 5,
      "ball_near_pct": 6.17,
      "pressure_sample_count": 68,
      "pressure_pct": 83.95,
      "avg_speed_body_heights_per_sec": 1.335,
      "p90_speed_body_heights_per_sec": 2.634,
      "max_speed_body_heights_per_sec": 3.492,
      "raw_max_speed_body_heights_per_sec": 6.296,
      "speed_outlier_count": 7,
      "high_intensity_sample_count": 25
    },
    "events": [
      {
        "time_sec": 9.3,
        "time_label": "00:09.3",
        "action": "run_into_space",
        "outcome": "neutral",
        "confidence": "medium",
        "evidence": "Peak movement speed: 3.49 body-heights/sec."
      },
      {
        "time_sec": 3.9,
        "time_label": "00:03.9",
        "action": "carrying_ball",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed."
      },
      {
        "time_sec": 2.7,
        "time_label": "00:02.7",
        "action": "pressing",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "Several nearby players were detected around the target; this may indicate pressure/duel context."
      }
    ],
    "rating": {
      "ai_player_rating": 8.53,
      "fifa_style_card": {
        "OVR": 85,
        "PAC": 87,
        "ACT": 92,
        "INV": 60,
        "REL": 95,
        "DEV": 84
      }
    },
    "artifacts": {
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate03\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate03\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate03\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate03\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  },
  {
    "run_name": "rknp_single_player_134136_candidate05",
    "report_path": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate05\\rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-41-36.mkv",
    "selected_player": {
      "mode": "seed_bbox",
      "time_sec": 2.5,
      "bbox_xyxy": {
        "x1": 1188,
        "y1": 341,
        "x2": 1223,
        "y2": 436
      },
      "description": "Manual target candidate 05 from candidate_selection.json."
    },
    "metrics": {
      "sample_count": 81,
      "duration_sec": 16.0,
      "visible_sample_count": 81,
      "trusted_sample_count": 81,
      "visibility_pct": 100.0,
      "trusted_pct": 100.0,
      "ball_near_sample_count": 5,
      "ball_near_pct": 6.17,
      "pressure_sample_count": 55,
      "pressure_pct": 67.9,
      "avg_speed_body_heights_per_sec": 1.016,
      "p90_speed_body_heights_per_sec": 1.921,
      "max_speed_body_heights_per_sec": 3.539,
      "raw_max_speed_body_heights_per_sec": 10.807,
      "speed_outlier_count": 1,
      "high_intensity_sample_count": 14
    },
    "events": [
      {
        "time_sec": 10.1,
        "time_label": "00:10.1",
        "action": "run_into_space",
        "outcome": "neutral",
        "confidence": "medium",
        "evidence": "Peak movement speed: 3.54 body-heights/sec."
      },
      {
        "time_sec": 12.9,
        "time_label": "00:12.9",
        "action": "carrying_ball",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed."
      },
      {
        "time_sec": 2.7,
        "time_label": "00:02.7",
        "action": "pressing",
        "outcome": "neutral",
        "confidence": "low",
        "evidence": "Several nearby players were detected around the target; this may indicate pressure/duel context."
      }
    ],
    "rating": {
      "ai_player_rating": 8.32,
      "fifa_style_card": {
        "OVR": 83,
        "PAC": 81,
        "ACT": 86,
        "INV": 56,
        "REL": 95,
        "DEV": 80
      }
    },
    "artifacts": {
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate05\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate05\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate05\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134136_candidate05\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  }
]