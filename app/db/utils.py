from app.db.database import db

async def has_client_first_name(phone: str) -> bool:
    query = "SELECT first_name FROM clients WHERE phone = :phone"
    row = await db.fetch_one(query=query, values={"phone": phone})
    return bool(row and row["first_name"])

async def save_client_first_name(phone: str, first_name: str):
    query = """
    UPDATE clients
    SET first_name = :first_name
    WHERE phone = :phone
    """
    result = await db.execute(query=query, values={"phone": phone, "first_name": first_name})
    return result
