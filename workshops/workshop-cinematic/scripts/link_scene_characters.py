#!/usr/bin/env python3
"""
Update character_names for all 30 scenes in Cyber-Chibi RAG video.
Ensures Google Imagen 3 references approved Character & Location Master Media IDs.
"""
import asyncio
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.db.schema import init_db, close_db
from agent.db import crud

VIDEO_ID = "613b3bb3-2b07-47a8-98be-1664bc529556"

SCENE_REFS = {
    1: ["Viện Công Nghệ Tí Hon"],
    2: ["Byte", "Viện Công Nghệ Tí Hon"],
    3: ["Byte", "Viện Công Nghệ Tí Hon"],
    4: ["Byte", "Viện Công Nghệ Tí Hon"],
    5: ["Byte", "Viện Công Nghệ Tí Hon"],
    6: ["Byte", "Viện Công Nghệ Tí Hon"],
    7: ["Bọ Ảo Giác", "Viện Công Nghệ Tí Hon"],
    8: ["Bọ Ảo Giác", "Viện Công Nghệ Tí Hon"],
    9: ["Byte", "Viện Công Nghệ Tí Hon"],
    10: ["Byte", "Viện Công Nghệ Tí Hon"],
    11: ["Byte", "Bọ Ảo Giác", "Viện Công Nghệ Tí Hon"],
    12: ["Byte", "Viện Công Nghệ Tí Hon"],
    13: ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
    14: ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
    15: ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
    16: ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
    17: ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
    18: ["Tiến sĩ Kael", "Kho Lưu Trữ Dữ Liệu Vector"],
    19: ["Tiến sĩ Kael", "Kho Lưu Trữ Dữ Liệu Vector"],
    20: ["Kho Lưu Trữ Dữ Liệu Vector"],
    21: ["Byte", "Kho Lưu Trữ Dữ Liệu Vector"],
    22: ["Tiến sĩ Kael", "Kho Lưu Trữ Dữ Liệu Vector"],
    23: ["Byte", "Tiến sĩ Kael", "Kho Lưu Trữ Dữ Liệu Vector"],
    24: ["Byte", "Kho Lưu Trữ Dữ Liệu Vector"],
    25: ["Byte", "Tiến sĩ Kael", "Kho Lưu Trữ Dữ Liệu Vector"],
    26: ["Byte", "Viện Công Nghệ Tí Hon"],
    27: ["Bọ Ảo Giác", "Viện Công Nghệ Tí Hon"],
    28: ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
    29: ["Byte", "Viện Công Nghệ Tí Hon"],
    30: ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
}

async def main():
    await init_db()
    scenes = await crud.list_scenes(VIDEO_ID)
    print(f"[*] Updating reference entities for {len(scenes)} scenes in video {VIDEO_ID}...")

    for s in scenes:
        order = s["display_order"]
        refs = SCENE_REFS.get(order, ["Byte"])
        await crud.update_scene(s["id"], character_names=json.dumps(refs, ensure_ascii=False))
        print(f"  [SCENE {order:02d}] Linked refs: {refs}")

    await close_db()
    print("[OK] All scene references updated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
