from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from assemble_104_gen_v_master import render_segment

print("Testing render_segment(1)...")
seg = render_segment(1)
print(f"Segment 1 rendered successfully: {seg} ({seg.stat().st_size:,} bytes)")
