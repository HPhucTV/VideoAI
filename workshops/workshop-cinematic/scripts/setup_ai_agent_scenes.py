#!/usr/bin/env python3
"""
Setup and enrich the 12 scenes for "AI Agent Là Gì? Giải Thích Trong 1 Phút"
with cinematic visual prompts, video prompts, and character references.
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

VIDEO_ID = "21b50be7-cbb9-4077-ab7f-c568ab304971"
PROJECT_ID = "4d3d8226-e74e-4da6-9630-021236da4820"
BYTE_CHAR_ID = "9f871770-b24f-427a-b561-96d26b3ff0c3"

SCENE_CONFIGS = [
    {
        "order": 1,
        "title": "Cảnh 01: Giới thiệu AI hiện nay - Nói nhiều làm ít",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic wide shot establishing high-tech miniature Cyber-Chibi laboratory diorama, cute 3D robot Byte entering slowly, warm ambient lighting, glowing pastel server racks, cute glowing monitor screen displaying floating text cursor, Octane Render 8K, Unreal Engine 5 aesthetic.",
        "video_prompt": "Cinematic slow dolly in shot, cute Cyber-Chibi robot Byte entering high-tech miniature laboratory diorama, warm ambient lighting, pointing gently at glowing monitor displaying typing text, subtle blinking LED eyes, 4K composition.",
        "duration": 5.0
    },
    {
        "order": 2,
        "title": "Cảnh 02: Chatbot truyền thống bất động",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic medium over-the-shoulder shot in miniature tech lab, Cyber-Chibi robot Byte shaking head sympathetically beside an adorable frozen retro computer mascot trapped inside a glowing glass bubble, warm studio rim light, Octane Render 8K.",
        "video_prompt": "Medium OTS shot, cute Cyber-Chibi Byte gently shaking head beside a frozen retro mascot inside glowing glass bubble, subtle expressive gestures, soft volumetric tech haze, cinematic lighting.",
        "duration": 5.0
    },
    {
        "order": 3,
        "title": "Cảnh 03: Byte giới thiệu AI Agent",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic medium close-up hero shot, cute Cyber-Chibi robot Byte smiling proudly with glowing expressive LED eyes, mini rocket pack emitting soft cyan neon glow, laboratory background with floating light particles, Octane Render 8K.",
        "video_prompt": "Medium close-up zoom in punch, Cyber-Chibi Byte smiling proudly as mini jetpack glows with cyan neon energy, speaking with lively mouth movement and expressive blue LED eyes, dynamic camera movement.",
        "duration": 6.0
    },
    {
        "order": 4,
        "title": "Cảnh 04: AI Agent - Hệ thống tự chủ lập kế hoạch",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic low-angle dramatic shot, cute Cyber-Chibi robot Byte hovering gracefully, intricate glowing golden holographic flowchart and geometric blueprints unfurling in midair, Octane Render 8K.",
        "video_prompt": "Low-angle dramatic dolly in and tilt up, Cyber-Chibi Byte hovering smoothly in laboratory, holographic interface unfurling around him in glowing gold lines and geometric rings, speaking with enthusiasm.",
        "duration": 5.0
    },
    {
        "order": 5,
        "title": "Cảnh 05: Bộ não suy luận & chia nhỏ nhiệm vụ",
        "character_names": ["Byte", "Kho Lưu Trữ Dữ Liệu Vector"],
        "image_prompt": "Cinematic close-up shot, cute Cyber-Chibi robot Byte cradling a glowing translucent purple neural network sphere, golden branched task cards floating neatly around, ethereal quantum cosmos background, Octane Render 8K.",
        "video_prompt": "Close-up dolly in shot, Byte holding glowing purple holographic brain orb while golden task node cards float and connect in air, glowing micro-circuits, gentle eye blink and mouth movement.",
        "duration": 5.0
    },
    {
        "order": 6,
        "title": "Cảnh 06: Bộ nhớ dài hạn không quên ngữ cảnh",
        "character_names": ["Byte", "Kho Lưu Trữ Dữ Liệu Vector"],
        "image_prompt": "Cinematic shot in ethereal Vector Vault, cute Cyber-Chibi robot Byte standing amidst spiraling translucent cyan and amber memory crystal cubes, radiant laser data streams connecting overhead, Octane Render 8K.",
        "video_prompt": "Smooth 180-degree orbit camera, floating blue crystal memory data stream swirling gently around Cyber-Chibi Byte, volumetric rim lights, subtle head turn and curious intelligent expression.",
        "duration": 5.0
    },
    {
        "order": 7,
        "title": "Cảnh 07: Công cụ tương tác máy tính",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic dynamic shot, cute Cyber-Chibi robot Byte typing fast on floating holographic keyboard, 3D luminous app icons orbiting: miniature web browser, command terminal, email envelope, Octane Render 8K.",
        "video_prompt": "Fast zoom in punch, Byte's cute metallic hands tapping holographic keyboard, glowing tool icons expanding: web browser, terminal, mail envelope, cheerful energetic expression.",
        "duration": 5.0
    },
    {
        "order": 8,
        "title": "Cảnh 08: Đặt vé máy bay và lịch trình tự động",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic high-angle shot focusing on miniature laptop diorama, glowing holographic airplane trajectory flying between miniature 3D globe cities, calendar booking confirmation checkmarks appearing in green, Octane Render 8K.",
        "video_prompt": "High-angle tilt down, miniature laptop screen showing automated workflow: miniature 3D airplane flying across glowing globe, comparing flight prices, calendar updating with green checkmarks.",
        "duration": 6.0
    },
    {
        "order": 9,
        "title": "Cảnh 09: Người dùng thảnh thơi uống cà phê",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic medium shot, cute Cyber-Chibi robot Byte relaxing peacefully on tiny designer armchair holding steaming miniature espresso cup, glowing task progress bar showing 100% completed in background, warm afternoon sunbeam lighting, Octane Render 8K.",
        "video_prompt": "Medium cinematic shot, Cyber-Chibi Byte relaxing with tiny steaming coffee mug on clean diorama desk, satisfied smiling facial expression, steam rising softly, camera holding steady.",
        "duration": 5.0
    },
    {
        "order": 10,
        "title": "Cảnh 10: Kỷ nguyên AI làm việc thực sự",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic dramatic low-angle shot, cute Cyber-Chibi robot Byte standing proudly on high-tech pedestal, panoramic laboratory window revealing futuristic glowing sunrise horizon, golden light beams, Octane Render 8K.",
        "video_prompt": "Dramatic tilt up from diorama floor, Byte standing tall on glowing laboratory platform, inspiring sunrise lighting pouring through panoramic window, majestic cinematic atmosphere.",
        "duration": 5.0
    },
    {
        "order": 11,
        "title": "Cảnh 11: Bạn đã sẵn sàng sở hữu AI Agent?",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic extreme close-up hero shot of cute Cyber-Chibi robot Byte, playful wink, big expressive glowing LED eyes, glossy ceramic textures, soft turquoise and magenta studio lighting, Octane Render 8K.",
        "video_prompt": "Extreme close-up hero shot, Cyber-Chibi Byte winking playfully, subtle lip sync movement speaking directly to camera, studio rim lights, adorable charming head tilt.",
        "duration": 5.0
    },
    {
        "order": 12,
        "title": "Cảnh 12: Đón đầu làn sóng tự động hóa",
        "character_names": ["Byte", "Viện Công Nghệ Tí Hon"],
        "image_prompt": "Cinematic wide slow dolly out shot, miniature high-tech diorama laboratory fully illuminated, floating holographic subscribe button and bell icon sparkling with golden bokeh, Octane Render 8K.",
        "video_prompt": "Wide slow dolly out crane shot, laboratory illuminated with festive tech glow, glowing follow banner and bell icon floating gently, smooth cinematic finish.",
        "duration": 5.0
    }
]

async def main():
    await init_db()
    scenes = await crud.list_scenes(VIDEO_ID)
    print(f"[*] Found {len(scenes)} scenes for Video ID: {VIDEO_ID}")
    scenes_by_order = {s["display_order"]: s for s in scenes}

    for cfg in SCENE_CONFIGS:
        order = cfg["order"]
        scene = scenes_by_order.get(order)
        if not scene:
            print(f"[!] Warning: Scene {order} not found")
            continue
        sid = scene["id"]
        updates = {
            "title": cfg["title"],
            "image_prompt": cfg["image_prompt"],
            "video_prompt": cfg["video_prompt"],
            "character_names": json.dumps(cfg["character_names"], ensure_ascii=False),
            "character_id": BYTE_CHAR_ID,
            "duration": cfg["duration"]
        }
        await crud.update_scene(sid, **updates)
        print(f"  [OK] Updated Scene {order:02d} ({sid[:8]}): {cfg['title']}")

    await close_db()
    print("✅ All 12 scenes successfully enriched with cinematic prompts!")

if __name__ == "__main__":
    asyncio.run(main())
