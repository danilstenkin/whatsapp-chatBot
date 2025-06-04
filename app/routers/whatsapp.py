from fastapi import APIRouter, Request
from app.db.database import save_message
from app.services.messenger import send_whatsapp_response
from app.services.gpt import generate_reply

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()

    from_number = form.get("From")
    message_text = form.get("Body")

    print("📨 Получено сообщение:")
    print("📱 От номера:", from_number)
    print("💬 Текст:", message_text)

    if from_number and from_number.startswith("whatsapp:"):
        from_number = from_number[len("whatsapp:"):]
    
    # 💾 Сохраняем сообщение клиента
    await save_message(from_number, message_text, role="client")

    # 🧠 Получаем ответ от GPT
    gpt_reply = await generate_reply(from_number, message_text)

    # 🖨️ Печатаем вместо отправки
    print("🤖 GPT-ответ (не отправлен в WhatsApp из-за лимита):", gpt_reply)

    # 💾 Сохраняем сообщение от бота
    await save_message(from_number, gpt_reply, role="bot")

    return {"status": "ok"}
