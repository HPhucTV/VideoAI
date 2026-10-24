#!/usr/bin/env python3
"""
OmniVideo Studio — Edge-TTS Vietnamese Neural Voice Service
High-quality, native Vietnamese voice synthesis with per-character modulation.
All output resampled to 48,000 Hz Stereo 192k AAC/MP3.
"""
import logging
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("EdgeTTSVietnam")

def _find_python_tts() -> str:
    candidates = [
        Path(r"c:\Users\tranh\Documents\Duy\VideoAI\workshops\workshop-whiteboard\.venv\Scripts\python.exe"),
        Path(__file__).resolve().parents[3] / "workshop-whiteboard" / ".venv" / "Scripts" / "python.exe",
        Path(sys.executable),
    ]
    for c in candidates:
        if c.exists():
            return str(c.resolve())
    return "python"

PYTHON_TTS = _find_python_tts()

# Accurate character voice acoustic presets for authentic Donghua dubbing
CHARACTER_PRESETS = {
    "lâm diệp": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "-4Hz",
        "rate": "-3%",
        "desc": "Trầm tĩnh, uy nghiêm, sắc lạnh, ngạo cốt Kiếm Tôn chư thiên"
    },
    "nguyệt thiền nhi": {
        "voice": "vi-VN-HoaiMyNeural",
        "pitch": "+1Hz",
        "rate": "-2%",
        "desc": "Nhu mì, trong trẻo, chân thành, nghẹn ngào tình cảm"
    },
    "lâm hạo": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+3Hz",
        "rate": "+8%",
        "desc": "Chói gắt, kiêu căng, đay nghiến của thiếu gia hống hách"
    },
    "tử dao tiên tử": {
        "voice": "vi-VN-HoaiMyNeural",
        "pitch": "-1Hz",
        "rate": "+0%",
        "desc": "Lạnh lùng, đoạn tuyệt, ngụy quân tử tiên môn"
    },
    "gia đinh": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+2Hz",
        "rate": "+10%",
        "desc": "Nịnh bợ, giễu cợt, giậu đổ bìm leo"
    },
    "tiểu linh": {
        "voice": "vi-VN-HoaiMyNeural",
        "pitch": "+1Hz",
        "rate": "-2%",
        "desc": "Trong trẻo, thanh tao, thông minh, tinh nghịch của nữ Khí Linh"
    },
    "đạo sư": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "-4Hz",
        "rate": "-3%",
        "desc": "Trầm ấm, uy nghiêm, thông thái của bậc tôn sư công nghệ"
    },
    "tâm ma": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+3Hz",
        "rate": "+8%",
        "desc": "The thé, giễu cợt, quỷ dị của ảo tưởng hallucination"
    },
    "người kể chuyện": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+0Hz",
        "rate": "+0%",
        "desc": "Cổ phong, hào sảng, bi tráng, tạo chiều sâu sử thi"
    },
    "người dẫn chuyện": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+0Hz",
        "rate": "+0%",
        "desc": "Cổ phong, hào sảng, bi tráng, tạo chiều sâu sử thi"
    },
    "byte": {
        "voice": "vi-VN-HoaiMyNeural",
        "pitch": "+0Hz",
        "rate": "+4%",
        "desc": "Trong trẻo, dễ thương, tinh nghịch của bé Chatbot Chibi 1:3"
    },
    "tiến sĩ kael": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+0Hz",
        "rate": "+0%",
        "desc": "Trầm ấm, uyên bác, thông thái, tạo sự tin cậy tuyệt đối"
    },
    "bọ ảo giác": {
        "voice": "vi-VN-NamMinhNeural",
        "pitch": "+7Hz",
        "rate": "+12%",
        "desc": "The thé, ranh mãnh, giễu cợt của quái vật ảo giác AI"
    }
}

DEFAULT_PRESET = CHARACTER_PRESETS["người kể chuyện"]


def synthesize_edge_tts(
    text: str,
    output_path: Path | str,
    speaker_name: str = "người kể chuyện",
    speed_factor: float = 1.0,
    retries: int = 4,
    retry_delay: float = 3.0
) -> Path:
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    temp_raw = out_p.parent / f"temp_{out_p.stem}.mp3"

    key = speaker_name.strip().lower()
    preset = CHARACTER_PRESETS.get(key, DEFAULT_PRESET)

    # Calculate effective rate based on speed_factor (e.g. 1.25x)
    base_rate_str = preset["rate"].rstrip("%")
    base_rate_val = float(base_rate_str) if base_rate_str else 0.0
    effective_rate_val = (1.0 + base_rate_val / 100.0) * speed_factor - 1.0
    rate_pct = int(round(effective_rate_val * 100))
    rate_flag = f"+{rate_pct}%" if rate_pct >= 0 else f"{rate_pct}%"

    logger.info("Synthesizing Edge-TTS for [%s] (voice=%s, pitch=%s, rate=%s [x%.2f]): %s...",
                speaker_name, preset["voice"], preset["pitch"], rate_flag, speed_factor, text[:35])

    cmd_tts = [
        PYTHON_TTS, "-m", "edge_tts",
        "--text", text,
        "--voice", preset["voice"],
        f"--pitch={preset['pitch']}",
        f"--rate={rate_flag}",
        "--write-media", str(temp_raw)
    ]
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            subprocess.run(cmd_tts, check=True)
            if temp_raw.exists() and temp_raw.stat().st_size > 1000:
                break
        except Exception as e:
            last_err = e
            logger.warning("Edge-TTS attempt %d/%d for [%s] failed: %s. Retrying in %.1fs...",
                           attempt, retries, speaker_name, e, retry_delay * attempt)
            time.sleep(retry_delay * attempt)
    else:
        raise RuntimeError(f"Edge-TTS failed after {retries} attempts: {last_err}")

    # Studio normalization: 48,000 Hz Stereo 192k
    cmd_ff = [
        "ffmpeg", "-y",
        "-i", str(temp_raw),
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        str(out_p)
    ]
    subprocess.run(cmd_ff, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_raw.unlink(missing_ok=True)

    logger.info("Successfully synthesized & resampled: %s (48kHz Stereo)", out_p.name)
    return out_p


if __name__ == "__main__":
    test_out = Path("output/test_edge_tts_vietnam.mp3")
    synthesize_edge_tts("Thiên Đạo bất công, Cửu U Kiếm Tôn ta vĩnh viễn bất diệt!", test_out, speaker_name="Lâm Diệp")
    print("Test passed! Saved to:", test_out)
