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
