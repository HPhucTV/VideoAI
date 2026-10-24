import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from agent.db.schema import init_db, close_db
from agent.db import crud

async def check():
    await init_db()
    reqs = await crud.list_actionable_requests(limit=10)
    print("Actionable requests count:", len(reqs))
    for r in reqs:
        print(f"ID={r['id'][:8]} type={r['type']} vid={r['video_id'][:8]} scene={r['scene_id'][:8]} status={r['status']}")
    await close_db()

asyncio.run(check())
