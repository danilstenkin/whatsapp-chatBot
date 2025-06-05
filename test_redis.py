import asyncio
from app.db.redis_client import redis_client

async def main():
    await redis_client.set("hello", "world")
    value = await redis_client.get("hello")
    print("🔌 Redis test value:", value)

if __name__ == "__main__":
    asyncio.run(main())
