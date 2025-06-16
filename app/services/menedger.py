from app.db.database import save_message
from app.services.messenger import send_whatsapp_response
from app.services.deepSeek import generate_reply
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
    update_social_status_by_phone,
    update_has_children_by_phone, 
    update_problem_description_by_phone,
    get_full_client_data
)
from app.services.security import encrypt
from app.validators.credit_types import parse_credit_selection, parse_social_status_selection, parse_buisness_selection

from app.services.create_task_in_bitrix import send_lead_to_bitrix


async def dialog_menedger(from_number: str, message_text: str):
    state = await get_lead_state(from_number)

    if state is None:
        welcome_text = (
            "Здравствуйте! 👋\n"
            "Вы написали в юридическую компанию *YCG – Защита прав заёмщиков* ⚖️\n\n"
            "Мы помогаем решить финансовые вопросы:\n"
            "📌 Восстановление платёжеспособности\n"
            "📌 Банкротство физических лиц\n"
            "📌 Переговоры с банками и МФО\n\n"
            "Расскажите, пожалуйста, с какой проблемой вы столкнулись? Мы постараемся вам помочь 🤝"
        )
        await save_lead_state(phone=from_number)
        await send_whatsapp_response(from_number, welcome_text)
            


            
    elif state == "gpt_problem_empathy":

            base = ("""
                    РАЗГОВАРИВАЙ ВСЕГДА НА ВЫ
Ты — доброжелательный юридический консультант компании YCG. Клиент только что поделился своей финансовой проблемой.

Твоя задача — проявить сочувствие, показать, что он выажен, и мягко уточнить, какой нибудь уточняющий вопрос который будет полезен для юриста. Пиши по-человечески, не как робот., будь краток»
попроси чтобы ответили одним сообщением
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
попроси чтобы ответили одним сообщением
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
              await send_whatsapp_response(from_number, "Хорошо, если передумаете - мы всегда готовы помочь!")
       elif message_text == "да":
              await send_whatsapp_response(from_number, "Отлично! Давайте заполним анкету для записи на консультацию.")
              await set_lead_state(from_number, "awaiting_full_name")
              await send_whatsapp_response(from_number, 
              "🔹 *Укажите ваше полное ФИО*\n"
              "Формат: Фамилия Имя Отчество\n"
              "Пример: *Иванов Иван Иванович*"
              )
       else:
              await send_whatsapp_response(from_number, "Пожалуйста, ответьте 'Да' или 'Нет'")

    elif state == "awaiting_full_name":
       if is_valid_full_name(message_text):
              message_text = encrypt(message_text)
              await update_full_name_by_phone(from_number, message_text)
              await send_whatsapp_response(from_number, "✅ ФИО успешно сохранено")
              await set_lead_state(from_number, "awaiting_city")
              await send_whatsapp_response(from_number, 
              "🔹 *Укажите ваш город проживания*\n"
              "Пример: *Алматы*"
              )
       else:
              await send_whatsapp_response(from_number, 
              "Неверный формат ФИО. Пожалуйста, укажите:\n"
              "▸ Фамилию\n▸ Имя\n▸ Отчество (при наличии)\n"
              "Пример: *Иванов Иван Иванович*"
              )

    elif state == "awaiting_city":
       city = message_text.strip().title()
       if len(city) >= 2:
              await update_city_by_phone(from_number, city)
              await set_lead_state(from_number, "awaiting_iin")
              await send_whatsapp_response(from_number, 
              "✅ Город сохранен\n"
              "🔹 *Укажите ваш ИИН*"
              )
       else:
              await send_whatsapp_response(from_number, 
              "❗ Некорректное название города\n"
              "Пожалуйста, укажите реальный город проживания"
              )

    elif state == "awaiting_iin":
       if is_valid_iin(message_text):
              message_text = encrypt(message_text)
              await update_iin_by_phone(from_number, message_text)
              await send_whatsapp_response(from_number, 
              "✅ ИИН принят\n"
              "🔹 *Выберите типы ваших кредитов:*\n\n"
              "1. Потребительский кредит\n"
              "2. Залоговый кредит\n"
              "3. Автокредит\n"
              "4. Ипотека\n"
              "5. Микрозаймы\n"
              "6. Долги перед физ.лицами\n"
              "7. Алименты\n"
              "8. Другое\n\n"
              "Можно выбрать несколько через запятую\n"
              "Пример: *1, 4, 5*"
              )
              await set_lead_state(from_number, "awaiting_credit_types")
       else:
              await send_whatsapp_response(from_number, "❗ Неверный формат ИИН\n"
              "Пожалуйста, укажите 12 цифр без пробелов")

    elif state == "awaiting_credit_types":
       selected = parse_credit_selection(message_text)
       if selected:
              await update_credit_types_by_phone(from_number, selected)
              await set_lead_state(from_number, "awaiting_debt_amount")
              await send_whatsapp_response(from_number, 
              "✅ Данные сохранены\n"
              "🔹 *Укажите общую сумму задолженности*\n"
              "Можно указать примерную сумму в тенге\n"
              "Если неизвестно - отправьте '-'"
              )
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, выберите из списка\n"
              "Пример: *1, 3, 5*"
              )

    elif state == "awaiting_debt_amount":
       if message_text == "-":
              await send_whatsapp_response(from_number, 
              "🔹 *Укажите ваш ежемесячный платеж по кредитам*\n"
              "Пример: *120000 тг*\n"
              "Если неизвестно - отправьте '-'"
              )
              await set_lead_state(from_number, "awaiting_monthly_payment")
       else:  
              totalDebt = extract_float_from_text(message_text)
              if totalDebt is not None:            
                     await update_total_debt_by_phone(from_number, totalDebt)
                     await send_whatsapp_response(from_number, 
                            "✅ Сумма задолженности сохранена\n"
                            "🔹 *Укажите ваш ежемесячный платеж*\n"
                            "Пример: *120000 тг*\n"
                            "Если неизвестно - отправьте '-'"
                     )
                     await set_lead_state(from_number, "awaiting_monthly_payment")
              else:
                     await send_whatsapp_response(from_number, 
                            "❗ Не удалось распознать сумму\n"
                            "Пожалуйста, укажите число\n"
                            "Пример: *1000000 тг*"
                     )

    elif state == "awaiting_monthly_payment":
       if message_text == "-":
              await send_whatsapp_response(from_number, 
              "🔹 *Есть ли у вас просрочки?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "waiting_has_overdue")
       else:  
              totalDebt = extract_float_from_text(message_text)
              if totalDebt is not None:            
                     await update_monthly_payment_by_phone(from_number, totalDebt)
                     await send_whatsapp_response(from_number, 
                            "✅ Данные сохранены\n"
                            "🔹 *Есть ли у вас просрочки?*\n"
                            "Ответьте Да/Нет"
                     )
                     await set_lead_state(from_number, "waiting_has_overdue")
              else:
                     await send_whatsapp_response(from_number, 
                            "❗ Не удалось распознать сумму\n"
                            "Пожалуйста, укажите число\n"
                            "Пример: *100000 тг*"
                     )

    elif state == "waiting_has_overdue":
       msg = message_text.strip().lower()
       if msg in ["да", "есть", "да есть", "да, есть"]:
              await update_has_overdue_by_phone(from_number, True)
              await send_whatsapp_response(from_number, 
              "🔹 *Укажите количество дней просрочки*"
              )
              await set_lead_state(from_number, "awaiting_overdue_days")
       elif msg in ["нет", "не было", "отсутствует"]:
              await send_whatsapp_response(from_number, 
              "🔹 *Есть ли у вас официальный доход?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "awaiting_has_official_income")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, ответьте Да или Нет"
              )

    elif state == "awaiting_overdue_days":
       await update_overdue_days_by_phone(from_number, message_text)
       await send_whatsapp_response(from_number, 
              "✅ Данные сохранены\n"
              "🔹 *Есть ли у вас официальный доход?*\n"
              "Ответьте Да/Нет"
       )
       await set_lead_state(from_number, "awaiting_has_official_income")

    elif state == "awaiting_has_official_income":
       msg = message_text.strip().lower()
       if msg in ["да", "есть", "да есть", "да, есть"]:
              await update_has_official_income_by_phone(from_number, True)
              await send_whatsapp_response(from_number, 
              "🔹 *Имеется ли у вас ТОО или ИП?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "waiting_has_business")
       elif msg in ["нет", "не было", "отсутствует"]:
              await send_whatsapp_response(from_number, 
              "🔹 *Имеется ли у вас ТОО или ИП?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "waiting_has_business")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, ответьте Да или Нет"
              )

    elif state == "waiting_has_business":
       msg = message_text.strip().lower()
       if msg in ["да", "есть", "да есть", "да, есть"]:
              await update_has_business_by_phone(from_number, True)
              await send_whatsapp_response(from_number, 
              "🔹 *Имеется ли у вас имущество?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "awaiting_has_property")
       elif msg in ["нет", "не было", "отсутствует"]:
              await send_whatsapp_response(from_number, 
              "🔹 *Имеется ли у вас имущество?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "awaiting_has_property")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, ответьте Да или Нет"
              )

    elif state == "awaiting_has_property":
       msg = message_text.strip().lower()
       if msg in ["да", "есть", "да есть", "да, есть"]:
              await update_has_property_by_phone(from_number, True)
              await send_whatsapp_response(from_number,
              "🔹 *Укажите ваше имущество:*\n\n"
              "1. Дом\n2. Квартира\n3. Гараж\n4. Доля\n"
              "5. Автомобиль\n6. Акции\n7. Другое\n8. Нет имущества\n\n"
              "Можно выбрать несколько через запятую\n"
              "Пример: *1, 3, 5*"
              )
              await set_lead_state(from_number, "awaiting_property_types")
       elif msg in ["нет", "не было", "отсутствует"]:
              await send_whatsapp_response(from_number, 
              "🔹 *Есть ли у вас супруг(а)?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, " awaiting_has_spouse")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, ответьте Да или Нет"
              )

    elif state == "awaiting_property_types":
       selected = parse_buisness_selection(message_text)
       if selected:
              await update_property_types_by_phone(from_number, selected)
              await send_whatsapp_response(from_number, 
              "✅ Данные сохранены\n"
              "🔹 *Есть ли у вас супруг(а)?*\n"
              "Ответьте Да/Нет"
              )
              await set_lead_state(from_number, "awaiting_has_spouse")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, выберите из списка\n"
              "Пример: *1, 3, 5*"
              )

    elif state == "awaiting_has_spouse":
       msg = message_text.strip().lower()
       if msg in ["да", "есть", "да есть", "да, есть"]:
              await update_has_spouse_by_phone(from_number, True)
              await send_whatsapp_response(from_number, 
              "🔹 *Есть ли у вас несовершеннолетние дети?*\n"
              "Ответьте Да или Нет"
              )
              await set_lead_state(from_number, "awaiting_has_children")
       elif msg in ["нет", "не было", "отсутствует"]:
              await send_whatsapp_response(from_number, 
              "🔹 *Есть ли у вас несовершеннолетние дети?*\n"
              "Ответьте Да или Нет"
              )
              await set_lead_state(from_number, "awaiting_has_children")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, ответьте Да или Нет"
              )

    elif state == "awaiting_has_children":
       msg = message_text.strip().lower()
       if msg in ["да", "есть", "да есть", "да, есть"]:
              await update_has_children_by_phone(from_number, True)
              await send_whatsapp_response(from_number, 
              "🔹 *Выберите ваш социальный статус:*\n\n"
              "1. Лицо с инвалидностью\n2. Получатель АСП\n"
              "3. Многодетная семья\n4. Иные пособия/льготы\n"
              "5. Не отношусь к льготным категориям\n\n"
              "Можно выбрать несколько через запятую\n"
              "Пример: *2, 3*"
              )
              await set_lead_state(from_number, "awaiting_social_status")
       elif msg in ["нет", "не было", "отсутствует"]:
              await update_has_children_by_phone(from_number, False)
              await send_whatsapp_response(from_number, 
              "🔹 *Выберите ваш социальный статус:*\n\n"
              "1. Лицо с инвалидностью\n2. Получатель АСП\n"
              "3. Многодетная семья\n4. Иные пособия/льготы\n"
              "5. Не отношусь к льготным категориям\n\n"
              "Можно выбрать несколько через запятую\n"
              "Пример: *2, 3*"
              )
              await set_lead_state(from_number, "awaiting_social_status")
       else:
              await send_whatsapp_response(from_number, 
              "❗ Пожалуйста, ответьте Да или Нет"
              )

    elif state == "awaiting_social_status":
       try:
              selected = parse_social_status_selection(message_text)
              if not selected:
                     await send_whatsapp_response(
                            from_number,
                            "❗ Пожалуйста, выберите из списка\nПример: *1, 2, 3*"
                     )
                     return

              # 1. Обновляем социальный статус
              await update_social_status_by_phone(from_number, selected)
              
              # 2. Генерируем описание проблемы
              base = """Твоя задача - создать краткое описание проблемы клиента для юристов  это сообщение пойдет в Bitrix24 и мы юристы из Казахстана, не ставь нигде ** и * если что надо сделать жирным ьексьом используй такую конструкцию [b]Дети:[/b]"""
              problem = await generate_reply(from_number, "", base)
              await update_problem_description_by_phone(from_number, problem)
              
              # 3. Логируем в консоль (для отладки)
              print("✅ Анкета заполнена для номера:", from_number)
              
              # 4. Отправляем сообщение клиенту
              await send_whatsapp_response(
              from_number,
              "✅ Анкета успешно заполнена!\n"
              "Наш специалист свяжется с вами в ближайшее время.\n\n"
              "Спасибо за предоставленную информацию!"
              )
              
              # 5. Получаем данные и отправляем в Bitrix24
              client_data = await get_full_client_data(from_number)
              if not client_data:
                     await send_whatsapp_response(from_number, "❌ Ошибка при обработке ваших данных")
                     return
              
              bitrix_result = await send_lead_to_bitrix(client_data)
              
              # Дополнительная проверка результата
              if not bitrix_result or 'error' in bitrix_result:
                     print("⚠️ Ошибка при отправке в Bitrix24:", bitrix_result.get('error', 'Unknown error'))
              
       except Exception as e:
              print(f"❌ Критическая ошибка в обработчике: {str(e)}")
              await send_whatsapp_response(
              from_number,
              "⚠️ Произошла техническая ошибка. Пожалуйста, попробуйте позже."
              )