from app.db.database import save_message
from app.services.messenger import send_whatsapp_response
from app.services.gpt import generate_reply
from app.db.redis_client import set_lead_state, save_lead_state, get_lead_state
from app.db.utils import save_client_first_name

async def dialog_menedger (from_number: str, message_text:str):
    state = await get_lead_state(from_number)

    if state is None:
            
            base =  ("""
👋 Доброго времени суток!  
    Вас приветствует юридическая компания **YCG** — мы помогаем заемщикам решать проблемы с долгами, МФО и банками.
Благодарим за обращение — ваша ситуация важна для нас.  
                     
Пожалуйста, опишите только проблему с которой вы столкнулись (одним сообщением). Мы внимательно изучим ваш случай и предложим решение.
    """)
            await save_lead_state(phone=from_number)
            await send_whatsapp_response(from_number, base)
            


            
    elif state == "NEW":

            base = ("""
Спасибо, что поделились своей ситуацией 🙏  
Чтобы записать вас на бесплатную консультацию с юристом, мне нужно уточнить несколько деталей.

Сейчас я задам вам несколько вопросов. Это поможет нам подготовиться и предложить наиболее подходящее решение 📋

""")
            await send_whatsapp_response (from_number, base)
            print ("Напшите пожалуйста ваше Имя")
            await send_whatsapp_response(from_number, "Напшите пожалуйста ваше Имя")
            await set_lead_state (from_number, "waiting_for_name")
    
    elif state == "waiting_for_name":
           base = (
                """Тебе придет сообщение тебе нужно из него извлечь только имя
Ответь только именем (пример: Алексей).  
Если имя отсутствует — напиши только: none (строго с маленькой буквы, без кавычек и дополнительных слов)."""
            )
           await save_message(from_number, message_text, role="user")
           gpt_reply = await generate_reply(from_number, message_text, base)

           print ("ОтветЖЖЖЖЖЖ ",gpt_reply)

           if gpt_reply == "none":
                  await send_whatsapp_response (from_number, "Извините, вам нужно указать свое имя" )
                  print ("Извините, вам нужно указать свое имя")
                  return {"status": "ok"}
           else:
                  print(f"Отлично, {gpt_reply}, теперь напишите вашу фамилию")
                  await send_whatsapp_response (from_number, f"Отлично, {gpt_reply}, теперь напишите вашу фамилию")
                  await save_client_first_name(from_number, gpt_reply)
                  await save_message (from_number, gpt_reply,role="assistant")
                  await set_lead_state (from_number, "DONE")
        
           print("🤖 GPT-ответ:", gpt_reply)