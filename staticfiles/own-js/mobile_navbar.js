// Mobile Navigation Module
document.addEventListener('DOMContentLoaded', function() {
    // ======================================
    // CONSTANTS & CONFIG
    // ======================================
    const MOBILE_BREAKPOINT = 991; // Mobile breakpoint in px
    
    // ======================================
    // ELEMENT REFERENCES
    // ======================================
    const mobileNav = document.querySelector('.mobile-nav');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuBackdrop = document.querySelector('.mobile-menu__backdrop');
    const menuToggleButtons = document.querySelectorAll('.js-menu-toggle');
    const menuCloseButtons = document.querySelectorAll('.js-menu-close');
    const catalogFilter = document.querySelector('.mobile-catalog-filter');
    const catalogCloseButtons = document.querySelectorAll('.js-catalog-close');
    
    if (!mobileNav) return; // Exit if mobile nav not present
    
    // ======================================
    // INITIALIZATION
    // ======================================
    setupMobileNav();
    setupSafeAreaSupport();
    
    // Re-apply spacing when window is resized
    window.addEventListener('resize', function() {
        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            adjustMobileNavSpacing();
        }
    });
    
    // ======================================
    // EVENT LISTENERS
    // ======================================
    // Menu toggle
    menuToggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleMobileMenu(true);
        });
    });
    
    // Menu close
    menuCloseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            toggleMobileMenu(false);
        });
    });
    
    // Backdrop click
    mobileMenuBackdrop?.addEventListener('click', function() {
        toggleMobileMenu(false);
    });
    
    // Catalog filter close
    catalogCloseButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (catalogFilter) {
                catalogFilter.classList.remove('active');
            }
        });
    });
    
    // ======================================
    // CORE FUNCTIONS
    // ======================================
    // Toggle mobile menu visibility
    function toggleMobileMenu(show) {
        if (mobileMenu) {
            if (show) {
                mobileMenu.classList.add('active');
                mobileMenuBackdrop.classList.add('active');
                document.body.style.overflow = 'hidden';
            } else {
                mobileMenu.classList.remove('active');
                mobileMenuBackdrop.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    }
    
    // Setup mobile navigation
    function setupMobileNav() {
        // Highlight active nav item based on current URL
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.mobile-nav-item');
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && (href === currentPath || (href !== '/' && currentPath.startsWith(href)))) {
                item.classList.add('active');
            }
        });
        
        // Apply initial spacing
        if (window.innerWidth <= MOBILE_BREAKPOINT) {
            adjustMobileNavSpacing();
        }
    }
    
    // Adjust content spacing based on mobile nav height
    function adjustMobileNavSpacing() {
        if (!mobileNav) return;
        
        const navHeight = mobileNav.offsetHeight;
        document.body.style.paddingBottom = navHeight + 'px';
    }
    
    // Setup iOS safe area support
    function setupSafeAreaSupport() {
        // Check if the browser supports CSS environment variables (iOS 11+)
        if (CSS.supports('padding-bottom: env(safe-area-inset-bottom)')) {
            // Add a meta tag if it doesn't exist
            let viewportMeta = document.querySelector('meta[name="viewport"]');
            
            if (viewportMeta) {
                let content = viewportMeta.getAttribute('content');
                if (!content.includes('viewport-fit=cover')) {
                    viewportMeta.setAttribute('content', content + ', viewport-fit=cover');
                }
            }
        }
    }
}); 