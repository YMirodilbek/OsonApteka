// Real-time Search Module
document.addEventListener('DOMContentLoaded', function() {
    // ======================================
    // INITIALIZATION & CONSTANTS
    // ======================================
    const SEARCH_DELAY = 300; // ms to wait before triggering search
    const MAX_HISTORY_ITEMS = 5; // maximum number of search history items
    const MOBILE_BREAKPOINT = 991; // mobile breakpoint in px
    
    // ======================================
    // ELEMENT REFERENCES
    // ======================================
    const searchInput = document.querySelector('.search-input');
    const searchForm = document.querySelector('.search-form');
    if (!searchInput) return;
    
    // ======================================
    // STATE VARIABLES
    // ======================================
    let searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
    let searchTimeout;
    let isSearchActive = false;
    
    // ======================================
    // INITIALIZATION
    // ======================================
    // Clean up any stray elements and create containers
    initializeSearchElements();
    
    // DOM references for containers
    const mobileSearchContainer = document.querySelector('.mobile-search-container');
    const mobileSearchInput = mobileSearchContainer.querySelector('.mobile-search-input');
    const mobileSearchBack = mobileSearchContainer.querySelector('.mobile-search-back');
    const mobileSearchClear = mobileSearchContainer.querySelector('.mobile-search-clear');
    const mobileSearchBody = mobileSearchContainer.querySelector('.mobile-search-body');
    const mobileSearchHistoryItems = mobileSearchContainer.querySelector('.mobile-search-history-items');
    const mobileSearchHistoryClear = mobileSearchContainer.querySelector('.mobile-search-history-clear');

    // Create desktop dropdown if it doesn't exist
    let dropdown = document.querySelector('.real-time-search-dropdown');
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.className = 'real-time-search-dropdown';
        searchForm.appendChild(dropdown);
    }
    
    // Initial rendering
    renderSearchHistory();
    
    // ======================================
    // EVENT LISTENERS
    // ======================================
    // Desktop search input
    searchInput.addEventListener('input', handleSearchInput);
    searchInput.addEventListener('focus', handleSearchFocus);
    searchInput.addEventListener('blur', handleSearchBlur);
    
    // Mobile search back button
    mobileSearchBack.addEventListener('click', hideSearchContainer);
    
    // Mobile search input and clear button
    mobileSearchInput.addEventListener('input', handleMobileSearchInput);
    mobileSearchClear.addEventListener('click', clearMobileSearchInput);
    
    // Mobile history clear button
    mobileSearchHistoryClear.addEventListener('click', clearSearchHistory);
    
    // Mobile history item click and "Add to cart" functionality using event delegation
    mobileSearchBody.addEventListener('click', handleMobileSearchClick);
    
    // Desktop dropdown interaction (item click and "Add to cart") using event delegation
    dropdown.addEventListener('mousedown', handleDropdownInteraction);
    
    // Prevent search form submission
    searchForm?.addEventListener('submit', handleSearchFormSubmit);
    
    // ======================================
    // SETUP FUNCTIONS
    // ======================================
    // Initialize and clean up search elements
    function initializeSearchElements() {
        // Clean up any stray search elements
        document.querySelectorAll('.mobile-search-history:not(.mobile-search-container .mobile-search-history)').forEach(el => {
            el.parentNode?.removeChild(el);
        });
        
        // Create mobile search container if it doesn't exist
        if (!document.querySelector('.mobile-search-container')) {
            const container = document.createElement('div');
            container.className = 'mobile-search-container';
            container.innerHTML = `
                <div class="mobile-search-header">
                    <button class="mobile-search-back">
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <div class="mobile-search-input-container">
                        <input type="text" class="mobile-search-input" placeholder="Поиск лекарств и товаров...">
                        <button class="mobile-search-clear">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="mobile-search-body">
                    <div class="mobile-search-history">
                        <div class="mobile-search-history-header">
                            <div class="mobile-search-history-title">История поиска</div>
                            <button class="mobile-search-history-clear">Очистить</button>
                        </div>
                        <div class="mobile-search-history-items"></div>
                    </div>
                </div>
            `;
            document.body.appendChild(container);
        } else {
            // Clean up any duplicate containers
            const containers = document.querySelectorAll('.mobile-search-container');
            if (containers.length > 1) {
                for (let i = 1; i < containers.length; i++) {
                    containers[i].parentNode?.removeChild(containers[i]);
                }
            }
        }
    }
    
    // ======================================
    // EVENT HANDLERS
    // ======================================
    function handleSearchInput() {
        const value = this.value.trim();
        
        if (!value) {
            hideDropdown();
            return;
        }

        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }

        // Set new timeout for search
        searchTimeout = setTimeout(() => {
            if (window.innerWidth <= MOBILE_BREAKPOINT) {
                // Mobile search
                showSearchContainer();
                mobileSearchInput.value = value;
                showMobileLoading();
                
                performSearch(value, showMobileResults);
            } else {
                // Desktop search
                performSearch(value, showDropdown);
            }
        }, SEARCH_DELAY);
    }
    
    function handleSearchFocus() {
        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            showSearchContainer();
            // Reset any search history that might be visible
            document.querySelectorAll('.mobile-search-history:not(.mobile-search-container .mobile-search-history)').forEach(el => {
                el.style.display = 'none';
            });
        } else if (this.value.trim()) {
            dropdown.style.display = 'block';
        }
    }
    
    function handleSearchBlur() {
        if (window.innerWidth > MOBILE_BREAKPOINT) {
            setTimeout(hideDropdown, 120);
        }
    }
    
    function handleMobileSearchInput() {
        const value = this.value.trim();
        
        // Show/hide clear button
        if (value) {
            mobileSearchClear.classList.add('active');
        } else {
            mobileSearchClear.classList.remove('active');
            renderSearchHistory();
            return;
        }
        
        // Clear previous timeout
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        // Set new timeout for search
        searchTimeout = setTimeout(() => {
            showMobileLoading();
            performSearch(value, showMobileResults);
        }, SEARCH_DELAY);
    }
    
    function handleMobileSearchClick(e) {
        // Handle history item click
        const historyItem = e.target.closest('.mobile-search-history-item');
        if (historyItem) {
            const query = historyItem.dataset.query;
            mobileSearchInput.value = query;
            mobileSearchClear.classList.add('active');
            
            showMobileLoading();
            performSearch(query, showMobileResults);
            return;
        }
        
        // Handle add to cart
        const addButton = e.target.closest('.mobile-search-add');
        if (addButton) {
            const productId = addButton.dataset.id;
            const originalHtml = addButton.innerHTML;
            
            addButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            addButton.disabled = true;
            
            addToCart(productId, () => {
                addButton.innerHTML = '<i class="fas fa-check"></i>';
                setTimeout(() => {
                    addButton.innerHTML = originalHtml;
                    addButton.disabled = false;
                }, 1500);
            }, () => {
                addButton.innerHTML = '<i class="fas fa-exclamation-circle"></i>';
                setTimeout(() => {
                    addButton.innerHTML = originalHtml;
                    addButton.disabled = false;
                }, 1500);
            });
        }
    }
    
    function handleDropdownInteraction(e) {
        // Add to cart button clicked
        if (e.target.classList.contains('real-time-search-add') || e.target.closest('.real-time-search-add')) {
            e.preventDefault();
            
            const button = e.target.closest('.real-time-search-add');
            const productId = button.dataset.productId;
            const item = button.closest('.real-time-search-item');
            const name = item.querySelector('.real-time-search-name').textContent;
            
            addToCart(productId, () => {
                showNotification(`${name} добавлен в корзину`);
            }, () => {
                showNotification('Ошибка при добавлении в корзину');
            });
            
            return;
        }
        
        // Item clicked (not the add button)
        if (e.target.classList.contains('real-time-search-item') || e.target.closest('.real-time-search-item')) {
            const item = e.target.closest('.real-time-search-item');
            const name = item.querySelector('.real-time-search-name').textContent;
            searchInput.value = name;
            hideDropdown();
        }
    }
    
    function handleSearchFormSubmit(e) {
        e.preventDefault();
        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            showSearchContainer();
        }
    }
    
    // ======================================
    // UI HELPERS
    // ======================================
    function showDropdown(results, query) {
        if (!results || !results.length) {
            dropdown.innerHTML = '<div class="real-time-search-noresult">Ничего не найдено</div>';
        } else {
            let html = '';
            for (const product of results) {
                html += `
                    <div class="real-time-search-item" tabindex="0">
                        <img class="real-time-search-img" src="${product.image1 || '/media/default.jpg'}" alt="${product.name || ''}">
                        <div class="real-time-search-info">
                            <div class="real-time-search-name">${highlightMatch(product.name, query)}</div>
                            <div class="real-time-search-price">${formatPrice(product.prices?.[0])} сум</div>
                            <div class="real-time-search-producer">${product.producer || ''}</div>
                        </div>
                        <button class="real-time-search-add" data-product-id="${product.id}">
                            <i class="fas fa-cart-plus"></i> В корзину
                        </button>
                    </div>
                `;
            }
            dropdown.innerHTML = html;
        }
        dropdown.style.display = 'block';
    }

    function hideDropdown() {
        dropdown.style.display = 'none';
    }
    
    function showMobileResults(results, query) {
        if (!results || !results.length) {
            mobileSearchBody.innerHTML = `
                <div class="mobile-search-empty">
                    <div class="mobile-search-empty-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <div class="mobile-search-empty-title">Ничего не найдено</div>
                    <div class="mobile-search-empty-text">
                        По запросу "${query}" не найдено ни одного товара
                    </div>
                </div>
            `;
            return;
        }
        
        let resultsHtml = '';
        for (const product of results) {
            const price = product.prices && product.prices.length > 0 ? product.prices[0] : 0;
            resultsHtml += `
                <div class="mobile-search-item" data-id="${product.id}">
                    <img class="mobile-search-img" src="${product.image1 || '/media/default.jpg'}" alt="${product.name || ''}">
                    <div class="mobile-search-info">
                        <div class="mobile-search-name">${highlightMatch(product.name, query)}</div>
                        <div class="mobile-search-price">${formatPrice(price)} сум</div>
                        ${product.producer ? `<div class="mobile-search-producer">${product.producer}</div>` : ''}
                    </div>
                    <button class="mobile-search-add" data-id="${product.id}">
                        <i class="fas fa-cart-plus"></i>
                    </button>
                </div>
            `;
        }
        
        mobileSearchBody.innerHTML = `
            <div class="mobile-search-results">
                ${resultsHtml}
            </div>
        `;
        
        // Save to history if results found
        if (results.length > 0) {
            saveToHistory(query);
        }
    }
    
    function showMobileLoading() {
        mobileSearchBody.innerHTML = `
            <div class="mobile-search-loading">
                <div class="mobile-search-loading-spinner"></div>
                <div>Поиск...</div>
            </div>
        `;
    }
    
    function showSearchContainer() {
        // Hide any stray elements
        document.querySelectorAll('.mobile-search-history:not(.mobile-search-container .mobile-search-history)').forEach(el => {
            el.style.display = 'none';
        });
        
        mobileSearchContainer.classList.add('active');
        document.body.style.overflow = 'hidden';
        isSearchActive = true;
        
        // Focus input and render history
        setTimeout(() => {
            mobileSearchInput.focus();
            renderSearchHistory();
        }, 100);
    }
    
    function hideSearchContainer() {
        mobileSearchContainer.classList.remove('active');
        document.body.style.overflow = '';
        isSearchActive = false;
        
        // Clear input
        mobileSearchInput.value = '';
        mobileSearchClear.classList.remove('active');
    }
    
    // ======================================
    // SEARCH HISTORY HELPERS
    // ======================================
    function saveToHistory(query) {
        query = query.trim();
        if (!query || query.length < 3) return;
        
        // Remove if already exists
        searchHistory = searchHistory.filter(item => item.toLowerCase() !== query.toLowerCase());
        
        // Add to beginning of array
        searchHistory.unshift(query);
        
        // Limit to max items
        if (searchHistory.length > MAX_HISTORY_ITEMS) {
            searchHistory = searchHistory.slice(0, MAX_HISTORY_ITEMS);
        }
        
        // Save to localStorage
        localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
        
        // Render search history
        renderSearchHistory();
    }
    
    function renderSearchHistory() {
        if (!mobileSearchContainer.classList.contains('active')) {
            return; // Don't render history if container is not active
        }
        
        if (searchHistory.length === 0) {
            mobileSearchHistoryItems.innerHTML = `
                <div style="color: #888; font-size: 13px;">История поиска пуста</div>
            `;
            return;
        }
        
        mobileSearchHistoryItems.innerHTML = searchHistory.map(query => `
            <div class="mobile-search-history-item" data-query="${query}">
                <i class="fas fa-history"></i>${query}
            </div>
        `).join('');
    }
    
    function clearSearchHistory() {
        searchHistory = [];
        localStorage.removeItem('searchHistory');
        renderSearchHistory();
    }
    
    function clearMobileSearchInput() {
        mobileSearchInput.value = '';
        mobileSearchClear.classList.remove('active');
        renderSearchHistory();
        mobileSearchInput.focus();
    }
    
    // ======================================
    // FORMAT HELPERS
    // ======================================
    function highlightMatch(text, query) {
        if (!query || !text) return text || '';
        const re = new RegExp('('+query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')+')', 'ig');
        return text.replace(re, '<mark>$1</mark>');
    }
    
    function formatPrice(price) {
        if (!price) return "0";
        return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }
    
    // ======================================
    // API FUNCTIONS
    // ======================================
    function performSearch(query, callback) {
        fetch(`/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                callback(data, query);
            })
            .catch(error => {
                console.error('Search error:', error);
                if (callback === showMobileResults) {
                    mobileSearchBody.innerHTML = `
                        <div class="mobile-search-empty">
                            <div class="mobile-search-empty-icon">
                                <i class="fas fa-exclamation-circle"></i>
                            </div>
                            <div class="mobile-search-empty-title">Ошибка</div>
                            <div class="mobile-search-empty-text">
                                Произошла ошибка при поиске. Попробуйте позже.
                            </div>
                        </div>
                    `;
                } else {
                    dropdown.innerHTML = '<div class="real-time-search-noresult">Ошибка поиска</div>';
                    dropdown.style.display = 'block';
                }
            });
    }
    
    function addToCart(productId, successCallback, errorCallback) {
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
                // Update cart badges
                const cartBadges = document.querySelectorAll('.cart-badge');
                cartBadges.forEach(badge => {
                    badge.setAttribute('data-count', data.cart_count);
                });
                
                showNotification('Товар добавлен в корзину');
                
                if (successCallback) successCallback();
            } else {
                throw new Error(data.message || 'Failed to add to cart');
            }
        })
        .catch(error => {
            console.error('Add to cart error:', error);
            showNotification('Ошибка при добавлении в корзину');
            
            if (errorCallback) errorCallback();
        });
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