import subprocess
from pathlib import Path
from PIL import Image

sys_test = Path("workshops/workshop-threads/cache/test_render/test_brand_avatar.html")
sys_test.parent.mkdir(parents=True, exist_ok=True)
avatar_path = Path("shared-assets/branding/hanshin_avatar.png").resolve().as_posix()

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    width: 400px;
    height: 300px;
    background: #181818;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: sans-serif;
  }}
  .brand-avatar {{
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
    border: 3px solid rgba(255, 255, 255, 0.95);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.85);
    background: transparent;
  }}
  .brand-name {{
    margin-top: 10px;
    font-size: 20px;
    font-weight: 900;
    color: white;
  }}
</style>
</head>
<body>
  <img class="brand-avatar" src="file:///{avatar_path}" />
  <div class="brand-name">HANSHIN THREADS</div>
</body>
</html>"""

sys_test.write_text(html, encoding="utf-8")
out_img = Path("workshops/workshop-threads/cache/test_render/test_brand_avatar.png").resolve()

cmd = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "--headless",
    "--disable-gpu",
    "--window-size=400,300",
    f"--screenshot={str(out_img)}",
    f"file:///{sys_test.resolve().as_posix()}",
]
subprocess.run(cmd, check=True)
print("SUCCESS: Rendered test avatar:", out_img)
