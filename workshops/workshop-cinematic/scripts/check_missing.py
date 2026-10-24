from pathlib import Path
images_dir = Path("output/cinematic/job-mcp-explained-7min/images")
existing = set()
for f in images_dir.glob("shot_*.jpg"):
    try:
        num = int(f.stem.split("_")[1])
        existing.add(num)
    except:
        pass
missing = [i for i in range(1, 106) if i not in existing]
print("Existing:", len(existing))
print("Missing shots:", missing)
