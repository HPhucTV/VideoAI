"""
Download authentic viral TikTok / Shorts meme MP4 clips from Tenor
"""
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

out_dir = Path(__file__).resolve().parent.parent / "workshops" / "workshop-threads" / "assets" / "memes_video"
out_dir.mkdir(parents=True, exist_ok=True)

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

clips = {
    "the_rock.mp4": "https://media.tenor.com/kHcmsxlKHEAAAAPo/rock-one-eyebrow-raised-rock-staring.mp4",
    "side_eye_dog.mp4": "https://media.tenor.com/wy2zHeWyf2gAAAPo/side-eye-dog-suspicious-look.mp4",
    "huh_cat.mp4": "https://media.tenor.com/7t63GFnoIPUAAAPo/huh-cat-huh-m4rtin.mp4",
    "pop_cat.mp4": "https://media.tenor.com/P1gzXH98ZqEAAAPo/pop-cat.mp4",
    "emotional_damage.mp4": "https://media.tenor.com/3F2fisXdTdYAAAPo/emotional-damage-emotional-damage-gif.mp4",
    "banana_cat.mp4": "https://media.tenor.com/u8M7kk5ZXmwAAAPo/banana-cat-crying.mp4",
    "sad_cat.mp4": "https://media.tenor.com/tuzl1hVGlIQAAAPo/sad-cat-sad-cat-meme.mp4",
    "metal_pipe.mp4": "https://media.tenor.com/iS8_wMys4GwAAAPo/metal-pipe-gggg.mp4",
    "disappointed_fan.mp4": "https://media.tenor.com/ZRfF7ykR3_QAAAPo/edan-ready-go.mp4",
}

print(f"Downloading authentic viral meme MP4s to {out_dir}...")
for name, url in clips.items():
    dest = out_dir / name
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = resp.read()
            dest.write_bytes(data)
            print(f"OK: {name} ({len(data)//1024} KB)")
    except Exception as e:
        print(f"FAILED: {name} - {e}")
