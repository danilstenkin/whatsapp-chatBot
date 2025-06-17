# app/db/redis_client.py
import redis.asyncio as redis
import os
import json
from app.logger_config import logger

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

REDIS_TTL = 60 * 60 * 24 * 30  # 30 дней

async def get_lead_state(phone: str) -> str | None:
    data = await redis_client.get(phone)
    return data  # Просто строка, без json.loads

async def save_lead_state(phone: str):
    if await redis_client.set(phone, "gpt_problem_empathy", ex=REDIS_TTL):
        logger.info(f"[REDIS][{phone}] - Первое состояние успешно сохранино в Redis")
    else:
        logger.error(f"['REDIS'][{phone}] - Не удалось сохранить первое состояние в Redis")
 
async def set_lead_state(phone: str, state: str) -> bool:
    if await redis_client.set(phone, state):
        logger.info(f"[REDIS][{phone}][{state}] -  состояние успешно сохранино в Redis")
    else:
        logger.error(f"[REDIS][{phone}][{state}] - Не удалось сохранить первое состояние в Redis")
