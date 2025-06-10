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
async def generate_reply(phone: str, new_message: str, promt: str):
    history = await get_last_messages(phone)

    messages = []

   
    
    messages.append({"role": "system", "content": promt})

    for row in history:
        messages.append({"role": row["sender_role"], "content": row["message"]})

    print (messages)
    
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
