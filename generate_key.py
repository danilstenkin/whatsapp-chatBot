from cryptography.fernet import Fernet

key = Fernet.generate_key()
print("🔐 Ваш ENCRYPTION_KEY:")
print(key.decode())
