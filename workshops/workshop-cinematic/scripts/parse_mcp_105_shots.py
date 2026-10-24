#!/usr/bin/env python3
"""
OmniVideo Studio - Workshop 4 (Cinematic AI Video Studio)
Parse and validate 105 shots from KICH_BAN_MCP_GIAI_MA_105_SHOTS.md
"""
import re
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCREENPLAY_PATH = Path(r"C:\Users\tranh\.gemini\antigravity\brain\74745d7e-e139-4bc8-b6d1-fbc945ef19d8\KICH_BAN_MCP_GIAI_MA_105_SHOTS.md")
OUTPUT_MANIFEST = Path(r"C:\Users\tranh\Documents\Duy\VideoAI\output\cinematic\job-mcp-explained-7min\mcp_105_manifest.json")

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
            
            # Determine speaker badge
            speaker_badge = "BÉ BYTE (AI AGENT)"
            if 42 <= num <= 73:
                speaker_badge = "BÉ BYTE (MCP SERVER)"
            elif 74 <= num <= 94:
                speaker_badge = "BÉ BYTE (BẢO MẬT MCP)"
                
            current_shot = {
                "shot_num": num,
                "timing": timing,
                "shot_type": shot_type,
                "visual_desc": visual_desc,
                "dialogue": "",
                "speaker_badge": speaker_badge
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
    empty_dialogues = [s["shot_num"] for s in shots if not s["dialogue"]]
    print("Empty dialogues:", empty_dialogues)
    
    OUTPUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MANIFEST.write_text(json.dumps(shots, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest written to {OUTPUT_MANIFEST}")
