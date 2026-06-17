// ============ ТОВАРЫ ============
let products = [];

// API URL
const API_URL = "http://localhost:8000/api";

// ============ ЗАГРУЗКА ТОВАРОВ С API ============

async function loadProducts() {
  console.log("🔄 Загрузка товаров с сервера...");

  try {
    // Проверяем, есть ли контейнер для популярных товаров
    const popularContainer = document.getElementById("popularProducts");
    const catalogContainer = document.getElementById("productsGrid");

    if (popularContainer) {
      popularContainer.innerHTML =
        '<div style="text-align: center; padding: 50px">⏳ Загрузка популярных товаров...</div>';
    }
    if (catalogContainer) {
      catalogContainer.innerHTML =
        '<div style="text-align: center; padding: 50px">⏳ Загрузка товаров...</div>';
    }

    console.log("📡 Отправляем запрос на:", `${API_URL}/products`);

    const response = await fetch(`${API_URL}/products`);

    console.log("📡 Статус ответа:", response.status);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    products = await response.json();
    window.products = products;

    console.log(`✅ Загружено ${products.length} товаров`);
    console.log("📦 Товары:", products);

    renderProducts();
  } catch (error) {
    console.error("❌ Ошибка загрузки товаров:", error);

    // Показываем ошибку в обоих контейнерах
    const popularContainer = document.getElementById("popularProducts");
    const catalogContainer = document.getElementById("productsGrid");

    const errorHtml = `
            <div style="text-align: center; padding: 50px; color: #ef4444;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 15px;"></i>
                <p>Ошибка загрузки товаров: ${error.message}</p>
                <p>Убедитесь что сервер запущен: python api.py</p>
                <p style="font-size: 12px; margin-top: 10px;">API URL: ${API_URL}/products</p>
                <button onclick="location.reload()" style="margin-top: 15px; padding: 10px 20px; background: #e67e22; color: white; border: none; border-radius: 40px; cursor: pointer;">
                    Попробовать снова
                </button>
            </div>
        `;

    if (popularContainer) popularContainer.innerHTML = errorHtml;
    if (catalogContainer) catalogContainer.innerHTML = errorHtml;

    showNotification("Ошибка подключения к серверу", "error");
  }
}

// ============ ДОБАВЛЕНИЕ В КОРЗИНУ ============

async function addToCartLocal(productId) {
  console.log("🛒 Добавление товара ID:", productId);

  const product = products.find((p) => p.id === productId);
  if (!product) {
    console.error("Товар не найден");
    showNotification("Ошибка: товар не найден", "error");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/cart`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        product_id: productId,
        quantity: 1,
      }),
    });

    if (!response.ok) {
      throw new Error(`Ошибка: ${response.status}`);
    }

    console.log("✅ Товар добавлен в корзину");
    showNotification(`${product.name} добавлен в корзину!`, "success");

    if (typeof window.updateCartCounter === "function") {
      await window.updateCartCounter();
    }
  } catch (error) {
    console.error("❌ Ошибка добавления:", error);
    showNotification("Ошибка добавления в корзину", "error");
  }
}

// ============ ОБНОВЛЕНИЕ СЧЕТЧИКА ============

async function updateCartCounter() {
  try {
    const response = await fetch(`${API_URL}/cart`, {
      credentials: "include",
    });

    if (response.ok) {
      const cart = await response.json();
      const totalItems = cart.reduce(
        (sum, item) => sum + (item.quantity || 1),
        0,
      );
      const cartCountSpan = document.getElementById("cartCount");
      if (cartCountSpan) {
        cartCountSpan.textContent = totalItems;
        console.log("🔄 Счетчик обновлен:", totalItems);
      }
    }
  } catch (error) {
    console.error("Ошибка обновления счетчика:", error);
  }
}

// ============ РЕНДЕРИНГ ТОВАРОВ ============

function renderPopularProducts() {
  const container = document.getElementById("popularProducts");
  if (!container) {
    console.log("⚠️ Контейнер popularProducts не найден");
    return;
  }

  console.log("🎨 Рендеринг популярных товаров, количество:", products.length);

  const popular = products.filter((p) => p.popular).slice(0, 4);

  if (popular.length === 0) {
    container.innerHTML =
      '<div style="text-align: center; padding: 50px;">Нет популярных товаров</div>';
    return;
  }

  container.innerHTML = popular
    .map((product) => createProductCard(product))
    .join("");
  attachEvents();

  console.log("✅ Отображено популярных товаров:", popular.length);
}

function renderCatalogProducts() {
  const container = document.getElementById("productsGrid");
  if (!container) {
    console.log("⚠️ Контейнер productsGrid не найден");
    return;
  }

  console.log("🎨 Рендеринг каталога, количество товаров:", products.length);

  let filtered = [...products];

  const categoryFilter = document.getElementById("categoryFilter");
  if (categoryFilter && categoryFilter.value !== "all") {
    filtered = filtered.filter((p) => p.category === categoryFilter.value);
  }

  const searchInput = document.getElementById("searchInput");
  if (searchInput && searchInput.value.trim()) {
    const term = searchInput.value.toLowerCase();
    filtered = filtered.filter(
      (p) =>
        p.name.toLowerCase().includes(term) ||
        p.category.toLowerCase().includes(term),
    );
  }

  const sortSelect = document.getElementById("sortSelect");
  if (sortSelect) {
    if (sortSelect.value === "price-asc")
      filtered.sort((a, b) => a.price - b.price);
    else if (sortSelect.value === "price-desc")
      filtered.sort((a, b) => b.price - a.price);
  }

  const noResults = document.getElementById("noResults");
  if (filtered.length === 0) {
    container.innerHTML = "";
    if (noResults) noResults.style.display = "block";
    return;
  }
  if (noResults) noResults.style.display = "none";

  container.innerHTML = filtered
    .map((product) => createProductCard(product))
    .join("");
  attachEvents();

  console.log("✅ Отображено товаров в каталоге:", filtered.length);
}

function createProductCard(product) {
  return `
        <div class="product-item" data-id="${product.id}">
            <div class="product-img">${product.img || "🔧"}</div>
            <div class="product-info">
                <div class="product-title">${escapeHtml(product.name)}</div>
                <div class="price">${Number(product.price).toLocaleString()} ₽</div>
                <div style="color: #666; font-size: 0.85rem; margin-bottom: 10px;">${product.category}</div>
                <button class="btn-small view-product" data-id="${product.id}">Подробнее</button>
                <button class="btn-small add-to-cart-btn" data-id="${product.id}">В корзину</button>
            </div>
        </div>
    `;
}

function attachEvents() {
  document.querySelectorAll(".view-product").forEach((btn) => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const id = parseInt(btn.dataset.id);
      showProductModal(id);
    };
  });

  document.querySelectorAll(".add-to-cart-btn").forEach((btn) => {
    btn.onclick = (e) => {
      e.stopPropagation();
      const id = parseInt(btn.dataset.id);
      addToCartLocal(id);
    };
  });
}

// ============ МОДАЛЬНОЕ ОКНО ============

function showProductModal(id) {
  const product = products.find((p) => p.id === id);
  if (!product) return;

  let modal = document.getElementById("productModal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "productModal";
    modal.className = "modal";
    modal.innerHTML = `
            <div class="modal-content">
                <div style="font-size: 4rem; margin-bottom: 15px;">${product.img || "🔧"}</div>
                <h3 id="modalTitle"></h3>
                <p id="modalDesc" style="margin: 15px 0; color: #666;"></p>
                <p id="modalPrice" style="font-size: 1.5rem; color: #e67e22; margin: 15px 0;"></p>
                <button onclick="window.closeModal()" style="padding: 10px 20px; margin-right: 10px; background: #0f3b5c; color: white; border: none; border-radius: 40px; cursor: pointer;">Закрыть</button>
                <button id="modalAddCart" style="padding: 10px 20px; background: #e67e22; color: white; border: none; border-radius: 40px; cursor: pointer;">В корзину</button>
            </div>
        `;
    document.body.appendChild(modal);
  }

  document.getElementById("modalTitle").innerText = product.name;
  document.getElementById("modalDesc").innerText =
    product.description || "Описание не указано";
  document.getElementById("modalPrice").innerHTML =
    `${Number(product.price).toLocaleString()} ₽`;

  const modalAddBtn = document.getElementById("modalAddCart");
  modalAddBtn.onclick = () => {
    addToCartLocal(product.id);
    closeModal();
  };

  modal.style.display = "flex";
}

function closeModal() {
  const modal = document.getElementById("productModal");
  if (modal) modal.style.display = "none";
}

// ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/[&<>]/g, function (m) {
    if (m === "&") return "&amp;";
    if (m === "<") return "&lt;";
    if (m === ">") return "&gt;";
    return m;
  });
}

function showNotification(message, type = "success") {
  let toast = document.getElementById("siteToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "siteToast";
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
            animation: slideIn 0.3s ease-out;
        `;
    document.body.appendChild(toast);
  }
  toast.innerText = message;
  toast.style.display = "block";
  toast.style.opacity = "1";

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => {
      toast.style.display = "none";
      toast.style.opacity = "1";
    }, 300);
  }, 2500);
}

function initFilters() {
  const categoryFilter = document.getElementById("categoryFilter");
  const sortSelect = document.getElementById("sortSelect");
  const searchInput = document.getElementById("searchInput");
  const resetBtn = document.getElementById("resetFilters");

  if (categoryFilter)
    categoryFilter.addEventListener("change", () => renderCatalogProducts());
  if (sortSelect)
    sortSelect.addEventListener("change", () => renderCatalogProducts());
  if (searchInput)
    searchInput.addEventListener("input", () => renderCatalogProducts());
  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      if (categoryFilter) categoryFilter.value = "all";
      if (sortSelect) sortSelect.value = "default";
      if (searchInput) searchInput.value = "";
      renderCatalogProducts();
    });
  }
}

function renderProducts() {
  console.log("🎨 Рендеринг всех товаров...");

  if (document.getElementById("popularProducts")) {
    renderPopularProducts();
  }
  if (document.getElementById("productsGrid")) {
    renderCatalogProducts();
  }
}

// ============ ЗАПУСК ============

const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);

document.addEventListener("DOMContentLoaded", function () {
  console.log("🚀 DOM загружен, инициализация...");
  console.log("📍 Текущая страница:", window.location.pathname);

  loadProducts();
  initFilters();
  updateCartCounter();
});

window.renderCatalogProducts = renderCatalogProducts;
window.closeModal = closeModal;
window.addToCart = addToCartLocal;
window.updateCartCounter = updateCartCounter;
