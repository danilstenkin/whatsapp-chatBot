from pathlib import Path
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY")
if ENCRYPTION_KEY is None:
    raise ValueError("❌ ENCRYPTION_KEY не найден в .env!")

fernet = Fernet(ENCRYPTION_KEY)

def encrypt(data: str) -> str:
    if not data:
        return ""
    return fernet.encrypt(data.encode()).decode()

def decrypt(token: str) -> str:
    if not token:
        return ""
    return fernet.decrypt(token.encode()).decode()

