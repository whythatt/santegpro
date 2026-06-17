// ============ ОСНОВНОЙ JS ФАЙЛ ============

// Версия для слабовидящих
function initVisionMode() {
    const visionBtn = document.getElementById('visionToggle');
    if (!visionBtn) return;
    
    // Загружаем сохраненные настройки
    const savedVision = localStorage.getItem('visually_impaired');
    if (savedVision === 'true') {
        document.body.classList.add('visually-impaired');
        visionBtn.innerHTML = '<i class="fas fa-eye"></i> Обычная версия';
    } else {
        visionBtn.innerHTML = '<i class="fas fa-eye"></i> Версия для слабовидящих';
    }
    
    visionBtn.addEventListener('click', function() {
        document.body.classList.toggle('visually-impaired');
        const isActive = document.body.classList.contains('visually-impaired');
        localStorage.setItem('visually_impaired', isActive);
        
        if (isActive) {
            visionBtn.innerHTML = '<i class="fas fa-eye"></i> Обычная версия';
        } else {
            visionBtn.innerHTML = '<i class="fas fa-eye"></i> Версия для слабовидящих';
        }
    });
}

// Инициализация корзины (иконка в шапке) - для всех страниц
function initCartIcon() {
    const cartIcon = document.getElementById('cartIcon');
    if (!cartIcon) return;
    
    // Удаляем старые обработчики
    const newCartIcon = cartIcon.cloneNode(true);
    cartIcon.parentNode.replaceChild(newCartIcon, cartIcon);
    
    newCartIcon.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        window.location.href = 'cart.html';
    });
}

// Обновление счетчика корзины на всех страницах
function updateCartCounterDisplay() {
    const counters = document.querySelectorAll('#cartCount');
    if (counters.length === 0) return;
    
    // Получаем корзину из localStorage
    const saved = localStorage.getItem('santehpro_cart');
    let cartItems = saved ? JSON.parse(saved) : [];
    const totalCount = cartItems.reduce((sum, item) => sum + (item.quantity || 1), 0);
    
    counters.forEach(el => {
        if (el) el.innerText = totalCount;
    });
    console.log('🔄 Счетчик обновлен:', totalCount);
}

// Глобальный поиск
function initGlobalSearch() {
    const searchInput = document.getElementById('searchInputGlobal');
    if (!searchInput) return;
    
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                sessionStorage.setItem('searchTerm', searchTerm);
                window.location.href = 'catalog.html';
            }
        }
    });
}

// Инициализация всех функций
function initAll() {
    console.log('🚀 Инициализация сайта...');
    initVisionMode();
    initCartIcon();
    initGlobalSearch();
    updateCartCounterDisplay();
}

// Запуск при загрузке страницы
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
} else {
    initAll();
}

// Слушаем изменения в localStorage (для обновления счетчика)
window.addEventListener('storage', function(e) {
    if (e.key === 'santehpro_cart') {
        updateCartCounterDisplay();
    }
});

// Экспортируем функцию обновления счетчика
window.updateCartCounter = updateCartCounterDisplay;