from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def round_float(value: Any, digits: int = 3) -> float | None:
    try:
        return round(float(value), digits)
    except Exception:
        return None


def quality_from_legacy_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback quality gate for old reports that do not yet include quality_gate."""
    metrics = report.get("metrics") or {}
    records = report.get("records") or []
    total = max(1, len(records))
    lost_count = len([r for r in records if not r.get("bbox_xyxy")])
    lost_pct = 100.0 * lost_count / total
    visible = float(metrics.get("visibility_pct") or 0.0)
    trusted = float(metrics.get("trusted_pct") or 0.0)
    outliers = int(metrics.get("speed_outlier_count") or 0)
    color_rejects = len([r for r in records if str(r.get("trust_label") or "") == "lost_color_mismatch"])
    motion_rejects = len([r for r in records if str(r.get("trust_label") or "") == "lost_motion_jump"])
    reasons: List[str] = []
    if lost_pct >= 15.0:
        reasons.append("target_lost")
    if outliers >= 4 or motion_rejects:
        reasons.append("bbox_drift_or_motion_jump")
    if color_rejects:
        reasons.append("opposite_team_confusion")
    if float(metrics.get("pressure_pct") or 0.0) >= 70.0:
        reasons.append("close_players_or_occlusion_risk")
    if float(metrics.get("ball_near_pct") or 0.0) <= 0.0:
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
    if outliers >= 6:
        penalties += 2
    elif outliers >= 3:
        penalties += 1
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
    return {
        "tracking_confidence": round(max(0.0, min(100.0, 0.55 * visible + 0.35 * trusted - 1.8 * outliers - 3.0 * color_rejects)), 2),
        "visual_reliability_label": label,
        "demo_suitable": label == "high" and visible >= 90.0 and not hard_demo_blockers,
        "lost_pct": round(lost_pct, 2),
        "motion_jump_reject_count": motion_rejects,
        "color_mismatch_reject_count": color_rejects,
        "failure_taxonomy": sorted(set(reasons)),
        "hard_demo_blockers": bool(hard_demo_blockers),
        "legacy_gate": True,
    }


def row_from_report(path: Path) -> Dict[str, Any]:
    report = load_json(path)
    metrics = report.get("metrics") or {}
    rating = report.get("rating") or {}
    quality = report.get("quality_gate") or quality_from_legacy_report(report)
    selected = report.get("selected_player") or {}
    score = float(quality.get("tracking_confidence") or 0.0)
    score += 0.06 * float(metrics.get("trusted_pct") or 0.0)
    score += 0.02 * float(metrics.get("visibility_pct") or 0.0)
    score -= 1.8 * int(metrics.get("speed_outlier_count") or 0)
    if not quality.get("demo_suitable"):
        score -= 25.0
    return {
        "run_name": path.parent.name,
        "report_path": str(path),
        "selected_mode": selected.get("mode"),
        "rating": rating.get("ai_player_rating"),
        "visibility_pct": metrics.get("visibility_pct"),
        "trusted_pct": metrics.get("trusted_pct"),
        "ball_near_pct": metrics.get("ball_near_pct"),
        "pressure_pct": metrics.get("pressure_pct"),
        "speed_outlier_count": metrics.get("speed_outlier_count"),
        "tracking_confidence": quality.get("tracking_confidence"),
        "visual_reliability_label": quality.get("visual_reliability_label"),
        "demo_suitable": bool(quality.get("demo_suitable")),
        "failure_taxonomy": quality.get("failure_taxonomy") or [],
        "selector_score": round(score, 3),
    }


def build_markdown(rows: List[Dict[str, Any]]) -> str:
    suitable = [r for r in rows if r["demo_suitable"]]
    failure = [r for r in rows if not r["demo_suitable"] or r["failure_taxonomy"]]
    lines = [
        "# RKNP Demo Selector Summary",
        "",
        "This file ranks existing `rknp_single_player_report.json` runs for a contest demo.",
        "Use top suitable runs as main demo clips and use risky runs as failure-case evidence.",
        "",
        "## Top Demo Candidates",
        "",
        "| rank | run | suitable | reliability | confidence | visibility | trusted | outliers | score |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for rank, row in enumerate(suitable[:10], 1):
        lines.append(
            f"| {rank} | `{row['run_name']}` | {row['demo_suitable']} | {row['visual_reliability_label']} | "
            f"{row['tracking_confidence']} | {row['visibility_pct']} | {row['trusted_pct']} | "
            f"{row['speed_outlier_count']} | {row['selector_score']} |"
        )
    if not suitable:
        lines.append("| - | No suitable run found | - | - | - | - | - | - | - |")
    lines.extend([
        "",
        "## Failure / Caution Cases",
        "",
        "| run | suitable | reliability | reasons |",
        "|---|---:|---|---|",
    ])
    for row in failure[:15]:
        reasons = ", ".join(row["failure_taxonomy"]) or "manual visual QA still required"
        lines.append(f"| `{row['run_name']}` | {row['demo_suitable']} | {row['visual_reliability_label']} | {reasons} |")
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> Dict[str, Any]:
    report_paths: List[Path] = []
    for item in args.reports:
        path = Path(item)
        if path.is_dir():
            report_paths.extend(sorted(path.rglob("rknp_single_player_report.json")))
        elif path.is_file():
            report_paths.append(path)
    rows = [row_from_report(p) for p in sorted(set(report_paths))]
    rows.sort(key=lambda r: r["selector_score"], reverse=True)
    output_dir = Path(args.output_dir)
    payload = {"run_count": len(rows), "rows": rows}
    save_json(output_dir / "demo_selector_summary.json", payload)
    save_text(output_dir / "demo_selector_summary.md", build_markdown(rows))
    print(json.dumps({
        "run_count": len(rows),
        "best_run": rows[0]["run_name"] if rows else None,
        "summary_json": str(output_dir / "demo_selector_summary.json"),
        "summary_md": str(output_dir / "demo_selector_summary.md"),
    }, ensure_ascii=False, indent=2))
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Rank RKNP report JSON files for contest demo suitability.")
    parser.add_argument("--reports", nargs="+", required=True, help="Report files or directories containing reports.")
    parser.add_argument("--output_dir", default="debug/rknp_demo_selector")
    return parser


if __name__ == "__main__":
    run(build_parser().parse_args())
