from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_json_from_text(text: str) -> Dict[str, Any]:
    text = str(text or "").strip()
    if not text:
        return {"parse_status": "empty"}
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            data["parse_status"] = "ok"
            return data
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict):
                data["parse_status"] = "ok_recovered"
                return data
        except Exception:
            pass
    return {"parse_status": "failed", "raw_text": text[:8000]}


def maybe_repair_mojibake(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text
    markers = ("Р ", "РЎ", "РІР", "Рќ", "Рњ", "Р°", "Рµ")
    if not any(marker in text for marker in markers):
        return text
    for encoding in ("cp1251", "latin1"):
        try:
            repaired = text.encode(encoding, errors="ignore").decode("utf-8", errors="ignore")
        except Exception:
            continue
        if repaired and sum(repaired.count(marker) for marker in markers) < sum(text.count(marker) for marker in markers):
            return repaired
    return text


def repair_payload(value: Any) -> Any:
    if isinstance(value, str):
        return maybe_repair_mojibake(value)
    if isinstance(value, list):
        return [repair_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: repair_payload(item) for key, item in value.items()}
    return value



def quality_from_legacy_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Post-hoc quality gate for old sample reports that were generated before quality_gate existed.

    This does not pretend to re-run CV. It only converts existing metrics/records into an
    honest reliability label so the OpenAI text layer can stay grounded.
    """
    metrics = report.get("metrics") or {}
    records = report.get("records") or []
    total = max(1, len(records))
    lost_count = len([r for r in records if not r.get("bbox_xyxy")])
    lost_pct = 100.0 * lost_count / total
    visible = float(metrics.get("visibility_pct") or 0.0)
    trusted = float(metrics.get("trusted_pct") or 0.0)
    outliers = int(metrics.get("speed_outlier_count") or 0)
    pressure = float(metrics.get("pressure_pct") or 0.0)
    ball_near = float(metrics.get("ball_near_pct") or 0.0)
    color_rejects = len([r for r in records if str(r.get("trust_label") or "") == "lost_color_mismatch"])
    motion_rejects = len([r for r in records if str(r.get("trust_label") or "") == "lost_motion_jump"])

    reasons: List[str] = []
    if lost_pct >= 15.0:
        reasons.append("target_lost")
    if outliers >= 4 or motion_rejects:
        reasons.append("bbox_drift_or_motion_jump")
    if color_rejects:
        reasons.append("opposite_team_confusion")
    if pressure >= 70.0:
        reasons.append("close_players_or_occlusion_risk")
    if trusted < 70.0:
        reasons.append("identity_unverified")
    if ball_near <= 0.0:
        reasons.append("ball_not_visible_or_not_detected")

    penalties = 0
    if visible < 90.0:
        penalties += 2
    elif visible < 97.0:
        penalties += 1
    if trusted < 75.0:
        penalties += 2
    elif trusted < 90.0:
        penalties += 1
    if lost_pct >= 15.0:
        penalties += 2
    elif lost_pct > 5.0:
        penalties += 1
    if outliers >= 6 or motion_rejects >= 3:
        penalties += 4
    elif outliers >= 3 or motion_rejects >= 1:
        penalties += 2
    if color_rejects:
        penalties += 2

    label = "high" if penalties <= 1 else "medium" if penalties <= 3 else "low"
    hard_demo_blockers = (
        outliers >= 4
        or motion_rejects >= 2
        or color_rejects > 0
        or lost_pct >= 10.0
        or "bbox_drift_or_motion_jump" in reasons
        or "opposite_team_confusion" in reasons
    )
    confidence = max(0.0, min(100.0, 0.55 * visible + 0.35 * trusted - 1.8 * outliers - 3.0 * color_rejects))
    return {
        "tracking_confidence": round(confidence, 2),
        "visual_reliability_label": label,
        "demo_suitable": bool(label == "high" and visible >= 90.0 and not hard_demo_blockers),
        "demo_note": "post-hoc quality gate from legacy report; visually confirm contact sheet",
        "manual_confirmation_required": True,
        "lost_sample_count": lost_count,
        "lost_pct": round(lost_pct, 2),
        "motion_jump_reject_count": motion_rejects,
        "color_mismatch_reject_count": color_rejects,
        "failure_taxonomy": sorted(set(reasons)),
        "hard_demo_blockers": bool(hard_demo_blockers),
        "quality_gate_source": "posthoc_legacy_metrics_v3",
        "guardrail": "If demo_suitable is false, use this run as a caution/failure case, not as the main demo.",
    }


def compact_report(path: Path) -> Dict[str, Any]:
    report = load_json(path)
    artifacts = report.get("artifacts") or {}
    selected = report.get("selected_player") or {}
    return {
        "run_name": path.parent.name,
        "report_path": str(path),
        "input_video": report.get("input_video"),
        "selected_player": {
            "mode": selected.get("mode"),
            "time_sec": selected.get("time_sec"),
            "bbox_xyxy": selected.get("bbox_xyxy"),
            "description": selected.get("description") or "",
        },
        "metrics": report.get("metrics") or {},
        "quality_gate": report.get("quality_gate") or quality_from_legacy_report(report),
        "events": report.get("events") or [],
        "rating": report.get("rating") or {},
        "artifacts": {
            "target_overlay_video": artifacts.get("target_overlay_video"),
            "player_centered_video": artifacts.get("player_centered_video"),
            "candidate_selection_sheet": artifacts.get("candidate_selection_sheet"),
            "target_tracking_contact_sheet": artifacts.get("target_tracking_contact_sheet"),
        },
        "limitations": report.get("limitations") or [],
    }


def build_prompt(reports: List[Dict[str, Any]], project_context: str) -> str:
    payload = json.dumps(reports, ensure_ascii=False, indent=2)
    return f"""
Ты помогаешь подготовить научный проект для конкурса РКНП.

Контекст проекта:
{project_context}

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
{{
  "coach_summary": "2-4 предложения",
  "player_comparison": [
    {{
      "run_name": "...",
      "short_label": "Игрок A/B/C",
      "episode_profile": "краткий профиль по метрикам",
      "strengths": ["..."],
      "development_zones": ["..."],
      "training_recommendations": ["..."],
      "rating_interpretation": "как читать рейтинг без завышенных обещаний"
    }}
  ],
  "best_demo_player": {{
    "run_name": "...",
    "reason": "почему этот запуск лучше всего подходит для демонстрации"
  }},
  "research_interpretation": [
    "какой научный вывод можно защищать по этим метрикам",
    "какое ограничение надо честно сказать судьям"
  ],
  "limitations": ["..."]
}}

JSON-метрики:
{payload}
""".strip()


def call_openai(model: str, prompt: str) -> Dict[str, Any]:
    try:
        from openai import OpenAI
    except Exception as exc:
        return {"provider_status": "openai_sdk_missing", "error": str(exc)}
    if not os.environ.get("OPENAI_API_KEY"):
        return {"provider_status": "openai_api_key_missing"}
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You write careful, evidence-based youth football analysis in Russian. Use only the provided metrics.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        parsed = parse_json_from_text(content)
        parsed = repair_payload(parsed)
        parsed["provider_status"] = "ok"
        parsed["model"] = model
        return parsed
    except Exception as exc:
        return {"provider_status": "api_error", "model": model, "error": str(exc)}



def build_fallback_analysis(reports: List[Dict[str, Any]], provider_status: str, model: str) -> Dict[str, Any]:
    """Deterministic local report if OpenAI SDK/key is missing.

    This keeps the demo usable offline and avoids empty reports during a contest.
    The fallback is deliberately conservative and uses only JSON metrics.
    """
    def num(v: Any, default: float = 0.0) -> float:
        try:
            return float(v)
        except Exception:
            return default

    def explain_report(r: Dict[str, Any], idx: int) -> Dict[str, Any]:
        metrics = r.get("metrics") or {}
        quality = r.get("quality_gate") or {}
        rating = r.get("rating") or {}
        run_name = r.get("run_name") or f"run_{idx}"
        visible = num(metrics.get("visibility_pct"))
        trusted = num(metrics.get("trusted_pct"))
        ball = num(metrics.get("ball_near_pct"))
        pressure = num(metrics.get("pressure_pct"))
        outliers = int(num(metrics.get("speed_outlier_count")))
        qlabel = quality.get("visual_reliability_label") or "unknown"
        suitable = bool(quality.get("demo_suitable"))
        reasons = quality.get("failure_taxonomy") or []

        strengths: List[str] = []
        development: List[str] = []
        training: List[str] = []

        if visible >= 95 and trusted >= 90 and outliers < 4:
            strengths.append("Трек игрока достаточно стабилен для короткого демонстрационного эпизода.")
        if pressure >= 70:
            strengths.append("Игрок часто находился рядом с другими игроками, поэтому эпизод полезен для анализа игры под давлением.")
        if ball >= 10:
            strengths.append("В части кадров мяч был рядом с игроком; можно осторожно обсуждать вовлеченность в игровой эпизод.")
        else:
            development.append("По этому клипу недостаточно данных для вывода о владении мячом, передачах или дриблинге.")
        if outliers >= 4 or not suitable:
            development.append("Нужно визуально проверить contact sheet: возможны скачки bbox, occlusion или нестабильность tracking.")
        if pressure >= 70:
            training.append("Можно проверить упражнения на открывание под давлением и принятие решений в плотных эпизодах.")
        else:
            training.append("Можно использовать клип для базовой оценки движения без завышенных выводов о технике.")
        training.append("Следующий шаг — сравнить этот эпизод с 2-3 другими клипами того же игрока.")

        if not strengths:
            strengths.append("Есть измеримые визуальные метрики по короткому эпизоду, но выводы должны быть осторожными.")
        if reasons:
            development.append("Ограничения запуска: " + ", ".join(str(x) for x in reasons) + ".")

        return {
            "run_name": run_name,
            "short_label": f"Игрок {idx}",
            "episode_profile": (
                f"Видимость {visible:.1f}%, trusted tracking {trusted:.1f}%, "
                f"ball-near {ball:.1f}%, pressure {pressure:.1f}%, "
                f"quality={qlabel}, demo_suitable={suitable}."
            ),
            "strengths": strengths,
            "development_zones": development,
            "training_recommendations": training,
            "rating_interpretation": (
                f"Рейтинг {rating.get('ai_player_rating')} — относительная мотивационная оценка внутри короткого клипа, "
                "а не показатель профессионального уровня игрока."
            ),
        }

    ranked = sorted(
        reports,
        key=lambda r: (bool((r.get("quality_gate") or {}).get("demo_suitable")), num((r.get("quality_gate") or {}).get("tracking_confidence"))),
        reverse=True,
    )
    best = ranked[0] if ranked else {}
    best_quality = best.get("quality_gate") or {}
    return {
        "provider_status": provider_status,
        "model": model,
        "fallback_mode": True,
        "coach_summary": (
            "OpenAI API недоступен, поэтому создан локальный fallback-отчет по JSON-метрикам. "
            "Главный демонстрационный запуск следует выбирать по visual evidence и quality_gate, а не только по рейтингу."
        ),
        "player_comparison": [explain_report(r, i + 1) for i, r in enumerate(reports)],
        "best_demo_player": {
            "run_name": best.get("run_name"),
            "reason": f"Лучший по demo_suitable={best_quality.get('demo_suitable')} и tracking_confidence={best_quality.get('tracking_confidence')}."
        },
        "research_interpretation": [
            "Короткий выбранный эпизод позволяет получить базовые image-space метрики и evidence-видео.",
            "Плотные эпизоды, близкие игроки и скачки bbox должны рассматриваться как ограничения tracking, а не скрываться."
        ],
        "limitations": [
            "Без калибровки поля нельзя честно заявлять скорость в км/ч или дистанцию в метрах.",
            "Без надежной детекции мяча нельзя заявлять точные передачи, владение или xG.",
            "OpenAI/LLM является только текстовым слоем поверх рассчитанных метрик."
        ],
    }


def build_markdown(result: Dict[str, Any], reports: List[Dict[str, Any]]) -> str:
    lines = [
        "# OpenAI Coach Analysis",
        "",
        f"- created_at_utc: `{utc_now()}`",
        f"- provider_status: `{result.get('provider_status')}`",
        f"- model: `{result.get('model')}`",
        "",
    ]
    if result.get("fallback_mode"):
        lines.append("> **⚠️ Offline Fallback Mode:** OpenAI API was unavailable. This report is generated locally from JSON metrics only. OpenAI did NOT watch the video.")
        lines.append("")
    else:
        lines.append("> **Note:** OpenAI/LLM only explains existing JSON metrics. It does NOT perform computer vision or watch the video directly.")
        lines.append("")
    lines.extend([
        "## Coach Summary",
        "",
        str(result.get("coach_summary") or "No summary."),
        "",
        "## Player Comparison",
        "",
    ])
    for item in result.get("player_comparison") or []:
        lines.append(f"### {item.get('short_label') or item.get('run_name')}")
        lines.append("")
        lines.append(str(item.get("episode_profile") or ""))
        lines.append("")
        lines.append("Strengths:")
        lines.extend([f"- {x}" for x in item.get("strengths") or []])
        lines.append("")
        lines.append("Development zones:")
        lines.extend([f"- {x}" for x in item.get("development_zones") or []])
        lines.append("")
        lines.append("Training recommendations:")
        lines.extend([f"- {x}" for x in item.get("training_recommendations") or []])
        lines.append("")
        lines.append(f"Rating interpretation: {item.get('rating_interpretation') or ''}")
        lines.append("")
    best = result.get("best_demo_player") or {}
    lines.extend([
        "## Best Demo Player",
        "",
        f"- run: `{best.get('run_name')}`",
        f"- reason: {best.get('reason') or ''}",
        "",
        "## Research Interpretation",
        "",
    ])
    lines.extend([f"- {x}" for x in result.get("research_interpretation") or []])
    lines.extend(["", "## Limitations", ""])
    lines.extend([f"- {x}" for x in result.get("limitations") or []])
    lines.extend(["", "## Source Reports", ""])
    for report in reports:
        metrics = report.get("metrics") or {}
        rating = report.get("rating") or {}
        quality = report.get("quality_gate") or {}
        lines.append(
            f"- `{report['run_name']}` rating=`{rating.get('ai_player_rating')}` "
            f"visibility=`{metrics.get('visibility_pct')}` trusted=`{metrics.get('trusted_pct')}` "
            f"ball_near=`{metrics.get('ball_near_pct')}` pressure=`{metrics.get('pressure_pct')}` "
            f"quality=`{quality.get('visual_reliability_label')}` suitable=`{quality.get('demo_suitable')}`"
        )
    lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> Dict[str, Any]:
    reports = [compact_report(resolve_path(path)) for path in args.reports]
    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    project_context = args.project_context or (
        "Мобильное приложение для детских и юношеских футбольных академий: тренер загружает видео, "
        "выбирает одного игрока, система возвращает evidence-метрики, краткий анализ, FIFA-style карточку "
        "и осторожные персональные рекомендации. Цель - снизить субъективность и сделать базовую аналитику доступной."
    )
    prompt = build_prompt(reports, project_context)
    save_text(output_dir / "openai_prompt.md", prompt)
    result = call_openai(args.model, prompt)
    if result.get("provider_status") != "ok":
        result = build_fallback_analysis(reports, result.get("provider_status") or "unknown", args.model)
    package = {
        "schema_version": "1.0",
        "stage": "rknp_openai_player_analysis",
        "created_at_utc": utc_now(),
        "model": args.model,
        "reports": reports,
        "openai_result": result,
    }
    save_json(output_dir / "openai_player_analysis.json", package)
    save_text(output_dir / "openai_player_analysis.md", build_markdown(result, reports))
    print(json.dumps({
        "stage": package["stage"],
        "provider_status": result.get("provider_status"),
        "model": result.get("model") or args.model,
        "output_dir": str(output_dir),
        "analysis_json": str(output_dir / "openai_player_analysis.json"),
        "analysis_md": str(output_dir / "openai_player_analysis.md"),
        "player_count": len(reports),
    }, ensure_ascii=False, indent=2))
    return package


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate OpenAI coach analysis from RKNP player metric JSON reports.")
    parser.add_argument("--reports", nargs="+", required=True)
    parser.add_argument("--output_dir", default=str(PROJECT_ROOT / "debug" / "rknp_openai_player_analysis"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--project_context", default="")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
