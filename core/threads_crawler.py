import sys
import subprocess
_WIN_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
import json
import re
import urllib.request
import hashlib
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT_DIR / "workshops" / "workshop-threads" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
AVATAR_DIR = CACHE_DIR / "real_avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR = CACHE_DIR / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def download_file(url: str, dest_path: Path) -> bool:
    try:
        if not url or not url.startswith("http"):
            return False
        if dest_path.exists() and dest_path.stat().st_size > 0:
            return True
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False

def crawl_threads_post(url: str) -> dict:
    # Normalize URL
    clean_url = url.strip().replace("threads.com", "threads.net")
    print(f"[*] Crawling Threads URL via Headless Chrome: {clean_url}", file=sys.stderr)

    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--dump-dom",
        "--disable-gpu",
        "--no-sandbox",
        clean_url
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=35, creationflags=_WIN_FLAGS)
    html = res.stdout.decode("utf-8", errors="ignore")

    # 1. Extract og:description (post text)
    og_desc_match = re.search(r'<meta property="og:description" content="(.*?)"', html)
    post_content = og_desc_match.group(1) if og_desc_match else ""
    if not post_content:
        # Fallback to description
        desc_m = re.search(r'<meta name="description" content="(.*?)"', html)
        post_content = desc_m.group(1) if desc_m else "Nội dung bài viết Threads"

    # 2. Extract username
    og_title_match = re.search(r'<meta property="og:title" content="(.*?)"', html)
    og_title = og_title_match.group(1) if og_title_match else ""
    u_match = re.search(r'@([\w\.\-]+)', og_title)
    if not u_match:
        u_match = re.search(r'@([\w\.\-]+)', clean_url)
    username = u_match.group(1) if u_match else "threads_user"

    # 3. Extract og:image (post media/meme image)
    og_img_match = re.search(r'<meta property="og:image" content="(.*?)"', html)
    post_media_url = og_img_match.group(1).replace("&amp;", "&") if og_img_match else None

    local_post_media = None
    if post_media_url:
        media_hash = hashlib.md5(post_media_url.encode()).hexdigest()[:10]
        media_file = MEDIA_DIR / f"post_media_{username}_{media_hash}.jpg"
        if download_file(post_media_url, media_file):
            local_post_media = str(media_file.resolve())

    # 4. Extract user avatar and replies from embedded JSON
    scripts = re.findall(r'<script type="application/json"[^>]*>(.*?)</script>', html)
    
    post_avatar_url = None
    comments = []
    seen_comments = set()

    for s in scripts:
        if '"text_post_app_info"' in s or '"profile_pic_url"' in s:
            try:
                data = json.loads(s)
                def walk(obj):
                    nonlocal post_avatar_url
                    if isinstance(obj, dict):
                        if "user" in obj and isinstance(obj["user"], dict):
                            u = obj["user"]
                            u_name = u.get("username")
                            p_url = u.get("profile_pic_url")
                            if u_name == username and p_url and not post_avatar_url:
                                post_avatar_url = p_url

                        if "caption" in obj and isinstance(obj["caption"], dict):
                            c_text = obj["caption"].get("text", "")
                            u_info = obj.get("user") or {}
                            c_user = u_info.get("username", "user_reply")
                            c_avatar = u_info.get("profile_pic_url")
                            c_key = f"{c_user}:{c_text[:30]}"
                            if c_text and c_key not in seen_comments and c_text != post_content:
                                seen_comments.add(c_key)
                                comments.append({
                                    "username": c_user,
                                    "time": "vừa xong",
                                    "content": c_text,
                                    "avatar_url": c_avatar,
                                    "likes": "128",
                                    "comments": "8",
                                    "reposts": "3"
                                })

                        for v in obj.values():
                            walk(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            walk(item)

                walk(data)
            except Exception:
                pass

    # Download author avatar
    local_post_avatar = None
    if post_avatar_url:
        av_hash = hashlib.md5(post_avatar_url.encode()).hexdigest()[:8]
        av_file = AVATAR_DIR / f"avatar_{username}_{av_hash}.jpg"
        if download_file(post_avatar_url, av_file):
            local_post_avatar = str(av_file.resolve())

    # Format comments with downloaded avatars & voice assignment
    formatted_comments = []
    voices = ["vi-VN-NamMinhNeural", "vi-VN-HoaiMyNeural"]
    for i, c in enumerate(comments[:6]):
        c_av = c.get("avatar_url")
        loc_av = None
        if c_av:
            c_hash = hashlib.md5(c_av.encode()).hexdigest()[:8]
            c_file = AVATAR_DIR / f"avatar_{c['username']}_{c_hash}.jpg"
            if download_file(c_av, c_file):
                loc_av = str(c_file.resolve())
        
        # If no avatar downloaded, fallback to author avatar if available
        if not loc_av and local_post_avatar:
            loc_av = local_post_avatar

        formatted_comments.append({
            "username": c["username"],
            "time": c.get("time", "1 giờ"),
            "content": c["content"],
            "avatar_url": loc_av or c.get("avatar_url"),
            "likes": c.get("likes", "120"),
            "voice": voices[i % len(voices)]
        })

    # Prepare standard thread_data structure for Workshop 5
    job_id = f"job_thread_{username}_{int(time.time())}"
    thread_data = {
        "url": clean_url,
        "job_id": job_id,
        "post": {
            "username": username,
            "time": "vừa xong",
            "content": post_content,
            "avatar_url": local_post_avatar or post_avatar_url,
            "post_image_url": local_post_media,
            "likes": "458",
            "comments": str(len(formatted_comments) * 12 + 18),
            "reposts": "22",
            "voice": "vi-VN-HoaiMyNeural" if "girl" in username.lower() or "linh" in username.lower() else "vi-VN-NamMinhNeural"
        },
        "comments": formatted_comments
    }

    # Save to cache
    cached_json_path = CACHE_DIR / "latest_crawled_thread.json"
    with open(cached_json_path, "w", encoding="utf-8") as f:
        json.dump(thread_data, f, ensure_ascii=False, indent=2)

    return {
        "success": True,
        "job_id": job_id,
        "thread_data": thread_data,
        "cached_file": str(cached_json_path.resolve()),
        "total_comments": len(formatted_comments),
        "post_preview": {
            "username": username,
            "content": post_content,
            "has_media": bool(local_post_media),
            "has_avatar": bool(local_post_avatar)
        }
    }

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.threads.net/@janus.tvd/post/De3ZFkBAU_5"
    res = crawl_threads_post(test_url)
    print(json.dumps(res, ensure_ascii=False, indent=2))
