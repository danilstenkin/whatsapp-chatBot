# app/dialog/lead_state_manager.py

from app.db.redis_client import redis_client




async def set_lead_state(phone: str):
    """Установить состояние клиента (с TTL)."""
    await redis_client.set(phone, "HAVE", ex=3600)  # 1 час хранения

async def set_lead_state2(phone: str):
    """Установить состояние клиента (с TTL)."""
    await redis_client.set(phone, "NEW", ex=3600)  # 1 час хранения


