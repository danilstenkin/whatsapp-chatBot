import httpx
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

BITRIX_WEBHOOK = "https://b24-imkpl7.bitrix24.kz/rest/1/rm2pidyky98kq624"

async def send_lead_to_bitrix(client_data: dict) -> bool:
    """
    Создаёт лид и оставляет комментарий с анкетой клиента.
    """
    comments = (
        f"[b]Имя:[/b] {client_data['full_name']}\n"
        f"[b]Телефон:[/b] {client_data['phone']}\n"
        f"[b]ИИН:[/b] {client_data['iin']}\n"
        f"[b]Город:[/b] {client_data['city']}\n"
        f"[b]Кредиты:[/b] {', '.join(client_data['credit_types'])}\n"
        f"[b]Сумма долга:[/b] {client_data['total_debt']:.2f}\n"
        f"[b]Ежемесячный платёж:[/b] {client_data['monthly_payment']:.2f}\n"
        f"[b]Просрочка:[/b] {'Да' if client_data['has_overdue'] else 'Нет'} ({client_data['overdue_days']})\n"
        f"[b]Офиц. доход:[/b] {'Да' if client_data['has_official_income'] else 'Нет'}\n"
        f"[b]Бизнес:[/b] {'Да' if client_data['has_business'] else 'Нет'}\n"
        f"[b]Имущество:[/b] {'Да' if client_data['has_property'] else 'Нет'} ({', '.join(client_data['property_types'])})\n"
        f"[b]Супруг(а):[/b] {'Да' if client_data['has_spouse'] else 'Нет'}\n"
        f"[b]Дети:[/b] {'Да' if client_data['has_children'] else 'Нет'}\n"
        f"[b]Соц. статус:[/b] {', '.join(client_data['social_status'])}\n"
        f"\n[b]Описание проблемы:[/b]\n{client_data['problem_description']}"
)


    payload = {
        "fields": {
            "TITLE": f"Лид с WhatsApp: {client_data['full_name']}",
            "NAME": client_data["full_name"],
            "PHONE": [{"VALUE": client_data["phone"], "VALUE_TYPE": "WORK"}],
            "COMMENTS": comments # можно оставить или убрать
        }
    }

    try:
        async with httpx.AsyncClient() as client:
            # 1. Создаём лид
            response = await client.post(f"{BITRIX_WEBHOOK}/crm.lead.add.json", json=payload)

            if response.status_code != 200 or not response.json().get("result"):
                logger.error(f"Ошибка при создании лида: {response.text}")
                return False

            lead_id = response.json()["result"]
            logger.info(f"✅ Лид создан: ID {lead_id}")

            return True

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке в Bitrix24: {str(e)}")
        return False
