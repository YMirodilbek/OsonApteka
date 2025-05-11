// Mini Cart Module
document.addEventListener('DOMContentLoaded', function() {
    // ======================================
    // ELEMENT REFERENCES AND INITIALIZATION
    // ======================================
    const cartAction = document.querySelector('#cart-action');
    const mobileCartButton = document.querySelector('#mobile-cart-button');
    
    if (!cartAction && !mobileCartButton) return;

    // ======================================
    // STATE VARIABLES
    // ======================================
    let cartItems = [];
    let cartTotal = 0;
    let cartCount = 0;
    
    // Initialize mini cart element if not exists
    let miniCart = document.getElementById('mini-cart-modal');
    if (!miniCart) {
        miniCart = document.createElement('div');
        miniCart.id = 'mini-cart-modal';
        document.body.appendChild(miniCart);
    }
    
    // ======================================
    // CORE FUNCTIONALITY
    // ======================================
    
    // Initial cart data fetch
    fetchCartData();
    
    // Open mini cart from desktop and mobile buttons
    cartAction?.addEventListener('click', openMiniCart);
    mobileCartButton?.addEventListener('click', openMiniCart);
    
    // Event delegation for cart actions (close, remove, quantity changes)
    document.body.addEventListener('click', handleCartEvents);
    
    // ======================================
    // EVENT HANDLERS
    // ======================================
    
    // Open mini cart
    function openMiniCart(e) {
        e.preventDefault();
        fetchCartData(); // Refresh cart data before showing
        renderMiniCart();
        miniCart.classList.add('open');
    }
    
    // Handle all cart-related click events with event delegation
    function handleCartEvents(e) {
        // Close mini cart
        if (e.target.classList.contains('mini-cart-backdrop') || 
            e.target.classList.contains('mini-cart-close')) {
            miniCart.classList.remove('open');
            return;
        }
        
        // Remove item
        if (e.target.closest && e.target.closest('.mini-cart-item__remove')) {
            const btn = e.target.closest('.mini-cart-item__remove');
            const id = btn.getAttribute('data-id');
            
            removeFromCart(id);
            return;
        }
        
        // Increase quantity
        if (e.target.closest && e.target.closest('.quantity-btn.increase')) {
            const btn = e.target.closest('.quantity-btn.increase');
            const id = btn.getAttribute('data-id');
            
            changeQuantity(id, 'increase');
            return;
        }
        
        // Decrease quantity
        if (e.target.closest && e.target.closest('.quantity-btn.decrease')) {
            const btn = e.target.closest('.quantity-btn.decrease');
            const id = btn.getAttribute('data-id');
            
            changeQuantity(id, 'decrease');
            return;
        }
        
        // Checkout button
        if (e.target.classList.contains('mini-cart-checkout')) {
            if (cartItems.length === 0) {
                showNotification('Корзина пуста');
                return;
            }
            window.location.href = 'checkout/';
            return;
        }
    }
    
    // ======================================
    // CART API FUNCTIONS
    // ======================================
    
    // Fetch cart data from server
    function fetchCartData() {
        fetch('/cart-json/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 200) {
                    // Update state
                    cartItems = data.cart_items;
                    cartTotal = data.cart_total;
                    cartCount = data.cart_count;
                    
                    // Update UI
                    updateCartBadges();
                    
                    // Re-render if cart is open
                    if (miniCart && miniCart.classList.contains('open')) {
                        renderMiniCart();
                    }
                }
            })
            .catch(error => console.error('Error fetching cart:', error));
    }
    
    // Remove item from cart
    function removeFromCart(productId) {
        fetch(`/remove_from_cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 200) {
                fetchCartData();
                showNotification('Товар удален из корзины');
            } else {
                showNotification('Ошибка при удалении товара');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Ошибка при удалении товара');
        });
    }
    
    // Change item quantity
    function changeQuantity(productId, action) {
        const endpoint = action === 'increase' ? 
            `/increase-quantity/${productId}/` : 
            `/decrease-quantity/${productId}/`;
        
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 200) {
                fetchCartData();
                
                if (action === 'decrease' && data.quantity === 0) {
                    showNotification('Товар удален из корзины');
                } else {
                    showNotification(action === 'increase' ? 
                        'Количество увеличено' : 
                        'Количество уменьшено'
                    );
                }
            } else {
                showNotification('Ошибка при изменении количества');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Ошибка при изменении количества');
        });
    }
    
    // ======================================
    // UI HELPERS
    // ======================================
    
    // Update all cart badges with current count
    function updateCartBadges() {
        const cartBadges = document.querySelectorAll('.cart-badge');
        cartBadges.forEach(badge => {
            badge.setAttribute('data-count', cartCount);
        });
    }
    
    // Render mini cart with current items
    function renderMiniCart() {
        let itemsHtml = '';
        if (!cartItems || cartItems.length === 0) {
            itemsHtml = '<p>Ваша корзина пуста.</p>';
        } else {
            itemsHtml = `<ul class="mini-cart-list">` + cartItems.map(item => `
                <li class="mini-cart-item">
                    <img src="${item.img}" alt="${item.name}" class="mini-cart-item__img">
                    <div class="mini-cart-item__info">
                        <div class="mini-cart-item__name">${item.name}</div>
                        <div class="mini-cart-item__meta">
                            <div class="quantity-controls">
                                <button class="quantity-btn decrease" data-id="${item.id}">-</button>
                                <span class="quantity">${item.qty}</span>
                                <button class="quantity-btn increase" data-id="${item.id}">+</button>
                            </div>
                            <span class="mini-cart-item__price">${formatPrice(item.price)} сум</span>
                        </div>
                    </div>
                    <button class="mini-cart-item__remove" data-id="${item.id}"><i class="fas fa-trash"></i></button>
                </li>
            `).join('') + `</ul>
            <div class="mini-cart-total">
                <span>Итого:</span>
                <span class="mini-cart-total__price">${formatPrice(cartTotal)} сум</span>
            </div>
            <button class="mini-cart-checkout">Оформить заказ</button>
            `;
        }
        
        miniCart.innerHTML = `
            <div class="mini-cart-backdrop"></div>
            <div class="mini-cart-content">
                <button class="mini-cart-close">&times;</button>
                <h4>Корзина</h4>
                <div class="mini-cart-items">
                    ${itemsHtml}
                </div>
            </div>
        `;
    }
    
    // Format price with thousand separators
    function formatPrice(price) {
        return price.toLocaleString();
    }
});

// Helper function to get CSRF token
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
