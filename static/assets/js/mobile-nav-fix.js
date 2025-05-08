// Mobile Navigation Fix Script - Positioning Only

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize mobile navigation display
    checkMobileNav();
    
    // Handle mobile navigation positioning on resize
    window.addEventListener('resize', checkMobileNav);
});

// Function to check screen width and handle mobile nav spacing
function checkMobileNav() {
    const mobileNav = document.querySelector('.mobile-bottom-nav');
    if (!mobileNav) return;
    
    if (window.innerWidth <= 991) {
        // Show mobile nav on small screens
        mobileNav.style.display = 'flex';
        
        // Add padding to bottom of page to prevent content being hidden behind nav
        document.body.style.paddingBottom = (mobileNav.offsetHeight + 5) + 'px';
        
        // Add margin to footer
        const footer = document.querySelector('.site-footer');
        if (footer) {
            footer.style.marginBottom = (mobileNav.offsetHeight + 5) + 'px';
        }
        
        // Position the catalog menu correctly for mobile
        setupMobileCatalogMenu();
    } else {
        // Hide mobile nav on large screens
        mobileNav.style.display = 'none';
        
        // Reset body padding
        document.body.style.paddingBottom = '';
        
        // Reset footer margin
        const footer = document.querySelector('.site-footer');
        if (footer) {
            footer.style.marginBottom = '';
        }
    }
}

// Fix catalog menu positioning on mobile
function setupMobileCatalogMenu() {
    const catalogMenu = document.querySelector('#mobileCatalogDropdown .catalog-menu');
    if (!catalogMenu) return;
    
    // Add event listener to catalog toggle button if not already added
    const catalogButton = document.querySelector('.mobile-bottom-nav a[onclick*="toggleCatalogMenu"]');
    if (catalogButton && !catalogButton._positionHandlerAdded) {
        // Mark as handler added to avoid duplicate listeners
        catalogButton._positionHandlerAdded = true;
        
        // Add a handler after the original onclick
        const originalOnclick = catalogButton.onclick;
        catalogButton.onclick = function(e) {
            // Call original function first
            if (originalOnclick) {
                originalOnclick.call(this, e);
            } else {
                // Fallback if no original handler
                toggleCatalogMenu('mobileCatalogDropdown');
            }
            
            // Then fix positioning
            setTimeout(function() {
                if (catalogMenu.style.display === 'block' && window.innerWidth <= 991) {
                    // Make menu appear from bottom on mobile
                    catalogMenu.style.position = 'fixed';
                    catalogMenu.style.bottom = '60px'; // Match height of mobile nav
                    catalogMenu.style.left = '0';
                    catalogMenu.style.width = '100%';
                    catalogMenu.style.maxHeight = '70vh';
                    catalogMenu.style.zIndex = '990';
                }
            }, 10);
        };
    }
} 