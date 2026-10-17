import json
import re
import shutil
import subprocess
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPT_FILE = REPO_ROOT / "prompts" / "MASTER_STORY_PROMPT.md"


def test_master_prompt_file_exists():
    assert PROMPT_FILE.exists(), f"Không tìm thấy file prompt tại {PROMPT_FILE}"
    assert PROMPT_FILE.stat().st_size > 0, "File prompt rỗng"


def extract_sample_json_from_prompt():
    content = PROMPT_FILE.read_text(encoding="utf-8")
    # Trích xuất khối json từ markdown block ```json ... ```
    match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", content)
    assert match is not None, "Không tìm thấy khối JSON mẫu ```json ... ``` trong MASTER_STORY_PROMPT.md"
    raw_json_str = match.group(1)
    data = json.loads(raw_json_str)
    return data


def test_master_prompt_schema_core_fields():
    job = extract_sample_json_from_prompt()

    # Kiểm tra các trường cốt lõi của VideoJob
    assert "jobId" in job and isinstance(job["jobId"], str) and len(job["jobId"]) > 0
    assert "title" in job and isinstance(job["title"], str) and len(job["title"]) > 0
    assert job.get("workshop") == "whiteboard", "Workshop bắt buộc phải là 'whiteboard'"
    assert job.get("archetype") == "storytelling", "Archetype bắt buộc phải là 'storytelling'"
    assert job.get("targetPlatform") == "youtube_long"

    # Kiểm tra canvas 16:9 1080p 30fps
    canvas = job.get("canvas", {})
    assert canvas.get("width") == 1920
    assert canvas.get("height") == 1080
    assert canvas.get("fps") == 30

    # Kiểm tra cấu hình voice
    voice = job.get("voice", {})
    assert voice.get("provider") == "edge-tts"
    assert voice.get("voiceId") == "vi-VN-NamMinhNeural"
    assert voice.get("rate") == "+25%", "Tốc độ đọc mặc định cho storytelling phải là +25%"


def test_master_prompt_metadata():
    job = extract_sample_json_from_prompt()
    metadata = job.get("metadata", {})
    assert isinstance(metadata, dict), "metadata phải là một object"
    assert "channel" in metadata
    
    # Kiểm tra characters và characters_voice
    characters = metadata.get("characters")
    assert isinstance(characters, list) and len(characters) >= 3, "metadata.characters phải có ít nhất 3 nhân vật"
    assert "Lâm Mặc" in characters
    assert "Người Kể Chuyện" in characters

    characters_voice = metadata.get("characters_voice")
    assert isinstance(characters_voice, dict) and len(characters_voice) >= 2, "metadata.characters_voice phải có cấu hình giọng"
    assert "lâm mặc" in characters_voice
    assert "triệu trưởng lão" in characters_voice


def test_master_prompt_15s_golden_hook_and_beats():
    job = extract_sample_json_from_prompt()
    beats = job.get("beats")
    assert isinstance(beats, list), "beats phải là danh sách"
    assert len(beats) >= 3, "Kịch bản mẫu phải có ít nhất 3 beats"

    # Beat 01: Hook Teaser
    beat_01 = beats[0]
    assert beat_01["id"] == "beat_01"
    assert beat_01["role"] == "hook_teaser"
    assert "hook" in beat_01["visual"]["badge"].lower() or "cao trào" in beat_01["visual"]["badge"].lower()

    # Beat 02: Hook Intro & CTA
    beat_02 = beats[1]
    assert beat_02["id"] == "beat_02"
    assert beat_02["role"] == "hook_intro"

    # Kiểm tra tất cả các beat
    for idx, beat in enumerate(beats):
        assert "id" in beat, f"Beat {idx} thiếu 'id'"
        assert "speaker" in beat and len(beat["speaker"].strip()) > 0, f"Beat {idx} thiếu 'speaker'"
        assert "rawText" in beat and len(beat["rawText"].strip()) > 0, f"Beat {idx} thiếu 'rawText'"
        assert "visual" in beat, f"Beat {idx} thiếu 'visual'"
        assert "sceneId" in beat["visual"], f"Beat {idx} thiếu 'visual.sceneId'"

        # Quy tắc tuyệt đối: rawText KHÔNG ĐƯỢC CHỨA TÊN VAI HAY DẤU HAI CHẤM XƯNG VAI
        raw_text = beat["rawText"]
        assert "Người Kể Chuyện:" not in raw_text, f"Beat {idx} chứa tiền tố 'Người Kể Chuyện:' trong rawText"
        assert "Lâm Mặc:" not in raw_text, f"Beat {idx} chứa tiền tố 'Lâm Mặc:' trong rawText"
        assert "Triệu Trưởng Lão:" not in raw_text, f"Beat {idx} chứa tiền tố 'Triệu Trưởng Lão:' trong rawText"
        
        # Regex kiểm tra không có prefix Tên: ở đầu câu
        assert not re.match(r"^[A-ZÀ-Ỹ][\w\s]{1,30}:", raw_text.strip()), (
            f"Beat {idx} ({beat['id']}) có vẻ chứa tiền tố tên xưng vai: '{raw_text[:30]}'"
        )


def test_master_prompt_zod_schema_validation():
    """Kiểm tra tính hợp lệ 100% bằng cách gọi trực tiếp Zod VideoJobSchema qua Node.js."""
    node_bin = shutil.which("node")
    if not node_bin:
        pytest.skip("Node.js không được cài đặt trên máy, bỏ qua bước Zod validation")

    job = extract_sample_json_from_prompt()
    job_str = json.dumps(job, ensure_ascii=False)

    node_script = f"""
    import('./core/schema/job.ts').then(({{ VideoJobSchema }}) => {{
        const sample = JSON.parse(process.argv[1]);
        VideoJobSchema.parse(sample);
        console.log('ZOD_OK');
    }}).catch(err => {{
        console.error(err);
        process.exit(1);
    }});
    """

    res = subprocess.run(
        [node_bin, "--experimental-strip-types", "-e", node_script, job_str],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    assert res.returncode == 0, f"Zod Schema validation thất bại:\nSTDERR: {res.stderr}\nSTDOUT: {res.stdout}"
    assert "ZOD_OK" in res.stdout
