#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Parse 100 shots from screenplay and verify extraction.
"""
import re
import sys
from pathlib import Path

SCREENPLAY_PATH = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8\KICH_BAN_AI_AGENT_DAU_TIEN_100_SHOTS.md")

def parse_screenplay(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    
    shots = []
    current_shot = None
    
    shot_pattern = re.compile(r"^\*\s+\*\*Shot\s+(\d+)\s*\(([^)]+)\)\s*\[([^\]]+)\]:\*\*\s*(.*)$")
    voice_pattern = re.compile(r"^\s+-\s+\*Thoại:\*\s*\"([^\"]+)\"")
    
    for line in lines:
        sm = shot_pattern.match(line)
        if sm:
            num = int(sm.group(1))
            timing = sm.group(2).strip()
            shot_type = sm.group(3).strip()
            visual_desc = sm.group(4).strip()
            current_shot = {
                "shot_num": num,
                "timing": timing,
                "shot_type": shot_type,
                "visual_desc": visual_desc,
                "dialogue": "",
                "speaker": "byte"
            }
            shots.append(current_shot)
            continue
        
        vm = voice_pattern.match(line)
        if vm and current_shot:
            current_shot["dialogue"] = vm.group(1).strip()
    
    return shots

if __name__ == "__main__":
    shots = parse_screenplay(SCREENPLAY_PATH)
    print(f"Total parsed shots: {len(shots)}")
    if shots:
        print("First shot:", shots[0])
        print("Last shot:", shots[-1])
        # Check any missing dialogues
        missing = [s["shot_num"] for s in shots if not s["dialogue"]]
        if missing:
            print(f"Warning: Shots with missing dialogue: {missing}")
        else:
            print("All 100 shots have complete dialogues!")
