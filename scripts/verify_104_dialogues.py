import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import re
import json
from pathlib import Path

spec_path = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\STORYBOARD_SPEC_104_SHOTS.md")
with open(spec_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

shots = []
for line in lines:
    m = re.search(r'\*\s*\*\*Shot\s+(\d+)\s*\((.*?)\)\s*\[(.*?)\]:\*\*\s*(.*?)\s*\*\(Thoại:\s*\"(.*?)\"\)\*', line)
    if m:
        shots.append({
            "shot": int(m.group(1)),
            "time": m.group(2),
            "type": m.group(3),
            "visual": m.group(4).strip(),
            "dialogue": m.group(5).strip()
        })

print(f"Parsed {len(shots)} shots from spec.")
if len(shots) == 104:
    print("✅ All 104 shots have cleanly structured dialogues!")
    # Check words per sentence
    long_sentences = [s for s in shots if len(s["dialogue"].split()) > 20]
    print(f"Sentences > 20 words: {len(long_sentences)}")
