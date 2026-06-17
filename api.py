from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncpg
from typing import Optional
import uuid
from datetime import datetime
import os

app = FastAPI(title="СанТехПро API")

# Разрешаем запросы с вашего сайта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение к БД - ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ!
DB_CONFIG = {
    "user": os.environ.get("DB_USER", "santehpro_user"),
    "password": os.environ.get("DB_PASSWORD", "rx5jvjsOC8bPSB7lhOxr2SrV6M9LF06A"),
    "database": os.environ.get("DB_NAME", "santehpro_db"),
    "host": os.environ.get("DB_HOST", "dpg-d8pb7pkvikkc739emp00-a"),
    "port": os.environ.get("DB_PORT", 5432),
}
DATABASE_URL = "postgresql://santehpro_user:rx5jvjsOC8bPSB7lhOxr2SrV6M9LF06A@dpg-d8pb7pkvikkc739emp00-a.frankfurt-postgres.render.com/santehpro_db"


# ============ PYDANTIC МОДЕЛИ ============
class AddToCartRequest(BaseModel):
    """Модель для добавления товара в корзину"""

    product_id: int
    quantity: int = 1


class UpdateCartRequest(BaseModel):
    """Модель для обновления корзины"""

    product_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    """Модель для создания заказа"""

    name: str
    phone: str
    email: Optional[str] = None
    address: str
    delivery_method: Optional[str] = "courier"
    payment_method: Optional[str] = "card"
    promo_code: Optional[str] = None
    comment: Optional[str] = None
    discount: int = 0


class CreateProductRequest(BaseModel):
    """Модель для создания товара"""

    name: str
    category: str
    price: float
    img: Optional[str] = None
    description: Optional[str] = None
    stock: int = 10
    popular: bool = False


class UpdateProductRequest(BaseModel):
    """Модель для обновления товара"""

    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    img: Optional[str] = None
    description: Optional[str] = None
    stock: Optional[int] = None
    popular: Optional[bool] = None


async def get_db():
    """Получение соединения с БД"""
    try:
        # conn = await asyncpg.connect(**DB_CONFIG)
        conn = await asyncpg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        raise


# ============ ТОВАРЫ (ПУБЛИЧНЫЕ) ============
@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    popular: Optional[bool] = None,
    sort: Optional[str] = None,
):
    """Получить список товаров с фильтрацией"""
    conn = None
    try:
        conn = await get_db()

        query = "SELECT * FROM products WHERE 1=1"
        params = []
        param_index = 1

        if category and category != "all":
            query += f" AND category = ${param_index}"
            params.append(category)
            param_index += 1

        if search:
            query += (
                f" AND (name ILIKE ${param_index} OR category ILIKE ${param_index})"
            )
            params.append(f"%{search}%")
            param_index += 1

        if popular:
            query += f" AND popular = ${param_index}"
            params.append(popular)
            param_index += 1

        if sort:
            if sort == "price_asc":
                query += " ORDER BY price ASC"
            elif sort == "price_desc":
                query += " ORDER BY price DESC"
            else:
                query += " ORDER BY id ASC"
        else:
            query += " ORDER BY id ASC"

        rows = await conn.fetch(query, *params)

        result = []
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "name": row["name"],
                    "category": row["category"],
                    "price": float(row["price"]),
                    "img": row["img"],
                    "description": row["description"],
                    "stock": row["stock"],
                    "popular": row["popular"],
                }
            )

        return result

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Получить один товар"""
    conn = None
    try:
        conn = await get_db()
        row = await conn.fetchrow("SELECT * FROM products WHERE id = $1", product_id)

        if not row:
            raise HTTPException(status_code=404, detail="Товар не найден")

        return {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "price": float(row["price"]),
            "img": row["img"],
            "description": row["description"],
            "stock": row["stock"],
            "popular": row["popular"],
        }

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        if conn:
            await conn.close()


# ============ АДМИН: УПРАВЛЕНИЕ ТОВАРАМИ ============
@app.post("/api/admin/products")
async def create_product(product: CreateProductRequest):
    """Создать новый товар (админ-панель)"""
    conn = None
    try:
        conn = await get_db()

        # Проверяем, существует ли товар с таким названием
        existing = await conn.fetchrow(
            "SELECT id FROM products WHERE name = $1", product.name
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Товар с таким названием уже существует"
            )

        # Добавляем товар
        row = await conn.fetchrow(
            """
            INSERT INTO products (name, category, price, img, description, stock, popular)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, name, category, price, img, description, stock, popular, created_at
            """,
            product.name,
            product.category,
            product.price,
            product.img,
            product.description,
            product.stock,
            product.popular,
        )

        return {
            "success": True,
            "message": "Товар успешно создан",
            "product": {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": float(row["price"]),
                "img": row["img"],
                "description": row["description"],
                "stock": row["stock"],
                "popular": row["popular"],
                "created_at": str(row["created_at"]),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.put("/api/admin/products/{product_id}")
async def update_product(product_id: int, product: UpdateProductRequest):
    """Обновить товар (админ-панель)"""
    conn = None
    try:
        conn = await get_db()

        # Проверяем, существует ли товар
        existing = await conn.fetchrow(
            "SELECT * FROM products WHERE id = $1", product_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Собираем поля для обновления
        updates = []
        params = []
        param_index = 1

        if product.name is not None:
            updates.append(f"name = ${param_index}")
            params.append(product.name)
            param_index += 1

        if product.category is not None:
            updates.append(f"category = ${param_index}")
            params.append(product.category)
            param_index += 1

        if product.price is not None:
            updates.append(f"price = ${param_index}")
            params.append(product.price)
            param_index += 1

        if product.img is not None:
            updates.append(f"img = ${param_index}")
            params.append(product.img)
            param_index += 1

        if product.description is not None:
            updates.append(f"description = ${param_index}")
            params.append(product.description)
            param_index += 1

        if product.stock is not None:
            updates.append(f"stock = ${param_index}")
            params.append(product.stock)
            param_index += 1

        if product.popular is not None:
            updates.append(f"popular = ${param_index}")
            params.append(product.popular)
            param_index += 1

        if not updates:
            raise HTTPException(status_code=400, detail="Нет полей для обновления")

        # Добавляем product_id в конец параметров
        params.append(product_id)
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ${param_index} RETURNING *"

        row = await conn.fetchrow(query, *params)

        return {
            "success": True,
            "message": "Товар успешно обновлён",
            "product": {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": float(row["price"]),
                "img": row["img"],
                "description": row["description"],
                "stock": row["stock"],
                "popular": row["popular"],
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.delete("/api/admin/products/{product_id}")
async def delete_product(product_id: int):
    """Удалить товар (админ-панель)"""
    conn = None
    try:
        conn = await get_db()

        # Проверяем, существует ли товар
        existing = await conn.fetchrow(
            "SELECT id, name FROM products WHERE id = $1", product_id
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Удаляем товар (каскадно удалит записи в корзине, если есть)
        await conn.execute("DELETE FROM products WHERE id = $1", product_id)

        return {
            "success": True,
            "message": f"Товар '{existing['name']}' (ID: {product_id}) успешно удалён",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


# ============ КОРЗИНА ============
def get_session_id(request: Request):
    """Получить или создать session_id"""
    session_id = request.cookies.get("cart_session")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


@app.get("/api/cart")
async def get_cart(request: Request):
    """Получить корзину"""
    conn = None
    try:
        session_id = get_session_id(request)
        conn = await get_db()

        rows = await conn.fetch(
            """
            SELECT c.product_id, c.quantity, p.name, p.price, p.img, p.category 
            FROM carts c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.session_id = $1
            """,
            session_id,
        )

        cart_items = []
        for row in rows:
            cart_items.append(
                {
                    "id": row["product_id"],
                    "name": row["name"],
                    "price": float(row["price"]),
                    "img": row["img"],
                    "category": row["category"],
                    "quantity": row["quantity"],
                }
            )

        response = JSONResponse(content=cart_items)
        response.set_cookie(
            key="cart_session", value=session_id, max_age=2592000, httponly=False
        )
        return response

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.post("/api/cart", response_model=dict)
async def add_to_cart(item: AddToCartRequest, request: Request):
    """Добавить товар в корзину"""
    conn = None
    try:
        print(
            f"📦 Получен запрос: product_id={item.product_id}, quantity={item.quantity}"
        )

        session_id = get_session_id(request)
        product_id = item.product_id
        quantity = item.quantity

        conn = await get_db()

        # Проверяем, существует ли товар
        product = await conn.fetchrow(
            "SELECT * FROM products WHERE id = $1", product_id
        )
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")

        # Проверяем, есть ли уже товар
        existing = await conn.fetchrow(
            "SELECT * FROM carts WHERE session_id = $1 AND product_id = $2",
            session_id,
            product_id,
        )

        if existing:
            await conn.execute(
                "UPDATE carts SET quantity = quantity + $1 WHERE session_id = $2 AND product_id = $3",
                quantity,
                session_id,
                product_id,
            )
            print(
                f"🔄 Обновлен товар {product_id}, новое количество: {existing['quantity'] + quantity}"
            )
        else:
            await conn.execute(
                "INSERT INTO carts (session_id, product_id, quantity) VALUES ($1, $2, $3)",
                session_id,
                product_id,
                quantity,
            )
            print(f"✨ Добавлен новый товар {product_id}")

        response = JSONResponse(content={"success": True, "message": "Товар добавлен"})
        response.set_cookie(
            key="cart_session", value=session_id, max_age=2592000, httponly=False
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.put("/api/cart")
async def update_cart_item(item: UpdateCartRequest, request: Request):
    """Обновить количество товара"""
    conn = None
    try:
        session_id = get_session_id(request)
        product_id = item.product_id
        quantity = item.quantity

        conn = await get_db()

        if quantity <= 0:
            await conn.execute(
                "DELETE FROM carts WHERE session_id = $1 AND product_id = $2",
                session_id,
                product_id,
            )
        else:
            await conn.execute(
                "UPDATE carts SET quantity = $1, updated_at = CURRENT_TIMESTAMP WHERE session_id = $2 AND product_id = $3",
                quantity,
                session_id,
                product_id,
            )

        response = JSONResponse(content={"success": True})
        response.set_cookie(key="cart_session", value=session_id, max_age=2592000)
        return response

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.delete("/api/cart/{product_id}")
async def remove_from_cart(product_id: int, request: Request):
    """Удалить товар из корзины"""
    conn = None
    try:
        session_id = get_session_id(request)
        conn = await get_db()

        await conn.execute(
            "DELETE FROM carts WHERE session_id = $1 AND product_id = $2",
            session_id,
            product_id,
        )

        response = JSONResponse(content={"success": True})
        response.set_cookie(key="cart_session", value=session_id, max_age=2592000)
        return response

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


# ============ ЗАКАЗЫ ============
@app.post("/api/orders")
async def create_order(order: CreateOrderRequest, request: Request):
    """Создать заказ"""
    conn = None
    try:
        session_id = get_session_id(request)
        conn = await get_db()

        # Получаем корзину
        cart_items = await conn.fetch(
            """
            SELECT c.*, p.name, p.price 
            FROM carts c 
            JOIN products p ON c.product_id = p.id 
            WHERE c.session_id = $1
            """,
            session_id,
        )

        if not cart_items:
            raise HTTPException(status_code=400, detail="Корзина пуста")

        # Считаем суммы
        subtotal = sum(item["price"] * item["quantity"] for item in cart_items)
        delivery_cost = (
            500
            if order.delivery_method == "courier"
            else (300 if order.delivery_method == "post" else 0)
        )
        discount = order.discount
        total = subtotal - discount + delivery_cost

        # Генерируем номер заказа
        order_number = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Создаем заказ
        await conn.execute(
            """
            INSERT INTO orders (
                order_number, customer_name, customer_phone, customer_email, customer_address,
                delivery_method, payment_method, subtotal, discount, delivery_cost, total,
                promo_code, comment, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, 'pending')
            """,
            order_number,
            order.name,
            order.phone,
            order.email,
            order.address,
            order.delivery_method,
            order.payment_method,
            subtotal,
            discount,
            delivery_cost,
            total,
            order.promo_code,
            order.comment,
        )

        # Получаем ID заказа
        order_id_row = await conn.fetchrow(
            "SELECT id FROM orders WHERE order_number = $1", order_number
        )
        order_id = order_id_row["id"]

        # Добавляем товары в заказ
        for item in cart_items:
            await conn.execute(
                """
                INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                VALUES ($1, $2, $3, $4, $5)
                """,
                order_id,
                item["product_id"],
                item["name"],
                item["quantity"],
                item["price"],
            )

            # Уменьшаем остаток
            await conn.execute(
                "UPDATE products SET stock = stock - $1 WHERE id = $2",
                item["quantity"],
                item["product_id"],
            )

        # Очищаем корзину
        await conn.execute("DELETE FROM carts WHERE session_id = $1", session_id)

        response = JSONResponse(content={"success": True, "order_number": order_number})
        response.set_cookie(key="cart_session", value=session_id, max_age=2592000)
        return response

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


@app.get("/api/orders")
async def get_orders():
    """Получить список заказов"""
    conn = None
    try:
        conn = await get_db()
        rows = await conn.fetch(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 50"
        )

        result = []
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "order_number": row["order_number"],
                    "customer_name": row["customer_name"],
                    "total": float(row["total"]),
                    "status": row["status"],
                    "created_at": str(row["created_at"]),
                }
            )

        return result

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


# ============ ПРОМОКОДЫ ============
@app.get("/api/promo/{code}")
async def check_promo(code: str, subtotal: float = 0):
    """Проверить промокод"""
    conn = None
    try:
        conn = await get_db()

        promo = await conn.fetchrow(
            """
            SELECT * FROM promocodes 
            WHERE code = $1 AND is_active = true 
            AND (expires_at IS NULL OR expires_at > CURRENT_DATE)
            AND min_order_amount <= $2
            """,
            code.upper(),
            subtotal,
        )

        if promo:
            if promo["discount_type"] == "percent":
                discount = subtotal * float(promo["discount_value"]) / 100
            else:
                discount = float(promo["discount_value"])

            return {
                "valid": True,
                "discount": discount,
                "type": promo["discount_type"],
                "code": code,
            }

        return {"valid": False}

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            await conn.close()


# ============ ТЕСТОВЫЙ ЭНДПОИНТ ============
@app.get("/api/test")
async def test():
    """Тестовый эндпоинт для проверки работы API"""
    return {"status": "ok", "message": "API работает!"}


# ============ ЗАПУСК ============
if __name__ == "__main__":
    import uvicorn

    print("🚀 Запуск сервера на http://localhost:8000")
    print("📖 Документация API: http://localhost:8000/docs")
    print("🧪 Тест: http://localhost:8000/api/test")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
