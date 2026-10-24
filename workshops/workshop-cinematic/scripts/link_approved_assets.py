import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agent.db.schema import init_db, close_db
from agent.db import crud

async def main():
    await init_db()
    # Link Xiao Ling approved character media ID
    await crud.update_character('529c5b07-9acc-4b46-9f74-182ae1f0512b', media_id='0d027e85-0278-413e-843a-f213875b44e1')
    # Link Ancient Scriptorium location media ID
    await crud.update_character('cf63a7aa-c8ed-4cca-9bb9-67b6ad6349d2', media_id='285a08bd-ec12-4b86-aceb-d34c25bef1e2')
    print("[OK] Linked Character and Location Media IDs successfully!")
    await close_db()

if __name__ == '__main__':
    asyncio.run(main())
