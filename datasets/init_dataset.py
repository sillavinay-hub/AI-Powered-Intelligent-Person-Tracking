import os
import csv
from pathlib import Path
from datetime import datetime, timedelta

DATASET_ROOT = Path(__file__).resolve().parent / "custom_resort"
DATASET_ROOT.mkdir(parents=True, exist_ok=True)

# Create camera01 through camera25 subdirectories
for i in range(1, 26):
    cam_folder = DATASET_ROOT / f"camera{i:02d}"
    cam_folder.mkdir(exist_ok=True)
    # Add a .gitkeep so empty directories are preserved in git
    gitkeep = cam_folder / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

# Generate sample ground truth annotations CSV
csv_path = DATASET_ROOT / "annotations.csv"
if not csv_path.exists():
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["person_id", "camera_id", "timestamp", "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2", "ground_truth_label"])
        
        base_time = datetime(2026, 9, 2, 9, 15, 0)
        sample_annotations = [
            ("P001", "CAM-01", (base_time + timedelta(seconds=22)).isoformat(), 280, 110, 360, 320, "authorized_vip"),
            ("P001", "CAM-03", (base_time + timedelta(minutes=6, seconds=18)).isoformat(), 290, 120, 370, 330, "authorized_vip"),
            ("P001", "CAM-04", (base_time + timedelta(minutes=19, seconds=10)).isoformat(), 310, 130, 390, 340, "authorized_vip"),
            ("P001", "CAM-06", (base_time + timedelta(minutes=37, seconds=5)).isoformat(), 300, 125, 380, 335, "authorized_vip"),
            ("P001", "CAM-08", (base_time + timedelta(hours=1, minutes=27, seconds=17)).isoformat(), 320, 140, 400, 350, "authorized_vip"),
        ]
        for row in sample_annotations:
            writer.writerow(row)

print(f"Initialized dataset hierarchy in {DATASET_ROOT} with 25 camera folders and annotations.csv.")
