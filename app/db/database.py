from databases import Database
from app.config import DATABASE_URL
from app.logger_config import logger

# Переименовали переменную, чтобы избежать конфликта
db = Database(DATABASE_URL)

async def connect_db():
    await db.connect()

async def disconnect_db():
    await db.disconnect()

async def save_message(phone: str, message: str, role: str):
    # 1. Пытаемся вставить клиента с возвратом id
    insert_client_query = """
    INSERT INTO clients (phone)
    VALUES (:phone)
    ON CONFLICT (phone) DO NOTHING
    RETURNING id;
    """
    result = await db.fetch_one(query=insert_client_query, values={"phone": phone})
    
    if result:
        logger.info(f"[BD-clients][{phone}] сообщение успешно сохранено")

    # 2. Сохраняем сообщение
    insert_message_query = """
    INSERT INTO messages (phone, message, sender_role)
    VALUES (:phone, :message, :sender_role)
    RETURNING id;
    """
    result_mes = await db.fetch_one(query=insert_message_query, values={
        "phone": phone,
        "message": message,
        "sender_role": role  # 'user' или 'assistant'
    })
    if result_mes:
        logger.info(f"[BD-messages][{phone}] сообщение успешно сохранено")

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
