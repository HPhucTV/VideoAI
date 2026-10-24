import sys
from pathlib import Path

# Setup paths
root_dir = Path(__file__).resolve().parent.parent.parent.parent
workshop_dir = Path(__file__).resolve().parent.parent
src_dir = workshop_dir / "src"

for p in [root_dir, workshop_dir, src_dir]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tts_engine import normalize_slang, detect_emotion, synthesize_speech
from card_engine import render_card, find_browser_executable
from compositor import generate_karaoke_ass
from scraper import parse_raw_text_thread


def test_slang_normalizer():
    raw_text = "Hôm nay đi first date mà bạn ý bắt share bill qua ck, đt thì hết pin ko biết làm ntn"
    normalized = normalize_slang(raw_text)
    assert "hẹn hò lần đầu" in normalized
    assert "chia tiền" in normalized
    assert "chuyển khoản" in normalized
    assert "điện thoại" in normalized
    assert "không" in normalized
    assert "như thế nào" in normalized


def test_detect_emotion():
    e_shock = detect_emotion("Má y chang luôn!")
    assert e_shock["emotion"] == "shock"
    assert e_shock["sfx"] == "vine_boom.wav"
    assert e_shock["shake"] is True

    e_question = detect_emotion("Mấy câu này khó hiểu là sao?")
    assert e_question["emotion"] == "question"
    assert e_question["sfx"] == "huh.wav"

    e_sad = detect_emotion("đau không gì bằng...")
    assert e_sad["emotion"] == "sad"
    assert e_sad["pitch"] == "-3Hz"


def test_comedy_emotions():
    e_awkward = detect_emotion("quả hội đồng quản trị mất việc rồi quê ghê")
    assert e_awkward["emotion"] == "awkward"
    assert e_awkward["sfx"] == "record_scratch.wav"

    e_bruh = detect_emotion("tội nghiệp mấy thằng bạn tao cạn lời luôn")
    assert e_bruh["emotion"] == "bruh"
    assert e_bruh["sfx"] == "bruh.wav"

    e_damage = detect_emotion("câu nói này sát thương xát muối vào tim ghê")
    assert e_damage["emotion"] == "damage"
    assert e_damage["sfx"] == "emotional_damage.wav"

    e_fail = detect_emotion("toang rồi cả đám rớt môn bay màu hết")
    assert e_fail["emotion"] == "fail"
    assert e_fail["sfx"] == "sad_trombone.wav"

    e_pipe = detect_emotion("nghe xong té ngửa sụp đổ luôn")
    assert e_pipe["emotion"] == "pipe"
    assert e_pipe["sfx"] == "metal_pipe.wav"

    e_error = detect_emotion("não đơ lag máy sập nguồn không kịp load")
    assert e_error["emotion"] == "error"
    assert e_error["sfx"] == "windows_error.wav"

    e_wow = detect_emotion("pha xử lý kinh điển đỉnh nóc kịch trần")
    assert e_wow["emotion"] == "wow"
    assert e_wow["sfx"] == "anime_wow.wav"


def test_generate_karaoke_ass(tmp_path):
    timeline = [
        {"start": 0.0, "end": 2.0, "text": "Học sinh hai ca chín", "duration": 2.0}
    ]
    out_ass = tmp_path / "karaoke.ass"
    generate_karaoke_ass(timeline, out_ass)
    assert out_ass.exists()
    content = out_ass.read_text(encoding="utf-8")
    assert "Style: Karaoke" in content
    assert "\\k" in content
    assert "Học" in content


def test_nested_thread_card(tmp_path):
    out_png = tmp_path / "test_nested.png"
    rendered = render_card(
        username="commenter_1",
        time_str="1 giờ",
        content="Đây là câu trả lời kiểm thử cây hội thoại",
        output_png=out_png,
        parent_context={
            "username": "op_author",
            "time": "2 giờ",
            "content": "Đây là bài viết gốc cần được kết nối qua thread line",
        },
        theme="dark",
        width=720,
        height=1280,
    )
    assert rendered.exists()
    assert rendered.stat().st_size > 0


def test_hook_badge_card(tmp_path):
    out_png = tmp_path / "test_hook_badge.png"
    rendered = render_card(
        username="thanhtrucdayne",
        time_str="18 giờ",
        content="Xin lỗi hội đồng quản trị, cô gái xui xẻo đó là tao!",
        output_png=out_png,
        hook_badge="KHI BẠN THÂN CHỬI NGƯỜI YÊU BẠN... 🤡",
        theme="dark",
        width=720,
        height=1280,
    )
    assert rendered.exists()
    assert rendered.stat().st_size > 0


def test_synthesize_speech_with_tags(tmp_path):
    out_audio = tmp_path / "test_tag_speech.mp3"
    text = "Hội đồng quản trị... [pause:0.3] [sfx:pop.wav] giải tán luôn!"
    dur = synthesize_speech(text, out_audio, voice="vi-VN-NamMinhNeural", rate="+25%")
    assert out_audio.exists()
    assert out_audio.stat().st_size > 1000
    assert dur > 1.0


def test_parse_raw_text_thread():
    sample_text = """@hvy2908 | 12 giờ
Con trai chung thủy thật thà chết hết rồi à?
---
@dmin.music | 2 giờ
Không phải chết hết, mà trước giờ có tồn tại đâu."""
    res = parse_raw_text_thread(sample_text)
    assert res["post"]["username"] == "hvy2908"
    assert "chung thủy" in res["post"]["content"]
    assert len(res["comments"]) == 1
    assert res["comments"][0]["username"] == "dmin.music"


def test_render_card_png(tmp_path):
    browser = find_browser_executable()
    assert Path(browser).exists()

    out_png = tmp_path / "test_card.png"
    rendered = render_card(
        username="HanShin",
        time_str="1 giờ",
        content="Đây là nội dung kiểm thử thẻ bài viết phong cách Cyber Neon cho kênh HanShin.",
        output_png=out_png,
        theme="hanshin",
        width=720,
        height=1280,
    )
    assert rendered.exists()
    assert rendered.stat().st_size > 0


def test_bgm_library_and_sfx_suite():
    from compositor import _SFX_DIR
    bgm_dir = _SFX_DIR.parent / "bgm"
    
    # Kiểm tra đủ 4 thể loại nhạc nền chính
    assert (bgm_dir / "comedy_sneaky.mp3").exists()
    assert (bgm_dir / "comedy_monkeys.mp3").exists()
    assert (bgm_dir / "lofi_chill.mp3").exists()
    assert (bgm_dir / "drama_suspense.mp3").exists()
    
    # Kiểm tra đủ các Meme SFX kinh điển
    required_sfx = [
        "vine_boom.wav", "bruh.wav", "record_scratch.wav",
        "cricket.wav", "sad_trombone.wav", "huh.wav", "what.wav",
        "metal_pipe.wav", "emotional_damage.wav", "anime_wow.wav",
        "windows_error.wav", "quack.wav", "ding.wav", "pop.wav", "whoosh.wav"
    ]
    for sfx_name in required_sfx:
        sfx_file = _SFX_DIR / sfx_name
        assert sfx_file.exists(), f"Thiếu file SFX: {sfx_name}"
        assert sfx_file.stat().st_size > 5000, f"File SFX quá nhỏ/rỗng: {sfx_name}"


def test_meme_sticker_library_and_sfx_sync():
    from compositor import _MEMES_DIR, find_meme_for_sfx
    assert _MEMES_DIR.exists()
    
    meme_names = [
        "vine_boom.png", "bruh.png", "quack.png", "what.png",
        "huh.png", "sad_trombone.png", "metal_pipe.png", "emotional_damage.png",
        "anime_wow.png", "record_scratch.png"
    ]
    for m in meme_names:
        mf = _MEMES_DIR / m
        assert mf.exists(), f"Thiếu file Meme Sticker: {m}"
        assert mf.stat().st_size > 5000, f"File Meme Sticker quá nhỏ/rỗng: {m}"
        
    # Kiểm tra mapping SFX -> Meme Sticker
    assert find_meme_for_sfx("vine_boom.wav").name == "vine_boom.png"
    assert find_meme_for_sfx("bruh.wav").name == "bruh.png"
    assert find_meme_for_sfx("quack.wav").name == "quack.png"
    assert find_meme_for_sfx("what.wav").name == "what.png"
    assert find_meme_for_sfx("emotional_damage.wav").name == "emotional_damage.png"
    assert find_meme_for_sfx("non_existent.wav") is None


def test_expanded_slang_and_emoticon_cleaning():
    raw = "-)) bộ m ỉa mạnh dữ lắm hả, clm nó 😭"
    norm = normalize_slang(raw)
    assert "-))" not in norm
    assert "mày" in norm
    assert "vãi chưởng" in norm


def test_viral_meme_video_library():
    from compositor import _MEMES_VIDEO_DIR, find_meme_video, _ROUND_MASK_460, _ROUND_BORDER_460
    assert _MEMES_VIDEO_DIR.exists()
    assert _ROUND_MASK_460.exists()
    assert _ROUND_BORDER_460.exists()

    expected_videos = [
        "the_rock.mp4", "side_eye_dog.mp4", "pop_cat.mp4", "huh_cat.mp4",
        "emotional_damage.mp4", "banana_cat.mp4", "metal_pipe.mp4", "disappointed_fan.mp4"
    ]
    for v in expected_videos:
        vf = _MEMES_VIDEO_DIR / v
        assert vf.exists(), f"Thiếu clip Meme Video: {v}"
        assert vf.stat().st_size > 5000, f"File video quá nhỏ: {v}"

    # Kiểm tra mapping SFX -> Real Meme Video
    assert find_meme_video(sfx_name="vine_boom.wav").name == "the_rock.mp4"
    assert find_meme_video(sfx_name="bruh.wav").name == "side_eye_dog.mp4"
    assert find_meme_video(sfx_name="quack.wav").name == "pop_cat.mp4"
    assert find_meme_video(sfx_name="huh.wav").name == "huh_cat.mp4"
    assert find_meme_video(sfx_name="emotional_damage.wav").name == "emotional_damage.mp4"
    assert find_meme_video(sfx_name="what.wav").name == "disappointed_fan.mp4"
    assert find_meme_video(meme_name="the_rock").name == "the_rock.mp4"


def test_greenscreen_meme_library():
    from compositor import _MEMES_GREENSCREEN_DIR, find_greenscreen_meme
    assert _MEMES_GREENSCREEN_DIR.exists()
    
    expected_greenscreen = [
        "the_rock.mp4", "huh_cat.mp4", "pedro_pascal.mp4",
        "pop_cat.mp4", "side_eye.mp4", "walter_white.mp4"
    ]
    for v in expected_greenscreen:
        vf = _MEMES_GREENSCREEN_DIR / v
        assert vf.exists(), f"Thiếu meme phông xanh: {v}"
        assert vf.stat().st_size > 10000, f"File meme phông xanh quá nhỏ: {v}"

    assert find_greenscreen_meme(sfx_name="vine_boom").name == "the_rock.mp4"
    assert find_greenscreen_meme(sfx_name="huh").name == "huh_cat.mp4"
    assert find_greenscreen_meme(sfx_name="emotional_damage").name == "pedro_pascal.mp4"
    assert find_greenscreen_meme(sfx_name="bruh").name == "side_eye.mp4"
    assert find_greenscreen_meme(sfx_name="sad_trombone").name == "walter_white.mp4"


def test_multi_character_voice_casting():
    from tts_engine import get_voice_profile_for_speaker
    p0 = get_voice_profile_for_speaker(index=0)
    p1 = get_voice_profile_for_speaker(index=1)
    assert p0["voice"] != p1["voice"]

    # Test phụ huynh / người lớn tuổi nhận pitch trầm hơn
    p_parent = get_voice_profile_for_speaker(text="chú là người quen của nhi nè con")
    assert "-5Hz" in p_parent["pitch"] or "-2Hz" in p_parent["pitch"]


def test_smart_comedic_pauses():
    from tts_engine import smart_insert_comedic_pauses
    txt = "buồn cười thật... phụ huynh chào bằng ngón đó"
    res = smart_insert_comedic_pauses(txt)
    assert "[pause:0.35]" in res


def test_diverse_background_library():
    from pipeline import _BG_DIR
    gta = _BG_DIR / "gta5_ramp.mp4"
    subway = _BG_DIR / "subway_surfers.mp4"
    minecraft = _BG_DIR / "minecraft_parkour.mp4"

    assert gta.exists() and gta.stat().st_size > 1000000
    assert subway.exists() and subway.stat().st_size > 1000000
    assert minecraft.exists() and minecraft.stat().st_size > 1000000



