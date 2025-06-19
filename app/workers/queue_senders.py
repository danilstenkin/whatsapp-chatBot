import redis
import json
import os

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))

async def queue_whatsapp_message(phone: str, text: str):
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    r.rpush("send_message_queue", json.dumps({"phone": phone, "text": text}))