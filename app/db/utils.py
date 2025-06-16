from app.db.database import db
from app.services.create_task_in_bitrix import send_lead_to_bitrix
from typing import Optional, Dict, Any
import logging
from app.services.security import decrypt

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # или DEBUG

# Консольный вывод
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

from app.config import DATABASE_URL
import asyncpg



async def update_full_name_by_phone(phone: str, full_name: str):
    query = """
        UPDATE clients
        SET full_name = :full_name
        WHERE phone = :phone
    """
    await db.execute(query, {"phone": phone, "full_name": full_name})

async def update_city_by_phone(phone: str, city: str) -> bool:
    query = """
        UPDATE clients
        SET city = :city
        WHERE phone = :phone
    """
    await db.execute(query, {"city": city, "phone": phone})
    return True

async def update_iin_by_phone(phone: str, iin: str) -> bool:
    query = """
        UPDATE clients
        SET iin = :iin
        WHERE phone = :phone
        RETURNING id
    """
    result = await db.fetch_one(query, {"iin": iin, "phone": phone})
    return result is not None

async def update_credit_types_by_phone(phone: str, credit_types: list[str]) -> bool:
    query = """
        UPDATE clients
        SET credit_types = :credit_types
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"credit_types": credit_types, "phone": phone}) is not None

async def update_total_debt_by_phone(phone: str, total_debt: float) -> bool:
    query = """
    UPDATE clients 
    SET total_debt = :total_debt
    WHERE phone = :phone
    RETURNING id
"""
    return await db.fetch_one(query, {"total_debt": total_debt, "phone": phone}) is not None

async def update_monthly_payment_by_phone(phone: str, monthly_payment: float) -> bool:
    query = """
    UPDATE clients 
    SET monthly_payment = :monthly_payment
    WHERE phone = :phone
    RETURNING id
"""
    return await db.fetch_one(query, {"monthly_payment": monthly_payment, "phone": phone}) is not None


async def update_overdue_days_by_phone(phone: str, overdue_days: str) -> bool:
    query = """
    UPDATE clients 
    SET overdue_days = :overdue_days
    WHERE phone = :phone
    RETURNING id
"""  
    return await db.fetch_one(query, {"overdue_days": overdue_days, "phone": phone}) is not None

async def update_has_overdue_by_phone(phone: str, has_overdue: bool) -> bool:
    query = """
        UPDATE clients
        SET has_overdue = :has_overdue
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"has_overdue": has_overdue, "phone": phone}) is not None

async def update_has_official_income_by_phone(phone: str, has_official_income: bool) -> bool:
    query = """
        UPDATE clients
        SET has_official_income = :has_official_income
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"has_official_income": has_official_income, "phone": phone}) is not None

async def update_has_business_by_phone(phone: str, has_business: bool) -> bool:
    query = """
        UPDATE clients
        SET has_business = :has_business
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"has_business": has_business, "phone": phone}) is not None


async def update_has_property_by_phone(phone: str, has_property: bool) -> bool:
    query = """
        UPDATE clients
        SET has_property = :has_property
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"has_property": has_property, "phone": phone}) is not None


async def update_property_types_by_phone(phone: str, property_types: list[str]) -> bool:
    query = """
    UPDATE clients 
    SET property_types = :property_types
    WHERE phone = :phone
    RETURNING id
    """
    return await db.fetch_one(query, {"property_types": property_types, "phone": phone})

async def update_has_spouse_by_phone(phone: str, has_spouse: bool) -> bool:
    query = """
        UPDATE clients
        SET has_spouse = :has_spouse
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"has_spouse": has_spouse, "phone": phone}) is not None


async def update_social_status_by_phone(phone: str, social_status: list[str]) -> bool:
    query = """
    UPDATE clients 
    SET social_status = :social_status
    WHERE phone = :phone
    RETURNING id
    """
    return await db.fetch_one(query, {"social_status": social_status, "phone": phone})

async def update_has_children_by_phone(phone: str, has_children: bool) -> bool:
    query = """
        UPDATE clients
        SET has_children = :has_children
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"has_children": has_children, "phone": phone}) is not None

async def update_problem_description_by_phone(phone: str, problem_description: str) -> bool:
    query = """
        UPDATE clients
        SET problem_description = :problem_description
        WHERE phone = :phone
        RETURNING id
    """
    return await db.fetch_one(query, {"problem_description": problem_description, "phone": phone}) is not None
    

   
async def get_full_client_data(phone: str) -> Optional[Dict[str, Any]]:
    """
    Получает полные данные клиента из базы данных для отправки в Bitrix24
    
    Args:
        phone: Номер телефона в формате '+7XXXXXXXXXX'
    
    Returns:
        Словарь с данными клиента, готовыми для отправки в Bitrix24
        None если клиент не найден или произошла ошибка
    """
    conn = None
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Получаем данные клиента
        record = await conn.fetchrow(
            """
            SELECT 
                id, full_name, phone, iin, city, 
                credit_types, total_debt, monthly_payment,
                has_overdue, overdue_days, has_official_income,
                has_business, has_property, property_types,
                has_spouse, has_children, social_status,
                problem_description, created_at
            FROM clients 
            WHERE phone = $1
            """, 
            phone
        )
        
        if not record:
            logger.warning(f"Клиент с телефоном {phone} не найден в базе")
            return None
        
        # Преобразуем Record в словарь с обработкой специальных типов
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
        
        logger.info(f"Данные клиента {phone} успешно получены из БД")
        return client_data
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных клиента {phone}: {str(e)}")
        return None
    finally:
        if conn:
            await conn.close()