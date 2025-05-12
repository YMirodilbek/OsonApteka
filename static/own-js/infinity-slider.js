/**
 * Infinity Slider - бесконечный слайдер для product-list
 */
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех слайдеров
    initInfinitySliders();
    
    // Повторная инициализация слайдеров при изменении размера окна
    window.addEventListener('resize', debounce(function() {
        initInfinitySliders();
    }, 300));
    
    // Функция инициализации бесконечных слайдеров
    function initInfinitySliders() {
        const productLists = document.querySelectorAll('.product-list');
        
        productLists.forEach(slider => {
            // Очищаем предыдущие клонированные элементы
            const existingClones = slider.querySelectorAll('.product-item-card.cloned');
            existingClones.forEach(clone => clone.remove());
            
            // Находим контейнер и навигационные кнопки
            const container = slider.closest('.main-content__container');
            if (!container) return;
            
            const prevBtn = container.querySelector('.product-list__control.prev');
            const nextBtn = container.querySelector('.product-list__control.next');
            if (!prevBtn || !nextBtn) return;
            
            // Получаем оригинальные карточки
            const originalCards = slider.querySelectorAll('.product-item-card:not(.cloned)');
            if (originalCards.length === 0) return;
            
            // Подготовка слайдера к бесконечной прокрутке
            setupInfinitySlider(slider, originalCards, prevBtn, nextBtn);
        });
    }
    
    // Настройка бесконечного слайдера
    function setupInfinitySlider(slider, cards, prevBtn, nextBtn) {
        // Отключаем плавную прокрутку временно для моментальных переходов
        slider.style.scrollBehavior = 'auto';
        
        // Клонируем карточки для бесконечной прокрутки
        const cardWidth = cards[0].offsetWidth + parseInt(getComputedStyle(slider).gap);
        const visibleWidth = slider.clientWidth;
        const needCloneCount = Math.ceil(visibleWidth / cardWidth) * 3; // Создаем достаточно клонов
        
        // Создаем начальные клоны (в конец)
        for (let i = 0; i < needCloneCount; i++) {
            const index = i % cards.length;
            const clone = cards[index].cloneNode(true);
            clone.classList.add('cloned', 'clone-end');
            clone.dataset.originalIndex = index;
            slider.appendChild(clone);
        }
        
        // Создаем конечные клоны (в начало)
        for (let i = cards.length - 1; i >= Math.max(0, cards.length - needCloneCount); i--) {
            const clone = cards[i].cloneNode(true);
            clone.classList.add('cloned', 'clone-start');
            clone.dataset.originalIndex = i;
            slider.insertBefore(clone, slider.firstChild);
        }
        
        // Устанавливаем начальную позицию прокрутки для отображения оригинальных элементов
        slider.scrollLeft = cardWidth * needCloneCount;
        
        // Восстанавливаем плавную прокрутку
        setTimeout(() => {
            slider.style.scrollBehavior = 'smooth';
        }, 50);
        
        // Устанавливаем обработчики событий
        setupEventListeners(slider, cards, prevBtn, nextBtn, cardWidth, needCloneCount);
    }
    
    // Настройка обработчиков событий для слайдера
    function setupEventListeners(slider, cards, prevBtn, nextBtn, cardWidth, cloneCount) {
        // Удаляем существующие обработчики
        const newPrevBtn = prevBtn.cloneNode(true);
        const newNextBtn = nextBtn.cloneNode(true);
        prevBtn.parentNode.replaceChild(newPrevBtn, prevBtn);
        nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);
        prevBtn = newPrevBtn;
        nextBtn = newNextBtn;
        
        // Обработчик события прокрутки
        slider.addEventListener('scroll', function() {
            handleInfiniteScroll(slider, cards, cardWidth, cloneCount);
        });
        
        // Кнопка "Вперед"
        nextBtn.addEventListener('click', function() {
            slider.scrollBy({
                left: cardWidth * 2,
                behavior: 'smooth'
            });
        });
        
        // Кнопка "Назад"
        prevBtn.addEventListener('click', function() {
            slider.scrollBy({
                left: -cardWidth * 2,
                behavior: 'smooth'
            });
        });
        
        // Обработчик свайпов на мобильных устройствах
        let touchStartX = 0;
        
        slider.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
        }, { passive: true });
        
        slider.addEventListener('touchend', function(e) {
            const touchEndX = e.changedTouches[0].clientX;
            const touchDiff = touchStartX - touchEndX;
            
            // Если свайп достаточно длинный
            if (Math.abs(touchDiff) > 50) {
                if (touchDiff > 0) {
                    // Свайп влево - следующий слайд
                    nextBtn.click();
                } else {
                    // Свайп вправо - предыдущий слайд
                    prevBtn.click();
                }
            }
        }, { passive: true });
        
        // Поддержка перетаскивания мышью
        let isDown = false;
        let startX;
        let scrollLeft;
        
        slider.addEventListener('mousedown', function(e) {
            isDown = true;
            slider.style.cursor = 'grabbing';
            startX = e.pageX;
            scrollLeft = slider.scrollLeft;
            e.preventDefault();
        });
        
        slider.addEventListener('mouseleave', function() {
            isDown = false;
            slider.style.cursor = 'grab';
        });
        
        slider.addEventListener('mouseup', function() {
            isDown = false;
            slider.style.cursor = 'grab';
        });
        
        slider.addEventListener('mousemove', function(e) {
            if (!isDown) return;
            const x = e.pageX;
            const walk = (x - startX) * 2;
            slider.scrollLeft = scrollLeft - walk;
        });
        
        // Делегирование событий для клонированных карточек
        slider.addEventListener('click', function(e) {
            // Добавление в корзину
            if (e.target.closest('.cloned .add-to-cart')) {
                e.preventDefault();
                
                const button = e.target.closest('.add-to-cart');
                const card = button.closest('.product-item-card');
                const productId = card.getAttribute('data-product-id');
                
                addToCart(productId, button);
            }
            
            // Добавление в избранное
            if (e.target.closest('.cloned .product-item-card__button.wishlist')) {
                e.preventDefault();
                e.stopPropagation();
                
                const wishlistBtn = e.target.closest('.product-item-card__button.wishlist');
                const card = wishlistBtn.closest('.product-item-card');
                const productName = card.querySelector('h4').textContent;
                
                toggleWishlist(wishlistBtn, productName);
            }
        });
    }
    
    // Обработка бесконечной прокрутки
    function handleInfiniteScroll(slider, cards, cardWidth, cloneCount) {
        const totalWidth = slider.scrollWidth;
        const visibleWidth = slider.clientWidth;
        const maxScroll = totalWidth - visibleWidth;
        const currentScroll = slider.scrollLeft;
        const originalCardsWidth = cardWidth * cards.length;
        
        // Если прокрутили к концу клонов
        if (currentScroll > originalCardsWidth + (cardWidth * cloneCount * 0.7)) {
            slider.style.scrollBehavior = 'auto';
            slider.scrollLeft = currentScroll - originalCardsWidth;
            setTimeout(() => {
                slider.style.scrollBehavior = 'smooth';
            }, 50);
        }
        // Если прокрутили к началу клонов
        else if (currentScroll < cardWidth * (cloneCount * 0.3)) {
            slider.style.scrollBehavior = 'auto';
            slider.scrollLeft = currentScroll + originalCardsWidth;
            setTimeout(() => {
                slider.style.scrollBehavior = 'smooth';
            }, 50);
        }
    }
    
    // Функция добавления товара в корзину
    function addToCart(productId, button) {
        // Сохраняем исходный текст кнопки
        const originalText = button.textContent;
        button.textContent = 'Добавление...';
        button.style.backgroundColor = '#999';
        button.disabled = true;
        
        fetch(`/add_to_cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 200) {
                // Обновляем бейдж корзины
                const cartBadges = document.querySelectorAll('.cart-badge');
                cartBadges.forEach(badge => {
                    badge.setAttribute('data-count', data.cart_count);
                });
                
                // Меняем состояние кнопки
                button.textContent = 'Добавлено ✓';
                button.style.backgroundColor = '#4CAF50';
                
                // Показываем уведомление
                const productName = button.closest('.product-item-card').querySelector('h4').textContent;
                showNotification(`${productName} добавлен в корзину`);
                
                // Возвращаем исходное состояние кнопки
                setTimeout(() => {
                    button.textContent = originalText;
                    button.style.backgroundColor = '';
                    button.disabled = false;
                }, 1500);
            } else {
                showNotification('Ошибка при добавлении в корзину');
                button.textContent = originalText;
                button.style.backgroundColor = '';
                button.disabled = false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Ошибка при добавлении в корзину');
            button.textContent = originalText;
            button.style.backgroundColor = '';
            button.disabled = false;
        });
    }
    
    // Функция переключения избранного
    function toggleWishlist(button, productName) {
        const isActive = button.classList.contains('active');
        
        if (isActive) {
            button.classList.remove('active');
            button.querySelector('i').style.color = '';
            showNotification(`${productName} удален из избранного`);
        } else {
            button.classList.add('active');
            button.querySelector('i').style.color = '#D91F3D';
            showNotification(`${productName} добавлен в избранное`);
        }
    }
    
    // Функция показа уведомления
    function showNotification(message) {
        if (window.showNotification) {
            window.showNotification(message);
        } else {
            // Запасная реализация
            const notification = document.createElement('div');
            notification.className = 'product-notification';
            notification.textContent = message;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 3000);
        }
    }
    
    // Функция debounce для ограничения частоты вызовов
    function debounce(func, wait) {
        let timeout;
        return function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, arguments), wait);
        };
    }
    
    // Функция получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}); 