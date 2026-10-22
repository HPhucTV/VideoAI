"""
Xưởng 5: Threads & Social Drama (workshop-threads)
Module: tts_engine.py
Tính năng:
- Lồng tiếng tự động Edge-TTS tiếng Việt (vi-VN-NamMinhNeural & vi-VN-HoaiMyNeural).
- Slang & English Phonetic Normalizer:
  + Tự động loại bỏ sạch sẽ 100% icon mặt cười ASCII (:))), =))), :3, :v, ^^, xD,...) và Unicode Emoji để Edge-TTS không đọc rác.
  + Chuyển đổi toàn diện các từ mượn tiếng Anh / thuật ngữ công nghệ, học đường (teamwork -> tim quớc, deadline -> đét lai, slide -> xờ lai,...)
    sang phiên âm tiếng Việt tự nhiên, giúp giọng đọc phát âm chuẩn xác, không bị ngắc ngứ hay đọc sai bảng chữ cái tiếng Anh.
  + Chuẩn hóa các từ viết tắt mạng xã hội (tsv -> tân sinh viên, dh -> đại học, cmt -> bình luận,...).
- Đo thời lượng chính xác từng câu thoại bằng ffprobe.
"""
from __future__ import annotations

import asyncio
import os
import re
import subprocess
import sys
import time
import unicodedata
from pathlib import Path
from typing import Optional, Tuple

import edge_tts

# Từ điển chuyển âm tiếng Anh / thuật ngữ mượn sang ngữ âm tiếng Việt chuẩn xác cho Edge-TTS
ENGLISH_PHONETIC_MAP = [
    # Thuật ngữ học tập, nhóm & công sở (Ưu tiên từ ghép trước)
    (r"\btaowork\b|\bteam\s*work\b|\bteamwork\b", "tim quớc"),
    (r"\bteammate\b|\bteam\s*mate\b", "tim mét"),
    (r"\bgánh\s+team\b", "gánh tim"),
    (r"\bteam\b", "tim"),
    (r"\bdeadline\b|\bdl\b", "đét lai"),
    (r"\bslides?\b", "xờ lai"),
    (r"\bleader\b", "lít đờ"),
    (r"\bmentor\b", "men tò"),
    (r"\bpresentation\b|\bpresent\b", "p-re zen"),
    (r"\bproject\b|\bprj\b", "pờ rô dếch"),
    (r"\breport\b", "ri pót"),
    (r"\bfeedback\b", "phít bách"),
    (r"\breview\b", "ri viu"),
    (r"\bpass\b", "pát"),
    (r"\bfail\b", "phêu"),
    (r"\btask\b", "tát"),
    (r"\bcheck\b", "chếch"),
    (r"\bseminar\b", "xê mi na"),
    (r"\bmeeting\b", "mít ting"),
    (r"\bboss\b", "bót"),
    (r"\bintern\b", "in tơn"),

    # Tâm lý, cảm xúc & lối sống Gen Z
    (r"\btoxic\b", "tốc xích"),
    (r"\bdrama\b", "đra ma"),
    (r"\bcrush\b", "cờ rớt"),
    (r"\bflex\b", "phờ lếch"),
    (r"\bchill\b", "chiu"),
    (r"\boverthinking\b|\boverthink\b", "âu vơ thin kinh"),
    (r"\bvibes?\b", "vai bờ"),
    (r"\bstyle\b", "xì tai"),
    (r"\btrend\b", "tren"),
    (r"\bflop\b", "phờ lốp"),
    (r"\bfirst date\b", "hẹn hò lần đầu"),
    (r"\bshare bill\b", "chia tiền"),
    (r"\bred flag\b", "báo động đỏ"),
    (r"\bgreen flag\b", "dấu hiệu an toàn"),
    (r"\bex\b|\bnyc\b", "người yêu cũ"),
    (r"\bny\b", "người yêu"),
    (r"\bghost\b", "biến mất không lý do"),

    # Mạng xã hội, content & công nghệ
    (r"\bcontent\b", "con ten"),
    (r"\bposts?\b|\bpốt\b", "pốt"),
    (r"\bcomments?\b|\bcmt\b", "com mừn"),
    (r"\bshares?\b", "se"),
    (r"\blikes?\b", "lai"),
    (r"\bfollowers?\b|\bfollow\b", "pho lâu"),
    (r"\bpodcasts?\b", "pót cát"),
    (r"\breels?\b", "riu"),
    (r"\bshorts?\b", "sọt"),
    (r"\bstory\b|\bstories\b", "sờ to ri"),
    (r"\bcaptions?\b|\bcap\b", "cáp sừn"),
    (r"\bupdate\b", "ắp đết"),
    (r"\bcancel\b", "ken xồ"),
    (r"\bblock\b", "bờ lốc"),
    (r"\binbox\b|\bib\b", "in bốc"),
    (r"\btag\b", "tét"),
    (r"\bgroups?\b|\bgrp\b", "rúp"),
    (r"\bdeals?\b", "điu"),
    (r"\bsales?\b", "seo"),
    (r"\borders?\b", "o đờ"),
    (r"\bshippers?\b", "síp pơ"),
    (r"\badmin\b", "át min"),
    (r"\bvideo\b", "vi dê ô"),
    (r"\bgameplay\b", "ghem pờ lây"),
    (r"\bstreams?\b|\blivestreams?\b", "xờ trim"),
    (r"\bvlogs?\b", "vê lốc"),
    (r"\bzalo\b", "da lô"),
    (r"\bfacebook\b|\bfb\b", "phây búc"),
    (r"\btiktok\b", "tóp tóp"),
    (r"\bthreads\b", "thét"),
    (r"\bweverse\b", "uy vớt"),
    (r"\byoutube\b|\byt\b", "du túp"),
]

# Từ điển ánh xạ từ viết tắt / tiếng lóng mạng xã hội tiếng Việt
SLANG_DICTIONARY = [
    # Sinh viên & Nhà trường
    (r"\b2k(\d)\b", lambda m: f"hai ca {['không','một','hai','ba','bốn','năm','sáu','bảy','tám','chín'][int(m.group(1))]}"),
    (r"\bv-?act\b", "vê át"),
    (r"\bđgnl\b|\bdgnl\b", "đánh giá năng lực"),
    (r"\btsv\b", "tân sinh viên"),
    (r"\bdh\b|\bđh\b", "đại học"),
    (r"\bsv\b", "sinh viên"),
    (r"\bhs\b", "học sinh"),
    (r"\bclb\b", "câu lạc bộ"),
    (r"\bthpt\b", "trung học phổ thông"),
    (r"\bgpa\b", "gi pi ai"),
    (r"\bcv\b", "xi vi"),
    (r"\bhr\b", "hắc rờ"),
    (r"\bkols?\b|\bkol\b", "kây o eo"),
    (r"\bgen\s*z\b|\bgenz\b", "gien zi"),

    # Viết tắt thông dụng mạng xã hội
    (r"\bko\b|\bk\b|\bhok\b", "không"),
    (r"\bđc+\b|\bdc+\b", "được"),
    (r"\bđag\b", "đang"),
    (r"\bđii+\b", "đi"),
    (r"\buh\b|\buhm\b", "ừ"),
    (r"\bck\b", "chuyển khoản"),
    (r"\bđt\b|\bdt\b", "điện thoại"),
    (r"\bb\b", "bạn"),
    (r"\bngta\b|\bng ng\b", "người ta"),
    (r"\bntn\b", "như thế nào"),
    (r"\bnt\b", "nhắn tin"),
    (r"\bcx\b", "cũng"),
    (r"\br\b", "rồi"),
    (r"\bkhc\b", "khác"),
    (r"\bch\b", "chưa"),
    (r"\bt\b", "tao"),
    (r"\bm\b", "mày"),
    (r"\bmik\b|\bmk\b", "mình"),
    (r"\bnhg\b|\bnhma\b", "nhưng mà"),
    (r"\bi\s*chag\b", "y chang"),
    (r"\bduma\b|\bđuma\b", "má ơi"),
    (r"\bbcvl\b", "bất công vãi"),
    (r"\bvcl\b|\bvler\b|\bvch\b", "vãi thật"),
    (r"\bvl\b", "vãi"),
    (r"\bbl\b", "bình luận"),
    (r"\btr\b|\btrieu\b", "triệu"),
    (r"(\d+)\s*k\b", r"\1 nghìn"),
    (r"(\d+)\s*tr\b", r"\1 triệu"),
    (r"\bpkg\b", "gói hàng"),
    (r"\bchằm zn\b", "trầm cảm"),
    (r"\bquá đà\b", "quá đáng"),
    (r"\btsb\b", "trời đất ơi"),
    (r"\bts\b", "trời sinh"),
]


def clean_emoticons_and_noise(text: str) -> str:
    """
    Loại bỏ icon mặt cười ASCII, emoji và ký tự rác để tránh Edge-TTS đọc lỗi:
    - Loại bỏ :))), =))), :)), :D, :>, ^^, xD, :), :(, :3, :v, T_T, -.-,...
    - Loại bỏ Emoji Unicode (tránh đọc tên mã biểu tượng).
    - Chuẩn hóa các dấu câu trùng lặp: !!! -> !, ??? -> ?, ... -> .
    """
    cleaned = text

    # 1. Loại bỏ các icon cười dạng văn bản (text emoticons)
    # Ví dụ: =))), =)), =), :))), :)), :), :D, :P, :>, :v, :3, ^^, xD, T_T, ;)), <3
    emoticon_patterns = [
        r"[=;:][\)\(\]\[\}\{DPOpdp/\\>vV3]+",
        r"\b[xX][dD]\b",
        r"\^[\._]?\^|>_<|><|T[\._]?T|TAT|<3|</3|-_-|;\-;",
        r"\b(ha+ha+|he+he+|hi+hi+|hic\s*hic|hu\s*hu|k+k+k+)\b",
    ]
    for pat in emoticon_patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

    # 2. Loại bỏ Emoji Unicode toàn diện (cả BMP symbols & Astral emoji)
    emoji_pattern = re.compile(
        r"["
        r"\U00010000-\U0010ffff"
        r"\u2600-\u27bf"
        r"\u2300-\u23ff"
        r"\u2b50\u2b55\u200d\ufe0f\ufe0e"
        r"]+",
        flags=re.UNICODE,
    )
    cleaned = emoji_pattern.sub("", cleaned)

    # 3. Dọn dẹp dấu câu lặp lại và ký tự thừa
    cleaned = re.sub(r"!+", "!", cleaned)
    cleaned = re.sub(r"\?+", "?", cleaned)
    cleaned = re.sub(r"~+", "", cleaned)
    cleaned = re.sub(r"\.{2,}", ".", cleaned)

    return cleaned.strip()


def normalize_slang(text: str) -> str:
    """
    Chuyển đổi từ viết tắt, tiếng lóng và phiên âm tiếng Anh sang văn phong nói tự nhiên.
    Giữ nguyên nội dung gốc để hiển thị trên Card, chỉ biến đổi chuỗi nạp vào Edge-TTS.
    """
    # 1. Làm sạch icon rác và emoji
    normalized = clean_emoticons_and_noise(text)

    # 2. Phiên âm các thuật ngữ tiếng Anh / mượn sang âm đọc tiếng Việt
    for pattern, replacement in ENGLISH_PHONETIC_MAP:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # 3. Thay thế tiếng lóng và từ viết tắt
    for pattern, replacement in SLANG_DICTIONARY:
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # 4. Dọn dẹp khoảng trắng dư thừa và chuẩn hóa NFC
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return unicodedata.normalize("NFC", normalized)


def get_audio_duration(audio_path: str | Path) -> float:
    """Đo thời lượng file audio chính xác bằng ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return round(float(res.stdout.strip()), 2)


async def _synthesize_async(
    text: str,
    out_file: str | Path,
    voice: str = "vi-VN-NamMinhNeural",
    rate: str = "+25%",
) -> None:
    voices_to_try = [voice, "vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
    rates_to_try = [rate, "+25%", "+0%"]

    for v in dict.fromkeys(voices_to_try):
        for r in dict.fromkeys(rates_to_try):
            for attempt in range(1, 4):
                try:
                    communicate = edge_tts.Communicate(text, v, rate=r)
                    await communicate.save(str(out_file))
                    if Path(out_file).exists() and Path(out_file).stat().st_size > 500:
                        return
                except Exception:
                    await asyncio.sleep(0.5 * attempt)

    raise RuntimeError(f"Edge-TTS failed to synthesize text: {text[:50]}...")


def synthesize_speech(
    text: str,
    out_file: str | Path,
    voice: str = "vi-VN-NamMinhNeural",
    rate: str = "+25%",
    pitch: str = "+0Hz",
    apply_slang_norm: bool = True,
) -> float:
    """
    Sinh file âm thanh Edge-TTS tiếng Việt chuẩn 48kHz.
    Trả về thời lượng âm thanh tính bằng giây.
    """
    out_path = Path(out_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    tts_text = normalize_slang(text) if apply_slang_norm else unicodedata.normalize("NFC", text.strip())

    asyncio.run(_synthesize_async(tts_text, out_path, voice=voice, rate=rate))

    return get_audio_duration(out_path)
