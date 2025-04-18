import os
import glob
import rasterio
import imageio
import earthpy.plot as ep
import matplotlib.pyplot as plt
from datetime import datetime
import cv2
import numpy as np

# -------------------------
# 1. Load TIFF files
# -------------------------
tif_dir = "data"
tif_files = sorted(glob.glob(os.path.join(tif_dir, "*.[Tt][Ii][Ff]*")))

if not tif_files:
    raise FileNotFoundError("No TIFF files found.")

# -------------------------
# 2. Extract month names
# -------------------------
month_names = []
for tif_path in tif_files:
    filename = os.path.basename(tif_path)
    date_str = filename.split("_")[1]
    month_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B")
    month_names.append(month_name)

# -------------------------
# 3. Prepare Frames for GIF and MP4
# -------------------------
frames = []
video_frames = []

for i, tif_path in enumerate(tif_files):
    print(f"Processing: {tif_path}")
    with rasterio.open(tif_path) as src:
        img = src.read()

        # EarthPy expects the image to be in (bands, height, width) format
        if img.shape[0] < 3:
            print(f"Skipping {tif_path} — not RGB")
            continue

        # Set up the plot with EarthPy
        fig, ax = plt.subplots(figsize=(15, 7.5))  # Larger plot for 3600x1800
        ep.plot_rgb(img, ax=ax, title=f"{month_names[i]}")  # Removed scale=False
        
        # Save plot as PNG (high-res)
        tmp_file = "frame.png"
        plt.savefig(tmp_file, bbox_inches='tight', dpi=300)  # High DPI for clarity
        plt.close(fig)

        if os.path.exists(tmp_file):
            # Read the high-res PNG for GIF
            frame = imageio.imread(tmp_file)
            frames.append(frame)

            # Read the high-res PNG for MP4 (OpenCV needs BGR)
            frame_cv = cv2.imread(tmp_file)
            if frame_cv is not None:
                video_frames.append(frame_cv)
        else:
            print(f"Frame not saved for {tif_path}")

# -------------------------
# 4. Save GIF
# -------------------------
if frames:
    gif_duration = 1.5
    imageio.mimsave("bluemarble_timelapse_high_res.gif", frames, duration=gif_duration)
    print("✅ GIF saved as bluemarble_timelapse_high_res.gif")
else:
    print("❌ No GIF frames created.")

# -------------------------
# 5. Save MP4 (Higher Resolution)
# -------------------------
if video_frames:
    height, width, _ = video_frames[0].shape
    out = cv2.VideoWriter("bluemarble_timelapse_high_res.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 1, (width, height))

    for frame in video_frames:
        out.write(frame)

    out.release()
    print("✅ MP4 saved as bluemarble_timelapse_high_res.mp4")
else:
    print("❌ No MP4 frames created.")