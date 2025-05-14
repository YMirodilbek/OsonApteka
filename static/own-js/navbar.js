// Language Selector Functionality
document.querySelector('.language-selector').addEventListener('click', function() {
    // Add your language switching logic here
});

// Search Form Functionality
document.querySelector('.search-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const searchQuery = document.querySelector('.search-input').value;
    // Add your search logic here
});

// Mobile Menu Functionality (if needed)
function toggleMobileMenu() {
    const nav = document.querySelector('.top-bar__nav');
    nav.classList.toggle('active');
}

// // Sticky Header on Scroll
let lastScroll = 0;
const header = document.querySelector('.main-header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > lastScroll && currentScroll > 100) {
        // Scrolling down & past the header
        header.style.transform = 'translateY(-100%)';
    } else {
        // Scrolling up
        header.style.transform = 'translateY(0)';
    }

    lastScroll = currentScroll;
});

// Custom Select Functionality
document.addEventListener('DOMContentLoaded', function() {
    const customSelect = document.querySelector('.custom-select');

    if (!customSelect) return; // Agar element topilmasa, funksiyadan chiqish

    const selectHeader = customSelect.querySelector('.select-header');
    const searchInput = customSelect.querySelector('.search-box input');
    const options = customSelect.querySelectorAll('.option');
    const optionsContainer = customSelect.querySelector('.options-container');
    let selectedOption = null;

    // Add tooltips to options with long text
    options.forEach(option => {
        const text = option.textContent;
        option.setAttribute('title', text);
    });

    // Toggle dropdown
    selectHeader.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        const wasActive = customSelect.classList.contains('active');
        
        // Close all open dropdowns
        document.querySelectorAll('.custom-select.active').forEach(select => {
            select.classList.remove('active');
        });

        // If it was closed before, open it
        if (!wasActive) {
            customSelect.classList.add('active');
            
            // Reset search and options when opening
            if (searchInput) {
                searchInput.value = '';
                
                // Make all options visible
                options.forEach(opt => {
                    opt.classList.remove('hidden');
                    opt.innerHTML = opt.textContent; // Remove any highlighting
                });
                
                // Remove no results message if it exists
                const noResults = customSelect.querySelector('.no-results');
                if (noResults) noResults.remove();
                
                // Focus the search input
                setTimeout(() => {
                    searchInput.focus();
                }, 100);
            }
        }
    });
    
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const selects = document.querySelectorAll('.custom-select');
        selects.forEach(select => {
            if (!select.contains(e.target)) {
                select.classList.remove('active');
            }
        });
    });

    // Prevent dropdown from closing when clicking inside search box
    if (searchInput) {
        searchInput.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    // Improved search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase().trim();
            let hasVisibleOptions = false;

            // Handle empty search
            if (!searchTerm) {
                // Show all options when search is empty
                options.forEach(option => {
                    option.classList.remove('hidden');
                    option.innerHTML = option.textContent;
                });
                
                // Remove no results message if it exists
                const noResults = customSelect.querySelector('.no-results');
                if (noResults) noResults.remove();
                return;
            }

            options.forEach(option => {
                const text = option.textContent.toLowerCase();
                
                // Reset the option display
                option.innerHTML = option.textContent;
                
                // Check if the option matches the search term (full or partial word match)
                if (text.includes(searchTerm)) {
                    option.classList.remove('hidden');
                    hasVisibleOptions = true;
                    
                    // Highlight search term if it exists
                    try {
                        const escapedSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                        const regex = new RegExp(`(${escapedSearchTerm})`, 'gi');
                        const highlightedText = option.textContent.replace(
                            regex,
                            '<span class="highlight">$1</span>'
                        );
                        option.innerHTML = highlightedText;
                    } catch (error) {
                        console.log('Regex error:', error);
                    }
                } else {
                    option.classList.add('hidden');
                }
            });

            // Handle no results case
            const noResults = customSelect.querySelector('.no-results');
            
            if (!hasVisibleOptions) {
                if (!noResults) {
                    const message = document.createElement('div');
                    message.className = 'no-results';
                    message.textContent = 'Ничего не найдено';
                    optionsContainer.appendChild(message);
                }
            } else if (noResults) {
                noResults.remove();
            }
        });
    }

    // Option selection
    options.forEach(option => {
        option.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (selectedOption) {
                selectedOption.classList.remove('selected');
            }
            
            this.classList.add('selected');
            selectedOption = this;
            
            const headerSpan = selectHeader.querySelector('span');
            if (headerSpan) {
                // Get original text without HTML tags
                const originalText = this.dataset.value || this.textContent;
                headerSpan.textContent = originalText;
                
                // Add title attribute for tooltip on hover
                headerSpan.setAttribute('title', originalText);
            }
            
            customSelect.classList.remove('active');
            
            // Clear search
            if (searchInput) {
                searchInput.value = '';
                
                // Reset all options
                options.forEach(opt => {
                    opt.classList.remove('hidden');
                    // Display text without HTML
                    opt.innerHTML = opt.textContent;
                });
            }
            
            // Remove no results message if exists
            const noResults = customSelect.querySelector('.no-results');
            if (noResults) noResults.remove();

            // Custom event dispatch
            const event = new CustomEvent('optionSelected', {
                detail: {
                    value: this.dataset.value,
                    text: this.textContent.trim()
                }
            });
            customSelect.dispatchEvent(event);
        });
    });

    // Keyboard navigation
    customSelect.addEventListener('keydown', function(e) {
        // If dropdown is not active, don't handle keyboard navigation
        if (!customSelect.classList.contains('active')) return;

        const visibleOptions = [...options].filter(opt => !opt.classList.contains('hidden'));
        const currentIndex = selectedOption ? visibleOptions.indexOf(selectedOption) : -1;

        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (visibleOptions.length > 0) {
                    if (currentIndex < visibleOptions.length - 1) {
                        visibleOptions[currentIndex + 1].click();
                    } else {
                        visibleOptions[0].click(); // Cycle to first option
                    }
                    // Scroll to the selected option
                    if (selectedOption) {
                        selectedOption.scrollIntoView({ block: 'nearest' });
                    }
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                if (visibleOptions.length > 0) {
                    if (currentIndex > 0) {
                        visibleOptions[currentIndex - 1].click();
                    } else {
                        visibleOptions[visibleOptions.length - 1].click(); // Cycle to last option
                    }
                    // Scroll to the selected option
                    if (selectedOption) {
                        selectedOption.scrollIntoView({ block: 'nearest' });
                    }
                }
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedOption) {
                    selectedOption.click();
                } else if (visibleOptions.length > 0) {
                    visibleOptions[0].click(); // Select first option if none selected
                }
                break;
            case 'Escape':
                e.preventDefault();
                customSelect.classList.remove('active');
                break;
            // Tab key should close the dropdown
            case 'Tab':
                customSelect.classList.remove('active');
                break;
        }
    });
});

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    // Get menu toggle elements
    const menuToggle = document.querySelector('.js-menu-toggle');
    const menuClose = document.querySelector('.js-menu-close');
    const mobileMenu = document.querySelector('.mobile-menu');
    const backdrop = document.querySelector('.mobile-menu__backdrop');
    const catalogToggle = document.querySelector('.js-catalog-toggle');
    const catalogClose = document.querySelector('.js-catalog-close');
    const catalogFilter = document.querySelector('.mobile-catalog-filter');

    // Open menu
    menuToggle?.addEventListener('click', function(e) {
        e.preventDefault();
        if (mobileMenu && backdrop) {
            mobileMenu.classList.add('active');
            backdrop.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    });

    // Close menu
    const closeMenu = () => {
        if (mobileMenu && backdrop) {
            mobileMenu.classList.remove('active');
            backdrop.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    menuClose?.addEventListener('click', closeMenu);
    backdrop?.addEventListener('click', closeMenu);
    
    // Mobile Nav Spacing
    const mobileNav = document.querySelector('.mobile-nav');
    
    function adjustMobileNavSpacing() {
        if (window.innerWidth <= 991) {
            // Show mobile nav on small screens
            mobileNav.style.display = 'flex';
            
            // Add padding to bottom of page to prevent content being hidden behind nav
            const navHeight = mobileNav.offsetHeight;
            document.body.style.paddingBottom = (navHeight + 5) + 'px';
            
            // Add margin to footer if it exists
            const footer = document.querySelector('.site-footer');
            if (footer) {
                footer.style.marginBottom = (navHeight + 5) + 'px';
            }
        } else {
            // Hide mobile nav on large screens
            mobileNav.style.display = 'none';
            
            // Reset body padding
            document.body.style.paddingBottom = '';
            
            // Reset footer margin if it exists
            const footer = document.querySelector('.site-footer');
            if (footer) {
                footer.style.marginBottom = '';
            }
        }
    }
    
    // Run on page load and window resize
    if (mobileNav) {
        adjustMobileNavSpacing();
        window.addEventListener('resize', adjustMobileNavSpacing);
    }
    
    // Setup iOS safe area support
    function setupSafeAreaSupport() {
        if (CSS.supports('padding: env(safe-area-inset-bottom)')) {
            // iOS safe area support exists
            const elementsWithSafeArea = document.querySelectorAll('.mobile-nav, .mobile-menu, .mobile-catalog-filter, .mobile-search-container');
            elementsWithSafeArea.forEach(el => {
                el.style.paddingBottom = 'max(env(safe-area-inset-bottom), 15px)';
            });
        }
    }
    
    setupSafeAreaSupport();

    // Mobile Language Selector
    const mobileLangSelect = document.getElementById('mobile-language');
    const desktopLangSelect = document.querySelector('.language-select');

    mobileLangSelect?.addEventListener('change', function() {
        if (desktopLangSelect) {
            desktopLangSelect.value = this.value;
            // Trigger change event on desktop select if needed
            const event = new Event('change');
            desktopLangSelect.dispatchEvent(event);
        }
    });

    // Sync desktop language to mobile
    desktopLangSelect?.addEventListener('change', function() {
        if (mobileLangSelect) {
            mobileLangSelect.value = this.value;
        }
    });

    // Mobile Catalog Filter
    catalogToggle?.addEventListener('click', function(e) {
        e.preventDefault();
        catalogFilter.classList.add('active');
        backdrop.classList.add('active');
        document.body.style.overflow = 'hidden';
    });

    catalogClose?.addEventListener('click', function() {
        catalogFilter.classList.remove('active');
        backdrop.classList.remove('active');
        document.body.style.overflow = '';
    });

    // Close catalog filter when clicking backdrop
    backdrop?.addEventListener('click', function() {
        if (catalogFilter.classList.contains('active')) {
            catalogFilter.classList.remove('active');
            backdrop.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Mobile Catalog Search
    const catalogSearch = document.querySelector('.mobile-catalog-filter__search input');
    const catalogItems = document.querySelectorAll('.mobile-catalog-filter__item');

    catalogSearch?.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase().trim();

        catalogItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    });

    // Mobile menu item links - close menu when clicked
    const mobileMenuLinks = document.querySelectorAll('.mobile-menu__link:not(.js-menu-toggle)');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (mobileMenu) {
                closeMenu();
            }
        });
    });
});
