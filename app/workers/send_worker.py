import asyncio
import json
import redis.asyncio as aioredis
import os
from app.services.message_safe_sender import safe_send_message
from app.logger_config import logger

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
QUEUE_NAME = "send_message_queue"

async def process_message(redis_conn):
    item = await redis_conn.blpop(QUEUE_NAME)
    if not item:
        await asyncio.sleep(0.1)
        return None

    _, message_json = item
    logger.info("[QUEUE] Получено новое сообщение")

    try:
        message = json.loads(message_json)
        phone = message["phone"]
        text = message["text"]
        
        logger.info(f"[QUEUE] Обрабатываем сообщение для {phone}")
        await safe_send_message(phone, text)
        return True
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except KeyError as e:
        logger.error(f"Missing field: {e}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
    
    return False

async def worker():
    try:
        async with aioredis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}",
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True
        ) as redis_conn:
            
            logger.info("🚀 Worker запущен и ждёт сообщений...")
            while True:
                try:
                    await process_message(redis_conn)
                except aioredis.RedisError as e:
                    logger.error(f"Redis error: {e}")
                    await asyncio.sleep(1)
                    
    except asyncio.CancelledError:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal worker error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(worker())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
