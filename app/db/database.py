from databases import Database
from app.config import DATABASE_URL

# Переименовали переменную, чтобы избежать конфликта
db = Database(DATABASE_URL)

async def connect_db():
    await db.connect()

async def disconnect_db():
    await db.disconnect()

async def save_message(phone: str, message: str, role: str):
    # 1. Сохраняем клиента, если его ещё нет
    insert_client_query = """
    INSERT INTO clients (phone, first_name, last_name)
    VALUES (:phone, '', '')
    ON CONFLICT (phone) DO NOTHING;
    """

    # 2. Сохраняем сообщение
    insert_message_query = """
    INSERT INTO messages (phone, message, sender_role)
    VALUES (:phone, :message, :sender_role);
    """

    await db.execute(query=insert_client_query, values={"phone": phone})
    await db.execute(query=insert_message_query, values={"phone": phone, "message": message, "sender_role": role})

# Получение последних сообщений
async def get_last_messages(phone: str, limit: int = 100):
    query = """
        SELECT sender_role, message FROM messages
        WHERE phone = :phone
        ORDER BY received_at DESC
        LIMIT :limit
    """
    rows = await db.fetch_all(query, values={"phone": phone, "limit": limit})
    return list(reversed(rows))  # чтобы шли в хронологическом порядке
