from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path.resolve()


def parse_bbox(text: str) -> Dict[str, int]:
    parts = [int(round(float(x.strip()))) for x in str(text).split(",") if x.strip()]
    if len(parts) != 4:
        raise ValueError("bbox must be x1,y1,x2,y2")
    x1, y1, x2, y2 = parts
    if x2 <= x1 or y2 <= y1:
        raise ValueError("invalid bbox")
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def bbox_center(b: Dict[str, int]) -> Tuple[float, float]:
    return ((b["x1"] + b["x2"]) * 0.5, (b["y1"] + b["y2"]) * 0.5)


def clamp_bbox(b: Dict[str, int], w: int, h: int) -> Dict[str, int]:
    x1 = max(0, min(w - 2, int(round(b["x1"]))))
    y1 = max(0, min(h - 2, int(round(b["y1"]))))
    x2 = max(x1 + 1, min(w - 1, int(round(b["x2"]))))
    y2 = max(y1 + 1, min(h - 1, int(round(b["y2"]))))
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2}


def sample_frames(video_path: Path, start_sec: float, end_sec: float, sample_fps: float) -> Tuple[List[Tuple[int, float, np.ndarray]], Dict[str, Any]]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    start = int(round(start_sec * fps))
    end = int(round(end_sec * fps))
    step = max(1, int(round(fps / max(0.1, sample_fps))))
    rows: List[Tuple[int, float, np.ndarray]] = []
    for frame_idx in range(start, min(end, count - 1) + 1, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        if ok and frame is not None:
            rows.append((frame_idx, frame_idx / fps, frame))
    cap.release()
    return rows, {"fps": fps, "frame_count": count, "width": width, "height": height, "sample_fps": sample_fps}


def points_in_bbox(gray: np.ndarray, bbox: Dict[str, int], max_corners: int) -> Optional[np.ndarray]:
    mask = np.zeros(gray.shape, dtype=np.uint8)
    mask[bbox["y1"]:bbox["y2"], bbox["x1"]:bbox["x2"]] = 255
    pts = cv2.goodFeaturesToTrack(gray, maxCorners=max_corners, qualityLevel=0.01, minDistance=3, mask=mask, blockSize=5)
    return pts


def draw_frame(frame: np.ndarray, bbox: Optional[Dict[str, int]], label: str, status: str) -> np.ndarray:
    out = frame.copy()
    color = (40, 220, 40) if status == "tracked" else (0, 190, 255)
    if bbox:
        cv2.rectangle(out, (bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"]), color, 2)
    cv2.rectangle(out, (0, 0), (min(out.shape[1], 520), 30), (0, 0, 0), -1)
    cv2.putText(out, f"{label} {status}", (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def crop_with_bbox(frame: np.ndarray, bbox: Optional[Dict[str, int]], output_size: int, scale: float) -> np.ndarray:
    if not bbox:
        return np.zeros((output_size, output_size, 3), dtype=np.uint8)
    h, w = frame.shape[:2]
    cx, cy = bbox_center(bbox)
    side = max(100.0, max(bbox["x2"] - bbox["x1"], bbox["y2"] - bbox["y1"]) * scale)
    x1, y1 = int(cx - side / 2), int(cy - side / 2)
    x2, y2 = int(cx + side / 2), int(cy + side / 2)
    canvas = np.zeros((max(1, y2 - y1), max(1, x2 - x1), 3), dtype=np.uint8)
    sx1, sy1 = max(0, x1), max(0, y1)
    sx2, sy2 = min(w, x2), min(h, y2)
    dx1, dy1 = sx1 - x1, sy1 - y1
    if sx2 > sx1 and sy2 > sy1:
        canvas[dy1:dy1 + sy2 - sy1, dx1:dx1 + sx2 - sx1] = frame[sy1:sy2, sx1:sx2]
    resized = cv2.resize(canvas, (output_size, output_size), interpolation=cv2.INTER_LINEAR)
    scale_x = canvas.shape[1] / float(output_size)
    scale_y = canvas.shape[0] / float(output_size)
    rb = {
        "x1": int((bbox["x1"] - x1) / max(1e-6, scale_x)),
        "y1": int((bbox["y1"] - y1) / max(1e-6, scale_y)),
        "x2": int((bbox["x2"] - x1) / max(1e-6, scale_x)),
        "y2": int((bbox["y2"] - y1) / max(1e-6, scale_y)),
    }
    cv2.rectangle(resized, (rb["x1"], rb["y1"]), (rb["x2"], rb["y2"]), (40, 220, 40), 2)
    return resized


def write_video(path: Path, frames: List[np.ndarray], fps: float, size: Tuple[int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    if not writer.isOpened():
        raise RuntimeError(f"Cannot write video: {path}")
    try:
        for frame in frames:
            if frame.shape[1] != size[0] or frame.shape[0] != size[1]:
                frame = cv2.resize(frame, size)
            writer.write(frame)
    finally:
        writer.release()


def write_sheet(path: Path, frames: List[np.ndarray]) -> None:
    thumbs = [cv2.resize(f, (240, 180), interpolation=cv2.INTER_AREA) for f in frames[:24]]
    if not thumbs:
        return
    cols = 4
    rows = math.ceil(len(thumbs) / cols)
    sheet = np.zeros((rows * 180, cols * 240, 3), dtype=np.uint8)
    for i, thumb in enumerate(thumbs):
        y = (i // cols) * 180
        x = (i % cols) * 240
        sheet[y:y + 180, x:x + 240] = thumb
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), sheet)


def run(args: argparse.Namespace) -> Dict[str, Any]:
    video = resolve_path(args.input_video)
    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bbox = parse_bbox(args.target_seed_bbox_xyxy)
    rows, probe = sample_frames(video, args.clip_start_sec, args.clip_end_sec, args.analysis_fps)
    if not rows:
        raise RuntimeError("No frames sampled")
    h, w = rows[0][2].shape[:2]
    bbox = clamp_bbox(bbox, w, h)
    records: List[Dict[str, Any]] = []
    overlay_frames: List[np.ndarray] = []
    crop_frames: List[np.ndarray] = []
    prev_gray = cv2.cvtColor(rows[0][2], cv2.COLOR_BGR2GRAY)
    prev_pts = points_in_bbox(prev_gray, bbox, args.max_corners)
    current_bbox: Optional[Dict[str, int]] = dict(bbox)
    for idx, (frame_index, time_sec, frame) in enumerate(rows):
        status = "tracked" if current_bbox else "lost"
        if idx > 0 and current_bbox is not None and prev_pts is not None and len(prev_pts) >= 4:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            next_pts, st, _ = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None, winSize=(21, 21), maxLevel=3)
            if next_pts is None or st is None:
                good_old = np.empty((0, 1, 2), dtype=np.float32)
                good_new = np.empty((0, 1, 2), dtype=np.float32)
            else:
                good_old = prev_pts[st.flatten() == 1]
                good_new = next_pts[st.flatten() == 1]
            if len(good_new) >= 4:
                delta = (good_new.reshape(-1, 2) - good_old.reshape(-1, 2))
                dx, dy = np.median(delta, axis=0)
                if abs(float(dx)) <= args.max_step_px and abs(float(dy)) <= args.max_step_px:
                    current_bbox = clamp_bbox({
                        "x1": current_bbox["x1"] + int(round(float(dx))),
                        "y1": current_bbox["y1"] + int(round(float(dy))),
                        "x2": current_bbox["x2"] + int(round(float(dx))),
                        "y2": current_bbox["y2"] + int(round(float(dy))),
                    }, w, h)
                    status = "tracked"
                else:
                    status = "lost_jump"
                    current_bbox = None
                    prev_pts = None
            else:
                status = "lost_points"
                current_bbox = None
                prev_pts = None
            prev_gray = gray
            if current_bbox is not None:
                prev_pts = points_in_bbox(prev_gray, current_bbox, args.max_corners)
        elif idx > 0 and current_bbox is not None:
            status = "lost_points"
            current_bbox = None
            prev_pts = None
        label = f"LK {args.label} f={frame_index} t={time_sec:.2f}"
        overlay = draw_frame(frame, current_bbox, label, status)
        crop = crop_with_bbox(frame, current_bbox, args.output_crop_size, args.context_scale)
        overlay_frames.append(overlay)
        crop_frames.append(crop)
        records.append({"frame_index": frame_index, "time_sec": round(time_sec, 3), "bbox_xyxy": current_bbox, "status": status})
    overlay_video = output_dir / "lk_target_overlay.mp4"
    crop_video = output_dir / "lk_player_centered.mp4"
    write_video(overlay_video, overlay_frames, args.analysis_fps, (w, h))
    write_video(crop_video, crop_frames, args.analysis_fps, (args.output_crop_size, args.output_crop_size))
    write_sheet(output_dir / "lk_crop_sheet.jpg", crop_frames)
    report = {
        "stage": "rknp_lk_target_tracker",
        "input_video": str(video),
        "seed_bbox_xyxy": bbox,
        "probe": probe,
        "records": records,
        "visible_pct": round(100.0 * len([r for r in records if r["bbox_xyxy"]]) / max(1, len(records)), 2),
        "artifacts": {"overlay": str(overlay_video), "crop": str(crop_video), "sheet": str(output_dir / "lk_crop_sheet.jpg")},
    }
    with open(output_dir / "lk_tracking_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report["artifacts"] | {"visible_pct": report["visible_pct"]}, ensure_ascii=False, indent=2))
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_video", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--clip_start_sec", type=float, default=0.0)
    parser.add_argument("--clip_end_sec", type=float, default=6.0)
    parser.add_argument("--analysis_fps", type=float, default=10.0)
    parser.add_argument("--target_seed_bbox_xyxy", required=True)
    parser.add_argument("--label", default="target")
    parser.add_argument("--max_corners", type=int, default=60)
    parser.add_argument("--max_step_px", type=float, default=80.0)
    parser.add_argument("--output_crop_size", type=int, default=384)
    parser.add_argument("--context_scale", type=float, default=4.0)
    return parser


def main() -> int:
    run(build_parser().parse_args())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
