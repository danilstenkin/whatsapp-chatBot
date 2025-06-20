import json
from app.db.redis_client import redis_client
from app.logger_config import logger
from app.services.messenger import send_whatsapp_response, TwilioAPIError

MAX_RETRIES = 5  # обязательно поставь столько же, сколько у тебя в messenger.py

async def safe_send_message(phone: str, text: str):
    try:
        await send_whatsapp_response(phone, text)
    except TwilioAPIError as e:
        logger.error(f"[{phone}] Сообщение НЕ отправилось после {MAX_RETRIES} попыток: {str(e)}")

        failed_payload = {
            "phone": phone,
            "text": text
        }

        try:
            await redis_client.rpush("failed_message_queue", json.dumps(failed_payload))
            logger.warning(f"[{phone}] Сообщение добавлено в Dead Letter Queue (failed_message_queue)")
        except Exception as redis_error:
            logger.critical(f"[{phone}] Ошибка сохранения в Redis DLQ: {redis_error}")
