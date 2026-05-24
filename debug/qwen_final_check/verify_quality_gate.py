#!/usr/bin/env python3
"""
Synthetic verification script for build_quality_gate.
Stubs cv2 and ultralytics to avoid dependency issues.
Tests 5 synthetic cases without real video processing.
"""

import sys
import types

# Stub cv2
cv2_stub = types.ModuleType("cv2")
cv2_stub.__version__ = "4.0.0-stub"
sys.modules["cv2"] = cv2_stub

# Stub ultralytics with dummy YOLO class
ultralytics_stub = types.ModuleType("ultralytics")

class DummyYOLO:
    def __init__(self, *args, **kwargs):
        pass
    def track(self, *args, **kwargs):
        return []
    def predict(self, *args, **kwargs):
        return []

ultralytics_stub.YOLO = DummyYOLO
sys.modules["ultralytics"] = ultralytics_stub

# Now import build_quality_gate from the main module
from rknp_single_player_demo import build_quality_gate

def run_test(name, metrics, records, probe, selected_mode="manual", expected_label=None, expected_demo_suitable=None, expected_reasons=None):
    """Run a single test case and print results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    
    qg = build_quality_gate(metrics, records, probe, selected_mode)
    
    label = qg.get("visual_reliability_label", "UNKNOWN")
    demo = qg.get("demo_suitable", None)
    reasons = qg.get("reliability_reasons", [])
    occlusion_pct = qg.get("occlusion_risk_pct", "N/A")
    target_ratio = qg.get("median_target_area_ratio", "N/A")
    failure_tax = qg.get("failure_taxonomy", [])
    
    print(f"visual_reliability_label: {label}")
    print(f"demo_suitable: {demo}")
    print(f"failure_taxonomy: {failure_tax}")
    print(f"reliability_reasons: {reasons}")
    print(f"occlusion_risk_pct: {occlusion_pct}")
    print(f"median_target_area_ratio: {target_ratio}")
    
    # Validation
    passed = True
    if expected_label and label != expected_label:
        print(f"❌ FAIL: Expected label '{expected_label}', got '{label}'")
        passed = False
    if expected_demo_suitable is not None and demo != expected_demo_suitable:
        print(f"❌ FAIL: Expected demo_suitable '{expected_demo_suitable}', got '{demo}'")
        passed = False
    if expected_reasons:
        for reason in expected_reasons:
            if reason not in reasons and reason not in failure_tax:
                print(f"❌ FAIL: Expected reason '{reason}' not found in {reasons + failure_tax}")
                passed = False
    
    if passed:
        print("✅ PASS")
    
    return passed

def create_base_metrics():
    """Create base metrics dict."""
    return {
        "visibility_pct": 100.0,
        "trusted_pct": 100.0,
        "lost_frames_count": 0,
        "speed_outlier_count": 0,
        "ball_detection_weak": False,
    }

def create_base_record(bbox_xyxy=None, occlusion_risk=False, trust_label="good"):
    """Create a base track record with common fields.
    
    bbox_xyxy should be a dict with keys x1, y1, x2, y2.
    If None, uses default (100, 100, 150, 180).
    """
    if bbox_xyxy is None:
        bbox_xyxy = {"x1": 100, "y1": 100, "x2": 150, "y2": 180}  # area = 4000 px²
    
    return {
        "track_id": 1,
        "bbox_xyxy": bbox_xyxy,
        "conf_history": [0.9] * 100,
        "trust_label": trust_label,
        "occlusion_risk": occlusion_risk,
    }

def create_base_probe(width=640, height=480):
    """Create base probe dict with frame dimensions."""
    return {
        "width": width,
        "height": height,
    }

def main():
    print("Starting synthetic quality gate verification...")
    
    all_passed = True
    
    base_metrics = create_base_metrics()
    base_record = create_base_record()  # bbox (100,100,50,80) = 4000 px², frame 640x480=307200, ratio=0.013 > 0.002 ✓
    base_probe = create_base_probe(width=640, height=480)  # frame area = 307200
    
    # CASE A: Clean high reliability
    # bbox area = 50*80 = 4000, frame area = 307200, ratio = 0.013 > 0.002 ✓
    # No occlusion, no lost frames, no speed outliers
    all_passed &= run_test(
        "A. Clean High Reliability",
        metrics=base_metrics.copy(),
        records=[base_record.copy()],
        probe=base_probe.copy(),
        selected_mode="manual",
        expected_label="high",
        expected_demo_suitable=True,
        expected_reasons=[]
    )
    
    # CASE B: Small target (target_area_ratio < 0.002)
    # Need bbox area < 0.002 * 307200 = 614.4 px², so use tiny bbox like 5x8 = 40 px²
    small_record = create_base_record(bbox_xyxy={"x1": 10, "y1": 10, "x2": 15, "y2": 18})  # area = 40, ratio = 0.00013 < 0.002
    all_passed &= run_test(
        "B. Small Target (ratio < 0.002)",
        metrics=base_metrics.copy(),
        records=[small_record],
        probe=base_probe.copy(),
        selected_mode="manual",
        expected_label=None,  # Should be medium or low
        expected_demo_suitable=False,
        expected_reasons=["target_too_small"]
    )
    
    # CASE C: High occlusion (> 50%)
    # Create multiple records, > 50% with occlusion_risk=True
    occ_records = [create_base_record(occlusion_risk=True) for _ in range(6)] + \
                  [create_base_record(occlusion_risk=False) for _ in range(4)]
    all_passed &= run_test(
        "C. High Occlusion (> 50%)",
        metrics=base_metrics.copy(),
        records=occ_records,
        probe=base_probe.copy(),
        selected_mode="manual",
        expected_label=None,  # Should be low
        expected_demo_suitable=False,
        expected_reasons=["close_players_or_occlusion_risk"]
    )
    
    # CASE D: Speed outlier risk
    speed_metrics = base_metrics.copy()
    speed_metrics["speed_outlier_count"] = 5  # >= 4 triggers risk
    speed_record = create_base_record(trust_label="lost_motion_jump")
    all_passed &= run_test(
        "D. Speed Outlier Risk",
        metrics=speed_metrics,
        records=[speed_record],
        probe=base_probe.copy(),
        selected_mode="manual",
        expected_label=None,  # Should be medium or low
        expected_demo_suitable=False,
        expected_reasons=["speed_outlier_risk", "bbox_drift_or_motion_jump"]
    )
    
    # CASE E: Lost frames risk (>= 10%)
    # Simulate by having a record without bbox_xyxy
    lost_record_no_bbox = create_base_record()
    del lost_record_no_bbox["bbox_xyxy"]  # This counts as lost
    lost_records = [lost_record_no_bbox] + [create_base_record() for _ in range(9)]  # 10% lost
    lost_metrics = base_metrics.copy()
    lost_metrics["visibility_pct"] = 90.0  # 10% lost
    all_passed &= run_test(
        "E. Lost Frames Risk (>= 10%)",
        metrics=lost_metrics,
        records=lost_records,
        probe=base_probe.copy(),
        selected_mode="manual",
        expected_label=None,  # Should be medium or low
        expected_demo_suitable=False,
        expected_reasons=["lost_frames_risk"]  # Note: target_lost is not always added
    )
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print(f"{'='*60}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
