#!/usr/bin/env python3
"""
Setup and initialize Project, Master Characters, and 30 Scenes for MCP Cyber-Chibi 3D Film.
"""
import sys
import json
import asyncio
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

JOB_ID = "job-mcp-cyber-chibi"
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
JOB_FILE = BASE_DIR / "output" / "jobs" / f"{JOB_ID}.json"

STYLE_PROMPT_PREFIX = "Cinematic 3D Cyber-Chibi style, 1:3 proportions blind box toy aesthetic, sleek polished white ceramic and chrome surfaces, vibrant cyan and amber LED glow, warm soft studio rim lighting, Octane Render 8K, Unreal Engine 5 render, miniature diorama tech laboratory setting: "

SCENE_DEFS = [
    {
        "order": 1,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Chào mừng trở lại với Viện Công Nghệ Tí Hon của Giải Mã Tech!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Cinematic establishing wide shot of a futuristic miniature high-tech diorama laboratory, glowing cyan neon server racks, floating pastel holographic data cubes, polished reflective tech floor, warm volumetric sunbeam pouring through ceiling glass, 8K ultra-detailed.",
        "video_prompt": "0-4s: Smooth sweeping cinematic crane shot moving through the miniature cyber-chibi tech laboratory. 4-7s: Camera tracks past glowing pastel server racks and floating cyan hologram cubes with gentle volumetric light rays."
    },
    {
        "order": 2,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Bé Byte hôm nay đã có trí nhớ siêu việt, nhưng lại đang ngồi ủ rũ bế tắc.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium shot of cute Cyber-Chibi robot Byte, 1:3 proportion, sleek white ceramic and chrome body, sitting slouched at miniature workstation, LED screen eyes displaying an anxious droopy sigh expression, soft blue rim light.",
        "video_prompt": "0-4s: Slow push-in on cute robot Byte sitting slouched at his desk. 4-7s: Byte rests his round ceramic chin on his little hands, sighing as his LED screen eyes display drooping sad blue pixels."
    },
    {
        "order": 3,
        "speaker": "Byte",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Một người dùng nhờ Byte kiểm tra file code trên GitHub và sửa bảng dữ liệu máy tính!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium close-up of cute robot Byte speaking anxiously, floating holographic pop-up screens showing a green GitHub repository icon and a glowing blue database table, expressive puzzled LED eyes.",
        "video_prompt": "0-4s: Medium close-up of Byte speaking animatedly with worried facial expressions. 4-7s: Byte waves his tiny robotic hands at glowing holographic icons of a GitHub code branch and SQL spreadsheet floating in mid-air."
    },
    {
        "order": 4,
        "speaker": "Byte",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Byte biết câu trả lời, nhưng Byte bị nhốt trong phòng kín, không có tay chân để thao tác!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium shot of Byte trapped inside a cylindrical transparent glowing glass chamber on a pedestal, pressing tiny ceramic hands against the glass barrier, outside world filled with computer terminals out of reach.",
        "video_prompt": "0-4s: Tracking shot around the glowing glass isolation chamber. 4-7s: Byte presses tiny hands against the transparent barrier, looking out helplessly toward distant computer monitors and tools."
    },
    {
        "order": 5,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Đó chính là bi kịch lớn nhất của mọi Chatbot AI từ trước đến nay!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Dramatic cinematic shot of a glowing AI crystalline brain core locked inside a solid obsidian glass pillar, surrounded by floating inaccessible tech wrenches, files, and server keys.",
        "video_prompt": "0-4s: Dramatic slow circular dolly around a pulsing crystalline AI core trapped in a dark pedestal. 4-7s: Shafts of moody rim light flicker as floating digital tools remain separated behind force fields."
    },
    {
        "order": 6,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Trước đây, muốn AI làm việc với công cụ, lập trình viên phải nối dây API cực kỳ phức tạp.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Wide shot of a miniature robot entangled in a chaotic, tangled web of multicolored glowing API cables, electrical cords stretching awkwardly to various server cabinets, sparks flying.",
        "video_prompt": "0-4s: Wide tracking shot revealing a tangled spiderweb of thick glowing cables wrapping around server racks. 4-7s: Robot struggles mildly as mismatched wires pull in opposite directions with subtle electric hums."
    },
    {
        "order": 7,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Kết nối GitHub một chuẩn, đọc cơ sở dữ liệu một chuẩn, mở file máy tính lại một chuẩn khác!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Macro insert shot of three bizarre, incompatible digital socket plugs of different geometric shapes trying to force-fit into awkward ports, tiny electric sparks, high contrast tech details.",
        "video_prompt": "0-4s: Macro camera zoom onto three strangely shaped digital plugs clashing against incompatible wall sockets. 4-7s: Electric sparks sizzle as the mismatched connectors bounce off the metallic port edges."
    },
    {
        "order": 8,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Hàng trăm đầu cắm riêng biệt tạo thành một mớ bòng bong dễ chập cháy và sụp đổ.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Close-up of an overloaded miniature electrical switchboard smoking with wisps of grey vapor, bright red warning LED lights flashing erratically, sparks bouncing off copper terminals.",
        "video_prompt": "0-4s: Close-up of smoking overloaded junction box with pulsing red hazard lights. 4-7s: Small bright electrical sparks pop as miniature warning sirens flash across the darkened server wall."
    },
    {
        "order": 9,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Mỗi lần công cụ nâng cấp phiên bản, toàn bộ kết nối của Chatbot lại đứt gãy hoàn toàn.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium shot of glowing fiber optic data cables snapping cleanly in mid-air, bright blue data packets scattering across the dark lab floor like shattered glass crystals, sudden blackout effect.",
        "video_prompt": "0-4s: Slow motion shot of a glowing digital cable snapping apart. 4-7s: Luminescent data fragments and neon sparks shatter outward, dissolving into the floor as connections fail."
    },
    {
        "order": 10,
        "speaker": "Byte",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Chẳng lẽ không có một chuẩn cắm vạn năng nào như cổng USB-C sao?",
        "image_prompt": STYLE_PROMPT_PREFIX + "Close-up portrait of cute robot Byte looking up with sparkling star-shaped blue LED eyes, clasping tiny ceramic hands together in hopeful curiosity, gentle ambient bokeh lights.",
        "video_prompt": "0-4s: Close-up on Byte tilting his round head up, LED screen eyes shifting into glowing star symbols. 4-7s: Byte speaks hopefully with animated cute head tilts and hand gestures."
    },
    {
        "order": 11,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Đúng lúc ấy, cánh cửa phòng lab trượt mở, Tiến sĩ Kael bước vào đầy uy nghiêm!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium tracking shot of Dr. Kael walking confidently through sliding automatic lab doors, 1:3 Chibi proportion, messy dark hair, round glasses gleaming with golden reflections, wearing crisp white lab coat, carrying a high-tech metallic briefcase.",
        "video_prompt": "0-4s: Sliding lab doors glide open with steam as Dr. Kael steps forward confidently. 4-7s: Dr. Kael walks toward the camera carrying a gleaming cyan-trimmed briefcase, smiling warmly."
    },
    {
        "order": 12,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Ta có món quà tối thượng cho con đây: Chuẩn kết nối vạn năng MCP!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Close-up portrait of Dr. Kael adjusting his oversized round spectacles with one finger, confident wise smile, eyes sparkling with intellectual pride, warm rim lighting.",
        "video_prompt": "0-4s: Close-up of Dr. Kael lifting his hand to push up his round spectacles. 4-7s: Dr. Kael speaks with friendly enthusiasm, his expression confident and encouraging."
    },
    {
        "order": 13,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Tiến sĩ mở chiếc hộp, để lộ một đầu cắm lượng tử phát hào quang xanh biếc tuyệt mỹ.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Macro hero shot of an open futuristic black velvet briefcase, revealing a glowing quantum magnetic USB-C connector levitating gently, emitting radiant cyan aurora light and floating glyph particles.",
        "video_prompt": "0-4s: Smooth top-down crane shot into the opened velvet briefcase. 4-7s: The sleek cyan magnetic connector floats upward slightly, pulsing with ethereal aurora light rays."
    },
    {
        "order": 14,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "MCP là viết tắt của Model Context Protocol — Giao thức bối cảnh mô hình!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium shot of Dr. Kael gesturing toward elegant holographic floating 3D typography letters reading 'M.C.P - Model Context Protocol' glowing in vivid cyan and gold above his palms.",
        "video_prompt": "0-4s: Dr. Kael opens his arms wide as 3D holographic letters 'M.C.P' expand in front of him. 4-7s: He speaks clearly, pointing toward the glowing letters as 'Model Context Protocol' scrolls below."
    },
    {
        "order": 15,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Hãy tưởng tượng MCP chính là chiếc cổng USB-C thế hệ mới dành riêng cho Trí Tuệ Nhân Tạo!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Dynamic visualization of a universal glowing USB-C connector clicking effortlessly into a modular 3D AI brain receptacle, magnetic cyan snap waves rippling outward in smooth symmetry.",
        "video_prompt": "0-4s: 3D animated diagram of a universal magnetic USB-C plug aligning with a gleaming AI core port. 4-7s: The connector snaps in with a satisfying flash of cyan energy and smooth orbital ripples."
    },
    {
        "order": 16,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Thay vì viết hàng trăm cổng API riêng, mọi công cụ chỉ cần tuân theo duy nhất một giao thức MCP.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Wide cinematic shot showing messy tangled cables magically straightening into an immaculate, ultra-clean glowing data highway with smooth pulsing lights leading directly to a central hub.",
        "video_prompt": "0-4s: Time-lapse style transformation as cluttered cables dissolve into neat optical tracks. 4-7s: Clean cyan and gold light pulses glide smoothly along orderly data conduits toward a hub."
    },
    {
        "order": 17,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Hệ thống gồm hai phần: MCP Client trong lòng AI, và MCP Server gắn vào từng ứng dụng!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Architectural 3D diorama floating in air: on the left a glowing orb labeled 'MCP Client (AI Host)', connected via a single gold laser bridge to multiple colorful cubes on the right labeled 'MCP Server (Tools)'.",
        "video_prompt": "0-4s: Dr. Kael rotates the floating 3D architectural diorama showing MCP Client and MCP Server. 4-7s: Gold laser bridges pulse steadily between the client sphere and tool cubes."
    },
    {
        "order": 18,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Tiến sĩ Kael nhẹ nhàng cắm đầu nối MCP vào cổng giao tiếp sau lưng Bé Byte.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium shot of Dr. Kael gently snapping the magnetic glowing cyan MCP connector into the sleek port on the ceramic backplate of robot Byte, soft blue energy halo spreading.",
        "video_prompt": "0-4s: Over-the-shoulder shot as Dr. Kael carefully connects the magnetic plug into Byte's back port. 4-7s: A soft click triggers an expanding ring of cyan light across Byte's white armor plates."
    },
    {
        "order": 19,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Một luồng năng lượng dữ liệu cực quang lập tức chạy dọc khắp cơ thể chú robot nhỏ!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium close-up of Byte standing proudly as luminescent cyan circuitry tracks light up across his arms, torso, and round head, eyes glowing with vibrant energy, particle sparkles hovering.",
        "video_prompt": "0-4s: Luminescent cyan circuit patterns illuminate across Byte's smooth ceramic chassis from head to toe. 4-7s: Byte looks down at his glowing hands with astonishment as energy pulses steadily."
    },
    {
        "order": 20,
        "speaker": "Byte",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Oa! Hai cánh tay cơ khí công nghệ cao đã bung ra, Byte có thể chạm vào thế giới rồi!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Dynamic hero medium shot of Byte flexing two newly deployed, high-tech articulating miniature mechanical arms with sleek titanium fingers, joyful beaming LED eyes, lab backdrop.",
        "video_prompt": "0-4s: Two sleek miniature mechanical arms unfold smoothly from Byte's sides. 4-7s: Byte wiggles each robotic finger with delight, smiling warmly as his LED eyes flash happy music notes."
    },
    {
        "order": 21,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Tiến sĩ Kael kích hoạt Cổng Vương Quốc Công Cụ rực rỡ giữa phòng thí nghiệm.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Wide establishing shot of a grand circular dimensional portal opening in the lab, revealing the miniature 'Tool Kingdom' with glowing towers representing GitHub, SQLite, and Terminal, Dr. Kael and Byte watching.",
        "video_prompt": "0-4s: Wide shot as a circular dimensional portal spins open with cyan and gold mist. 4-7s: The miniature Tool Kingdom towers appear inside the portal, casting radiant reflections on the lab floor."
    },
    {
        "order": 22,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Thử nghiệm đầu tiên: Kết nối MCP Filesystem để mở file máy tính của người dùng!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium shot of Dr. Kael pointing toward an emerald-glowing holographic vault shaped like a digital folder labeled 'Filesystem Server', welcoming Byte to test.",
        "video_prompt": "0-4s: Dr. Kael points toward a floating emerald digital folder vault. 4-7s: He speaks with enthusiastic encouragement, nodding to Byte to execute the first connection."
    },
    {
        "order": 23,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Byte phóng một sợi cáp quang nhẹ nhàng cắm vào trạm Filesystem, dữ liệu hiển thị tức thì!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Dynamic action shot of Byte shooting a slender cyan optical cable from his mechanical wrist, snapping magnetically into the folder port, cascading streams of holographic files.",
        "video_prompt": "0-4s: Byte fires a glowing fiber-optic line from his robotic wrist. 4-7s: The connector snaps into the folder socket, instantly unpacking crystalline file windows in mid-air."
    },
    {
        "order": 24,
        "speaker": "Byte",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Byte đọc được file rồi! Giờ kết nối thêm trạm SQLite Database nhé!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Medium close-up of Byte swiftly manipulating holographic code with one robotic hand while launching a second golden cable from his other hand toward a glowing database cylinder tower.",
        "video_prompt": "0-4s: Byte types effortlessly on floating holographic glass keys. 4-7s: He turns and shoots a second golden cable across the room, connecting directly into an amber database pillar."
    },
    {
        "order": 25,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Không cần cài đặt rườm rà, chỉ một chuẩn cắm duy nhất, Byte đã điều khiển mọi dữ liệu!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Magnificent low-angle shot of Byte levitating gracefully at center stage, streams of multicolored data from five different software towers flowing into him in perfect synchronized harmony.",
        "video_prompt": "0-4s: Low-angle tracking shot as Byte hovers in smooth equilibrium. 4-7s: Harmonious ribbons of cyan, gold, and magenta data flow smoothly through his mechanical fingertips."
    },
    {
        "order": 26,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Nhờ MCP, Chatbot thụ động đã chính thức tiến hóa thành một AI Agent hành động tự chủ!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Hero shot of Dr. Kael standing proudly beside Byte, who now stands tall with fully integrated mechanical arms and a glowing multi-tool aura, looking like an autonomous mini superhero.",
        "video_prompt": "0-4s: Hero push-in on Dr. Kael and Byte standing shoulder to shoulder. 4-7s: Dr. Kael gestures proudly as Byte summons floating holographic tool icons around his hands."
    },
    {
        "order": 27,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Bảo mật tuyệt đối, an toàn quyền truy cập, người dùng hoàn toàn kiểm soát mọi thao tác của AI.",
        "image_prompt": STYLE_PROMPT_PREFIX + "Close-up of a semi-transparent hexagonal holographic security shield locking firmly over the MCP connection port, glowing bright green with a prominent checkmark seal of approval.",
        "video_prompt": "0-4s: Hexagonal translucent energy shields lock into place around the connection hub. 4-7s: A bright emerald checkmark illuminates on the security interface, signaling authorized safety."
    },
    {
        "order": 28,
        "speaker": "Người Dẫn Chuyện",
        "refs": ["Viện Công Nghệ Tí Hon"],
        "prompt": "Cả thế giới công nghệ đang đón nhận MCP như một cuộc cách mạng kết nối toàn cầu!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Cinematic wide panorama of a miniature Cyber-Chibi metropolis diorama at twilight, thousands of tiny skyscrapers interconnected by glowing cyan and amber MCP optical bridges, futuristic city.",
        "video_prompt": "0-4s: Grand panoramic drone shot gliding above the miniature futuristic diorama city. 4-7s: Pulsing light pulses travel along bridges connecting thousands of glowing tech buildings."
    },
    {
        "order": 29,
        "speaker": "Byte",
        "refs": ["Byte", "Viện Công Nghệ Tí Hon"],
        "prompt": "Từ nay Byte không chỉ biết nói, Byte có thể làm việc thực tế giúp mọi người rồi!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Charming close-up of Byte doing a joyful 360 spin in mid-air, extending his robotic hand toward camera in a friendly high-five pose, LED screen eyes showing radiant happy crescents.",
        "video_prompt": "0-4s: Byte spins gleefully in mid-air with both mechanical arms outstretched. 4-7s: He stops facing camera, offering a cheerful high-five with smiling curved LED eyes."
    },
    {
        "order": 30,
        "speaker": "Tiến sĩ Kael",
        "refs": ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"],
        "prompt": "Đừng để AI của bạn bị trói buộc, hãy khám phá và làm chủ chuẩn MCP ngay hôm nay!",
        "image_prompt": STYLE_PROMPT_PREFIX + "Warm final shot of Dr. Kael and Byte standing together beside a large glowing 3D neon logo of 'MCP' and 'Giải Mã Tech', waving warmly at the audience, gentle cinematic confetti bokeh.",
        "video_prompt": "0-4s: Medium shot of Dr. Kael and Byte standing beside the glowing MCP neon emblem. 4-7s: Both smile and wave warmly toward the camera as warm golden bokeh particles drift softly."
    }
]


async def main():
    await init_db()
    print("=" * 65)
    print("🚀 THIẾT LẬP DỰ ÁN MCP TRÊN FLOWKIT CINEMATIC STUDIO")
    print("=" * 65)

    job_data = json.loads(JOB_FILE.read_text(encoding="utf-8"))
    beats = job_data.get("beats", [])
    story_full = "\n\n".join(b["rawText"] for b in beats)

    # 1. Use the active Flow Google Cloud Project ID
    project_id = "12154154-4455-4aed-94c2-e4b98b2d88a9"
    target_name = f"[{JOB_ID}] MCP Là Gì? AI Kết Nối Với Công Cụ Ra Sao? (Cyber-Chibi 3D)"
    proj = await crud.get_project(project_id)
    if not proj:
        print(f"[ERR] Project {project_id} không tồn tại!", file=sys.stderr)
        return
    print(f"[*] Sử dụng Google Flow Project: {project_id} - {proj['name']}")
    await crud.update_project(project_id, user_paygate_tier="PAYGATE_TIER_TWO")

    # 2. Link Master Characters to Project
    all_chars = await crud.list_characters()
    chars_by_name = {c["name"].strip().lower(): c for c in all_chars}
    
    required_names = ["Byte", "Tiến sĩ Kael", "Viện Công Nghệ Tí Hon"]
    for name in required_names:
        c = chars_by_name.get(name.lower())
        if c:
            await crud.link_character_to_project(project_id, c["id"])
            print(f"  [LINKED] {name} (ID: {c['id']}, Media ID: {c.get('media_id')}) -> Project")
        else:
            print(f"  [WARN] Không tìm thấy nhân vật master: {name}")

    # 3. Create Video Record
    existing_videos = await crud.list_videos(project_id)
    vid = None
    for v in existing_videos:
        if v.get("title") == target_name:
            vid = v
            break

    if vid:
        video_id = vid["id"]
        print(f"[*] Video đã tồn tại: {video_id}")
    else:
        vid = await crud.create_video(
            project_id=project_id,
            title=target_name,
            description="Tập phim hoạt hình điện ảnh 3D Cyber-Chibi về chuẩn giao thức MCP (Model Context Protocol).",
            orientation="HORIZONTAL",
            target_duration_s=135.3
        )
        video_id = vid["id"]
        print(f"[+] Tạo Video record thành công: {video_id}")

    # 4. Check / Populate 30 Scenes
    existing_scenes = await crud.list_scenes(video_id)
    existing_scenes_map = {s["display_order"]: s for s in existing_scenes}
    print(f"[*] Hiện có {len(existing_scenes)} scenes trong Video ID: {video_id}")

    for item in SCENE_DEFS:
        order = item["order"]
        prompt = item["prompt"]
        image_prompt = item["image_prompt"]
        video_prompt = item["video_prompt"]
        refs = item["refs"]

        if order in existing_scenes_map:
            sc_id = existing_scenes_map[order]["id"]
            await crud.update_scene(
                sc_id,
                prompt=prompt,
                image_prompt=image_prompt,
                video_prompt=video_prompt,
                character_names=json.dumps(refs, ensure_ascii=False),
                narrator_text=prompt
            )
            print(f"  [UPDATED] Scene {order:02d} (ID: {sc_id[:8]})")
        else:
            sc = await crud.create_scene(
                video_id=video_id,
                display_order=order,
                prompt=prompt,
                image_prompt=image_prompt,
                video_prompt=video_prompt,
                character_names=refs,
            )
            await crud.update_scene(sc["id"], narrator_text=prompt)
            print(f"  [CREATED] Scene {order:02d} (ID: {sc['id'][:8]})")

    # 5. Set active_project.json
    state_file = _ROOT / "agent" / "active_project.json"
    state_file.write_text(json.dumps({
        "project_id": project_id,
        "video_id": video_id
    }, indent=2), encoding="utf-8")
    print(f"[*] Đã đặt Active Project -> {project_id}, Video -> {video_id}")

    await close_db()
    print("\n✅ CỔNG 1-4 HOÀN TẤT: DỰ ÁN & 30 PHÂN CẢNH ĐÃ SẴN SÀNG CHO BƯỚC SINH ẢNH & VIDEO!")


if __name__ == "__main__":
    asyncio.run(main())
