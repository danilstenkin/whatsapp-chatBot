from openai import AsyncOpenAI
from app.db.database import get_last_messages
from app.config import DEEPSEEK_API_KEY
from app.logger_config import logger  # убедись, что импортируешь свой логгер

client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

async def generate_reply(phone: str, new_message: str, promt: str):
    try:
        logger.info(f"[{phone}] Получено новое сообщение: {new_message!r}")

        history = await get_last_messages(phone)

        messages = [{"role": "system", "content": promt}]
        for row in history:
            messages.append({"role": row["sender_role"], "content": row["message"]})

        messages.append({"role": "user", "content": new_message})

        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )

        reply = response.choices[0].message.content.strip()
        logger.info(f"[DeepSeek][{phone}] Ответ ИИ отправлен")
        return reply

    except Exception as e:
        logger.exception(f"[DeepSeek][{phone}] ❌ Ошибка при генерации ответа от DeepSeek")
        return "Произошла ошибка при генерации ответа от ИИ."
