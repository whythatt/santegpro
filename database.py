import asyncpg
import asyncio

# Данные для подключения
DB_CONFIG = {
    "user": "santeh_user",
    "password": "santeh123",
    "database": "santehpro_db",
    "host": "localhost",
    "port": 5432,
}


async def create_database():
    """Создание базы данных если не существует"""
    try:
        # Подключаемся к postgres для создания БД
        conn = await asyncpg.connect(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database="postgres",
        )

        # Проверяем существует ли БД
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", DB_CONFIG["database"]
        )

        if not exists:
            await conn.execute(f'CREATE DATABASE {DB_CONFIG["database"]}')
            print(f"✅ База данных {DB_CONFIG['database']} создана")
        else:
            print(f"✅ База данных {DB_CONFIG['database']} уже существует")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Ошибка создания БД: {e}")
        return False


async def create_tables():
    """Создание всех таблиц"""
    try:
        # Сначала создаем БД
        await create_database()

        # Подключаемся к нашей БД
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Подключено к базе данных")

        # Удаляем старые таблицы (для пересоздания)
        await conn.execute("""
            DROP TABLE IF EXISTS order_items CASCADE;
            DROP TABLE IF EXISTS orders CASCADE;
            DROP TABLE IF EXISTS carts CASCADE;
            DROP TABLE IF EXISTS products CASCADE;
            DROP TABLE IF EXISTS promocodes CASCADE;
        """)
        print("✅ Старые таблицы удалены")

        # Создание таблицы товаров
        await conn.execute("""
            CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                img VARCHAR(50),
                description TEXT,
                stock INT DEFAULT 10,
                popular BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица products создана")

        # Создание таблицы корзины
        await conn.execute("""
            CREATE TABLE carts (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                quantity INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица carts создана")

        # Создание таблицы заказов
        await conn.execute("""
            CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                customer_name VARCHAR(100) NOT NULL,
                customer_phone VARCHAR(20) NOT NULL,
                customer_email VARCHAR(100),
                customer_address TEXT,
                delivery_method VARCHAR(50),
                payment_method VARCHAR(50),
                subtotal DECIMAL(10,2),
                discount DECIMAL(10,2) DEFAULT 0,
                delivery_cost DECIMAL(10,2) DEFAULT 0,
                total DECIMAL(10,2),
                promo_code VARCHAR(50),
                comment TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Таблица orders создана")

        # Создание таблицы товаров в заказе
        await conn.execute("""
            CREATE TABLE order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER REFERENCES products(id),
                product_name VARCHAR(255),
                quantity INTEGER NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
        """)
        print("✅ Таблица order_items создана")

        # Создание таблицы промокодов
        await conn.execute("""
            CREATE TABLE promocodes (
                id SERIAL PRIMARY KEY,
                code VARCHAR(50) UNIQUE NOT NULL,
                discount_type VARCHAR(20) DEFAULT 'percent',
                discount_value DECIMAL(10,2) NOT NULL,
                min_order_amount DECIMAL(10,2) DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                expires_at DATE
            )
        """)
        print("✅ Таблица promocodes создана")

        # Добавляем тестовые товары
        await conn.execute("""
            INSERT INTO products (name, category, price, img, description, popular, stock)
            VALUES 
                ('Смеситель Grohe Eurosmart', 'Смеситель', 5890, '🚰', 'Хромированный, поворотный излив, керамический картридж', true, 15),
                ('Душевая система Hansgrohe', 'Душевая', 12490, '🚿', 'Тропический дождь, термостат, 3 режима', true, 8),
                ('Унитаз подвесной Roca', 'Унитаз', 15990, '🚽', 'Компакт, сиденье микро-лифт', true, 5),
                ('Смеситель для раковины Lemark', 'Смеситель', 3450, '🚰', 'Однорычажный, керамический картридж', false, 20),
                ('Душевая стойка Lemax', 'Душевая', 7890, '🚿', 'С лейкой и верхним душем', false, 12),
                ('Раковина Blanco', 'Раковина', 8900, '💧', 'Керамическая, 60 см, с переливом', false, 7),
                ('Ванна акриловая Ravak', 'Ванна', 24990, '🛁', '170 см, с гидромассажем', false, 3),
                ('Смеситель с душем Kaiser', 'Смеситель', 4290, '🚰', 'Для ванны, с душевым шлангом', false, 10)
        """)
        print("✅ Тестовые товары добавлены")

        # Добавляем промокоды
        await conn.execute("""
            INSERT INTO promocodes (code, discount_type, discount_value, min_order_amount, is_active)
            VALUES 
                ('SANTEH20', 'percent', 20, 0, true),
                ('SANTEH500', 'fixed', 500, 3000, true),
                ('WELCOME10', 'percent', 10, 0, true)
        """)
        print("✅ Промокоды добавлены")

        # Проверяем результат
        product_count = await conn.fetchval("SELECT COUNT(*) FROM products")
        cart_count = await conn.fetchval("SELECT COUNT(*) FROM carts")

        print(f"\n📊 ИТОГО:")
        print(f"   - Товаров: {product_count}")
        print(f"   - Корзина: {cart_count} записей")
        print(f"   - Промокодов: 3")

        await conn.close()
        print("\n✅ База данных успешно создана и заполнена!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_connection():
    """Тест подключения"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Подключено к PostgreSQL: {version[:50]}...")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Не удалось подключиться: {e}")
        return False


async def main():
    print("=" * 50)
    print("🔄 НАСТРОЙКА БАЗЫ ДАННЫХ")
    print("=" * 50)

    # Тест подключения
    print("\n1. Проверка подключения...")
    if not await test_connection():
        print("\n⚠️ Убедитесь что PostgreSQL запущен:")
        print("   - Windows: net start postgresql")
        print("   - MacOS: brew services start postgresql")
        print("   - Linux: sudo service postgresql start")
        return

    # Создание таблиц
    print("\n2. Создание таблиц...")
    if await create_tables():
        print("\n" + "=" * 50)
        print("✅ ГОТОВО! База данных настроена.")
        print("=" * 50)
        print("\nТеперь запустите сервер:")
        print("   python api.py")
    else:
        print("\n❌ Ошибка при создании базы данных")


if __name__ == "__main__":
    asyncio.run(main())
