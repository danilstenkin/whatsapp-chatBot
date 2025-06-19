import asyncio
import json
import redis.asyncio as aioredis
import os
from app.services.messenger import send_whatsapp_response
from app.logger_config import logger  # Если у тебя уже подключен logger

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "send_message_queue"

async def worker():
    redis_conn = await aioredis.from_url(
        f"redis://{REDIS_HOST}:{REDIS_PORT}",
        decode_responses=True
    )

    logger.info("🚀 Воркер запущен и ждёт сообщений...")

    while True:
        try:
            item = await redis_conn.blpop(QUEUE_NAME)
            if not item:
                continue

            _, message_json = item
            message = json.loads(message_json)
            phone = message["phone"]
            text = message["text"]

            logger.info(f"[QUEUE] Получено сообщение для {phone}")

            await send_whatsapp_response(phone, text)

        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker())
