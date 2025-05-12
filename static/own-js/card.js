// Product Card Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get all add to cart buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    const wishlistButtons = document.querySelectorAll('.product-item-card__button.wishlist');
    const detailButtons = document.querySelectorAll('.product-item-card__button.about');
    const productCards = document.querySelectorAll('.product-item-card');
    
    // Track if we're dragging to prevent card clicks
    let isDragging = false;
    
    // Initialize cart count
    let cartCount = 0;
    const cartBadge = document.querySelector('.cart-badge');
    
    // Product List Slider functionality
    initProductSlider();
    
    // Handle window resize to update card widths
    window.addEventListener('resize', debounce(function() {
        initProductSlider();
    }, 250));
    
    // Debounce function to limit resize events
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                func.apply(context, args);
            }, wait);
        };
    }
    
    // Prevent card clicks when dragging
    productCards.forEach(card => {
        card.addEventListener('mousedown', () => {
            isDragging = false;
        });
        
        card.addEventListener('mousemove', () => {
            isDragging = true;
        });
        
        card.addEventListener('click', (e) => {
            if (isDragging) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
    });
    
    // Add to cart functionality
    addToCartButtons.forEach(button => {
        if (button.disabled) return;
        
        button.addEventListener('click', function() {
            // Get product info
            const card = this.closest('.product-item-card');
            const productId = card.getAttribute('data-product-id');
            const productName = card.querySelector('h4').textContent;
            
            // Send request to add to cart
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
                    // Update cart badge
                    const cartBadge = document.querySelector('.cart-badge');
                    if (cartBadge) {
                        cartBadge.setAttribute('data-count', data.cart_count);
                    }
                    
                    // Change button state temporarily
                    const originalText = this.textContent;
                    this.textContent = 'Добавлено ✓';
                    this.style.backgroundColor = '#4CAF50';
                    
                    // Show notification
                    showNotification(`${productName} добавлен в корзину`);
                    
                    // Reset button after delay
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.style.backgroundColor = '';
                    }, 1500);
                } else {
                    showNotification('Ошибка при добавлении в корзину');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Ошибка при добавлении в корзину');
            });
        });
    });
    
    // Wishlist functionality
    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event bubbling to parent elements
            
            // Toggle wishlist state
            const isActive = this.classList.contains('active');
            const card = this.closest('.product-item-card');
            const productName = card.querySelector('h4').textContent;
            
            if (isActive) {
                this.classList.remove('active');
                this.querySelector('i').style.color = '';
                showNotification(`${productName} удален из избранного`);
            } else {
                this.classList.add('active');
                this.querySelector('i').style.color = '#D91F3D';
                showNotification(`${productName} добавлен в избранное`);
            }
        });
    });
    
    // Product details functionality
    detailButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent event bubbling
            
            const card = this.closest('.product-item-card');
            const productName = card.querySelector('h4').textContent;
            
            // Here you would typically navigate to product detail page
            // For demo, we'll just show a notification
            showNotification(`Открываем информацию о товаре: ${productName}`);
        });
    });
    
    // Product List Slider initialization
    function initProductSlider() {
        const productLists = document.querySelectorAll('.product-list');
        
        productLists.forEach(list => {
            // Clean up existing event listeners first
            cleanupListeners(list);
            
            const container = list.closest('.main-content__container');
            const prevButton = container?.querySelector('.product-list__control.prev');
            const nextButton = container?.querySelector('.product-list__control.next');
            
            if (!container || !prevButton || !nextButton) return;
            
            // Get the actual card width including gap for accurate scrolling
            const cards = list.querySelectorAll('.product-item-card:not(.cloned)');
            if (!cards.length) return;
            
            const firstCard = cards[0];
            const cardStyle = window.getComputedStyle(firstCard);
            const cardActualWidth = firstCard.offsetWidth;
            const gapSize = parseInt(getComputedStyle(list).gap) || 20;
            const cardWidth = cardActualWidth + gapSize;
            
            // Count original cards
            const cardCount = cards.length;
            
            // Always enable infinite scrolling
            const enableInfiniteScroll = cardCount > 0;
            
            // Clean all cloned cards first
            list.querySelectorAll('.product-item-card.cloned').forEach(clone => {
                clone.remove();
            });
            
            // Setup infinite scrolling
            if (enableInfiniteScroll) {
                setupInfiniteScroll(list, cards);
            }
            
            // Next button click
            nextButton.addEventListener('click', function nextClickHandler() {
                const visibleWidth = list.clientWidth;
                const scrollAmount = Math.min(visibleWidth, cardWidth * 2);
                
                if (enableInfiniteScroll) {
                    const scrollMax = list.scrollWidth - visibleWidth;
                    
                    // If we're close to the end, prepare to loop
                    if (list.scrollLeft + scrollAmount >= scrollMax) {
                        // First finish the scroll animation to the end
                        list.scrollBy({
                            left: scrollAmount,
                            behavior: 'smooth'
                        });
                        
                        // Then set up a delayed reset to the beginning
                        setTimeout(() => {
                            list.style.scrollBehavior = 'auto';
                            list.scrollLeft = 0;
                            setTimeout(() => {
                                list.style.scrollBehavior = 'smooth';
                            }, 50);
                        }, 500); // This should match the scroll animation duration
                    } else {
                        // Normal scrolling
                        list.scrollBy({
                            left: scrollAmount,
                            behavior: 'smooth'
                        });
                    }
                } else {
                    // Regular scrolling for non-infinite lists
                    list.scrollBy({
                        left: scrollAmount,
                        behavior: 'smooth'
                    });
                }
            });
            
            // Previous button click
            prevButton.addEventListener('click', function prevClickHandler() {
                const visibleWidth = list.clientWidth;
                const scrollAmount = Math.min(visibleWidth, cardWidth * 2);
                
                if (enableInfiniteScroll) {
                    // If we're at the beginning, prepare to loop to the end
                    if (list.scrollLeft <= cardWidth) {
                        // Loop logic - get the maximum scroll position
                        const maxScroll = list.scrollWidth - visibleWidth;
                        
                        // Immediate jump to end
                        list.style.scrollBehavior = 'auto';
                        list.scrollLeft = maxScroll;
                        
                        // Force reflow then continue smooth scrolling
                        void list.offsetWidth; 
                        list.style.scrollBehavior = 'smooth';
                        
                        // Then smoothly scroll a bit back
                        list.scrollBy({
                            left: -scrollAmount,
                            behavior: 'smooth'
                        });
                    } else {
                        // Normal scrolling
                        list.scrollBy({
                            left: -scrollAmount,
                            behavior: 'smooth'
                        });
                    }
                } else {
                    // Regular scrolling for non-infinite lists
                    list.scrollBy({
                        left: -scrollAmount,
                        behavior: 'smooth'
                    });
                }
            });
            
            // Button states
            if (enableInfiniteScroll) {
                // Always enable both buttons for infinite scrolling
                prevButton.classList.remove('disabled');
                prevButton.style.opacity = '1';
                prevButton.style.cursor = 'pointer';
                nextButton.classList.remove('disabled');
                nextButton.style.opacity = '1';
                nextButton.style.cursor = 'pointer';
            } else {
                // Initial button states
                updateSliderButtons(list, prevButton, nextButton);
                
                // Update button states on scroll
                list.addEventListener('scroll', function scrollHandler() {
                    updateSliderButtons(list, prevButton, nextButton);
                });
            }
            
            // Handle touch events for mobile
            let startX, endX;
            
            list.addEventListener('touchstart', function touchStartHandler(e) {
                startX = e.touches[0].clientX;
            }, { passive: true });
            
            list.addEventListener('touchend', function touchEndHandler(e) {
                endX = e.changedTouches[0].clientX;
                const diff = startX - endX;
                
                // If significant swipe detected
                if (Math.abs(diff) > 50) {
                    if (diff > 0) {
                        // Swipe left, go next
                        nextButton.click();
                    } else {
                        // Swipe right, go previous
                        prevButton.click();
                    }
                }
            }, { passive: true });
            
            // Add mouse-based drag scrolling
            let isDown = false;
            let startScrollLeft;
            
            list.addEventListener('mousedown', function mouseDownHandler(e) {
                isDown = true;
                list.classList.add('active');
                startX = e.pageX;
                startScrollLeft = list.scrollLeft;
                e.preventDefault(); // Prevent text selection while dragging
            });
            
            list.addEventListener('mouseleave', function mouseLeaveHandler() {
                isDown = false;
                list.classList.remove('active');
            });
            
            list.addEventListener('mouseup', function mouseUpHandler() {
                isDown = false;
                list.classList.remove('active');
            });
            
            list.addEventListener('mousemove', function mouseMoveHandler(e) {
                if (!isDown) return;
                const x = e.pageX;
                const walk = (x - startX) * 2; // Scroll speed multiplier
                list.scrollLeft = startScrollLeft - walk;
            });
        });
    }
    
    // Clean up event listeners before reinitializing
    function cleanupListeners(list) {
        const container = list.closest('.main-content__container');
        const prevButton = container?.querySelector('.product-list__control.prev');
        const nextButton = container?.querySelector('.product-list__control.next');
        
        // Clone elements to remove all event listeners
        if (prevButton) {
            const newPrev = prevButton.cloneNode(true);
            prevButton.parentNode.replaceChild(newPrev, prevButton);
        }
        
        if (nextButton) {
            const newNext = nextButton.cloneNode(true);
            nextButton.parentNode.replaceChild(newNext, nextButton);
        }
        
        // Clone the list to remove scroll event listeners
        const parent = list.parentNode;
        const listClone = list.cloneNode(false); // Shallow clone without children
        
        // Move all non-cloned children to the new list
        Array.from(list.children).forEach(child => {
            if (!child.classList.contains('cloned')) {
                listClone.appendChild(child);
            }
        });
        
        // Replace the old list with the new one
        parent.replaceChild(listClone, list);
        
        return listClone;
    }
    
    // Setup infinite scrolling by cloning cards
    function setupInfiniteScroll(list, cards) {
        const originalHtml = list.innerHTML;
        
        // Clone all cards and append to the end
        cards.forEach(card => {
            const clone = card.cloneNode(true);
            clone.classList.add('cloned');
            list.appendChild(clone);
        });
        
        // Double clone for smoother looping in both directions
        cards.forEach(card => {
            const clone = card.cloneNode(true);
            clone.classList.add('cloned');
            list.appendChild(clone);
        });
        
        // Event delegation for cloned elements
        list.addEventListener('click', function(e) {
            // Handle add to cart clicks on cloned elements
            if (e.target.closest('.cloned .add-to-cart')) {
                e.preventDefault();
                
                const button = e.target.closest('.add-to-cart');
                const card = button.closest('.product-item-card');
                const productId = card.getAttribute('data-product-id');
                const productName = card.querySelector('h4').textContent;
                
                // Send request to add to cart
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
                        // Update cart badge
                        const cartBadge = document.querySelector('.cart-badge');
                        if (cartBadge) {
                            cartBadge.setAttribute('data-count', data.cart_count);
                        }
                        
                        // Change button state temporarily
                        const originalText = button.textContent;
                        button.textContent = 'Добавлено ✓';
                        button.style.backgroundColor = '#4CAF50';
                        
                        // Show notification
                        showNotification(`${productName} добавлен в корзину`);
                        
                        // Reset button after delay
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.backgroundColor = '';
                        }, 1500);
                    } else {
                        showNotification('Ошибка при добавлении в корзину');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Ошибка при добавлении в корзину');
                });
            }
            
            // Handle wishlist button clicks on cloned elements
            if (e.target.closest('.cloned .product-item-card__button.wishlist')) {
                e.preventDefault();
                e.stopPropagation();
                
                const wishlistBtn = e.target.closest('.product-item-card__button.wishlist');
                const card = wishlistBtn.closest('.product-item-card');
                const productName = card.querySelector('h4').textContent;
                const isActive = wishlistBtn.classList.contains('active');
                
                if (isActive) {
                    wishlistBtn.classList.remove('active');
                    wishlistBtn.querySelector('i').style.color = '';
                    showNotification(`${productName} удален из избранного`);
                } else {
                    wishlistBtn.classList.add('active');
                    wishlistBtn.querySelector('i').style.color = '#D91F3D';
                    showNotification(`${productName} добавлен в избранное`);
                }
            }
            
            // Handle product detail clicks on cloned elements
            if (e.target.closest('.cloned .product-item-card__button.about')) {
                e.preventDefault();
                e.stopPropagation();
                
                const detailBtn = e.target.closest('.product-item-card__button.about');
                const card = detailBtn.closest('.product-item-card');
                const productName = card.querySelector('h4').textContent;
                
                showNotification(`Открываем информацию о товаре: ${productName}`);
            }
        });
        
        // Set initial scroll position
        list.scrollLeft = 0;
    }
    
    // Update slider buttons based on scroll position
    function updateSliderButtons(list, prevButton, nextButton) {
        const scrollLeft = list.scrollLeft;
        const maxScrollLeft = list.scrollWidth - list.clientWidth;
        
        // Disable/enable previous button
        if (scrollLeft <= 0) {
            prevButton.classList.add('disabled');
            prevButton.style.opacity = '0.5';
            prevButton.style.cursor = 'default';
        } else {
            prevButton.classList.remove('disabled');
            prevButton.style.opacity = '1';
            prevButton.style.cursor = 'pointer';
        }
        
        // Disable/enable next button
        if (scrollLeft >= maxScrollLeft - 5) { // 5px threshold for rounding errors
            nextButton.classList.add('disabled');
            nextButton.style.opacity = '0.5';
            nextButton.style.cursor = 'default';
        } else {
            nextButton.classList.remove('disabled');
            nextButton.style.opacity = '1';
            nextButton.style.cursor = 'pointer';
        }
    }
    
    // Notification helper function
    function showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'product-notification';
        notification.textContent = message;
        
        // Add to document
        document.body.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
});

// Add CSRF token helper function
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

