# app/routers/whatsapp.py
from fastapi import APIRouter, Request
from app.services.menedger import dialog_menedger

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    from_number = form.get("From")
    message_text = form.get("Body")

    if from_number and from_number.startswith("whatsapp:"):
        from_number = from_number[len("whatsapp:"):]  # убираем префикс

    if form.get("MediaUrl0") is not None:
        print("🤖 К сожалению, я не могу слушать голосовые.")
        return {"status": "ok"}
    
    else:   
        await dialog_menedger(from_number, message_text)  
        return {"status": "ok"}


