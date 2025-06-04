# app/services/gpt.py

from openai import AsyncOpenAI
import os
from app.db.database import get_last_messages
from app.config import OPENROUTER_API_KEY

# Берем ключ из переменной окружения


# Создаем клиента с указанием кастомного endpoint OpenRouter
client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# Основная функция для генерации ответа
async def generate_reply(phone: str, new_message: str):
    history = await get_last_messages(phone)

    messages = [
        {
            "role": "system",
            "content": (
                "Ты должен подталкнуть клиента к записи в нашу компанию"
                "Ты — виртуальный помощник юридической компании YCG. "
                "Твоя задача — уточнить детали его проблемы с долгами, "
                "и направить его к записи на консультацию. "
                "Отвечай дружелюбно, по-человечески, компитентно и понятно."
                "Ты общаешься вежливо и всегда на вы"
            ),
        }
    ]

    for row in history:
        role = "user" if row["sender_role"] == "user" else "assistant"
        messages.append({"role": role, "content": row["message"]})

    messages.append({"role": "user", "content": new_message})

    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Ошибка GPT:", e)
        return "Произошла ошибка при генерации ответа."
