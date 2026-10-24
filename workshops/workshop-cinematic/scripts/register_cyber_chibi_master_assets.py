#!/usr/bin/env python3
"""
Populate and refine Character & Location Master Entities for Cyber-Chibi RAG Film.
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

PROJECT_ID = "063c4da5-e5ad-4fd2-8766-8d7bdbcc55b8"

MASTER_ASSETS = [
    {
        "name": "Byte",
        "entity_type": "character",
        "description": "Robot Chibi trợ lý ảo 1:3 tròn trĩnh đáng yêu, vỏ kim loại titan và gốm trắng bóng, mắt LED xanh dương biểu cảm thông minh, đeo tai nghe tổng đài viên tí hon.",
        "image_prompt": "Cinematic 3D Cyber-Chibi character portrait of a cute futuristic toy robot named Byte, proportion 1:3 blind box aesthetic, sleek polished white ceramic and chrome body, adorable expressive blue glowing LED eyes, miniature glowing communication headset, warm studio rim lighting, Octane Render, 8K ultra-detailed, Unreal Engine 5 render",
        "voice_description": "Trong trẻo, dễ thương, tinh nghịch của bé Chatbot Chibi"
    },
    {
        "name": "Tiến sĩ Kael",
        "entity_type": "character",
        "description": "Nhà khoa học Chibi 1:3 thông thái, tóc xù dễ thương, đeo kính tròn to bự, áo lab trắng công nghệ kết hợp mạch LED phát sáng.",
        "image_prompt": "Cinematic 3D Cyber-Chibi character portrait of Dr. Kael, a cute wise scientist with 1:3 proportion, fluffy messy dark hair, oversized round glasses reflecting amber data particles, wearing a clean miniature white lab coat over a sleek glowing cyan tech suit, cheerful confident smile, Octane Render, 8K hyper-detailed",
        "voice_description": "Trầm ấm, uyên bác, thông thái, tạo sự tin cậy"
    },
    {
        "name": "Bọ Ảo Giác",
        "entity_type": "character",
        "description": "Bé virus Chibi tí hon màu tím rực rỡ, sừng phát sáng, nụ cười tinh quái nhưng hài hước, đại diện cho lỗi ảo giác của LLM.",
        "image_prompt": "Cinematic 3D Cyber-Chibi character portrait of Bug Glitchy, a cute mischievous little purple virus monster, shiny vinyl toy figurine finish, glowing violet horns, quirky smirk with tiny fangs, floating playful glitch pixels around it, Octane Render, 8K, cinema grade",
        "voice_description": "The thé, ranh mãnh, tinh quái của virus ảo giác"
    },
    {
        "name": "Viện Công Nghệ Tí Hon",
        "entity_type": "location",
        "description": "Phòng thí nghiệm công nghệ cao thu nhỏ tí hon, các dãy tủ server phát sáng pastel, màn hình nổi hologram lung linh.",
        "image_prompt": "Cinematic establishing master plate of a futuristic miniature Cyber-Chibi high-tech laboratory diorama, glowing pastel neon server racks, floating soft cyan and amber hologram screens, glossy reflective tech floor, warm volumetric rim light, Octane Render 8K, Unreal Engine 5 aesthetic",
        "voice_description": None
    },
    {
        "name": "Kho Lưu Trữ Dữ Liệu Vector",
        "entity_type": "location",
        "description": "Thế giới số lộng lẫy với hàng ngàn khối pha lê thủy tinh dữ liệu lơ lửng, các luồng ánh sáng laser và hạt vector đan xen.",
        "image_prompt": "Cinematic establishing master plate of a vast ethereal Cyber-Chibi Quantum Vector Vault, infinite glowing floating amber and cyan translucent data crystal cubes in a miniature cosmic void, radiant neural laser connection beams, soft volumetric fog, Octane render 8K",
        "voice_description": None
    }
]


async def main():
    await init_db()
    print(f"[*] Updating Master Assets for Cyber-Chibi Project: {PROJECT_ID}...")

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
