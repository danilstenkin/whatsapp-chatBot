# 🤖 WhatsApp GPT-Бот для юридической компании

Этот проект представляет собой интеллектуального WhatsApp-бота, который помогает пользователям с юридическими вопросами по долгам и кредитам. Бот общается с клиентами, собирает данные, использует GPT для генерации ответов и сохраняет информацию в базу данных.

---

## 🚀 Стек технологий

- 🐍 Python 3.12
- ⚡ FastAPI
- 🐘 PostgreSQL
- 🔥 Redis
- 🧠 OpenAI (через OpenRouter API)
- 📞 Twilio WhatsApp API
- 🐳 Docker + Docker Compose

---

## 📦 Установка и запуск

1. **Клонируй репозиторий:**

```bash
git clone https://github.com/yourusername/whatsapp-chatBot.git
cd whatsapp-chatBot

Создай .env файл в корне проекта:

DB_USER=myuser
DB_PASS=mypassword
DB_NAME=whatsapp
DB_HOST=localhost
DB_PORT=5432

REDIS_HOST=127.0.0.1
REDIS_PORT=6379

OPENROUTER_API_KEY=sk-...

TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

ENCRYPTION_KEY=...

Запусти проект с Docker Compose:

docker-compose up --build

⚙️ Структура проекта

whatsapp-chatBot/
app/
│
├── core/              # Основная бизнес-логика (GPT, AI, менеджеры)
│   ├── gpt.py
│   ├── deepseek.py
│   └── menedger.py
│
├── services/          # Внешние интеграции (Twilio, Bitrix и др.)
│   ├── messenger.py
│   ├── create_task_in_bitrix.py
│   └── security.py
│
├── db/                # Работа с БД и инициализация
│   ├── database.py
│   ├── init.sql
│   ├── redis_client.py
│   └── utils.py
│
├── routers/           # Роуты FastAPI
│   └── whatsapp.py
│
├── state/             # Хранение логики состояний
│   └── lead_state.py
│
├── validators/        # Валидация данных
│   ├── credit_types.py
│   └── user_data.py
│
├── workers/           # Очереди, фоновые задачи
│   ├── send_worker.py
│   ├── queue_senders.py
│   └── config.py
│
├── logger_config.py   # Логгер
└── config.py          # Конфигурация проекта (dotenv, ключи и т.п.)


🔧 Возможности

    📲 Общение с клиентами через WhatsApp

    🧠 Ответы с помощью GPT (OpenRouter API)

    💾 Хранение информации в PostgreSQL

    ⚙️ Управление состоянием через Redis

    ✅ Валидация данных (ФИО, ИИН, кредиты, доходы и др.)

    📋 Пошаговая анкета для оценки банкротства

🧪 Примеры API

POST /whatsapp

Webhook для получения входящих сообщений от Twilio.
📄 Лицензия

MIT — свободно использовать, менять и распространять.
👨‍💻 Автор

Разработчик: @danilstenkin


