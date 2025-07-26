import os
import csv
import cv2
from pathlib import Path

# === Set your actual DAiSEE DataSet directory here ===
daisee_root = Path(r"C:\Users\kasif\Downloads\DAiSEE\DAiSEE\DataSet")
labels_csv = Path(r"C:\Users\kasif\Downloads\DAiSEE\DAiSEE\Labels\AllLabels.csv")  # UPDATE this path

# Define split mapping
splits = {
    "Train": "Train",
    "Validation": "Validation",
    "Test": "Test"
}

# Create `your_dataset/` in the current working directory
your_dataset_root = Path.cwd() / "your_dataset"
your_dataset_root.mkdir(exist_ok=True)
print(f"\n📁 Creating folder structure under: {your_dataset_root}")
print("📂 Current Working Directory:", Path.cwd())

# Create subfolders inside your_dataset
for split_dir in splits.values():
    (your_dataset_root / split_dir / "engaged").mkdir(parents=True, exist_ok=True)
    (your_dataset_root / split_dir / "not_engaged").mkdir(parents=True, exist_ok=True)

# ---------------------------
# Function: Load label CSV
# ---------------------------
def load_engagement_labels(label_path: Path) -> dict:
    label_dict = {}
    with open(label_path, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clip = row["ClipID"].strip()
            try:
                level = int(row["Engagement"])
            except ValueError:
                continue
            if level in [0, 1]:
                label_dict[clip] = "not_engaged"
            elif level in [2, 3]:
                label_dict[clip] = "engaged"
    return label_dict

# ---------------------------
# Function: Extract frames at 2 FPS
# ---------------------------
def extract_frames(video_path: Path, target_dir: Path, fps_rate=2):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ Failed to open video: {video_path}")
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(round(fps / fps_rate)) if fps > 0 else 15  # Fallback if FPS not available

    frame_count = 0
    saved_count = 0
    success, frame = cap.read()
    while success:
        if frame_count % interval == 0:
            frame_name = f"{video_path.stem}_frame_{saved_count:03d}.jpg"
            frame_path = target_dir / frame_name
            cv2.imwrite(str(frame_path), frame)
            saved_count += 1
        frame_count += 1
        success, frame = cap.read()

    cap.release()
    print(f"     ✅ Extracted {saved_count} frames from {video_path.name}")

# ---------------------------
# Main Processing
# ---------------------------
label_map = load_engagement_labels(labels_csv)
print(f"\n📊 Loaded {len(label_map)} valid engagement labels.")

total_video_count = 0

for split_name, split_folder in splits.items():
    split_path = daisee_root / split_name
    if not split_path.exists():
        print(f"\n❌ {split_name} folder not found at {split_path}")
        continue

    user_count = 0
    video_count = 0

    print(f"\n📁 {split_name} Summary:")

    for user_dir in split_path.iterdir():
        if not user_dir.is_dir():
            continue
        user_count += 1

        for session_dir in user_dir.iterdir():
            if not session_dir.is_dir():
                continue

            video_files = list(session_dir.glob("*.avi"))
            for video in video_files:
                if video.name in label_map:
                    engagement_label = label_map[video.name]
                    split_folder_name = splits[split_name]
                    target_dir = your_dataset_root / split_folder_name / engagement_label
                    print(f"    🎞️ {video.name} ➜ {target_dir}")

                    # Extract frames at 2 FPS and save to the correct directory
                    extract_frames(video_path=video, target_dir=target_dir)

                else:
                    print(f"     ❌ No Label: {video.name}")
            video_count += len(video_files)

    total_video_count += video_count
    print(f"  👤 User folders     : {user_count}")
    print(f"  🎬 Video files      : {video_count}")

print(f"\n🧮 Total videos across all splits: {total_video_count}")
print("\n✅ Done creating structure and extracting frames.")
