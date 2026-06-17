// ============ КОРЗИНА (для страницы cart.html) ============

const API_URL = "http://localhost:8000/api";

// Получение корзины с сервера
async function getCartFromServer() {
  try {
    const response = await fetch(`${API_URL}/cart`, {
      credentials: "include",
    });
    if (!response.ok) throw new Error("Ошибка загрузки корзины");
    return await response.json();
  } catch (error) {
    console.error("Ошибка загрузки корзины:", error);
    return [];
  }
}

// Обновление количества товара на сервере
async function updateCartOnServer(productId, quantity) {
  try {
    const response = await fetch(`${API_URL}/cart`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ product_id: productId, quantity: quantity }),
    });
    if (!response.ok) throw new Error("Ошибка обновления");
    return await response.json();
  } catch (error) {
    console.error("Ошибка обновления корзины:", error);
    throw error;
  }
}

// Удаление товара с сервера
async function removeFromCartServer(productId) {
  try {
    const response = await fetch(`${API_URL}/cart/${productId}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!response.ok) throw new Error("Ошибка удаления");
    return await response.json();
  } catch (error) {
    console.error("Ошибка удаления товара:", error);
    throw error;
  }
}

// Отображение корзины
async function renderCartPage() {
  const container = document.getElementById("cartContent");
  if (!container) return;

  try {
    container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px;">
                <i class="fas fa-spinner fa-pulse" style="font-size: 3rem; color: #e67e22;"></i>
                <p style="margin-top: 20px;">Загрузка корзины...</p>
            </div>
        `;

    const cart = await getCartFromServer();

    if (cart.length === 0) {
      container.innerHTML = `
                <div style="text-align: center; padding: 60px 20px;">
                    <i class="fas fa-shopping-cart" style="font-size: 4rem; color: #ccc; margin-bottom: 20px;"></i>
                    <p style="font-size: 1.2rem; color: #666; margin-bottom: 20px;">Ваша корзина пуста</p>
                    <a href="catalog.html" style="background: #e67e22; color: white; padding: 12px 30px; border-radius: 40px; text-decoration: none; display: inline-block;">Перейти в каталог</a>
                </div>
            `;
      return;
    }

    const subtotal = cart.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0,
    );
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    container.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 380px; gap: 30px;">
                <div style="background: white; border-radius: 24px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                    <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 0.5fr; padding: 15px 0; border-bottom: 2px solid #f0f0f0; font-weight: 600; color: #666;">
                        <span>Товар</span><span>Цена</span><span>Количество</span><span></span>
                    </div>
                    ${cart
                      .map(
                        (item) => `
                        <div style="display: grid; grid-template-columns: 3fr 1fr 1fr 0.5fr; align-items: center; padding: 20px 0; border-bottom: 1px solid #f0f0f0;">
                            <div style="display: flex; gap: 15px; align-items: center;">
                                <div style="width: 70px; height: 70px; background: #f1f5f9; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">${item.img || "🚿"}</div>
                                <div>
                                    <h4 style="margin-bottom: 5px;">${escapeHtml(item.name)}</h4>
                                    <p style="color: #94a3b8; font-size: 0.85rem;">${item.category || ""}</p>
                                </div>
                            </div>
                            <div style="font-weight: 600; color: #e67e22;">${item.price.toLocaleString()} ₽</div>
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <button onclick="window.updateQuantity(${item.id}, ${item.quantity - 1})" style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid #ddd; background: white; cursor: pointer;">-</button>
                                <span style="min-width: 40px; text-align: center; font-weight: 600;">${item.quantity}</span>
                                <button onclick="window.updateQuantity(${item.id}, ${item.quantity + 1})" style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid #ddd; background: white; cursor: pointer;">+</button>
                            </div>
                            <div onclick="window.removeFromCart(${item.id})" style="color: #ef4444; cursor: pointer; text-align: center; font-size: 1.2rem;">
                                <i class="fas fa-trash"></i>
                            </div>
                        </div>
                    `,
                      )
                      .join("")}
                </div>
                
                <div style="background: white; border-radius: 24px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); position: sticky; top: 120px;">
                    <h3 style="margin-bottom: 20px;">Итого</h3>
                    <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
                        <span>Товары (${totalItems} шт.)</span>
                        <span>${subtotal.toLocaleString()} ₽</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0;">
                        <span>Доставка</span>
                        <span>Рассчитывается при оформлении</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 1.3rem; font-weight: 700; color: #e67e22; margin-top: 15px; padding-top: 15px; border-top: 2px solid #f0f0f0;">
                        <span>Итого:</span>
                        <span>${subtotal.toLocaleString()} ₽</span>
                    </div>
                    <button onclick="window.checkout()" style="width: 100%; background: #e67e22; color: white; border: none; padding: 16px; border-radius: 40px; font-size: 1.1rem; font-weight: 600; cursor: pointer; margin-top: 20px;">Оформить заказ</button>
                    <button onclick="window.clearCart()" style="width: 100%; background: transparent; color: #ef4444; border: 1px solid #ef4444; padding: 12px; border-radius: 40px; cursor: pointer; margin-top: 10px;">Очистить корзину</button>
                </div>
            </div>
        `;

    await updateCartCounter();
  } catch (error) {
    console.error("Ошибка:", error);
    container.innerHTML = `<div style="text-align: center; padding: 60px; color: #ef4444;">Ошибка загрузки корзины</div>`;
  }
}

async function updateQuantity(productId, newQuantity) {
  if (newQuantity < 1) {
    await removeFromCart(productId);
    return;
  }
  try {
    await updateCartOnServer(productId, newQuantity);
    await renderCartPage();
  } catch (error) {
    showToast("Ошибка обновления", "error");
  }
}

async function removeFromCart(productId) {
  try {
    await removeFromCartServer(productId);
    await renderCartPage();
    showToast("Товар удален", "success");
  } catch (error) {
    showToast("Ошибка удаления", "error");
  }
}

async function clearCart() {
  if (!confirm("Очистить всю корзину?")) return;
  try {
    const cart = await getCartFromServer();
    for (const item of cart) {
      await removeFromCartServer(item.id);
    }
    await renderCartPage();
    showToast("Корзина очищена", "success");
  } catch (error) {
    showToast("Ошибка очистки", "error");
  }
}

async function updateCartCounter() {
  try {
    const cart = await getCartFromServer();
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const counter = document.getElementById("cartCount");
    if (counter) counter.textContent = totalItems;
  } catch (error) {
    console.error("Ошибка:", error);
  }
}

function checkout() {
  window.location.href = "checkout.html";
}

function showToast(message, type = "success") {
  let toast = document.getElementById("cartToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "cartToast";
    toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: ${type === "error" ? "#ef4444" : "#e67e22"};
            color: white;
            padding: 12px 24px;
            border-radius: 40px;
            z-index: 10000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            font-weight: 500;
        `;
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.style.display = "block";
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => {
      toast.style.display = "none";
      toast.style.opacity = "1";
    }, 300);
  }, 2500);
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>]/g, function (m) {
    if (m === "&") return "&amp;";
    if (m === "<") return "&lt;";
    if (m === ">") return "&gt;";
    return m;
  });
}

// Запуск
document.addEventListener("DOMContentLoaded", async function () {
  console.log("🛒 Загрузка страницы корзины...");
  await renderCartPage();
});

window.updateQuantity = updateQuantity;
window.removeFromCart = removeFromCart;
window.clearCart = clearCart;
window.checkout = checkout;
window.updateCartCounter = updateCartCounter;
