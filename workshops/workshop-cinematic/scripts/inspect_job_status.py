import requests

res = requests.get('http://127.0.0.1:8100/api/scenes?video_id=950039ae-6565-4a44-8bfa-0034d5d79a5b')
scenes = res.json()
imgs = [s for s in scenes if s.get('horizontal_image_url') or s.get('horizontal_image_media_id')]
vids = [s for s in scenes if s.get('horizontal_video_url') or s.get('horizontal_video_media_id')]

print(f"Total scenes: {len(scenes)}")
print(f"Scenes with Images: {len(imgs)}/{len(scenes)}")
print(f"Scenes with Videos: {len(vids)}/{len(scenes)}")

for s in imgs:
    order = s.get('display_order', 0)
    mid = s.get('horizontal_image_media_id') or 'N/A'
    url = s.get('horizontal_image_url') or 'N/A'
    print(f"  Scene {order:02d}: media_id={mid} | url={url[:60] if url else 'N/A'}")
