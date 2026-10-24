#!/usr/bin/env python3
"""
Populate and refine Character & Location Master Entities for RAG Xianxia Film.
"""
import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.db.schema import init_db, close_db
from agent.db import crud

PROJECT_ID = "cef0da57-d9e3-44f1-ac2f-9eac6b7cc8ad"

MASTER_ASSETS = [
    {
        "name": "Tiểu Linh",
        "entity_type": "character",
        "description": "Nữ Khí Linh Chatbot thông minh, dung nhan thanh tú, mắt sáng lấp lánh, y phục lụa thanh thiên thêu chỉ bạc lộng lẫy.",
        "image_prompt": "Cinematic 3D Donghua portrait of an elegant celestial fairy spirit girl, 18 years old appearance, luminous expressive obsidian eyes, wearing flowing cyan and silver embroidered silk robes, intricate jade hairpins, ethereal celestial aura, Octane Render, 8K ultra-detailed, photorealistic skin texture, Unreal Engine 5 aesthetic",
        "voice_description": "Trong trẻo, thanh tao, thông minh, tinh nghịch của nữ Khí Linh"
    },
    {
        "name": "Đạo Sư",
        "entity_type": "character",
        "description": "Bậc Đạo Sư công nghệ thời đại số, tiên phong đạo cốt, râu tóc bạc phơ gọn gàng, bạch y phiêu dật, tay cầm ngọc trượng trí tuệ.",
        "image_prompt": "Cinematic 3D Donghua portrait of an ancient venerable Taoist Master, calm wise demeanor, dignified silver hair with jade crown, pristine white and gold embroidered Taoist robes, holding a radiant jade scepter, heavenly volumetric mist, Octane Render, 8K hyper-detailed",
        "voice_description": "Trầm ấm, uy nghiêm, thông thái của bậc tôn sư công nghệ"
    },
    {
        "name": "Tâm Ma",
        "entity_type": "character",
        "description": "Hiện thân của ảo giác AI (Hallucination), bóng ma huyễn hoặc quấn quanh sương mù tím đậm, nụ cười ngạo mạn giễu cợt.",
        "image_prompt": "Cinematic 3D Donghua portrait of a shadowy phantom figure shrouded in swirling violet mystical smoke, piercing glowing purple eyes, arrogant haughty sneer, dynamic dark particle energy, Unreal Engine 5 volumetric lighting, high contrast cinema grade",
        "voice_description": "The thé, giễu cợt, quỷ dị của ảo tưởng hallucination"
    },
    {
        "name": "Vạn Cổ Tàng Kinh Các",
        "entity_type": "location",
        "description": "Đại điện kinh thư tiên hiệp cổ kính nguy nga, hàng ngàn kệ gỗ đàn hương bay giữa mây ngàn, kinh thư thẻ tre phát sáng.",
        "image_prompt": "Cinematic establishing master plate of a grand ancient celestial library palace, towering carved sandalwood bookshelves floating on ethereal clouds, glowing parchment scrolls drifting in mid-air, soft golden god rays through misty lattice windows, Epic 3D Donghua aesthetic, Octane Render, 8K",
        "voice_description": None
    },
    {
        "name": "Lôi Trì Vector Thức Hải",
        "entity_type": "location",
        "description": "Biển ý thức lượng tử số phát sáng với các luồng vector ma trận vàng kim và xanh lam đan xen vô tận.",
        "image_prompt": "Cinematic establishing master plate of a vast ethereal vector sea realm, infinite glowing cyan and amber data particles suspended in cosmic darkness, luminous floating jade stones connected by radiant neural laser beams, cinematic wide angle, volumetric neon fog, Octane render 8K",
        "voice_description": None
    }
]


async def main():
    await init_db()
    print(f"[*] Updating Master Assets for Project: {PROJECT_ID}...")

    # Fetch existing characters
    existing = await crud.list_characters()
    existing_map = {c["name"].strip().lower(): c for c in existing}

    for asset in MASTER_ASSETS:
        key = asset["name"].strip().lower()
        if key in existing_map:
            char_id = existing_map[key]["id"]
            await crud.update_character(
                char_id,
                description=asset["description"],
                image_prompt=asset["image_prompt"],
                voice_description=asset["voice_description"],
                entity_type=asset["entity_type"]
            )
            print(f"  [UPDATED] {asset['name']} ({asset['entity_type']}) -> ID: {char_id}")
        else:
            char = await crud.create_character(
                name=asset["name"],
                entity_type=asset["entity_type"],
                description=asset["description"],
                image_prompt=asset["image_prompt"],
                voice_description=asset["voice_description"]
            )
            char_id = char["id"]
            print(f"  [CREATED] {asset['name']} ({asset['entity_type']}) -> ID: {char_id}")

        await crud.link_character_to_project(PROJECT_ID, char_id)

    await close_db()
    print("[OK] Master Assets updated and linked successfully!")


if __name__ == "__main__":
    asyncio.run(main())
