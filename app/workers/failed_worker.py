import asyncio
import json
from app.services.messenger import send_whatsapp_response, TwilioAPIError
from app.db.redis_client import redis_client
from app.logger_config import logger

QUEUE_NAME = "failed_message_queue"
RETRY_DELAY = 10  # секунды между итерациями

async def process_failed_messages():
    logger.info("🚀 Запуск воркера для обработки failed_message_queue (DLQ)")

    while True:
        try:
            # Берём первый элемент из очереди (НЕ удаляем)
            message_json = await redis_client.lindex(QUEUE_NAME, 0)
            if not message_json:
                await asyncio.sleep(RETRY_DELAY)
                continue

            try:
                message = json.loads(message_json)
                phone = message["phone"]
                text = message["text"]

                logger.info(f"[{phone}] Попытка повторной отправки сообщения из DLQ")

                try:
                    await send_whatsapp_response(phone, text)
                    logger.info(f"[{phone}] Повторная отправка прошла успешно ✅")

                    # Только после успешной отправки — удаляем сообщение из очереди
                    await redis_client.lrem(QUEUE_NAME, count=1, value=message_json)
                    logger.info(f"[{phone}] Сообщение удалено из failed_message_queue")

                except TwilioAPIError as e:
                    logger.error(f"[{phone}] Ошибка при повторной отправке: {str(e)}")
                    await asyncio.sleep(RETRY_DELAY)

            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения из DLQ: {str(e)}")
                # Если вообще не можем распарсить — лучше удалить кривое сообщение:
                await redis_client.lrem(QUEUE_NAME, count=1, value=message_json)
                logger.warning(f"[DLQ] Некорректное сообщение удалено из очереди")

        except Exception as e:
            logger.error(f"Критическая ошибка в DLQ воркере: {str(e)}")
            await asyncio.sleep(RETRY_DELAY)

if __name__ == "__main__":
    asyncio.run(process_failed_messages())
