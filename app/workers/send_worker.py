import asyncio
import json
import redis.asyncio as aioredis  # обновлённый импорт
import os

# Импорт своей функции отправки
from app.services.messenger import send_whatsapp_response

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def worker():
    redis_conn = await aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        decode_responses=True
    )

    print("🚀 Воркер запущен и ждёт сообщений...")

    while True:
        try:
            item = await redis_conn.blpop("send_message_queue")
            if item:
                _, message_json = item
                message = json.loads(message_json)
                phone = message["phone"]
                text = message["text"]

                await send_whatsapp_response(phone, text)

        except Exception as e:
            print(f"❌ Ошибка при обработке сообщения: {e}")
            await asyncio.sleep(1)  # маленькая пауза в случае ошибки, чтобы не крутился бешено

if __name__ == "__main__":
    asyncio.run(worker())
