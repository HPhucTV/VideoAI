import asyncio, sys
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
from agent.db.schema import get_db, _db_lock, init_db, close_db

async def main():
    await init_db()
    db = await get_db()
    async with _db_lock:
        cur = await db.execute("UPDATE request SET status='PENDING', retry_count=0 WHERE video_id='da8930b1-0820-4546-b8c1-4a7bcf4d7c1e' AND status='FAILED'")
        await db.commit()
        print('Reset failed requests:', cur.rowcount)
    await close_db()

if __name__ == '__main__':
    asyncio.run(main())
