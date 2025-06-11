from app.db.database import save_message
from app.services.messenger import send_whatsapp_response
from app.services.gpt import generate_reply
from app.db.redis_client import set_lead_state, save_lead_state, get_lead_state


async def dialog_menedger (from_number: str, message_text:str):

    state = await get_lead_state(from_number)
    if state is None:
            
            base =  ("""
Здравствуйте! 👋  
Вы написали в юридическую компанию **YCG – Защита прав заёмщиков** ⚖️

Мы помогаем решить финансовые вопросы:  
📌 Восстановление платёжеспособности  
📌 Банкротство физических лиц  
📌 Переговоры с банками и МФО

Расскажите, пожалуйста, с какой проблемой вы столкнулись? Мы постараемся вам помочь 🤝
    """)    
            print(base)
            await save_lead_state(phone=from_number)
            await send_whatsapp_response(from_number, base)
            


            
    elif state == "gpt_problem_empathy":

            base = ("""
                    РАЗГОВАРИВАЙ ВСЕГДА НА ВЫ
Ты — доброжелательный юридический консультант компании YCG. Клиент только что поделился своей финансовой проблемой.

Твоя задача — проявить сочувствие, показать, что он выажен, и мягко уточнить, какой нибудь уточняющий вопрос который будет полезен для юриста. Пиши по-человечески, не как робот., будь краток»


""")            
            await save_message(from_number, message_text, role="user")
            gpt_reply = await generate_reply(from_number, message_text, base)
            await send_whatsapp_response(from_number, gpt_reply)
            await save_message(from_number, gpt_reply, role="assistant")
            await set_lead_state (from_number, "gpt_problem_dig_deeper")
            print(gpt_reply)

    elif state == "gpt_problem_dig_deeper":

            base = ("""
                    РАЗГОВАРИВАЙ ВСЕГДА НА ВЫ
Ты — юридический консультант YCG. Клиент рассказал о своей проблеме, теперь нужно уточнить детали: которые будут полезны юристом опирайся уже на диалог клиент это user, а ты assistant.
не говори что ему делать задай просто какой нибудь вопрос по делу просто вопрос  


""")            
            await save_message(from_number, message_text, role="user")
            gpt_reply = await generate_reply(from_number, message_text, base)
            await send_whatsapp_response(from_number, gpt_reply)
            await save_message(from_number, gpt_reply, role="assistant")
            await set_lead_state (from_number, "gpt_offer_consultation")
            print(gpt_reply)


    elif state == "gpt_offer_consultation":
           base = (
"""РАЗГОВАРИВАЙ ВСЕГДА НА ВЫ, вежливо и профессионально.

Вы — опытный юрист-консультант компании YCG. Клиент описал свою проблему с долгами (смотрите предыдущий диалог). Ваша задача — проанализировать ситуацию и донести, что в его случае крайне важно получить профессиональную помощь.

Сформулируйте, что без индивидуального подхода и анализа документов невозможно оценить риски и выбрать законный путь. Обязательно подчеркните:

— Ситуация требует внимательного подхода  
— Важно не откладывать решение  
— **Необходимо записаться на бесплатную консультацию в YCG**, чтобы разобраться в возможных вариантах

Никаких вопросов в конце, никаких фраз «хотите записаться?» — просто твёрдое, уважительное утверждение: консультация **необходима**, она бесплатна и поможет разобраться в ситуации.

Пример тона:
«Исходя из описанного, ваша ситуация требует внимательной юридической оценки. Важно не откладывать — с каждым днём последствия могут усиливаться.

Для того чтобы определить оптимальные законные шаги, вам обязательно нужно пройти бесплатную консультацию с юристом нашей компании YCG. Только так можно точно понять, какие действия сейчас возможны в вашем случае.»
"""
)

           
           await save_message(from_number, message_text, role="user")
           gpt_reply = await generate_reply(from_number, message_text, base)
           await save_message(from_number, gpt_reply, role="assistant")
           await set_lead_state (from_number, "DONE")
           await send_whatsapp_response(from_number, gpt_reply)
           print(gpt_reply)
           print("✅ Готовы ли Вы записаться на бесплатную консультацию?\nПожалуйста, напишите: Да или Нет")


    elif state == "DONE":
           print("STOOOP")
           
        
    