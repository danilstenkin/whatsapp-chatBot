-- Таблица клиентов
CREATE TABLE IF NOT EXISTS clients (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL DEFAULT '',                           -- Ф.И.О.
    phone VARCHAR(20) NOT NULL UNIQUE,                            -- Номер телефона
    iin TEXT NOT NULL DEFAULT '',                          -- ИИН
    city TEXT NOT NULL DEFAULT '',                                -- Город
    credit_types TEXT[] NOT NULL DEFAULT '{}',                    -- Виды кредитов (массив)
    total_debt NUMERIC(12, 2) NOT NULL DEFAULT 0.00,              -- Общая сумма задолженности
    monthly_payment NUMERIC(12, 2) NOT NULL DEFAULT 0.00,         -- Ежемесячный платёж
    has_overdue BOOLEAN NOT NULL DEFAULT FALSE,                  -- Есть ли просрочка
    overdue_days TEXT NOT NULL DEFAULT '',                     -- Кол-во дней просрочки
    has_official_income BOOLEAN NOT NULL DEFAULT FALSE,          -- Официальный доход
    has_business BOOLEAN NOT NULL DEFAULT FALSE,                 -- ИП или ТОО
    has_property BOOLEAN NOT NULL DEFAULT FALSE,                 -- Есть ли имущество
    property_types TEXT[] NOT NULL DEFAULT '{}',                 -- Типы имущества (массив)
    has_spouse BOOLEAN NOT NULL DEFAULT FALSE,                   -- Есть супруг/супруга
    has_children BOOLEAN NOT NULL DEFAULT FALSE,                 -- Есть дети
    social_status TEXT[] NOT NULL DEFAULT '{}',                  -- Социальное положение (массив)
    problem_description TEXT NOT NULL DEFAULT '',                -- Описание проблемы
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP               -- Время создания записи
);

-- Таблица сообщений
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    sender_role VARCHAR(10) NOT NULL CHECK (sender_role IN ('user', 'assistant')),
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (phone) REFERENCES clients(phone) ON DELETE CASCADE
);

ALTER DATABASE whatsapp SET TIME ZONE 'Asia/Almaty';


