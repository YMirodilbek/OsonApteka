// Slider Functionality
document.addEventListener('DOMContentLoaded', function() {
    const slider = document.querySelector('.main_picture_slider');
    if (!slider) return; // Exit if slider doesn't exist

    const slides = slider.querySelectorAll('.main_picture_slider__item');
    const dots = slider.querySelectorAll('.slider-dot');
    const prevBtn = slider.querySelector('.slider-nav.prev');
    const nextBtn = slider.querySelector('.slider-nav.next');
    
    let currentIndex = 0;
    let slideInterval;
    const slideDelay = 5000; // 5 seconds between automatic slides
    
    // Initialize the slider
    function initSlider() {
        // Set the first slide as active
        updateSlider();
        
        // Start automatic sliding
        startSlideTimer();
        
        // Add event listeners
        prevBtn.addEventListener('click', prevSlide);
        nextBtn.addEventListener('click', nextSlide);
        
        // Add dot navigation
        dots.forEach(dot => {
            dot.addEventListener('click', function() {
                currentIndex = parseInt(this.getAttribute('data-index'));
                updateSlider();
                resetSlideTimer();
            });
        });
        
        // Pause automatic sliding when hovering over the slider
        slider.addEventListener('mouseenter', stopSlideTimer);
        slider.addEventListener('mouseleave', startSlideTimer);
        
        // Add touch support
        let touchStartX = 0;
        let touchEndX = 0;
        
        slider.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
            stopSlideTimer();
        }, { passive: true });
        
        slider.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
            startSlideTimer();
        }, { passive: true });
        
        function handleSwipe() {
            const swipeThreshold = 50; // Minimum swipe distance
            const swipeDistance = touchEndX - touchStartX;
            
            if (swipeDistance > swipeThreshold) {
                prevSlide(); // Swipe right
            } else if (swipeDistance < -swipeThreshold) {
                nextSlide(); // Swipe left
            }
        }
    }
    
    // Update the slider display
    function updateSlider() {
        // Update slides
        slides.forEach((slide, index) => {
            if (index === currentIndex) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });
        
        // Update dots
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    // Go to the previous slide
    function prevSlide() {
        currentIndex = (currentIndex - 1 + slides.length) % slides.length;
        updateSlider();
        resetSlideTimer();
    }
    
    // Go to the next slide
    function nextSlide() {
        currentIndex = (currentIndex + 1) % slides.length;
        updateSlider();
        resetSlideTimer();
    }
    
    // Start the automatic sliding timer
    function startSlideTimer() {
        stopSlideTimer(); // Clear any existing timer
        slideInterval = setInterval(nextSlide, slideDelay);
    }
    
    // Stop the automatic sliding timer
    function stopSlideTimer() {
        if (slideInterval) {
            clearInterval(slideInterval);
        }
    }
    
    // Reset the automatic sliding timer
    function resetSlideTimer() {
        stopSlideTimer();
        startSlideTimer();
    }
    
    // Initialize the slider
    initSlider();
}); 