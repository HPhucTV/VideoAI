"""
Script: build_meme_sfx_library.py
Chuẩn hóa và đồng bộ 100% bộ âm thanh Meme SFX chính hãng, chất lượng 48,000 Hz:
- vine_boom.wav: Âm thanh Vine Boom bass punch siêu lực kinh điển
- bruh.wav: Giọng nam trầm "Bruh" chuẩn meme
- record_scratch.wav: Tiếng cào đĩa than DJ vinyl ngắt nhịp hài hước
- cricket.wav: Tiếng dế đêm kêu lúng túng (Awkward silence)
- sad_trombone.wav: Kèn đồng "wah wah wah wahhh" thất bại hài hước
- huh.wav: Tiếng "Huh?" ngơ ngác chuẩn meme
- what.wav: Tiếng "What?!" thảng thốt bàng hoàng
- metal_pipe.wav: Tiếng ống kim loại rơi vang dội hài hước
- emotional_damage.wav: "Emotional Damage!" kinh điển của Steven He
- anime_wow.wav: Tiếng anime "Woooow" trầm trồ hài hước
- windows_error.wav: Âm thanh báo lỗi Windows XP huyền thoại
- quack.wav: Tiếng vịt cao su bóp quác quác ngớ ngẩn
- ding.wav: Tiếng chuông leng keng trong trẻo (Aha / Ý tưởng)
- pop.wav: Tiếng pop bong bóng nảy mượt mà
- whoosh.wav: Tiếng gió lướt chuyển cảnh điện ảnh
"""
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SFX_DIR = Path("workshops/workshop-threads/assets/sfx")
SHARED_SFX_DIR = Path("shared-assets/sfx")
SCRATCH_DIR = Path("scratch/audio_dl")

SFX_DIR.mkdir(parents=True, exist_ok=True)
SHARED_SFX_DIR.mkdir(parents=True, exist_ok=True)

# Cấu hình cắt và chuẩn hóa từng SFX: (source, start_sec, duration_sec, target_name, loudness_I)
SFX_CONFIGS = [
    ("raw_vine_boom.wav", 0.0, 1.8, "vine_boom.wav", -11.0),
    ("raw_bruh.wav", 0.0, 0.85, "bruh.wav", -10.0),
    ("scratch/trimmed_scratch.wav", 0.0, 0.85, "record_scratch.wav", -11.0),
    ("raw_cricket.wav", 0.0, 2.0, "cricket.wav", -15.0),
    ("raw_sad_trombone.wav", 0.0, 3.2, "sad_trombone.wav", -11.0),
    ("scratch/test_huh.wav", 0.0, 1.0, "huh.wav", -10.0),
    ("scratch/test_what.wav", 0.0, 1.4, "what.wav", -10.0),
    ("raw_metal_pipe.wav", 0.0, 2.0, "metal_pipe.wav", -11.0),
    ("scratch/test_emo.wav", 0.0, 1.5, "emotional_damage.wav", -10.0),
    ("raw_anime_wow.wav", 0.8, 1.6, "anime_wow.wav", -11.0),
    ("raw_windows_error.wav", 0.5, 0.9, "windows_error.wav", -11.0),
    ("raw_quack.wav", 0.0, 0.8, "quack.wav", -11.0),
    ("raw_ding.wav", 1.8, 1.0, "ding.wav", -12.0),
    ("scratch/test_pop.wav", 0.0, 0.5, "pop.wav", -11.0),
    ("scratch/test_whoosh.wav", 0.0, 0.8, "whoosh.wav", -12.0),
]

def main():
    print("=== ĐỒNG BỘ VÀ CHUẨN HÓA BỘ MEME SFX CHÍNH HÃNG ===")
    for src, start_t, dur, target_name, loud_i in SFX_CONFIGS:
        src_path = Path(src) if Path(src).exists() else (SCRATCH_DIR / src)
        if not src_path.exists():
            print(f"Bỏ qua (không tìm thấy nguồn): {src}")
            continue
            
        target_path = SFX_DIR / target_name
        cmd = [
            "ffmpeg", "-y",
        ]
        if start_t > 0:
            cmd.extend(["-ss", f"{start_t:.3f}"])
        cmd.extend([
            "-i", str(src_path.resolve()),
            "-t", f"{dur:.3f}",
            "-af", f"loudnorm=I={loud_i}:TP=-0.5:LRA=7",
            "-ar", "48000",
            str(target_path.resolve())
        ])
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            # Sync to shared-assets
            sh_target = SHARED_SFX_DIR / target_name
            sh_target.write_bytes(target_path.read_bytes())
            print(f"✔ Hoàn thành SFX: {target_name:22} ({target_path.stat().st_size} bytes)")
        except Exception as e:
            print(f"❌ Lỗi xử lý {target_name}: {e}")

    print("\n=== TỔNG HỢP KHO SFX HIỆN TẠI ===")
    for f in sorted(SFX_DIR.glob("*.wav")):
        print(f"  - {f.name:22} | {f.stat().st_size} bytes")

if __name__ == "__main__":
    main()
