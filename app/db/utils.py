from app.db.database import db
from typing import Optional, Dict, Any
import logging
from app.services.security import decrypt
from app.logger_config import logger

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

async def update_full_name_by_phone(phone: str, full_name: str):
    query = """
        UPDATE clients
        SET full_name = :full_name
        WHERE phone = :phone
        RETURNING id
    """
    if await db.fetch_one(query, {"phone": phone, "full_name": full_name}):
        logger.debug(f"[{phone}][DB-clients] - ФИО сохранено")
    else:
        logger.error(f"[{phone}][DB-clients] - не удалось сохранить ")

async def update_city_by_phone(phone: str, city: str) -> bool:
    query = """
        UPDATE clients
        SET city = :city
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"city": city, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Город успешно обновлён: {city}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить город.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении города: {str(e)}", exc_info=True)
        return False


async def update_iin_by_phone(phone: str, iin: str) -> bool:
    query = """
        UPDATE clients
        SET iin = :iin
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"iin": iin, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] ИИН успешно обновлён: {iin}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить ИИН.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении ИИН: {str(e)}", exc_info=True)
        return False

async def update_credit_types_by_phone(phone: str, credit_types: list[str]) -> bool:
    query = """
        UPDATE clients
        SET credit_types = :credit_types
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"credit_types": credit_types, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Типы кредитов успешно обновлены: {credit_types}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить типы кредитов.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении типов кредитов: {str(e)}", exc_info=True)
        return False


async def update_total_debt_by_phone(phone: str, total_debt: float) -> bool:
    query = """
        UPDATE clients 
        SET total_debt = :total_debt
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"total_debt": total_debt, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Сумма долга успешно обновлена: {total_debt}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить сумму долга.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении суммы долга: {str(e)}", exc_info=True)
        return False


async def update_monthly_payment_by_phone(phone: str, monthly_payment: float) -> bool:
    query = """
        UPDATE clients 
        SET monthly_payment = :monthly_payment
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"monthly_payment": monthly_payment, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Ежемесячный платёж успешно обновлён: {monthly_payment}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить ежемесячный платёж.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении ежемесячного платежа: {str(e)}", exc_info=True)
        return False



async def update_overdue_days_by_phone(phone: str, overdue_days: str) -> bool:
    query = """
        UPDATE clients 
        SET overdue_days = :overdue_days
        WHERE phone = :phone
        RETURNING id
    """  
    try:
        result = await db.fetch_one(query, {"overdue_days": overdue_days, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Количество дней просрочки успешно обновлено: {overdue_days}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить количество дней просрочки.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении просрочки: {str(e)}", exc_info=True)
        return False


async def update_has_overdue_by_phone(phone: str, has_overdue: bool) -> bool:
    query = """
        UPDATE clients
        SET has_overdue = :has_overdue
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"has_overdue": has_overdue, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'has_overdue' успешно обновлено: {has_overdue}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'has_overdue'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'has_overdue': {str(e)}", exc_info=True)
        return False


async def update_has_official_income_by_phone(phone: str, has_official_income: bool) -> bool:
    query = """
        UPDATE clients
        SET has_official_income = :has_official_income
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"has_official_income": has_official_income, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'has_official_income' успешно обновлено: {has_official_income}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'has_official_income'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'has_official_income': {str(e)}", exc_info=True)
        return False


async def update_has_business_by_phone(phone: str, has_business: bool) -> bool:
    query = """
        UPDATE clients
        SET has_business = :has_business
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"has_business": has_business, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'has_business' успешно обновлено: {has_business}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'has_business'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'has_business': {str(e)}", exc_info=True)
        return False



async def update_has_property_by_phone(phone: str, has_property: bool) -> bool:
    query = """
        UPDATE clients
        SET has_property = :has_property
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"has_property": has_property, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'has_property' успешно обновлено: {has_property}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'has_property'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'has_property': {str(e)}", exc_info=True)
        return False



async def update_property_types_by_phone(phone: str, property_types: list[str]) -> bool:
    query = """
        UPDATE clients 
        SET property_types = :property_types
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"property_types": property_types, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'property_types' успешно обновлено: {property_types}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'property_types'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'property_types': {str(e)}", exc_info=True)
        return False


async def update_has_spouse_by_phone(phone: str, has_spouse: bool) -> bool:
    query = """
        UPDATE clients
        SET has_spouse = :has_spouse
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"has_spouse": has_spouse, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'has_spouse' успешно обновлено: {has_spouse}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'has_spouse'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'has_spouse': {str(e)}", exc_info=True)
        return False



async def update_social_status_by_phone(phone: str, social_status: list[str]) -> bool:
    query = """
        UPDATE clients 
        SET social_status = :social_status
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"social_status": social_status, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'social_status' успешно обновлено: {social_status}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'social_status'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'social_status': {str(e)}", exc_info=True)
        return False


async def update_has_children_by_phone(phone: str, has_children: bool) -> bool:
    query = """
        UPDATE clients
        SET has_children = :has_children
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"has_children": has_children, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Поле 'has_children' успешно обновлено: {has_children}")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить поле 'has_children'.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении поля 'has_children': {str(e)}", exc_info=True)
        return False


async def update_problem_description_by_phone(phone: str, problem_description: str) -> bool:
    query = """
        UPDATE clients
        SET problem_description = :problem_description
        WHERE phone = :phone
        RETURNING id
    """
    try:
        result = await db.fetch_one(query, {"problem_description": problem_description, "phone": phone})
        if result:
            logger.info(f"[{phone}][DB] Описание проблемы успешно обновлено.")
            return True
        else:
            logger.warning(f"[{phone}][DB] Не удалось обновить описание проблемы.")
            return False
    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при обновлении описания проблемы: {str(e)}", exc_info=True)
        return False


   
async def get_full_client_data(phone: str) -> Optional[Dict[str, Any]]:
    """
    Получает полные данные клиента из базы данных для отправки в Bitrix24.
    
    Args:
        phone: Номер телефона в формате '+7XXXXXXXXXX'
    
    Returns:
        Словарь с данными клиента или None, если клиент не найден или при ошибке.
    """
    query = """
        SELECT 
            id, full_name, phone, iin, city, 
            credit_types, total_debt, monthly_payment,
            has_overdue, overdue_days, has_official_income,
            has_business, has_property, property_types,
            has_spouse, has_children, social_status,
            problem_description, created_at
        FROM clients 
        WHERE phone = :phone
    """

    try:
        record = await db.fetch_one(query, {"phone": phone})
        if not record:
            logger.warning(f"[{phone}][DB] Клиент не найден в базе данных.")
            return None

        client_data = {
            "id": record["id"],
            "full_name": decrypt(record["full_name"]),
            "phone": record["phone"],
            "iin": decrypt(record["iin"]),
            "city": record["city"],
            "credit_types": list(record["credit_types"]) if record["credit_types"] else [],
            "total_debt": float(record["total_debt"]),
            "monthly_payment": float(record["monthly_payment"]),
            "has_overdue": record["has_overdue"],
            "overdue_days": record["overdue_days"],
            "has_official_income": record["has_official_income"],
            "has_business": record["has_business"],
            "has_property": record["has_property"],
            "property_types": list(record["property_types"]) if record["property_types"] else [],
            "has_spouse": record["has_spouse"],
            "has_children": record["has_children"],
            "social_status": list(record["social_status"]) if record["social_status"] else [],
            "problem_description": record["problem_description"],
            "created_at": record["created_at"].isoformat() if record["created_at"] else None
        }

        logger.info(f"[{phone}][DB] Данные клиента успешно получены.")
        return client_data

    except Exception as e:
        logger.error(f"[{phone}][DB] Ошибка при получении данных клиента: {str(e)}", exc_info=True)
        return None
