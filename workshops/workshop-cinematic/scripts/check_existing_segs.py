from pathlib import Path

seg_dir = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\segments")
existing = []
for i in range(1, 105):
    p = seg_dir / f"segment_{i:03d}.mp4"
    if p.exists() and p.stat().st_size > 200000:
        existing.append(i)

missing = [i for i in range(1, 105) if i not in existing]
print(f"Valid segments count: {len(existing)}/104")
print(f"Still to render: {missing}")
