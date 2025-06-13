from app.db.database import save_message
from app.services.messenger import send_whatsapp_response
from app.services.gpt import generate_reply
from app.db.redis_client import set_lead_state, save_lead_state, get_lead_state
from app.validators.user_data import is_valid_full_name, is_valid_iin, extract_float_from_text
from app.db.utils import (
    update_full_name_by_phone,
    update_city_by_phone,
    update_iin_by_phone,
    update_credit_types_by_phone,
    update_total_debt_by_phone,
    update_monthly_payment_by_phone,
    update_overdue_days_by_phone,
    update_has_overdue_by_phone,
    update_has_official_income_by_phone,
    update_has_business_by_phone,
    update_has_property_by_phone,
    update_property_types_by_phone,
    update_has_spouse_by_phone,
    update_social_status_by_phone
)
from app.services.security import encrypt
from app.validators.credit_types import parse_credit_selection


async def dialog_menedger(from_number: str, message_text: str):
    state = await get_lead_state(from_number)

    if state is None:
        welcome_text = (
            "Здравствуйте! 👋\n"
            "Вы написали в юридическую компанию **YCG – Защита прав заёмщиков** ⚖️\n\n"
            "Мы помогаем решить финансовые вопросы:\n"
            "📌 Восстановление платёжеспособности\n"
            "📌 Банкротство физических лиц\n"
            "📌 Переговоры с банками и МФО\n\n"
            "Расскажите, пожалуйста, с какой проблемой вы столкнулись? Мы постараемся вам помочь 🤝"
        )
        await save_lead_state(phone=from_number)
        await send_whatsapp_response(from_number, welcome_text)
        return
            


            
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
           await send_whatsapp_response(from_number, gpt_reply)
           print(gpt_reply)
           await send_whatsapp_response(from_number, "✅ Готовы ли Вы записаться на бесплатную консультацию?\nПожалуйста, напишите: Да или Нет")
           print("✅ Готовы ли Вы записаться на бесплатную консультацию?\nПожалуйста, напишите: Да или Нет")
           await set_lead_state (from_number, "questionnaire")


    elif state == "questionnaire":
           message_text = message_text.strip().lower()
           if message_text == "нет":
                  print("Заглушка№1")
           elif message_text == "да":
                  print("Отлично! Сейчас пройдём небольшую анкету, чтобы записать вас на консультацию.")
                  await send_whatsapp_response(from_number,"Отлично! Сейчас пройдём небольшую анкету, чтобы записать вас на консультацию." )
                  await set_lead_state(from_number, "awaiting_full_name")
                  await send_whatsapp_response(from_number, "*Пожалуйста, напишите вашу фамилию, имя и отчество полностью.*\n_Пример: Иванов Иван Иванович_")
                  print("*Пожалуйста, напишите вашу фамилию, имя и отчество полностью.*\n_Пример: Иванов Иван Иванович_")
           else:
                  print("Только Да или Нет")
                  await send_whatsapp_response(from_number, "Только Да или Нет")

    elif state == "awaiting_full_name":
           if is_valid_full_name(message_text):
                  message_text = encrypt(message_text)
                  await update_full_name_by_phone(from_number, message_text)        
                  print ("Отлично ваше ФИО записанно ✅")
                  await send_whatsapp_response(from_number ,"Отлично ваше ФИО записанно ✅")
                  await set_lead_state(from_number, "awaiting_city")
                  print("📍 Пожалуйста, укажите, в каком городе вы находитесь.\nПример: Алматы")
                  await send_whatsapp_response(from_number, "📍 Пожалуйста, укажите, в каком городе вы находитесь.\nПример: Алматы" )
                  
           else:
                  print("к сожалению не удалось записать ваше имя, попробуйте еще раз!")
                  await send_whatsapp_response(from_number, "к сожалению не удалось записать ваше имя, попробуйте еще раз!")



    elif state == "awaiting_city":
           city = message_text.strip().title()
           if len(city) >= 2:
                await update_city_by_phone(from_number, city)
                await set_lead_state(from_number, "awaiting_iin")  # следующее состояние
                await send_whatsapp_response(from_number, "✅ Спасибо! Теперь укажите, ваш ИИН")      
                print("✅ Спасибо! Теперь укажите, ваш ИИН")    
           else:
                await send_whatsapp_response(from_number, "❗️Пожалуйста, укажите корректное название города.")
                print("❗️Пожалуйста, укажите корректное название города.")

    elif state == "awaiting_iin":
           if is_valid_iin(message_text):
                  message_text = encrypt(message_text)
                  await update_iin_by_phone(from_number, message_text)
                  await send_whatsapp_response(from_number,"Cпасибо иин приняли!")
                  print("Cпасибо иин приняли!")
                  await send_whatsapp_response(from_number,
"📋 Выберите, какие кредиты у вас имеются (можно выбрать несколько через запятую):\n\n"
"1. Потребительский кредит\n"
"2. Залоговый кредит\n"
"3. Автокредит\n"
"4. Ипотека\n"
"5. Микрозаймы\n"
"6. Долги перед физ.лицами\n"
"7. Алименты\n"
"8. Другое\n\n"
"Пример ответа: *1, 4, 5*"
)
                  print("📋 Выберите, какие кредиты у вас имеются (можно выбрать несколько через запятую):\n\n"
"1. Потребительский кредит\n"
"2. Залоговый кредит\n"
"3. Автокредит\n"
"4. Ипотека\n"
"5. Микрозаймы\n"
"6. Долги перед физ.лицами\n"
"7. Алименты\n"
"8. Другое\n\n"
"Пример ответа: *1, 4, 5*")
                  await set_lead_state(from_number, "awaiting_credit_types")
           else:
                   await send_whatsapp_response(from_number, "❗️Пожалуйста, укажите корректный ИИН.")
                   print("❗️Пожалуйста, укажите корректный ИИН.")

                  
    elif state == "awaiting_credit_types":

        selected = parse_credit_selection(message_text)

        if selected:
                await update_credit_types_by_phone(from_number, selected)
                await set_lead_state(from_number, "awaiting_debt_amount")
                await send_whatsapp_response(from_number, "✅ Спасибо. Укажите, пожалуйста, общую сумму задолженности в тенге (можно примерно). \n Если не знаете отпрвьте '-'")    
        else:

                await send_whatsapp_response(from_number, "❗️Пожалуйста, выберите номера из списка, например: *1, 3, 5*")
                print("❗️Пожалуйста, выберите номера из списка, например: *1, 3, 5*")

    elif state == "awaiting_debt_amount":
           if message_text == "-":
                  await send_whatsapp_response(from_number,
    "✅ Спасибо. Следующий вопрос:\n\n*Какой у вас ежемесячный платёж по кредитам?*\n\nПожалуйста, укажите сумму числом.\nПример: *120000 тг*"
)
                  await set_lead_state(from_number, "awaiting_monthly_payment")
           else:  
              totalDebt = extract_float_from_text(message_text)
              if totalDebt != None:            
                     await update_total_debt_by_phone (from_number, totalDebt)
                     await set_lead_state(from_number, "awaiting_monthly_payment")
                     await send_whatsapp_response(from_number, "✅ Спасибо. Следующий вопрос:\n\n*Какой у вас ежемесячный платёж по кредитам?*\n\nПожалуйста, укажите сумму числом.\nПример: *120000 тг*")
                     
              else:
                     await send_whatsapp_response(from_number,
    "❗️К сожалению, не удалось распознать сумму. Пожалуйста, укажите её числом.\n\nПример: *1000000 тг*"
)


   
                  
    elif state == "awaiting_monthly_payment":
            if message_text == "-":
                     await send_whatsapp_response(from_number, "Есть ли у вас просрочка (Да или Нет)?")
                     await set_lead_state(from_number, "waiting_has_overdue")
            else:  
                     totalDebt = extract_float_from_text(message_text)
                     if totalDebt != None:            
                            await update_monthly_payment_by_phone (from_number, totalDebt)
                            await set_lead_state(from_number, "waiting_has_overdue")
                            await send_whatsapp_response(from_number, "Есть ли у вас просрочка (Да или Нет)?")

                            
                     else:
                            await send_whatsapp_response(from_number,
       "❗️К сожалению, не удалось распознать сумму. Пожалуйста, укажите её числом.\n\nПример: *1000000 тг*"
       )

    elif state == "waiting_has_overdue":
           msg = message_text.strip().lower()
           if msg in ["да", "есть", "да есть", "да, есть"]:
                  await update_has_overdue_by_phone(from_number, True)
                  print("Приняли ваши данные, Сколько дней просрочка ?")
                  send_whatsapp_response(from_number, "Приняли ваши данные, Сколько дней просрочка ?" )
                  await set_lead_state(from_number,"awaiting_overdue_days")
           elif msg in ["нет", "не было", "отсутствует"]:
                  await set_lead_state(from_number, "awaiting_has_official_income")
                  await send_whatsapp_response(from_number, "Приняли ваши данные, есть ли у вас официальный доход ?")

           else:
                  await send_whatsapp_response(from_number, "❗️Пожалуйста, ответьте *Да* или *Нет*. Есть ли у вас просрочка?")      
                     


    elif state == "awaiting_overdue_days":
           await update_overdue_days_by_phone(from_number, message_text)
           await set_lead_state(from_number, "awaiting_has_official_income")
           await send_whatsapp_response(from_number, "Приняли ваши данные, есть ли у вас официальный доход ?")

    elif state == "awaiting_has_official_income":
           msg = message_text.strip().lower()
           if msg in ["да", "есть", "да есть", "да, есть"]:
                  await update_has_official_income_by_phone(from_number, True)
                  await send_whatsapp_response(from_number, "Приняли ваш ответ,Есть ли у вас ТОО или ИП")
                  await set_lead_state(from_number, "waiting_has_business")
                 

           elif msg in ["нет", "не было", "отсутствует"]:
                  await set_lead_state(from_number, "waiting_has_business")
                  await send_whatsapp_response(from_number, "Приняли ваш ответ,Есть ли у вас ТОО или ИП")
           else:
                  await send_whatsapp_response(from_number, "Напишите только Да или Нет")

    elif state ==  "waiting_has_business":
           msg = message_text.strip().lower()
           if msg in ["да", "есть", "да есть", "да, есть"]:
                  await update_has_business_by_phone(from_number, True)
                  await set_lead_state(from_number, "waiting_has_property")
                  await send_whatsapp_response(from_number, "Приняли ваш ответ,Есть ли у вас имущество ?")

           elif msg in ["нет", "не было", "отсутствует"]:
                  await set_lead_state(from_number, "awaiting_has_property")
                  await send_whatsapp_response(from_number, "Приняли ваш ответ,Есть ли у вас имущество ?")
           else:
                  await send_whatsapp_response(from_number, "Напишите только Да или Нет")
           
    elif state == "awaiting_has_property":
           msg = message_text.strip().lower()
           if msg in ["да", "есть", "да есть", "да, есть"]:
                  await update_has_property_by_phone(from_number, True)
                  await send_whatsapp_response(from_number,
"🏠 Укажите, какое имущество у вас имеется (можно выбрать несколько через запятую):\n\n"
"1. Дом\n"
"2. Квартира\n"
"3. Гараж\n"
"4. Доля\n"
"5. Автомобиль\n"
"6. Акции\n"
"7. Другое\n"
"8. Нет имущества\n\n"
"Пример ответа: *1, 3, 5*"
)
                  await set_lead_state(from_number, "awaiting_property_types")


           elif msg in ["нет", "не было", "отсутствует"]:
                  await set_lead_state(from_number, "awaiting_has_spouse")
                  await send_whatsapp_response(from_number, "Есть ли у вас супруг/супруга ?")
           else:
                  await send_whatsapp_response(from_number, "Напишите только Да или Нет")
                  
    elif state == "awaiting_property_types":
       selected = parse_credit_selection(message_text)
       if selected:
              await update_property_types_by_phone(from_number, selected)
              await send_whatsapp_response(from_number, "✅ Спасибо. Укажите, пожалуйста, есть ли у вас супруг/супруга? (Да/Нет)")
              await set_lead_state(from_number, "waiting_has_spouse")
       else:
              await send_whatsapp_response(from_number, "❗️Пожалуйста, выберите номера из списка, например: *1, 3, 5*")

    elif state == "awaiting_has_spouse":
           msg = message_text.strip().lower()
           if msg in ["да", "есть", "да есть", "да, есть"]:
                  await update_has_spouse_by_phone(from_number, True)
                  await set_lead_state(from_number, "awaiting_social_status")
                  await send_whatsapp_response(from_number, 
            "❗️Пожалуйста, выберите номера из списка.\n\n"
            "1. Являюсь лицом с инвалидностью\n"
            "2. Являюсь получателем АСП\n"
            "3. Многодетная семья\n"
            "4. Получаю иные пособия и льготы\n"
            "5. Не отношусь к уязвимым слоям населения\n\n"
            "Пример: *2, 3, 5*")
                  
           elif msg in ["нет", "не было", "отсутствует"]:
                  await set_lead_state(from_number, "awaiting_social_status")
                  await send_whatsapp_response(from_number, 
            "❗️Пожалуйста, выберите номера из списка.\n\n"
            "1. Являюсь лицом с инвалидностью\n"
            "2. Являюсь получателем АСП\n"
            "3. Многодетная семья\n"
            "4. Получаю иные пособия и льготы\n"
            "5. Не отношусь к уязвимым слоям населения\n\n"
            "Пример: *2, 3, 5*")
                  
           else:
                  await send_whatsapp_response(from_number, "❗️Пожалуйста, выберите номера из списка, например: *1, 3, 5*")


    elif state == "awaiting_social_status":
              selected = parse_credit_selection(message_text)
              if selected:
                     await update_social_status_by_phone(from_number, selected)
                     await send_whatsapp_response(from_number, "✅ Спасибо, ваши данные записаны.")
                     # можешь задать следующий вопрос или завершить анкету
              else:
                     await send_whatsapp_response(from_number, 
                     "❗️Пожалуйста, выберите номера из списка.\n\n"
                     "1. Являюсь лицом с инвалидностью\n"
                     "2. Являюсь получателем АСП\n"
                     "3. Многодетная семья\n"
                     "4. Получаю иные пособия и льготы\n"
                     "5. Не отношусь к уязвимым слоям населения\n\n"
                     "Пример: *2, 3, 5*")

                  
                  
           

           
                  
                  
           
                  

                  
           




           


