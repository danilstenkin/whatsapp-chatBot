import httpx
from app.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from app.db.database import save_message  # ⬅️ добавили импорт

TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'

async def send_whatsapp_response(to_number: str, message: str):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"

    data = {
        'From': TWILIO_WHATSAPP_NUMBER,
        'To': f'whatsapp:{to_number}',
        'Body': message
    }

    auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, auth=auth)

    if response.status_code == 201:
        sid = response.json()["sid"]
        print("✅ Сообщение отправлено:", sid)

        # ✅ Сохраняем сообщение от бота в базу данных
        await save_message(to_number, message, "bot")

    else:
        print("❌ Ошибка Twilio:", response.status_code, response.text)
