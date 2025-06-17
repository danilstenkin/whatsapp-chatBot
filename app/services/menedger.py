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
from datetime import datetime
from app.logger_config import logger


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
       try:
              logger.info(f"Начало обработки состояния gpt_problem_empathy для {from_number}")
              
              base_prompt = """
              РАЗГОВАРИВАЙ ВСЕГДА НА ВЫ
              Ты — доброжелательный юридический консультант Казахстанской компании YCG. Клиент только что поделился своей финансовой проблемой.
              
              Твоя задача — проявить сочувствие, показать, что он важен, и мягко уточнить какой-нибудь вопрос, который будет полезен для юриста. 
              Пиши по-человечески, не как робот, будь краток.
              Попроси чтобы ответили одним сообщением
              """
              logger.debug(f"[{from_number}][{state}] - Сформирован промт для GPT: {base_prompt.strip()[:100]}...")

              await save_message(from_number, message_text, role="user")

              logger.info(f"[{from_number}][{state}] - Инициирован запрос к GPT для генерации ответа {from_number}")

              reply = await generate_reply(from_number, message_text, base_prompt)

              await send_whatsapp_response(from_number, reply)
              await save_message(from_number, reply, role="assistant")

              if await set_lead_state(from_number, "gpt_problem_dig_deeper"):
                    logger.info(f"[{from_number}][{state}] - Состояние изменено на gpt_problem_dig_deeper для {from_number}")

       except Exception as e:
              logger.error(f"[{from_number}][{state}] - Ошибка в состоянии gpt_problem_empathy для {from_number}: {str(e)}", exc_info=True)
              
              error_message = "Извините, возникла техническая ошибка. Пожалуйста, попробуйте написать позже."
              await send_whatsapp_response(from_number, error_message)
              logger.error(f"[{from_number}][{state}] - Пользователю {from_number} отправлено сообщение об ошибке")


    elif state == "gpt_problem_dig_deeper":
       try:
              logger.info(f"[DEEP DIVE] Начало обработки для {from_number}")
              logger.debug(f"Входящее сообщение: {message_text[:200]}...")

              base_prompt = """
              РАЗГОВАРИВАЙ ВСЕГДА НА ВЫ
              Ты — Казахстанский юридический консультант YCG. Клиент рассказал о своей проблеме, теперь нужно уточнить детали, которые будут полезны юристу.
              Опирайся на диалог (клиент - user, ты - assistant).
              Не говори что делать, задай конкретный уточняющий вопрос по делу.
              Попроси ответить одним сообщением.
              """
              await save_message(from_number, message_text, role="user")
              logger.info(f"[{from_number}][{state}] - Сообщение пользователя {from_number} сохранено в истории")

              start_time = datetime.now()
              gpt_reply = await generate_reply(from_number, message_text, base_prompt)
              exec_time = (datetime.now() - start_time).total_seconds()
              
              logger.info(f"[{from_number}][{state}] - GPT ответ сгенерирован за {exec_time:.2f} сек")
              logger.debug(f"[{from_number}][{state}] - Ответ GPT ({len(gpt_reply)} chars): {gpt_reply[:200]}...")

              if not gpt_reply or len(gpt_reply.strip()) < 10:
                     logger.error(f"[{from_number}][{state}] - GPT вернул пустой или слишком короткий ответ")
                     raise ValueError("Невалидный ответ от GPT")

              await send_whatsapp_response(from_number, gpt_reply)
              await save_message(from_number, gpt_reply, role="assistant")
              logger.info(f"[{from_number}][{state}] - Ответ успешно отправлен и сохранен")

              await set_lead_state(from_number, "gpt_offer_consultation")
              logger.info(f"[{from_number}][{state}] - Переход в состояние gpt_offer_consultation")

              if "?" not in gpt_reply:
                     logger.warning("GPT не задал вопрос в ответе")

       except Exception as e:
              logger.error(f"[{from_number}][{state}] - Ошибка в gpt_problem_dig_deeper: {str(e)}", exc_info=True)
              
              fallback_msg = "Благодарю за информацию. Чтобы предложить решение, мне нужно уточнить один момент. Расскажите, как давно у вас эта проблема?"
              await send_whatsapp_response(from_number, fallback_msg)
              await set_lead_state(from_number, "gpt_offer_consultation")
              
              logger.info(f"[{from_number}] - Отправлен fallback-ответ и осуществлен переход")


    elif state == "gpt_offer_consultation":   
          try:
                logger.info(f"[CONSULTATION OFFER] - Начало обработки для {from_number}")
                logger.debug(f"[{from_number}][{state}] - Входящее сообщение: {message_text[:200]}...")

                base = """
              Ты — ведущий Казахстанский юрист-консультант YCG. Сформулируй ответ клиенту по следующим правилам:

              1. Формат ответа:
              Исходя из описанной ситуации с {кратко_суть_проблемы}, мы наблюдаем {основные_риски}.
              Не задавай ни одного вопроса Будь краток и твоя главная задача убедить человека что ему надо к нам придти
              Когда хочешь сделать текст жирным делай вот так ->  *привет*

              2. Требования к стилю:
              ▸ Строго на "Вы"
              ▸ Уважительно, но твердо
              ▸ Без вопросов в конце
              ▸ Без фраз "хотите записаться?"
              ▸ Акцент на срочность и бесплатность

              3. Пример ответа:
              «Анализируя вашу ситуацию с долгами в 3 банках, мы видим риски:
              - Возможность ареста имущества в течение месяца
              - Рост задолженности на 15-20% ежеквартально

              Только после изучения договоров и судебной практики по вашему региону мы сможем:
              - Определить законные основания для отсрочки
              - Предложить варианты реструктуризации
              - Защитить ваши права как заемщика

              Запишитесь на бесплатную консультацию в YCG — это единственный способ получить точный прогноз и план действий.»

              5. Запрещено:
              × Давать конкретные юридические советы
              × Использовать шаблонные фразы
              × Упоминать конкурентов
              """
       
                await save_message(from_number, message_text, role="user")
                logger.debug(f"[{from_number}][{state}] - сообщение пользователя сохранено в историю")

                start_time = datetime.now()
                reply = await generate_reply(from_number, message_text, base)
                exec_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"[{from_number}][{state}] - GPT ответ сгенирован за {exec_time:.2f} сек")

                if not generate_reply or len(reply.strip()) < 20:
                      logger.error(f"[{from_number}][{state}] - GPT вернул неполноценный ответ")
                      raise ValueError("Недостаточный ответ от GPT")

                await send_whatsapp_response(from_number, reply)
                logger.info(f"[{from_number}][{state}] - отправлен ответ от GPT")
                await save_message(from_number, reply, role="assistant")
                logger.info(f"[{from_number}][{state}] - GPT ответ сохранен в БД")

                confirmation_msg = "✅ Готовы ли Вы записаться на бесплатную консультацию?\nПожалуйста, напишите: Да или Нет"
                try:
                     sent = await send_whatsapp_response(from_number, confirmation_msg)
                     if not sent:
                            logger.error(f"[{from_number}][{state}] - Не удалось отправить подтверждение")

                except Exception as e:
                     logger.error(f"[{from_number}][{state}] - Ошибка отправки: {str(e)}")

                await set_lead_state(from_number, "questionnaire")
                logger.info(f"[{from_number}][{state}] - переход на состояние -> 'questionnaire'")

          except Exception as e:
                logger.error(f"[{from_number}][{state}] - Критическая ошибка в gpt_offer_consultation: {str(e)}", exc_info=True)


                fallback_msg = (
              "Благодарю за информацию. Для точной оценки вашего случая "
              "необходима консультация юриста YCG. Это бесплатно и ни к чему не обязывает. "
              "Готовы ли вы продолжить? (Да/Нет)"
                )

                await send_whatsapp_response(from_number, fallback_msg)
                await set_lead_state(from_number, "questionnaire")
                logger.info(f"[{from_number}][{state}] - Отправлен fallback-вариант для {from_number}")


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

              # 4. Отправляем сообщение клиенту
              await send_whatsapp_response(
              from_number,
              "✅ Анкета успешно заполнена!\n"
              "Наш специалист свяжется с вами в ближайшее время.\n\n"
              "Спасибо за предоставленную информацию!"
              )
              
              # 2. Генерируем описание проблемы
              base = """Твоя задача - создать краткое описание проблемы клиента для юристов  это сообщение пойдет в Bitrix24 и мы юристы из Казахстана, не ставь нигде ** и * если что надо сделать жирным ьексьом используй такую конструкцию [b]Дети:[/b]"""
              problem = await generate_reply(from_number, "", base)
              await update_problem_description_by_phone(from_number, problem)
              
              # 3. Логируем в консоль (для отладки)
              print("✅ Анкета заполнена для номера:", from_number)
              
              
              
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