"""
Script: curate_audio_assets.py
Tự động tải về, chuẩn hóa và tối ưu hóa bộ âm thanh Meme SFX và Nhạc nền (BGM)
chính hãng, chất lượng cao 48kHz Stereo/Mono cho Workshop Threads và OmniVideo Studio.
"""
import os
import subprocess
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SFX_DIR = Path("workshops/workshop-threads/assets/sfx")
BGM_DIR = Path("workshops/workshop-threads/assets/bgm")
SHARED_SFX_DIR = Path("shared-assets/sfx")
SHARED_BGM_DIR = Path("shared-assets/bgm")
SCRATCH_DIR = Path("scratch/audio_dl")

SFX_DIR.mkdir(parents=True, exist_ok=True)
BGM_DIR.mkdir(parents=True, exist_ok=True)
SHARED_SFX_DIR.mkdir(parents=True, exist_ok=True)
SHARED_BGM_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)


def download_and_process(query: str, target_file: Path, duration: float = None, is_sfx: bool = True):
    print(f"\n--- Đang xử lý: {target_file.name} (query: '{query}') ---")
    raw_target = SCRATCH_DIR / f"raw_{target_file.stem}"
    
    # 1. Download audio using yt-dlp
    dl_cmd = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format", "wav" if is_sfx else "mp3",
        "--audio-quality", "0",
        "--no-playlist",
        "--match-filter", "!is_live",
        f"ytsearch1:{query}",
        "-o", f"{raw_target}.%(ext)s"
    ]
    
    try:
        subprocess.run(dl_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Lỗi khi tải {query}: {e}")
        return False
        
    ext = "wav" if is_sfx else "mp3"
    downloaded_raw = Path(f"{raw_target}.{ext}")
    if not downloaded_raw.exists():
        candidates = list(SCRATCH_DIR.glob(f"raw_{target_file.stem}.*"))
        if candidates:
            downloaded_raw = candidates[0]
        else:
            print(f"Không tìm thấy file tải về cho {target_file.name}")
            return False

    # 2. Chuẩn hóa âm thanh bằng FFmpeg (Peak normalize, sample rate 48000Hz, trim duration)
    # SFX chuẩn mono/stereo 48000Hz, BGM chuẩn stereo 48000Hz
    ffmpeg_filters = ["loudnorm=I=-16:TP=-1.5:LRA=11"] if not is_sfx else ["loudnorm=I=-14:TP=-1.0:LRA=7"]
    
    cmd_process = [
        "ffmpeg", "-y",
        "-i", str(downloaded_raw.resolve()),
    ]
    if duration:
        cmd_process.extend(["-t", f"{duration:.3f}"])
        
    cmd_process.extend([
        "-af", ",".join(ffmpeg_filters),
        "-ar", "48000",
        str(target_file.resolve())
    ])
    
    try:
        subprocess.run(cmd_process, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Thành công: {target_file.name} ({target_file.stat().st_size} bytes)")
        return True
    except Exception as e:
        print(f"Lỗi FFmpeg khi xử lý {target_file.name}: {e}")
        return False


def main():
    print("=== BẮT ĐẦU NÂNG CẤP BỘ ÂM THANH MEME SFX VÀ BGM CHUẨN ĐIỆN ẢNH ===")
    
    # 1. Danh mục Meme SFX gốc kinh điển
    sfx_items = [
        ("vine boom sound effect official", SFX_DIR / "vine_boom.wav", 1.8),
        ("bruh sound effect official #1", SFX_DIR / "bruh.wav", 1.2),
        ("record scratch sound effect", SFX_DIR / "record_scratch.wav", 0.9),
        ("cricket sound effect comedy awkward silence", SFX_DIR / "cricket.wav", 2.2),
        ("sad trombone sound effect wah wah wah", SFX_DIR / "sad_trombone.wav", 3.2),
        ("huh sound effect kevin hart", SFX_DIR / "huh.wav", 1.0),
        ("what sound effect meme screaming", SFX_DIR / "what.wav", 1.2),
        ("metal pipe falling sound effect official", SFX_DIR / "metal_pipe.wav", 2.5),
        ("emotional damage sound effect official", SFX_DIR / "emotional_damage.wav", 1.6),
        ("fairy tail wow sound effect anime", SFX_DIR / "anime_wow.wav", 1.6),
        ("rubber duck squeak quack sound effect", SFX_DIR / "quack.wav", 0.8),
        ("windows xp error sound effect", SFX_DIR / "windows_error.wav", 1.1),
        ("ding sound effect bell clean", SFX_DIR / "ding.wav", 1.0),
        ("clean pop sound effect bubble", SFX_DIR / "pop.wav", 0.5),
        ("whoosh sound effect transition clean", SFX_DIR / "whoosh.wav", 0.8),
    ]
    
    # 2. Danh mục BGM đa phong cách
    bgm_items = [
        ("Kevin MacLeod Sneaky Snitch official audio", BGM_DIR / "comedy_sneaky.mp3", 130.0),
        ("Kevin MacLeod Monkeys Spinning Monkeys official audio", BGM_DIR / "comedy_monkeys.mp3", 125.0),
        ("lofi hip hop beat chill study relaxing no copyright", BGM_DIR / "lofi_chill.mp3", 150.0),
        ("dramatic cinematic tension suspense pulse no copyright", BGM_DIR / "drama_suspense.mp3", 120.0),
    ]

    for query, target, dur in sfx_items:
        success = download_and_process(query, target, duration=dur, is_sfx=True)
        if success and target.exists():
            # Copy sang shared-assets
            sh_target = SHARED_SFX_DIR / target.name
            sh_target.write_bytes(target.read_bytes())
            
    for query, target, dur in bgm_items:
        success = download_and_process(query, target, duration=dur, is_sfx=False)
        if success and target.exists():
            # Copy sang shared-assets
            sh_target = SHARED_BGM_DIR / target.name
            sh_target.write_bytes(target.read_bytes())

    print("\n=== HOÀN TẤT NÂNG CẤP BỘ ASSETS ÂM THANH! ===")

if __name__ == "__main__":
    main()
