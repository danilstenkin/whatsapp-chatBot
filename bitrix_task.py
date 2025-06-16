import asyncio
from app.db.database import db  # или свой путь
from app.db.utils import sync_lead_by_phone  # где находится функция

async def main():
    await db.connect()
    await sync_lead_by_phone("+77071214296")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
