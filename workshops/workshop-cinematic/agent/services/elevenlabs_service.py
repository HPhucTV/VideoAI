#!/usr/bin/env python3
"""
OmniVideo Studio — ElevenLabs Multi-Character Voice Service
Handles voice assignment, synthesis via ElevenLabs Multilingual v2,
and audio normalization (48000 Hz, Stereo).
"""
import json
import logging
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ElevenLabsTTS")

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_ee0c2431cda373f205eaeb5eaa07487f7a625ae00596ce69")

# Map characters to ElevenLabs Voice IDs (all premade voices verified on Free Tier)
CHARACTER_VOICE_MAP = {
    "lâm diệp": "pNInz6obpgDQGcFmaJgB",        # Adam (Trầm tĩnh, sắc lạnh)
    "lâm hạo": "N2lVS1w4EtoT3dr4eOWO",         # Callum (Kiêu ngạo, the thé)
    "nguyệt thiền nhi": "pFZP5JQG7iQjIQuC4Bku", # Lily (Trong trẻo, dịu dàng)
    "lâm chấn": "SOYHLrjzK2X1ezoPC6cr",        # Harry (Nham hiểm, hung bạo)
    "lâm khiếu thiên": "pqHfZKP75CvOlQylNhV4",  # Bill (Lão giả tiên phong đạo cốt)
    "người kể chuyện": "JBFqnCBsd6RMkjVDRZzb",  # George (Warm, Captivating Storyteller)
}

DEFAULT_VOICE_ID = "pNInz6obpgDQGcFmaJgB"


def get_voice_id_for_character(speaker_name: str) -> str:
    key = str(speaker_name).strip().lower()
    return CHARACTER_VOICE_MAP.get(key, DEFAULT_VOICE_ID)


def synthesize_speech(
    text: str,
    output_path: Path | str,
    speaker_name: str | None = None,
    voice_id: str | None = None,
    stability: float = 0.5,
    similarity_boost: float = 0.75,
) -> Path:
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    temp_raw = out_p.parent / f"raw_{out_p.stem}.mp3"

    target_voice = voice_id or get_voice_id_for_character(speaker_name or "")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity_boost,
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
    )

    logger.info("Calling ElevenLabs TTS for [%s] (voice_id=%s): %s", speaker_name or "Unknown", target_voice, text[:30])
    with urllib.request.urlopen(req, timeout=60) as resp, open(temp_raw, "wb") as f:
        f.write(resp.read())

    # Resample to studio standard 48000 Hz Stereo
    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_raw),
        "-ar", "48000",
        "-ac", "2",
        "-b:a", "192k",
        str(out_p)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    temp_raw.unlink(missing_ok=True)

    logger.info("Successfully synthesized & resampled: %s (48kHz Stereo)", out_p.name)
    return out_p


if __name__ == "__main__":
    test_out = Path("output/test_voice_adam.mp3")
    synthesize_speech("Kiếm ý bất diệt, vạn thế duy ngã độc tôn!", test_out, speaker_name="Lâm Diệp")
    print("Test passed! Saved to:", test_out)
