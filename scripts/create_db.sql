-- LeaseGrow: создание схемы БД PostgreSQL
-- Соответствует моделям Django (core.models)

-- Проверка: если схема уже создана — не перезаписываем
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'role') THEN
    RAISE NOTICE 'База данных уже существует. Таблицы не пересоздаются.';
  END IF;
END $$;

-- Роли пользователей
CREATE TABLE IF NOT EXISTS role (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Аккаунты
CREATE TABLE IF NOT EXISTS account (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id BIGINT REFERENCES role(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_account_email ON account(email);
CREATE INDEX IF NOT EXISTS idx_account_username ON account(username);

-- Профили пользователей
CREATE TABLE IF NOT EXISTS user_profile (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL UNIQUE REFERENCES account(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) DEFAULT '',
    avatar_url VARCHAR(500) DEFAULT '',
    birth_date DATE,
    preferred_language VARCHAR(10) DEFAULT 'ru',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API токены
CREATE TABLE IF NOT EXISTS account_token (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(64) NOT NULL UNIQUE,
    account_id BIGINT NOT NULL REFERENCES account(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_account_token_key ON account_token(key);

-- Компании
CREATE TABLE IF NOT EXISTS company (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(500) DEFAULT '',
    inn VARCHAR(12) NOT NULL UNIQUE,
    kpp VARCHAR(9) DEFAULT '',
    ogrn VARCHAR(15) DEFAULT '',
    legal_address TEXT DEFAULT '',
    actual_address TEXT DEFAULT '',
    phone VARCHAR(20) DEFAULT '',
    email VARCHAR(255) DEFAULT '',
    bank_details JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'blocked', 'pending')),
    account_id BIGINT REFERENCES account(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Контакты компаний
CREATE TABLE IF NOT EXISTS company_contact (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(150) DEFAULT '',
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) DEFAULT '',
    is_main BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Категории техники (иерархия)
CREATE TABLE IF NOT EXISTS equipment_category (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    parent_id BIGINT REFERENCES equipment_category(id) ON DELETE SET NULL,
    description TEXT DEFAULT '',
    icon_url VARCHAR(500) DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Производители
CREATE TABLE IF NOT EXISTS manufacturer (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    country VARCHAR(100) DEFAULT '',
    website VARCHAR(500) DEFAULT '',
    description TEXT DEFAULT '',
    logo_url VARCHAR(500) DEFAULT ''
);

-- Техника
CREATE TABLE IF NOT EXISTS equipment (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(150) NOT NULL,
    category_id BIGINT NOT NULL REFERENCES equipment_category(id) ON DELETE RESTRICT,
    manufacturer_id BIGINT REFERENCES manufacturer(id) ON DELETE SET NULL,
    specifications JSONB DEFAULT '{}',
    year INTEGER,
    vin VARCHAR(100) UNIQUE,
    condition VARCHAR(50) DEFAULT 'new' CHECK (condition IN ('new', 'used', 'refurbished')),
    price DECIMAL(12, 2) NOT NULL,
    residual_value DECIMAL(12, 2),
    monthly_lease_rate DECIMAL(8, 2),
    status VARCHAR(50) DEFAULT 'available' CHECK (status IN ('available', 'leased', 'maintenance', 'sold')),
    location VARCHAR(500) DEFAULT '',
    images_urls JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Договоры лизинга
CREATE TABLE IF NOT EXISTS lease_contract (
    id BIGSERIAL PRIMARY KEY,
    contract_number VARCHAR(100) NOT NULL UNIQUE,
    company_id BIGINT NOT NULL REFERENCES company(id) ON DELETE RESTRICT,
    equipment_id BIGINT NOT NULL REFERENCES equipment(id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    lease_term_months INTEGER NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    advance_payment DECIMAL(12, 2),
    monthly_payment DECIMAL(10, 2) NOT NULL,
    payment_day INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'terminated')),
    signed_at TIMESTAMP WITH TIME ZONE,
    signed_by_id BIGINT REFERENCES account(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_id BIGINT REFERENCES account(id) ON DELETE SET NULL
);

-- График платежей
CREATE TABLE IF NOT EXISTS payment_schedule (
    id BIGSERIAL PRIMARY KEY,
    contract_id BIGINT NOT NULL REFERENCES lease_contract(id) ON DELETE CASCADE,
    payment_number INTEGER NOT NULL,
    due_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled')),
    paid_at TIMESTAMP WITH TIME ZONE,
    penalty_amount DECIMAL(10, 2) DEFAULT 0,
    UNIQUE(contract_id, payment_number)
);

-- Обслуживание техники
CREATE TABLE IF NOT EXISTS maintenance (
    id BIGSERIAL PRIMARY KEY,
    equipment_id BIGINT NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    description TEXT DEFAULT '',
    cost DECIMAL(10, 2),
    performed_at DATE NOT NULL,
    next_maintenance_date DATE,
    service_company VARCHAR(255) DEFAULT '',
    documents_urls JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by_id BIGINT REFERENCES account(id) ON DELETE SET NULL
);

-- Заявки на обслуживание
CREATE TABLE IF NOT EXISTS maintenance_request (
    id BIGSERIAL PRIMARY KEY,
    equipment_id BIGINT NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    company_id BIGINT NOT NULL REFERENCES company(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    urgency VARCHAR(50) DEFAULT 'normal' CHECK (urgency IN ('low', 'normal', 'high', 'critical')),
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'in_progress', 'completed', 'cancelled')),
    assigned_to_id BIGINT REFERENCES account(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Журнал аудита
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_fields JSONB DEFAULT '[]',
    performed_by_id BIGINT REFERENCES account(id) ON DELETE SET NULL,
    performed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_audit_table_record ON audit_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_audit_performed_at ON audit_log(performed_at);
