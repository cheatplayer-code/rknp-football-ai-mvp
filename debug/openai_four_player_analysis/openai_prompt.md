Ты помогаешь подготовить научный проект для конкурса РКНП.

Контекст проекта:
Мобильное приложение для детских и юношеских футбольных академий: тренер загружает видео, выбирает одного игрока, система возвращает evidence-метрики, краткий анализ, FIFA-style карточку и осторожные персональные рекомендации. Цель - снизить субъективность и сделать базовую аналитику доступной.

Ниже JSON-метрики нескольких запусков short-clip MVP. Это не профессиональная полная аналитика матча.
Это MVP:
- один выбранный игрок;
- короткий клип;
- YOLO/OpenCV evidence;
- bbox tracking;
- простые метрики видимости, движения, pressure context и ball-near;
- FIFA-style карточка как мотивационная визуализация, а не абсолютная оценка таланта.

Запрещено выдумывать:
- xG;
- точные передачи;
- удары;
- heatmap;
- дистанцию в метрах;
- скорость в км/ч;
- владение мячом;
- полноценную тактическую карту;
- уровень таланта игрока;
- технику, выносливость или качество принятия решений, если это прямо не следует из метрик.

Правила grounding:
- если ball_near_pct ниже 10%, напиши, что по этому клипу недостаточно данных для вывода о владении мячом, передачах, дриблинге или контроле;
- не превращай low ball_near в "слабое владение мячом": это может означать, что мяч не виден или игрок в эпизоде был без мяча;
- если speed_outlier_count высокий или quality_gate.demo_suitable=false, обязательно укажи риск camera motion / bbox jump / tracking instability;
- если quality_gate.visual_reliability_label low/medium, рекомендации должны быть осторожными;
- формулируй рекомендации как "можно проверить/развивать", а не "игрок слаб в...";
- OpenAI не делает computer vision: он только объясняет уже рассчитанные числа.

Сделай честный тренерский вывод на русском языке.

Верни строгий JSON:
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
    "reason": "почему этот запуск лучше всего подходит для демонстрации"
  },
  "research_interpretation": [
    "какой научный вывод можно защищать по этим метрикам",
    "какое ограничение надо честно сказать судьям"
  ],
  "limitations": ["..."]
}

JSON-метрики:
[
  {
    "run_name": "primary_134136",
    "report_path": "/mnt/data/audit_v2_norm/rknp_contest_clean_package_v2/sample_outputs/primary_134136/rknp_single_player_report.json",
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
    "quality_gate": {
      "tracking_confidence": 88.2,
      "visual_reliability_label": "high",
      "demo_suitable": true,
      "lost_pct": 0.0,
      "motion_jump_reject_count": 0,
      "color_mismatch_reject_count": 0,
      "failure_taxonomy": [],
      "hard_demo_blockers": false,
      "legacy_gate": true,
      "quality_gate_source": "posthoc_legacy_metrics_v3"
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
    "run_name": "backup_134049",
    "report_path": "/mnt/data/audit_v2_norm/rknp_contest_clean_package_v2/sample_outputs/backup_134049/rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-40-49.mkv",
    "selected_player": {
      "mode": "auto_lower_center",
      "time_sec": 2.5,
      "bbox_xyxy": {
        "x1": 494,
        "y1": 389,
        "x2": 548,
        "y2": 479
      },
      "description": "Auto-selected player for RKNP demo."
    },
    "metrics": {
      "sample_count": 58,
      "duration_sec": 11.4,
      "visible_sample_count": 58,
      "trusted_sample_count": 56,
      "visibility_pct": 100.0,
      "trusted_pct": 96.55,
      "ball_near_sample_count": 5,
      "ball_near_pct": 8.62,
      "pressure_sample_count": 50,
      "pressure_pct": 86.21,
      "avg_speed_body_heights_per_sec": 0.868,
      "p90_speed_body_heights_per_sec": 1.683,
      "max_speed_body_heights_per_sec": 2.208,
      "raw_max_speed_body_heights_per_sec": 33.621,
      "speed_outlier_count": 3,
      "high_intensity_sample_count": 5
    },
    "quality_gate": {
      "tracking_confidence": 83.39,
      "visual_reliability_label": "high",
      "demo_suitable": true,
      "lost_pct": 0.0,
      "motion_jump_reject_count": 0,
      "color_mismatch_reject_count": 0,
      "failure_taxonomy": [
        "close_players_or_occlusion_risk"
      ],
      "hard_demo_blockers": false,
      "legacy_gate": true,
      "quality_gate_source": "posthoc_legacy_metrics_v3"
    },
    "events": [
      {
        "time_sec": 11.7,
        "time_label": "00:11.7",
        "action": "run_into_space",
        "outcome": "neutral",
        "confidence": "medium",
        "evidence": "Peak movement speed: 2.21 body-heights/sec."
      },
      {
        "time_sec": 3.5,
        "time_label": "00:03.5",
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
      "ai_player_rating": 8.22,
      "fifa_style_card": {
        "OVR": 82,
        "PAC": 76,
        "ACT": 80,
        "INV": 59,
        "REL": 95,
        "DEV": 78
      }
    },
    "artifacts": {
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134049_auto\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134049_auto\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134049_auto\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\rknp_single_player_134049_auto\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  },
  {
    "run_name": "track_yellow_candidate03_t17",
    "report_path": "/mnt/data/audit_v2_norm/rknp_contest_clean_package_v2/sample_outputs/screenshot_yellow_vs_blue/track_yellow_candidate03_t17/rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-41-36.mkv",
    "selected_player": {
      "mode": "seed_bbox",
      "time_sec": 1.7,
      "bbox_xyxy": {
        "x1": 738,
        "y1": 231,
        "x2": 769,
        "y2": 285
      },
      "description": "Yellow player from user screenshot, candidate 3 at 1.70s."
    },
    "metrics": {
      "sample_count": 85,
      "duration_sec": 16.8,
      "visible_sample_count": 85,
      "trusted_sample_count": 85,
      "visibility_pct": 100.0,
      "trusted_pct": 100.0,
      "ball_near_sample_count": 3,
      "ball_near_pct": 3.53,
      "pressure_sample_count": 67,
      "pressure_pct": 78.82,
      "avg_speed_body_heights_per_sec": 1.653,
      "p90_speed_body_heights_per_sec": 3.161,
      "max_speed_body_heights_per_sec": 3.984,
      "raw_max_speed_body_heights_per_sec": 6.296,
      "speed_outlier_count": 8,
      "high_intensity_sample_count": 35
    },
    "quality_gate": {
      "tracking_confidence": 75.6,
      "visual_reliability_label": "medium",
      "demo_suitable": false,
      "lost_pct": 0.0,
      "motion_jump_reject_count": 0,
      "color_mismatch_reject_count": 0,
      "failure_taxonomy": [
        "bbox_drift_or_motion_jump",
        "close_players_or_occlusion_risk"
      ],
      "hard_demo_blockers": true,
      "legacy_gate": true,
      "quality_gate_source": "posthoc_legacy_metrics_v3"
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
        "time_sec": 1.9,
        "time_label": "00:01.9",
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
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_yellow_candidate03_t17\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_yellow_candidate03_t17\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_yellow_candidate03_t17\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_yellow_candidate03_t17\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  },
  {
    "run_name": "track_blue_candidate08_t17",
    "report_path": "/mnt/data/audit_v2_norm/rknp_contest_clean_package_v2/sample_outputs/screenshot_yellow_vs_blue/track_blue_candidate08_t17/rknp_single_player_report.json",
    "input_video": "C:\\Users\\erbos\\Videos\\2026-05-24 13-41-36.mkv",
    "selected_player": {
      "mode": "seed_bbox",
      "time_sec": 1.7,
      "bbox_xyxy": {
        "x1": 815,
        "y1": 225,
        "x2": 846,
        "y2": 281
      },
      "description": "Blue player from user screenshot, candidate 8 at 1.70s."
    },
    "metrics": {
      "sample_count": 85,
      "duration_sec": 16.8,
      "visible_sample_count": 85,
      "trusted_sample_count": 85,
      "visibility_pct": 100.0,
      "trusted_pct": 100.0,
      "ball_near_sample_count": 5,
      "ball_near_pct": 5.88,
      "pressure_sample_count": 72,
      "pressure_pct": 84.71,
      "avg_speed_body_heights_per_sec": 1.332,
      "p90_speed_body_heights_per_sec": 2.634,
      "max_speed_body_heights_per_sec": 3.492,
      "raw_max_speed_body_heights_per_sec": 6.296,
      "speed_outlier_count": 7,
      "high_intensity_sample_count": 26
    },
    "quality_gate": {
      "tracking_confidence": 77.4,
      "visual_reliability_label": "medium",
      "demo_suitable": false,
      "lost_pct": 0.0,
      "motion_jump_reject_count": 0,
      "color_mismatch_reject_count": 0,
      "failure_taxonomy": [
        "bbox_drift_or_motion_jump",
        "close_players_or_occlusion_risk"
      ],
      "hard_demo_blockers": true,
      "legacy_gate": true,
      "quality_gate_source": "posthoc_legacy_metrics_v3"
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
        "time_sec": 1.9,
        "time_label": "00:01.9",
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
      "target_overlay_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_blue_candidate08_t17\\target_overlay_sampled.mp4",
      "player_centered_video": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_blue_candidate08_t17\\player_centered_sampled.mp4",
      "candidate_selection_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_blue_candidate08_t17\\candidate_selection_sheet.jpg",
      "target_tracking_contact_sheet": "C:\\Users\\erbos\\Downloads\\zhanto_project\\debug\\target_from_screenshot\\track_blue_candidate08_t17\\target_tracking_contact_sheet.jpg"
    },
    "limitations": [
      "Short-clip MVP only.",
      "Single selected player only.",
      "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
      "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability."
    ]
  }
]