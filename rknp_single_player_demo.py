from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import cv2
import numpy as np
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parent
PERSON_CLASS_ID = 0
SPORTS_BALL_CLASS_ID = 32


@dataclass
class Detection:
    bbox: Dict[str, int]
    conf: float
    cls: int
    hist: Optional[np.ndarray] = None
    team_color: str = "unknown"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def save_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def parse_bbox(value: Optional[str]) -> Optional[Dict[str, int]]:
    text = str(value or "").strip()
    if not text:
        return None
    parts = [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]
    if len(parts) != 4:
        raise ValueError("--target_seed_bbox_xyxy must be x1,y1,x2,y2")
    x1, y1, x2, y2 = [int(round(float(part))) for part in parts]
    if x2 <= x1 or y2 <= y1:
        raise ValueError("Invalid target bbox: x2/y2 must be larger than x1/y1")
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def round_float(value: Any, digits: int = 3) -> Optional[float]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return round(number, digits)


def format_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    return f"{int(seconds // 60):02d}:{seconds % 60:04.1f}"


def bbox_center(bbox: Dict[str, int]) -> Tuple[float, float]:
    return ((bbox["x1"] + bbox["x2"]) * 0.5, (bbox["y1"] + bbox["y2"]) * 0.5)


def bbox_area(bbox: Dict[str, int]) -> float:
    return max(1.0, float(bbox["x2"] - bbox["x1"]) * float(bbox["y2"] - bbox["y1"]))


def bbox_height(bbox: Dict[str, int]) -> float:
    return max(1.0, float(bbox["y2"] - bbox["y1"]))


def bbox_iou(a: Dict[str, int], b: Dict[str, int]) -> float:
    x1 = max(a["x1"], b["x1"])
    y1 = max(a["y1"], b["y1"])
    x2 = min(a["x2"], b["x2"])
    y2 = min(a["y2"], b["y2"])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter <= 0:
        return 0.0
    union = bbox_area(a) + bbox_area(b) - inter
    return float(inter / max(1.0, union))


def expanded_bbox_contains_point(bbox: Dict[str, int], point: Tuple[float, float], scale: float) -> bool:
    cx, cy = bbox_center(bbox)
    w = (bbox["x2"] - bbox["x1"]) * scale
    h = (bbox["y2"] - bbox["y1"]) * scale
    x, y = point
    return (cx - w * 0.5) <= x <= (cx + w * 0.5) and (cy - h * 0.5) <= y <= (cy + h * 0.5)


def hsv_hist(frame: np.ndarray, bbox: Dict[str, int]) -> Optional[np.ndarray]:
    h, w = frame.shape[:2]
    x1, y1 = max(0, bbox["x1"]), max(0, bbox["y1"])
    x2, y2 = min(w, bbox["x2"]), min(h, bbox["y2"])
    if x2 <= x1 or y2 <= y1:
        return None
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([180, 255, 255]))
    hist = cv2.calcHist([hsv], [0, 1], mask, [18, 16], [0, 180, 0, 256])
    cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    return hist


def jersey_color_label(frame: np.ndarray, bbox: Dict[str, int]) -> str:
    h, w = frame.shape[:2]
    x1, y1 = max(0, bbox["x1"]), max(0, bbox["y1"])
    x2, y2 = min(w, bbox["x2"]), min(h, bbox["y2"])
    if x2 <= x1 or y2 <= y1:
        return "unknown"
    bw, bh = x2 - x1, y2 - y1
    # Use mostly upper torso. Full boxes contain too much grass and shorts.
    tx1 = x1 + int(0.20 * bw)
    tx2 = x1 + int(0.80 * bw)
    ty1 = y1 + int(0.12 * bh)
    ty2 = y1 + int(0.62 * bh)
    crop = frame[max(0, ty1):min(h, ty2), max(0, tx1):min(w, tx2)]
    if crop.size == 0:
        return "unknown"
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0].astype(np.float32)
    sat = hsv[:, :, 1].astype(np.float32)
    val = hsv[:, :, 2].astype(np.float32)
    vivid = (sat > 45) & (val > 45)
    if int(vivid.sum()) < 4:
        return "unknown"
    total = float(vivid.sum())
    yellow = float(((hue >= 16) & (hue <= 42) & vivid).sum()) / total
    blue = float(((hue >= 88) & (hue <= 135) & vivid).sum()) / total
    red = float((((hue <= 10) | (hue >= 165)) & vivid).sum()) / total
    green = float(((hue >= 43) & (hue <= 86) & vivid).sum()) / total
    if yellow >= 0.28 and yellow >= blue and yellow >= red:
        return "yellow"
    if blue >= 0.22 and blue >= yellow and blue >= red:
        return "blue"
    if red >= 0.25 and red >= yellow and red >= blue:
        return "red"
    if green >= 0.45:
        return "green_noise"
    return "unknown"


def hist_similarity(a: Optional[np.ndarray], b: Optional[np.ndarray]) -> float:
    if a is None or b is None:
        return 0.5
    score = float(cv2.compareHist(a, b, cv2.HISTCMP_CORREL))
    return clamp((score + 1.0) * 0.5, 0.0, 1.0)


def read_sampled_frames(video_path: Path, start_sec: float, end_sec: float, sample_fps: float) -> Tuple[Dict[int, np.ndarray], Dict[str, Any]]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"OpenCV could not open video: {video_path}")
    source_fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = frame_count / max(source_fps, 1e-6) if frame_count else 0.0
    start_sec = clamp(start_sec, 0.0, duration if duration else start_sec)
    end_sec = clamp(end_sec, start_sec + 1.0 / max(1.0, sample_fps), duration if duration else end_sec)
    start_frame = int(round(start_sec * source_fps))
    end_frame = int(round(end_sec * source_fps))
    step = max(1, int(round(source_fps / max(0.1, sample_fps))))
    frame_indices = list(range(start_frame, min(end_frame, max(0, frame_count - 1)) + 1, step))
    frames: Dict[int, np.ndarray] = {}
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if ok and frame is not None:
            frames[int(frame_index)] = frame
    cap.release()
    probe = {
        "path": str(video_path),
        "opencv_opened": True,
        "frame_count": frame_count,
        "fps": round_float(source_fps),
        "width": width,
        "height": height,
        "duration_sec": round_float(duration),
        "clip_start_sec": round_float(start_sec),
        "clip_end_sec": round_float(end_sec),
        "analysis_fps": round_float(sample_fps),
        "sampled_frame_count": len(frames),
    }
    return frames, probe


def detections_from_result(frame: np.ndarray, result: Any, conf: float) -> Tuple[List[Detection], List[Detection]]:
    persons: List[Detection] = []
    balls: List[Detection] = []
    if result.boxes is None:
        return persons, balls
    xyxy = result.boxes.xyxy.cpu().numpy()
    cls = result.boxes.cls.cpu().numpy().astype(int)
    scores = result.boxes.conf.cpu().numpy()
    for box, class_id, score in zip(xyxy, cls, scores):
        if float(score) < conf:
            continue
        bbox = {
            "x1": int(round(float(box[0]))),
            "y1": int(round(float(box[1]))),
            "x2": int(round(float(box[2]))),
            "y2": int(round(float(box[3]))),
        }
        if bbox["x2"] <= bbox["x1"] or bbox["y2"] <= bbox["y1"]:
            continue
        det = Detection(bbox=bbox, conf=float(score), cls=int(class_id), hist=hsv_hist(frame, bbox), team_color=jersey_color_label(frame, bbox))
        if class_id == PERSON_CLASS_ID:
            persons.append(det)
        elif class_id == SPORTS_BALL_CLASS_ID:
            balls.append(det)
    return persons, balls


def run_yolo(model_path: Path, frames: Dict[int, np.ndarray], conf: float, imgsz: int, device: Optional[str]) -> Dict[int, Dict[str, List[Detection]]]:
    model = YOLO(str(model_path))
    frame_indices = list(frames.keys())
    images = [frames[idx] for idx in frame_indices]
    kwargs: Dict[str, Any] = {"conf": conf, "imgsz": imgsz, "verbose": False}
    if device:
        kwargs["device"] = device
    results = model.predict(images, **kwargs)
    output: Dict[int, Dict[str, List[Detection]]] = {}
    for frame_index, frame, result in zip(frame_indices, images, results):
        persons, balls = detections_from_result(frame, result, conf)
        output[frame_index] = {"persons": persons, "balls": balls}
    return output


def choose_initial_detection(
    frames: Dict[int, np.ndarray],
    detections: Dict[int, Dict[str, List[Detection]]],
    *,
    start_sec: float,
    fps: float,
    seed_time_sec: Optional[float],
    seed_bbox: Optional[Dict[str, int]],
    strategy: str,
) -> Tuple[int, Detection, str]:
    frame_indices = sorted(frames)
    if not frame_indices:
        raise RuntimeError("No sampled frames were loaded")
    if seed_bbox:
        seed_sec = float(seed_time_sec if seed_time_sec is not None else start_sec)
        target_frame = min(frame_indices, key=lambda idx: abs(idx / max(fps, 1e-6) - seed_sec))
        persons = detections.get(target_frame, {}).get("persons", [])
        if not persons:
            raise RuntimeError(f"No person detections near target seed time {seed_sec:.2f}s")
        ranked = sorted(
            persons,
            key=lambda det: (bbox_iou(det.bbox, seed_bbox), -center_distance(det.bbox, seed_bbox), det.conf),
            reverse=True,
        )
        return target_frame, ranked[0], "seed_bbox"
    for frame_index in frame_indices:
        persons = detections.get(frame_index, {}).get("persons", [])
        if not persons:
            continue
        h, w = frames[frame_index].shape[:2]
        if strategy == "largest":
            chosen = max(persons, key=lambda det: bbox_area(det.bbox))
        elif strategy == "lower_center":
            anchor = (w * 0.5, h * 0.72)
            chosen = min(persons, key=lambda det: point_distance(bbox_center(det.bbox), anchor))
        else:
            anchor = (w * 0.5, h * 0.5)
            chosen = min(persons, key=lambda det: point_distance(bbox_center(det.bbox), anchor))
        return frame_index, chosen, f"auto_{strategy}"
    raise RuntimeError("YOLO did not detect any players in the sampled clip")


def point_distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return float(math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2))


def center_distance(a: Dict[str, int], b: Dict[str, int]) -> float:
    return point_distance(bbox_center(a), bbox_center(b))


def color_compatible(target_color: str, candidate_color: str) -> bool:
    if target_color in {"unknown", "green_noise"}:
        return True
    if candidate_color in {"unknown", "green_noise"}:
        return True
    return target_color == candidate_color


def score_candidate(candidate: Detection, last_bbox: Dict[str, int], ref_hist: Optional[np.ndarray], target_color: str) -> float:
    dist = center_distance(candidate.bbox, last_bbox)
    scale = max(80.0, bbox_height(last_bbox) * 3.2)
    distance_score = 1.0 - clamp(dist / scale, 0.0, 1.0)
    color_score = hist_similarity(ref_hist, candidate.hist)
    area_ratio = bbox_area(candidate.bbox) / max(1.0, bbox_area(last_bbox))
    size_score = 1.0 - clamp(abs(math.log(max(1e-6, area_ratio))) / 1.2, 0.0, 1.0)
    score = float(0.52 * distance_score + 0.33 * color_score + 0.15 * size_score)
    if not color_compatible(target_color, candidate.team_color):
        score *= 0.12
    elif target_color not in {"unknown", "green_noise"} and candidate.team_color == "unknown":
        score *= 0.72
    return score


def track_direction(
    frame_order: List[int],
    detections: Dict[int, Dict[str, List[Detection]]],
    *,
    seed_bbox: Dict[str, int],
    seed_hist: Optional[np.ndarray],
    seed_color: str,
) -> Dict[int, Dict[str, Any]]:
    records: Dict[int, Dict[str, Any]] = {}
    last_bbox = dict(seed_bbox)
    ref_hist = seed_hist
    target_color = seed_color if seed_color not in {"", "green_noise"} else "unknown"
    for frame_index in frame_order:
        persons = detections.get(frame_index, {}).get("persons", [])
        balls = detections.get(frame_index, {}).get("balls", [])
        if target_color == "unknown":
            for person in persons:
                if bbox_iou(person.bbox, seed_bbox) > 0.5 and person.team_color not in {"unknown", "green_noise"}:
                    target_color = person.team_color
                    break
        if not persons:
            records[frame_index] = {
                "bbox_xyxy": None,
                "tracking_score": 0.0,
                "trust_label": "missing",
                "person_count": 0,
                "ball_count": len(balls),
                "ball_near": False,
                "nearby_player_count": 0,
                "target_color": target_color,
                "selected_color": None,
            }
            continue
        ranked = sorted(persons, key=lambda det: score_candidate(det, last_bbox, ref_hist, target_color), reverse=True)
        chosen = ranked[0]
        score = score_candidate(chosen, last_bbox, ref_hist, target_color)
        second_score = score_candidate(ranked[1], last_bbox, ref_hist, target_color) if len(ranked) > 1 else 0.0
        margin = score - second_score
        jump_distance = center_distance(chosen.bbox, last_bbox)
        max_allowed_jump = max(120.0, bbox_height(last_bbox) * 4.2)
        if jump_distance > max_allowed_jump:
            trust = "motion_rejected"
        elif not color_compatible(target_color, chosen.team_color):
            trust = "color_rejected"
        elif score >= 0.58 and margin >= 0.035:
            trust = "trusted"
        elif score >= 0.42:
            trust = "usable"
        elif score >= 0.28:
            trust = "uncertain"
        else:
            records[frame_index] = {
                "bbox_xyxy": None,
                "tracking_score": round_float(score),
                "trust_label": "lost",
                "person_count": len(persons),
                "ball_count": len(balls),
                "ball_near": False,
                "nearby_player_count": 0,
                "target_color": target_color,
                "selected_color": chosen.team_color,
                "candidate_margin": round_float(margin),
                "jump_distance_px": round_float(jump_distance, 2),
            }
            continue
        if trust == "color_rejected":
            records[frame_index] = {
                "bbox_xyxy": None,
                "tracking_score": round_float(score),
                "trust_label": "lost_color_mismatch",
                "person_count": len(persons),
                "ball_count": len(balls),
                "ball_near": False,
                "nearby_player_count": 0,
                "target_color": target_color,
                "selected_color": chosen.team_color,
                "candidate_margin": round_float(margin),
                "jump_distance_px": round_float(jump_distance, 2),
            }
            continue
        if trust == "motion_rejected":
            records[frame_index] = {
                "bbox_xyxy": None,
                "tracking_score": round_float(score),
                "trust_label": "lost_motion_jump",
                "person_count": len(persons),
                "ball_count": len(balls),
                "ball_near": False,
                "nearby_player_count": 0,
                "target_color": target_color,
                "selected_color": chosen.team_color,
                "candidate_margin": round_float(margin),
                "jump_distance_px": round_float(jump_distance, 2),
            }
            continue
        if trust in {"trusted", "usable"}:
            last_bbox = dict(chosen.bbox)
            if chosen.hist is not None:
                ref_hist = chosen.hist if ref_hist is None else cv2.addWeighted(ref_hist, 0.75, chosen.hist, 0.25, 0)
        center = bbox_center(chosen.bbox)
        height = bbox_height(chosen.bbox)
        ball_near = False
        nearest_ball_distance = None
        for ball in balls:
            ball_center = bbox_center(ball.bbox)
            distance = point_distance(center, ball_center)
            nearest_ball_distance = distance if nearest_ball_distance is None else min(nearest_ball_distance, distance)
            if expanded_bbox_contains_point(chosen.bbox, ball_center, 3.0) or distance <= height * 2.4:
                ball_near = True
        nearby_players = 0
        for person in persons:
            if person.bbox == chosen.bbox:
                continue
            if point_distance(center, bbox_center(person.bbox)) <= height * 2.2:
                nearby_players += 1
        records[frame_index] = {
            "bbox_xyxy": chosen.bbox,
            "tracking_score": round_float(score),
            "trust_label": trust,
            "person_count": len(persons),
            "ball_count": len(balls),
            "ball_near": bool(ball_near),
            "nearest_ball_distance_px": round_float(nearest_ball_distance, 2),
            "nearby_player_count": nearby_players,
            "target_color": target_color,
            "selected_color": chosen.team_color,
            "candidate_margin": round_float(margin),
            "jump_distance_px": round_float(jump_distance, 2),
        }
    return records


def track_target(
    frames: Dict[int, np.ndarray],
    detections: Dict[int, Dict[str, List[Detection]]],
    *,
    init_frame: int,
    init_detection: Detection,
    fps: float,
) -> List[Dict[str, Any]]:
    frame_indices = sorted(frames)
    before = [idx for idx in frame_indices if idx < init_frame]
    after = [idx for idx in frame_indices if idx > init_frame]
    backward_records = track_direction(
        list(reversed(before)),
        detections,
        seed_bbox=init_detection.bbox,
        seed_hist=init_detection.hist,
        seed_color=init_detection.team_color,
    )
    forward_records = track_direction(
        after,
        detections,
        seed_bbox=init_detection.bbox,
        seed_hist=init_detection.hist,
        seed_color=init_detection.team_color,
    )
    init_balls = detections.get(init_frame, {}).get("balls", [])
    init_persons = detections.get(init_frame, {}).get("persons", [])
    init_center = bbox_center(init_detection.bbox)
    init_height = bbox_height(init_detection.bbox)
    init_ball_near = any(point_distance(init_center, bbox_center(ball.bbox)) <= init_height * 2.4 for ball in init_balls)
    records: List[Dict[str, Any]] = []
    for idx in frame_indices:
        if idx == init_frame:
            record = {
                "bbox_xyxy": init_detection.bbox,
                "tracking_score": 1.0,
                "trust_label": "trusted",
                "person_count": len(init_persons),
                "ball_count": len(init_balls),
                "ball_near": init_ball_near,
                "nearby_player_count": 0,
                "target_color": init_detection.team_color,
                "selected_color": init_detection.team_color,
                "candidate_margin": None,
            }
        elif idx < init_frame:
            record = backward_records.get(idx, {})
        else:
            record = forward_records.get(idx, {})
        record = dict(record)
        record.update({
            "frame_index": idx,
            "time_sec": round_float(idx / max(fps, 1e-6), 3),
            "time_label": format_time(idx / max(fps, 1e-6)),
            "analysis_usable": record.get("bbox_xyxy") is not None and record.get("trust_label") in {"trusted", "usable", "uncertain"},
            "analysis_trusted": record.get("bbox_xyxy") is not None and record.get("trust_label") == "trusted",
        })
        records.append(record)
    return records


def pairwise_speeds(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    speeds: List[Dict[str, Any]] = []
    prev: Optional[Dict[str, Any]] = None
    for record in records:
        bbox = record.get("bbox_xyxy")
        if not record.get("analysis_usable") or not bbox:
            continue
        if prev and prev.get("bbox_xyxy"):
            dt = float(record["time_sec"]) - float(prev["time_sec"])
            if dt > 1e-6:
                cx, cy = bbox_center(bbox)
                px, py = bbox_center(prev["bbox_xyxy"])
                avg_h = max(1.0, 0.5 * (bbox_height(bbox) + bbox_height(prev["bbox_xyxy"])))
                speed = math.sqrt((cx - px) ** 2 + (cy - py) ** 2) / avg_h / dt
                speeds.append({"time_sec": record["time_sec"], "speed_body_heights_per_sec": float(speed)})
        prev = record
    return speeds


def percentile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    arr = sorted(values)
    idx = min(len(arr) - 1, max(0, int(round((len(arr) - 1) * q))))
    return float(arr[idx])


def summarize(records: List[Dict[str, Any]], speed_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    usable = [r for r in records if r.get("analysis_usable")]
    trusted = [r for r in records if r.get("analysis_trusted")]
    ball_near = [r for r in usable if r.get("ball_near")]
    pressure = [r for r in usable if int(r.get("nearby_player_count") or 0) >= 2]
    raw_speeds = [float(row["speed_body_heights_per_sec"]) for row in speed_rows]
    speeds = [value for value in raw_speeds if value <= 4.0]
    start_time = float(records[0]["time_sec"]) if records else 0.0
    end_time = float(records[-1]["time_sec"]) if records else start_time
    return {
        "sample_count": total,
        "duration_sec": round_float(max(0.0, end_time - start_time), 3),
        "visible_sample_count": len(usable),
        "trusted_sample_count": len(trusted),
        "visibility_pct": round(100.0 * len(usable) / max(1, total), 2),
        "trusted_pct": round(100.0 * len(trusted) / max(1, total), 2),
        "ball_near_sample_count": len(ball_near),
        "ball_near_pct": round(100.0 * len(ball_near) / max(1, len(usable)), 2),
        "pressure_sample_count": len(pressure),
        "pressure_pct": round(100.0 * len(pressure) / max(1, len(usable)), 2),
        "avg_speed_body_heights_per_sec": round(float(np.mean(speeds)) if speeds else 0.0, 3),
        "p90_speed_body_heights_per_sec": round(percentile(speeds, 0.9), 3),
        "max_speed_body_heights_per_sec": round(max(speeds) if speeds else 0.0, 3),
        "raw_max_speed_body_heights_per_sec": round(max(raw_speeds) if raw_speeds else 0.0, 3),
        "speed_outlier_count": len([value for value in raw_speeds if value > 4.0]),
        "high_intensity_sample_count": len([s for s in speeds if s >= 1.7]),
    }


def classify_failure_reasons(records: List[Dict[str, Any]], metrics: Dict[str, Any], probe: Dict[str, Any]) -> List[str]:
    """Convert tracker symptoms into a stable, contest-friendly failure taxonomy."""
    reasons: List[str] = []
    total = max(1, len(records))
    lost_count = len([r for r in records if not r.get("bbox_xyxy")])
    lost_pct = 100.0 * lost_count / total
    trust_labels = [str(r.get("trust_label") or "missing") for r in records]
    if lost_pct >= 15.0:
        reasons.append("target_lost")
    if any(label == "lost_motion_jump" for label in trust_labels) or int(metrics.get("speed_outlier_count") or 0) >= 4:
        reasons.append("bbox_drift_or_motion_jump")
    if any(label == "lost_color_mismatch" for label in trust_labels):
        reasons.append("opposite_team_confusion")
    if float(metrics.get("pressure_pct") or 0.0) >= 70.0:
        reasons.append("close_players_or_occlusion_risk")
    if float(metrics.get("trusted_pct") or 0.0) < 70.0:
        reasons.append("identity_unverified")
    if float(metrics.get("ball_near_pct") or 0.0) <= 0.0:
        reasons.append("ball_not_visible_or_not_detected")

    heights = [bbox_height(r["bbox_xyxy"]) for r in records if r.get("bbox_xyxy")]
    frame_h = float(probe.get("height") or 0.0)
    if heights and frame_h > 0:
        median_height_pct = 100.0 * float(np.median(heights)) / frame_h
        if median_height_pct < 5.0:
            reasons.append("target_too_small")
    return sorted(set(reasons))


def build_quality_gate(metrics: Dict[str, Any], records: List[Dict[str, Any]], probe: Dict[str, Any], selected_mode: str) -> Dict[str, Any]:
    """Honest reliability layer: tells whether this run is safe to show as a demo."""
    total = max(1, len(records))
    lost_count = len([r for r in records if not r.get("bbox_xyxy")])
    uncertain_count = len([r for r in records if str(r.get("trust_label") or "") == "uncertain"])
    motion_jump_count = len([r for r in records if str(r.get("trust_label") or "") == "lost_motion_jump"])
    color_mismatch_count = len([r for r in records if str(r.get("trust_label") or "") == "lost_color_mismatch"])
    lost_pct = 100.0 * lost_count / total
    visible_pct = float(metrics.get("visibility_pct") or 0.0)
    trusted_pct = float(metrics.get("trusted_pct") or 0.0)
    speed_outlier_count = int(metrics.get("speed_outlier_count") or 0)
    heights = [bbox_height(r["bbox_xyxy"]) for r in records if r.get("bbox_xyxy")]
    frame_h = float(probe.get("height") or 0.0)
    median_target_height_px = float(np.median(heights)) if heights else 0.0
    median_target_height_pct = 100.0 * median_target_height_px / frame_h if frame_h > 0 else 0.0
    failure_reasons = classify_failure_reasons(records, metrics, probe)

    penalties = 0
    if visible_pct < 90.0:
        penalties += 2
    elif visible_pct < 97.0:
        penalties += 1
    if trusted_pct < 75.0:
        penalties += 2
    elif trusted_pct < 90.0:
        penalties += 1
    if lost_pct >= 15.0:
        penalties += 2
    elif lost_pct > 5.0:
        penalties += 1
    if speed_outlier_count >= 6 or motion_jump_count >= 3:
        penalties += 4
    elif speed_outlier_count >= 3 or motion_jump_count >= 1:
        penalties += 2
    if color_mismatch_count > 0:
        penalties += 2
    if median_target_height_pct and median_target_height_pct < 5.0:
        penalties += 1

    if penalties <= 1:
        label = "high"
    elif penalties <= 3:
        label = "medium"
    else:
        label = "low"

    hard_demo_blockers = (
        speed_outlier_count >= 4
        or motion_jump_count >= 2
        or lost_pct >= 10.0
        or color_mismatch_count > 0
        or "bbox_drift_or_motion_jump" in failure_reasons
        or "opposite_team_confusion" in failure_reasons
    )
    demo_suitable = label == "high" and visible_pct >= 90.0 and not hard_demo_blockers
    if selected_mode.startswith("auto_"):
        # Auto target selection is okay for a quick smoke test, but the contest demo should still
        # show the candidate sheet and explain the planned coach-click workflow.
        demo_note = "auto-selected target; visually confirm candidate sheet before showing as final demo"
    else:
        demo_note = "manual seed bbox / coach-click style initialization"

    return {
        "tracking_confidence": round(clamp(0.55 * visible_pct + 0.35 * trusted_pct - 1.8 * speed_outlier_count - 3.0 * color_mismatch_count, 0.0, 100.0), 2),
        "visual_reliability_label": label,
        "demo_suitable": bool(demo_suitable),
        "demo_note": demo_note,
        "manual_confirmation_required": True,
        "lost_sample_count": lost_count,
        "lost_pct": round(lost_pct, 2),
        "uncertain_sample_count": uncertain_count,
        "motion_jump_reject_count": motion_jump_count,
        "color_mismatch_reject_count": color_mismatch_count,
        "median_target_height_px": round_float(median_target_height_px, 2),
        "median_target_height_pct_of_frame": round_float(median_target_height_pct, 2),
        "failure_taxonomy": failure_reasons,
        "hard_demo_blockers": bool(hard_demo_blockers),
        "guardrail": "If demo_suitable is false, use this run as a caution/failure case, not as the main demo.",
    }


def build_events(records: List[Dict[str, Any]], speed_rows: List[Dict[str, Any]], summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    speed_by_time = {round(float(row["time_sec"]), 3): float(row["speed_body_heights_per_sec"]) for row in speed_rows}
    robust_speed_rows = [row for row in speed_rows if float(row["speed_body_heights_per_sec"]) <= 4.0]
    if robust_speed_rows:
        top_speed = max(robust_speed_rows, key=lambda row: float(row["speed_body_heights_per_sec"]))
        action = "run_into_space" if float(top_speed["speed_body_heights_per_sec"]) >= 1.0 else "running_support"
        if action == "run_into_space":
            events.append({
                "time_sec": round_float(top_speed["time_sec"], 2),
                "time_label": format_time(float(top_speed["time_sec"])),
                "action": "run_into_space",
                "outcome": "neutral",
                "confidence": "medium" if float(top_speed["speed_body_heights_per_sec"]) >= 1.7 else "low",
                "evidence": f"Peak movement speed: {float(top_speed['speed_body_heights_per_sec']):.2f} body-heights/sec.",
            })
    ball_records = [r for r in records if r.get("analysis_usable") and r.get("ball_near")]
    if ball_records:
        first = ball_records[0]
        speed = speed_by_time.get(round(float(first["time_sec"]), 3), 0.0)
        events.append({
            "time_sec": round_float(first["time_sec"], 2),
            "time_label": first["time_label"],
            "action": "carrying_ball" if speed >= 0.45 else "receiving_ball",
            "outcome": "neutral",
            "confidence": "low",
            "evidence": "YOLO detected the ball near the tracked player; exact pass/dribble outcome is not claimed.",
        })
    pressure_records = [r for r in records if r.get("analysis_usable") and int(r.get("nearby_player_count") or 0) >= 2]
    if pressure_records:
        first = pressure_records[0]
        events.append({
            "time_sec": round_float(first["time_sec"], 2),
            "time_label": first["time_label"],
            "action": "pressing",
            "outcome": "neutral",
            "confidence": "low",
            "evidence": "Several nearby players were detected around the target; this may indicate pressure/duel context.",
        })
    if not events:
        events.append({
            "time_sec": round_float(records[0]["time_sec"], 2) if records else 0.0,
            "time_label": records[0]["time_label"] if records else "00:00.0",
            "action": "run_into_space" if float(summary.get("avg_speed_body_heights_per_sec") or 0.0) >= 0.45 else "receiving_ball",
            "outcome": "unclear",
            "confidence": "low",
            "evidence": "No reliable ball-specific event was detected; report falls back to movement evidence.",
        })
    return events[:5]


def rating_and_card(summary: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    visibility = float(summary.get("visibility_pct") or 0.0) / 100.0
    trusted = float(summary.get("trusted_pct") or 0.0) / 100.0
    avg_speed = min(1.0, float(summary.get("avg_speed_body_heights_per_sec") or 0.0) / 1.2)
    p90_speed = min(1.0, float(summary.get("p90_speed_body_heights_per_sec") or 0.0) / 2.2)
    ball = float(summary.get("ball_near_pct") or 0.0) / 100.0
    pressure = float(summary.get("pressure_pct") or 0.0) / 100.0
    rating = 5.4 + 1.2 * visibility + 0.5 * trusted + 0.75 * avg_speed + 0.45 * p90_speed + 0.35 * ball + 0.25 * pressure
    if visibility < 0.55:
        rating -= 0.8
    rating = round(clamp(rating, 3.0, 10.0), 2)
    pace = int(round(clamp(42 + 45 * p90_speed, 1, 99)))
    activity = int(round(clamp(38 + 42 * avg_speed + 12 * visibility, 1, 99)))
    involvement = int(round(clamp(35 + 35 * ball + 18 * pressure + 8 * avg_speed, 1, 99)))
    reliability = int(round(clamp(30 + 55 * visibility + 10 * trusted, 1, 99)))
    development = int(round(clamp((pace + activity + involvement + reliability) / 4.0, 1, 99)))
    return {
        "ai_player_rating": rating,
        "fifa_style_card": {
            "OVR": int(round(clamp(rating * 10.0, 1, 99))),
            "PAC": pace,
            "ACT": activity,
            "INV": involvement,
            "REL": reliability,
            "DEV": development,
        },
    }


def crop_square_with_bbox(frame: np.ndarray, bbox: Optional[Dict[str, int]], output_size: int, context_scale: float) -> Tuple[np.ndarray, Optional[Dict[str, int]]]:
    if not bbox:
        return np.zeros((output_size, output_size, 3), dtype=np.uint8), None
    h, w = frame.shape[:2]
    cx, cy = bbox_center(bbox)
    side = max(80.0, max(bbox["x2"] - bbox["x1"], bbox["y2"] - bbox["y1"]) * context_scale)
    x1 = int(math.floor(cx - side * 0.5))
    y1 = int(math.floor(cy - side * 0.5))
    x2 = int(math.ceil(cx + side * 0.5))
    y2 = int(math.ceil(cy + side * 0.5))
    src_x1, src_y1 = max(0, x1), max(0, y1)
    src_x2, src_y2 = min(w, x2), min(h, y2)
    canvas = np.zeros((max(1, y2 - y1), max(1, x2 - x1), 3), dtype=np.uint8)
    dst_x1, dst_y1 = src_x1 - x1, src_y1 - y1
    if src_x2 > src_x1 and src_y2 > src_y1:
        canvas[dst_y1:dst_y1 + src_y2 - src_y1, dst_x1:dst_x1 + src_x2 - src_x1] = frame[src_y1:src_y2, src_x1:src_x2]
    scale_x = canvas.shape[1] / float(output_size)
    scale_y = canvas.shape[0] / float(output_size)
    rel_bbox = {
        "x1": int(round((bbox["x1"] - x1) / max(1e-6, scale_x))),
        "y1": int(round((bbox["y1"] - y1) / max(1e-6, scale_y))),
        "x2": int(round((bbox["x2"] - x1) / max(1e-6, scale_x))),
        "y2": int(round((bbox["y2"] - y1) / max(1e-6, scale_y))),
    }
    return cv2.resize(canvas, (output_size, output_size), interpolation=cv2.INTER_LINEAR), rel_bbox


def draw_record(frame: np.ndarray, record: Dict[str, Any], label: str) -> np.ndarray:
    out = frame.copy()
    bbox = record.get("bbox_xyxy")
    trust = str(record.get("trust_label") or "missing")
    color = (40, 220, 40) if trust == "trusted" else (0, 210, 255) if trust == "usable" else (0, 140, 255)
    if bbox:
        cv2.rectangle(out, (bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"]), color, 2)
    cv2.rectangle(out, (0, 0), (out.shape[1], 30), (0, 0, 0), -1)
    text = f"{label} t={record.get('time_label')} trust={trust} score={record.get('tracking_score')}"
    cv2.putText(out, text[:110], (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def draw_crop_record(frame: np.ndarray, rel_bbox: Optional[Dict[str, int]], record: Dict[str, Any], label: str) -> np.ndarray:
    out = frame.copy()
    trust = str(record.get("trust_label") or "missing")
    color = (40, 220, 40) if trust == "trusted" else (0, 210, 255) if trust == "usable" else (0, 140, 255)
    if rel_bbox:
        cv2.rectangle(out, (rel_bbox["x1"], rel_bbox["y1"]), (rel_bbox["x2"], rel_bbox["y2"]), color, 2)
    cv2.rectangle(out, (0, 0), (out.shape[1], 28), (0, 0, 0), -1)
    text = f"{label} t={record.get('time_label')} {trust} color={record.get('selected_color')}"
    cv2.putText(out, text[:90], (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def write_video(path: Path, frames: List[np.ndarray], fps: float, size: Tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    if not writer.isOpened():
        raise RuntimeError(f"Could not open video writer: {path}")
    try:
        for frame in frames:
            if frame.shape[1] != size[0] or frame.shape[0] != size[1]:
                frame = cv2.resize(frame, size, interpolation=cv2.INTER_LINEAR)
            writer.write(frame)
    finally:
        writer.release()


def write_contact_sheet(path: Path, frames: List[np.ndarray], cols: int = 4, thumb_size: Tuple[int, int] = (320, 180)) -> None:
    if not frames:
        return
    thumbs = [cv2.resize(frame, thumb_size, interpolation=cv2.INTER_AREA) for frame in frames]
    rows = int(math.ceil(len(thumbs) / float(cols)))
    canvas = np.zeros((rows * thumb_size[1], cols * thumb_size[0], 3), dtype=np.uint8)
    for idx, thumb in enumerate(thumbs):
        y = (idx // cols) * thumb_size[1]
        x = (idx % cols) * thumb_size[0]
        canvas[y:y + thumb_size[1], x:x + thumb_size[0]] = thumb
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), canvas)


def write_candidate_sheet(path: Path, frame: np.ndarray, persons: List[Detection], chosen: Detection, frame_time: float) -> None:
    out = frame.copy()
    for idx, person in enumerate(persons, 1):
        color = (40, 220, 40) if person.bbox == chosen.bbox else (0, 190, 255)
        b = person.bbox
        cv2.rectangle(out, (b["x1"], b["y1"]), (b["x2"], b["y2"]), color, 2)
        cv2.putText(out, str(idx), (b["x1"], max(18, b["y1"] - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    cv2.rectangle(out, (0, 0), (out.shape[1], 34), (0, 0, 0), -1)
    cv2.putText(out, f"Candidate sheet at {frame_time:.2f}s; green = selected target", (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 1, cv2.LINE_AA)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), out)


def candidate_rows(persons: List[Detection], chosen: Detection) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for idx, person in enumerate(persons, 1):
        rows.append({
            "candidate_id": idx,
            "bbox_xyxy": person.bbox,
            "confidence": round_float(person.conf),
            "selected": person.bbox == chosen.bbox,
        })
    return rows


def build_markdown(report: Dict[str, Any]) -> str:
    summary = report["metrics"]
    card = report["rating"]["fifa_style_card"]
    lines = [
        "# RKNP Single Player Demo Report",
        "",
        f"- input_video: `{report['input_video']}`",
        f"- status: `{report['status']}`",
        f"- selected_player_mode: `{report['selected_player']['mode']}`",
        f"- analyzed_duration_sec: `{summary['duration_sec']}`",
        f"- visibility_pct: `{summary['visibility_pct']}`",
        f"- AI Player Rating: `{report['rating']['ai_player_rating']}`",
        f"- tracking_confidence: `{(report.get('quality_gate') or {}).get('tracking_confidence')}`",
        f"- visual_reliability_label: `{(report.get('quality_gate') or {}).get('visual_reliability_label')}`",
        f"- demo_suitable: `{(report.get('quality_gate') or {}).get('demo_suitable')}`",
        "",
        "## Tracking Quality Gate",
        "",
        f"- lost_pct: `{(report.get('quality_gate') or {}).get('lost_pct')}`",
        f"- motion_jump_reject_count: `{(report.get('quality_gate') or {}).get('motion_jump_reject_count')}`",
        f"- color_mismatch_reject_count: `{(report.get('quality_gate') or {}).get('color_mismatch_reject_count')}`",
        f"- median_target_height_pct_of_frame: `{(report.get('quality_gate') or {}).get('median_target_height_pct_of_frame')}`",
        f"- failure_taxonomy: `{', '.join((report.get('quality_gate') or {}).get('failure_taxonomy') or []) or 'none'}`",
        f"- note: {(report.get('quality_gate') or {}).get('demo_note')}",
        "",
        "## FIFA-Style Card",
        "",
        f"- OVR: `{card['OVR']}`",
        f"- PAC: `{card['PAC']}`",
        f"- ACT: `{card['ACT']}`",
        f"- INV: `{card['INV']}`",
        f"- REL: `{card['REL']}`",
        f"- DEV: `{card['DEV']}`",
        "",
        "## Краткий анализ игрока",
        "",
        report["narrative"]["summary"],
        "",
        "## Сильные стороны",
        "",
    ]
    lines.extend([f"- {item}" for item in report["narrative"]["strengths"]])
    lines.extend(["", "## Зоны развития", ""])
    lines.extend([f"- {item}" for item in report["narrative"]["weaknesses"]])
    lines.extend(["", "## Персональные упражнения", ""])
    lines.extend([f"- {item}" for item in report["narrative"]["training_recommendations"]])
    lines.extend(["", "## Action Evidence", ""])
    for event in report["events"]:
        lines.append(f"- `{event['time_label']}` `{event['action']}` / `{event['outcome']}` / `{event['confidence']}`: {event['evidence']}")
    lines.extend([
        "",
        "## Honest Limitations",
        "",
        "- Demo analyzes one short episode, not a full match.",
        "- Exact passes, xG, heatmaps and tactical network maps are not claimed.",
        "- Ball detection is unreliable on broadcast/screen-recorded footage, so ball-related events use low confidence unless evidence is strong.",
        "- Rating is an explainable MVP score for motivation and coaching support, not an official player level.",
        "",
    ])
    return "\n".join(lines)


def build_narrative(summary: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
    visibility = float(summary.get("visibility_pct") or 0.0)
    avg_speed = float(summary.get("avg_speed_body_heights_per_sec") or 0.0)
    p90 = float(summary.get("p90_speed_body_heights_per_sec") or 0.0)
    ball_pct = float(summary.get("ball_near_pct") or 0.0)
    pressure_pct = float(summary.get("pressure_pct") or 0.0)
    if p90 >= 1.7:
        movement_text = "показал высокоинтенсивное ускорение и активно менял позицию"
    elif avg_speed >= 0.45:
        movement_text = "активно перемещался и поддерживал эпизод"
    else:
        movement_text = "больше сохранял позицию, чем ускорял игру"
    summary_text = (
        f"В коротком эпизоде система удержала выбранного игрока на {visibility:.1f}% sampled-кадров. "
        f"По движению игрок {movement_text}. "
        f"Близость мяча к игроку зафиксирована на {ball_pct:.1f}% видимых кадров, "
        f"контекст давления рядом с другими игроками — на {pressure_pct:.1f}%."
    )
    strengths = []
    if visibility >= 75:
        strengths.append("Игрок достаточно стабильно виден в кадре, поэтому его действия можно использовать как evidence для тренера.")
    if p90 >= 1.4:
        strengths.append("Есть заметные ускорения: это полезно для оценки рывков, открываний и реакции на эпизод.")
    if ball_pct > 0:
        strengths.append("В эпизоде есть признаки вовлечения рядом с мячом, но точный исход действия требует ручной проверки.")
    if not strengths:
        strengths.append("Главная ценность эпизода — базовая видимость и движение выбранного игрока для разбора с тренером.")
    weaknesses = []
    if visibility < 70:
        weaknesses.append("Низкая/средняя видимость: игрок частично теряется из-за качества видео, интерфейса записи или похожих игроков.")
    if avg_speed < 0.35:
        weaknesses.append("Мало выраженных ускорений: для оценки темпа лучше добавить эпизод с открыванием, прессингом или атакой.")
    if ball_pct == 0:
        weaknesses.append("Мяч не был надежно найден рядом с игроком, поэтому система не делает выводы о передачах, ударах или дриблинге.")
    if not weaknesses:
        weaknesses.append("Главное ограничение — короткая длительность эпизода; для устойчивой оценки нужны несколько клипов из матча.")
    training = [
        "3x6 ускорений 10-15 м с изменением направления после визуального сигнала тренера.",
        "Упражнение 4v2/5v3 на открывание под передачу и быстрое решение после приема.",
        "Видео-разбор 2-3 эпизодов: где игрок открылся вовремя, где мог дать лучший угол поддержки.",
    ]
    if any(event["action"] == "pressing" for event in events):
        training.append("Прессинг-триггеры: старт давления после плохого приема соперника или передачи назад.")
    return {
        "summary": summary_text,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "training_recommendations": training,
    }


def run(args: argparse.Namespace) -> Dict[str, Any]:
    input_video = resolve_path(args.input_video)
    output_dir = resolve_path(args.output_dir)
    model_path = resolve_path(args.model)
    output_dir.mkdir(parents=True, exist_ok=True)
    seed_bbox = parse_bbox(args.target_seed_bbox_xyxy)
    clip_end = float(args.clip_end_sec) if args.clip_end_sec is not None else 999999.0
    frames, probe = read_sampled_frames(input_video, float(args.clip_start_sec), clip_end, float(args.analysis_fps))
    detections = run_yolo(model_path, frames, float(args.conf), int(args.imgsz), args.device)
    init_frame, init_detection, init_mode = choose_initial_detection(
        frames,
        detections,
        start_sec=float(args.clip_start_sec),
        fps=float(probe["fps"] or 30.0),
        seed_time_sec=args.target_seed_time_sec,
        seed_bbox=seed_bbox,
        strategy=args.target_strategy,
    )
    records = track_target(frames, detections, init_frame=init_frame, init_detection=init_detection, fps=float(probe["fps"] or 30.0))
    speed_rows = pairwise_speeds(records)
    metrics = summarize(records, speed_rows)
    events = build_events(records, speed_rows, metrics)
    rating = rating_and_card(metrics, events)
    narrative = build_narrative(metrics, events)
    quality_gate = build_quality_gate(metrics, records, probe, init_mode)

    record_by_frame = {record["frame_index"]: record for record in records}
    overlay_frames: List[np.ndarray] = []
    crop_frames: List[np.ndarray] = []
    thumbs: List[np.ndarray] = []
    for idx in sorted(frames):
        record = record_by_frame[idx]
        overlay = draw_record(frames[idx], record, "RKNP target")
        crop, rel_bbox = crop_square_with_bbox(frames[idx], record.get("bbox_xyxy"), int(args.output_crop_size), float(args.context_scale))
        crop = draw_crop_record(crop, rel_bbox, record, "center crop")
        overlay_frames.append(overlay)
        crop_frames.append(crop)
        if len(thumbs) < 24:
            thumbs.append(overlay)

    source_size = (probe["width"], probe["height"])
    overlay_video = output_dir / "target_overlay_sampled.mp4"
    crop_video = output_dir / "player_centered_sampled.mp4"
    write_video(overlay_video, overlay_frames, float(args.analysis_fps), source_size)
    write_video(crop_video, crop_frames, float(args.analysis_fps), (int(args.output_crop_size), int(args.output_crop_size)))
    contact_sheet = output_dir / "target_tracking_contact_sheet.jpg"
    write_contact_sheet(contact_sheet, thumbs)
    candidate_sheet = output_dir / "candidate_selection_sheet.jpg"
    write_candidate_sheet(candidate_sheet, frames[init_frame], detections[init_frame]["persons"], init_detection, init_frame / float(probe["fps"] or 30.0))
    candidates_json = output_dir / "candidate_selection.json"
    save_json(candidates_json, {
        "frame_index": init_frame,
        "time_sec": round_float(init_frame / float(probe["fps"] or 30.0), 3),
        "mode": init_mode,
        "candidates": candidate_rows(detections[init_frame]["persons"], init_detection),
        "manual_confirmation_required": True,
        "instruction": "Use the green bbox as the target only after visual confirmation by coach/user.",
    })
    status_summary = output_dir / "status_summary.json"
    save_json(status_summary, {
        "stage": "rknp_single_player_demo_quality_gate",
        "status": "complete",
        "input_video": str(input_video),
        "output_dir": str(output_dir),
        "selected_mode": init_mode,
        "metrics": metrics,
        "quality_gate": quality_gate,
    })

    report = {
        "schema_version": "1.0",
        "stage": "rknp_single_player_demo",
        "created_at_utc": utc_now(),
        "status": "complete",
        "input_video": str(input_video),
        "output_dir": str(output_dir),
        "video_probe": probe,
        "selected_player": {
            "mode": init_mode,
            "frame_index": init_frame,
            "time_sec": round_float(init_frame / float(probe["fps"] or 30.0), 3),
            "bbox_xyxy": init_detection.bbox,
            "confidence": round_float(init_detection.conf),
            "description": str(args.target_player_description or ""),
        },
        "metrics": metrics,
        "events": events,
        "rating": rating,
        "quality_gate": quality_gate,
        "narrative": narrative,
        "artifacts": {
            "target_overlay_video": str(overlay_video),
            "player_centered_video": str(crop_video),
            "candidate_selection_sheet": str(candidate_sheet),
            "candidate_selection_json": str(candidates_json),
            "target_tracking_contact_sheet": str(contact_sheet),
            "status_summary_json": str(status_summary),
        },
        "records": records,
        "speed_rows": speed_rows,
        "limitations": [
            "Short-clip MVP only.",
            "Single selected player only.",
            "No xG, exact pass map, heatmap, team network, or full-match tactical claim.",
            "Screen-recorded broadcast clips include UI artifacts; clean trimming improves reliability.",
        ],
    }
    report_json = output_dir / "rknp_single_player_report.json"
    report_md = output_dir / "rknp_single_player_report.md"
    save_json(report_json, report)
    save_text(report_md, build_markdown(report))
    print(json.dumps({
        "stage": report["stage"],
        "status": report["status"],
        "input_video": report["input_video"],
        "output_dir": str(output_dir),
        "report_json": str(report_json),
        "report_md": str(report_md),
        "target_overlay_video": str(overlay_video),
        "player_centered_video": str(crop_video),
        "candidate_selection_sheet": str(candidate_sheet),
        "candidate_selection_json": str(candidates_json),
        "contact_sheet": str(contact_sheet),
        "metrics": metrics,
        "rating": rating,
        "quality_gate": quality_gate,
    }, ensure_ascii=False, indent=2))
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RKNP short-clip single-player football demo.")
    parser.add_argument("--input_video", required=True)
    parser.add_argument("--output_dir", default=str(PROJECT_ROOT / "debug" / "rknp_single_player_demo"))
    parser.add_argument("--model", default=str(PROJECT_ROOT / "yolov8n.pt"))
    parser.add_argument("--clip_start_sec", type=float, default=0.0)
    parser.add_argument("--clip_end_sec", type=float, default=None)
    parser.add_argument("--analysis_fps", type=float, default=5.0)
    parser.add_argument("--conf", type=float, default=0.20)
    parser.add_argument("--imgsz", type=int, default=960)
    parser.add_argument("--device", default=None)
    parser.add_argument("--target_seed_time_sec", type=float, default=None)
    parser.add_argument("--target_seed_bbox_xyxy", default=None)
    parser.add_argument("--target_strategy", default="center", choices=("center", "largest", "lower_center"))
    parser.add_argument("--target_player_description", default="")
    parser.add_argument("--output_crop_size", type=int, default=384)
    parser.add_argument("--context_scale", type=float, default=3.2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
