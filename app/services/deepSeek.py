from openai import AsyncOpenAI
from app.db.database import get_last_messages
from app.config import DEEPSEEK_API_KEY

# Важно: обязательно укажи /v1 в конце base_url
client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# Функция генерации ответа
async def generate_reply(phone: str, new_message: str, promt: str):
    try:
        history = await get_last_messages(phone)

        messages = [{"role": "system", "content": promt}]
        for row in history:
            messages.append({"role": row["sender_role"], "content": row["message"]})

        # Добавляем текущее сообщение от клиента
        messages.append({"role": "user", "content": new_message})

        print("🔹 DeepSeek messages:", messages)

        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Ошибка DeepSeek:", e)
        return "Произошла ошибка при генерации ответа от ИИ."
