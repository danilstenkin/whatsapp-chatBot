from app.db.database import db

async def has_client_first_name(phone: str) -> bool:
    query = "SELECT first_name FROM clients WHERE phone = :phone"
    row = await db.fetch_one(query=query, values={"phone": phone})
    return bool(row and row["first_name"])
