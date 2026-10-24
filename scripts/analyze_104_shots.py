import sys
import re
from pathlib import Path

spec_path = Path(r"c:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-ai-agent-giaimatech-10min\STORYBOARD_SPEC_104_SHOTS.md")
with open(spec_path, "r", encoding="utf-8") as f:
    text = f.read()

# Pattern matching: *(Thoại: "...")*
dialogues = re.findall(r'\*\(Thoại:\s*\"(.*?)\"\)\*', text)
print(f"Total dialogue beats found: {len(dialogues)}")
total_words = sum(len(d.split()) for d in dialogues)
print(f"Total words in dialogues: {total_words}")
if dialogues:
    print(f"Average words per beat: {total_words/len(dialogues):.1f}")
    print(f"Estimated audio duration at 135 wpm: {total_words/135*60:.1f} seconds ({total_words/135:.2f} minutes)")
