import glob
import os
from pathlib import Path

img_dir = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\images")
files = sorted(img_dir.glob("shot_*.jpg"))
print(f"Total image files found: {len(files)}")
indices = [int(f.stem.replace("shot_", "")) for f in files]
print(f"Range: from {min(indices)} to {max(indices)}")

missing = [i for i in range(1, 105) if i not in indices]
print(f"Missing image indices (count={len(missing)}): {missing}")
