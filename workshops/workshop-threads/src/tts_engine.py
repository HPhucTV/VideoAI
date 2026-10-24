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
_WIN_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
from pathlib import Path
from typing import Optional, Tuple

import edge_tts

_SFX_DIR = Path(__file__).resolve().parent.parent / "assets" / "sfx"

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

    # Viết tắt thông dụng mạng xã hội & Teen-code
    (r"\bclm\b|\bclmm\b", "vãi chưởng"),
    (r"\bđcm\b|\bđcmm\b|\bdcm\b", "bực thật"),
    (r"\bvcl\b|\bvler\b|\bvch\b", "vãi thật"),
    (r"\bvl\b", "vãi"),
    (r"\bvc\b", "vãi chưởng"),
    (r"\bhđqt\b|\bhdqt\b", "hội đồng quản trị"),
    (r"\bbcuoi\b|\bbuonc\b", "buồn cười"),
    (r"\btr\s+ơi\b|\btr\s+oi\b", "trời ơi"),
    (r"\bko\b|\bk\b|\bhok\b|\bhơm\b", "không"),
    (r"\bđc+\b|\bdc+\b|\bđccc+\b", "được"),
    (r"\bđag\b|\bdag\b", "đang"),
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
    (r"\bẻ\b", "ỉa"),
    (r"\bvs\b", "với"),
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
    # Ví dụ: =))), =)), =), :))), :)), :), :D, :P, :>, :v, :3, ^^, xD, T_T, ;)), <3, -)), ~))
    emoticon_patterns = [
        r"[-=;:][\)\(\]\[\}\{DPOpdp/\\>vV3]+",
        r"-+[\)\(]+|~+[\)\(]+",
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


def get_voice_profile_for_speaker(
    role: str = "commenter",
    index: int = 0,
    text: str = "",
    default_male: str = "vi-VN-NamMinhNeural",
    default_female: str = "vi-VN-HoaiMyNeural",
) -> dict:
    """
    Tự động phân vai giọng đọc (Voice Casting) đa dạng cho từng nhân vật & bình luận:
    - Tránh việc toàn bộ video chỉ dùng 1 giọng đọc đều đều gây buồn ngủ.
    - Luân phiên Nam - Nữ và điều biến cao độ (Pitch Modulation) theo độ tuổi / tính cách.
    """
    t_lower = text.lower()
    
    # Nếu nội dung thể hiện vai phụ huynh, ông chú, trưởng bối
    if any(k in t_lower for k in ["chú", "bác", "bố", "phụ huynh", "mẹ", "thầy", "cô"]):
        if any(k in t_lower for k in ["mẹ", "cô"]):
            return {"voice": default_female, "rate": "+18%", "pitch": "-2Hz"}
        return {"voice": default_male, "rate": "+16%", "pitch": "-5Hz"}

    # Luân phiên giọng đọc theo thứ tự bình luận (comment index)
    profiles = [
        {"voice": default_female, "rate": "+24%", "pitch": "+1Hz"},  # Nữ trẻ trung
        {"voice": default_male, "rate": "+26%", "pitch": "+0Hz"},    # Nam năng động
        {"voice": default_female, "rate": "+25%", "pitch": "+2Hz"},  # Nữ lanh lợi
        {"voice": default_male, "rate": "+22%", "pitch": "-3Hz"},    # Nam trầm hài hước
        {"voice": default_female, "rate": "+26%", "pitch": "-1Hz"},  # Nữ điềm tĩnh
        {"voice": default_male, "rate": "+28%", "pitch": "+2Hz"},    # Nam phấn khích
    ]
    return profiles[index % len(profiles)]


def smart_insert_comedic_pauses(text: str) -> str:
    """
    Tự động chuyển đổi các dấu ba chấm (...) và dấu ngắt kịch tính thành thẻ [pause:0.35]
    để tạo khoảng lặng chết tiệt (Awkward Silence), nâng tầm điểm rơi gây cười (comedic timing).
    """
    if "[pause:" in text:
        return text

    # Chuyển đổi '...' hoặc '…' ở giữa câu thành nhịp ngắt 0.35s
    res = re.sub(r"\s*(\.{3,}|…)\s*", " [pause:0.35] ", text)
    return res.strip()


def detect_emotion(text: str) -> dict:
    """
    Tự động nhận diện ngữ cảnh và cảm xúc câu thoại để:
    - Tự động điều biến cao độ (pitch), tốc độ (rate)
    - Tự động gán Meme SFX kinh điển chuẩn 100% (Vine Boom, Bruh, Record Scratch, Emotional Damage, Metal Pipe, Huh, What, Windows Error, Anime Wow, Sad Trombone, Cricket,...)
    """
    t_lower = text.lower()

    # 1. Shock / Dramatic Impact -> Vine Boom
    shock_keywords = [
        "má ơi", "y chang", "vãi", "trời ơi", "vcl", "vch", "sốc",
        "duma", "đuma", "bất ngờ", "đột nhiên", "tốc xích", "kinh khủng", "chấn động"
    ]
    if any(k in t_lower for k in shock_keywords) or (("má" in t_lower or "y chang" in t_lower) and "!" in text):
        return {
            "emotion": "shock",
            "rate": "+28%",
            "pitch": "+2Hz",
            "sfx": "vine_boom.wav",
            "shake": True,
        }

    # 2. Emotional Damage / Cà khịa cay đắng / Sát thương tinh thần -> Emotional Damage
    damage_keywords = [
        "sát thương", "xát muối", "chửi thấm", "đau ví", "đau lòng", "cay",
        "nhột", "nhục", "vỡ mộng", "phũ", "cay đắng", "tự nhục", "chửi người yêu", "tác hại"
    ]
    if any(k in t_lower for k in damage_keywords):
        return {
            "emotion": "damage",
            "rate": "+24%",
            "pitch": "+0Hz",
            "sfx": "emotional_damage.wav",
            "shake": True,
        }

    # 3. Metal Pipe / Va chạm sụp đổ / Té ngửa -> Metal Pipe
    pipe_keywords = [
        "té ngửa", "vấp ngã", "sụp đổ", "va vào", "đập đầu", "tiếng ống"
    ]
    if any(k in t_lower for k in pipe_keywords):
        return {
            "emotion": "pipe",
            "rate": "+28%",
            "pitch": "+1Hz",
            "sfx": "metal_pipe.wav",
            "shake": True,
        }

    # 4. What / Bàng hoàng phẫn nộ -> What Screaming
    what_keywords = [
        "cái gì vậy", "cái gì cơ", "nani", "điên hả", "điên à", "gì cơ"
    ]
    if any(k in t_lower for k in what_keywords):
        return {
            "emotion": "what",
            "rate": "+30%",
            "pitch": "+3Hz",
            "sfx": "what.wav",
            "shake": True,
        }

    # 5. Awkward / Plot-twist / Facepalm -> Record Scratch
    awkward_keywords = [
        "quê", "xui xẻo", "mất việc", "hãm", "xỉu", "bất lực", "ngượng", "tăng xông", "lúng túng", "sượng", "sượng trân"
    ]
    if any(k in t_lower for k in awkward_keywords):
        return {
            "emotion": "awkward",
            "rate": "+24%",
            "pitch": "-1Hz",
            "sfx": "record_scratch.wav",
            "shake": True,
        }

    # 6. Bruh / Speechless / Deadpan -> Bruh
    bruh_keywords = [
        "tội nghiệp", "cạn lời", "hết cứu", "bó tay", "chịu", "lạy"
    ]
    if any(k in t_lower for k in bruh_keywords):
        return {
            "emotion": "bruh",
            "rate": "+20%",
            "pitch": "-4Hz",
            "sfx": "bruh.wav",
            "shake": False,
        }

    # 7. Fail / Clown / Thất bại thảm hại -> Sad Trombone
    fail_keywords = [
        "toang", "rớt môn", "thất bại", "chia tay", "cắm sừng", "bị lừa", "mất tiền", "bay màu", "kiệt sức", "thảm"
    ]
    if any(k in t_lower for k in fail_keywords):
        return {
            "emotion": "fail",
            "rate": "+20%",
            "pitch": "-3Hz",
            "sfx": "sad_trombone.wav",
            "shake": False,
        }

    # 8. Awkward Silence / Lúng túng im bặt -> Cricket
    silence_keywords = [
        "im lặng", "im bặt", "không ai nói", "chết lặng", "ngớ người", "đứng hình"
    ]
    if any(k in t_lower for k in silence_keywords):
        return {
            "emotion": "silence",
            "rate": "+20%",
            "pitch": "-2Hz",
            "sfx": "cricket.wav",
            "shake": False,
        }

    # 9. Windows Error / Đơ máy lag não -> Windows Error
    error_keywords = [
        "đơ", "lag", "đứng máy", "sập nguồn", "quá tải", "load không kịp", "mất sóng"
    ]
    if any(k in t_lower for k in error_keywords):
        return {
            "emotion": "error",
            "rate": "+20%",
            "pitch": "-2Hz",
            "sfx": "windows_error.wav",
            "shake": False,
        }

    # 10. Wow / Trầm trồ kinh điển / Khen đểu -> Anime Wow
    wow_keywords = [
        "kinh điển", "đỉnh nóc", "kịch trần", "đỉnh chóp", "bá đạo", "ảo thật", "siêu phẩm", "quá đỉnh"
    ]
    if any(k in t_lower for k in wow_keywords):
        return {
            "emotion": "wow",
            "rate": "+26%",
            "pitch": "+2Hz",
            "sfx": "anime_wow.wav",
            "shake": False,
        }

    # 11. Quack / Ngớ ngẩn hề hước -> Quack
    quack_keywords = [
        "hề", "ngáo", "tấu hài", "ngớ ngẩn", "trẻ trâu"
    ]
    if any(k in t_lower for k in quack_keywords):
        return {
            "emotion": "quack",
            "rate": "+26%",
            "pitch": "+1Hz",
            "sfx": "quack.wav",
            "shake": False,
        }

    # 12. Confusion / Quizzical -> Huh?
    question_keywords = [
        "là sao", "hổng", "chật vật", "không hiểu", "quên sạch",
        "sao lại", "quăng", "bỏ đi", "chịu luôn", "lú"
    ]
    if any(k in t_lower for k in question_keywords) or "?" in text:
        return {
            "emotion": "question",
            "rate": "+22%",
            "pitch": "+1Hz",
            "sfx": "huh.wav",
            "shake": False,
        }

    # 13. Insight / Idea / Aha -> Ding
    aha_keywords = [
        "chuẩn", "chính xác", "bí quyết", "hiểu rồi", "nhớ rồi", "ra rồi", "hay quá", "sáng suốt"
    ]
    if any(k in t_lower for k in aha_keywords):
        return {
            "emotion": "aha",
            "rate": "+25%",
            "pitch": "+0Hz",
            "sfx": "ding.wav",
            "shake": False,
        }

    # 14. Lament / Sadness -> Whoosh
    sad_keywords = [
        "đau", "khóc", "rớt", "bất công", "bcvl", "xu cà na"
    ]
    if any(k in t_lower for k in sad_keywords) or "💔" in text:
        return {
            "emotion": "sad",
            "rate": "+18%",
            "pitch": "-3Hz",
            "sfx": "whoosh.wav",
            "shake": False,
        }

    # 15. Neutral -> Pop
    return {
        "emotion": "neutral",
        "rate": "+25%",
        "pitch": "+0Hz",
        "sfx": "pop.wav",
        "shake": False,
    }


def get_audio_duration(audio_path: str | Path) -> float:
    """Đo thời lượng file audio chính xác bằng ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True, creationflags=_WIN_FLAGS)
    return round(float(res.stdout.strip()), 2)


async def _synthesize_async(
    text: str,
    out_file: str | Path,
    voice: str = "vi-VN-NamMinhNeural",
    rate: str = "+25%",
    pitch: str = "+0Hz",
) -> None:
    # Nếu văn bản chỉ toàn dấu câu, dấu chấm hoặc rỗng, sinh 0.3s silence an toàn
    clean_alpha = "".join(c for c in text if c.isalnum())
    if not clean_alpha:
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.3", "-c:a", "libmp3lame", str(out_file)]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=_WIN_FLAGS)
        return

    voices_to_try = [voice, "vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
    rates_to_try = [rate, "+25%", "+0%"]
    pitches_to_try = [pitch, "+0Hz"]

    for v in dict.fromkeys(voices_to_try):
        for r in dict.fromkeys(rates_to_try):
            for p in dict.fromkeys(pitches_to_try):
                for attempt in range(1, 4):
                    try:
                        communicate = edge_tts.Communicate(text, v, rate=r, pitch=p)
                        await communicate.save(str(out_file))
                        if Path(out_file).exists() and Path(out_file).stat().st_size > 500:
                            return
                    except Exception:
                        await asyncio.sleep(0.5 * attempt)

    raise RuntimeError(f"Edge-TTS failed to synthesize text: {text[:50]}...")


def add_audio_tail_padding(audio_path: Path, pad_dur: float = 0.35) -> Path:
    """Thêm khoảng lặng an toàn ở đuôi audio để chống nuốt âm tiết cuối của TTS."""
    temp_pad = audio_path.parent / f"pad_{audio_path.name}"
    cmd = [
        "ffmpeg", "-y",
        "-i", str(audio_path.resolve()),
        "-af", f"apad=pad_dur={pad_dur:.3f}",
        "-c:a", "libmp3lame" if audio_path.suffix.lower() == ".mp3" else "pcm_s16le",
        str(temp_pad.resolve())
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=_WIN_FLAGS)
    if temp_pad.exists():
        temp_pad.replace(audio_path)
    return audio_path


def synthesize_speech(
    text: str,
    out_file: str | Path,
    voice: str = "vi-VN-NamMinhNeural",
    rate: str = "+25%",
    pitch: str = "+0Hz",
    apply_slang_norm: bool = True,
    auto_emotion: bool = False,
    auto_pause: bool = True,
    tail_padding: float = 0.35,
) -> float:
    """
    Sinh file âm thanh Edge-TTS tiếng Việt chuẩn 48kHz.
    Hỗ trợ chèn các thẻ ngắt nhịp hài hước & Meme SFX:
    - [pause:0.5]: Dừng im lặng 0.5 giây (Awkward Silence).
    - [sfx:record_scratch.wav]: Chèn âm thanh record scratch dừng đĩa than.
    - [sfx:cricket.wav]: Chèn tiếng dế kêu ngượng ngùng.
    - [sfx:sad_trombone.wav]: Chèn tiếng trombone thất bại hài hước.
    - [sfx:bruh.wav]: Chèn âm thanh bruh câm nín.
    """
    out_path = Path(out_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if auto_emotion:
        emo = detect_emotion(text)
        rate = emo.get("rate", rate)
        pitch = emo.get("pitch", pitch)

    # Tự động chèn nhịp dừng hài hước nếu gặp dấu ba chấm kịch tính
    if auto_pause:
        text = smart_insert_comedic_pauses(text)

    tag_pattern = r"(\[sfx:[^\]]+\]|\[pause:[0-9.]+\])"
    if not re.search(tag_pattern, text):
        tts_text = normalize_slang(text) if apply_slang_norm else unicodedata.normalize("NFC", text.strip())
        asyncio.run(_synthesize_async(tts_text, out_path, voice=voice, rate=rate, pitch=pitch))
        if tail_padding > 0:
            add_audio_tail_padding(out_path, tail_padding)
        return get_audio_duration(out_path)

    # Xử lý đa phân đoạn có nhịp dừng & SFX hài hước
    raw_tokens = [t.strip() for t in re.split(tag_pattern, text) if t.strip()]
    temp_dir = out_path.parent / f"temp_{out_path.stem}_chunks"
    temp_dir.mkdir(parents=True, exist_ok=True)

    audio_chunks = []
    for idx, token in enumerate(raw_tokens):
        chunk_file = temp_dir / f"chunk_{idx}.wav"
        if token.startswith("[pause:") and token.endswith("]"):
            dur_str = token[7:-1]
            try:
                pause_dur = float(dur_str)
            except ValueError:
                pause_dur = 0.4
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                "-t", f"{pause_dur:.3f}",
                "-c:a", "pcm_s16le",
                str(chunk_file)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=_WIN_FLAGS)
            audio_chunks.append(chunk_file)

        elif token.startswith("[sfx:") and token.endswith("]"):
            sfx_spec = token[5:-1].split(":")
            sfx_name = sfx_spec[0].strip()
            sfx_dur = float(sfx_spec[1]) if len(sfx_spec) > 1 else None

            sfx_src = _SFX_DIR / sfx_name
            if not sfx_src.exists():
                sfx_src = _SFX_DIR / "pop.wav"

            if sfx_dur:
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(sfx_src.resolve()),
                    "-t", f"{sfx_dur:.3f}",
                    "-ar", "24000", "-ac", "1",
                    "-c:a", "pcm_s16le",
                    str(chunk_file)
                ]
            else:
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(sfx_src.resolve()),
                    "-ar", "24000", "-ac", "1",
                    "-c:a", "pcm_s16le",
                    str(chunk_file)
                ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=_WIN_FLAGS)
            audio_chunks.append(chunk_file)

        else:
            sub_tts = normalize_slang(token) if apply_slang_norm else unicodedata.normalize("NFC", token.strip())
            sub_mp3 = temp_dir / f"chunk_{idx}.mp3"
            asyncio.run(_synthesize_async(sub_tts, sub_mp3, voice=voice, rate=rate, pitch=pitch))
            cmd = [
                "ffmpeg", "-y",
                "-i", str(sub_mp3.resolve()),
                "-ar", "24000", "-ac", "1",
                "-c:a", "pcm_s16le",
                str(chunk_file)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=_WIN_FLAGS)
            audio_chunks.append(chunk_file)

    if audio_chunks:
        inputs = []
        filter_parts = []
        for c_idx, c_path in enumerate(audio_chunks):
            inputs.extend(["-i", str(c_path.resolve())])
            filter_parts.append(f"[{c_idx}:a]")
        concat_str = f"{''.join(filter_parts)}concat=n={len(audio_chunks)}:v=0:a=1[a_out]"

        cmd_concat = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", concat_str,
            "-map", "[a_out]",
            "-c:a", "libmp3lame" if out_path.suffix.lower() == ".mp3" else "pcm_s16le",
            str(out_path)
        ]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, creationflags=_WIN_FLAGS)
        if tail_padding > 0:
            add_audio_tail_padding(out_path, tail_padding)

    return get_audio_duration(out_path)
