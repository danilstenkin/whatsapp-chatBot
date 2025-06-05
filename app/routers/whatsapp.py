from fastapi import APIRouter, Request
from app.db.database import save_message
from app.services.messenger import send_whatsapp_response
from app.services.gpt import generate_reply
from app.state.lead_state_manager import dialog_manager

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request): # Функция которая принимает из FastApi реквест(запрос). Запрос состоит из 
                                              # заголовки (request.headers)
    form = await request.form()               # тело запроса (request.body())
    from_number = form.get("From")
    message_text = form.get("Body")

    print("FORM DATA:", dict(form))
    print("💬 Имя:", form.get("ProfileName"))
    print("📨 Получено новое сообщение:")
    print("📱 От номера:", from_number)
    print("💬 Текст:", message_text)

    if from_number and from_number.startswith("whatsapp:"):
        from_number = from_number[len("whatsapp:"):]

    if form.get("MediaUrl0") is not None:
        print("🤖 К сожалению, я не могу слушать голосовые !!!")
    else:
        await dialog_manager(from_number)
        print("Сохранено в редис")
        # 💾 Сохраняем сообщение клиента
        await save_message(from_number, message_text, role="user")
         # 🧠 Получаем ответ от GPT
        gpt_reply = await generate_reply(from_number, message_text)
        # 💾 Сохраняем сообщение от бота

        await save_message(from_number, gpt_reply, role="assistant")
         # 🖨️ Печатаем вместо отправки
        print("🤖 GPT-ответ (не отправлен в WhatsApp из-за лимита):", gpt_reply)
         
        

    return {"status": "ok"}
