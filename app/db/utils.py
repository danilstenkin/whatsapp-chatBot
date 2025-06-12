from app.db.database import db

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
