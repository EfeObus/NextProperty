// Modern Interactive Animations for NextProperty Real Estate

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

// Initialize scroll animations
document.addEventListener('DOMContentLoaded', function() {
    initScrollAnimations();
    initPropertyCardAnimations();
    initCountUpAnimations();
    initParallaxEffects();
    initSearchFormAnimations();
});

// Scroll animations for elements with animate-on-scroll class
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const delay = element.classList.contains('delay-1') ? 100 :
                             element.classList.contains('delay-2') ? 200 :
                             element.classList.contains('delay-3') ? 300 :
                             element.classList.contains('delay-4') ? 400 :
                             element.classList.contains('delay-5') ? 500 :
                             element.classList.contains('delay-6') ? 600 : 0;
                
                setTimeout(() => {
                    element.classList.add('animate-visible');
                }, delay);
                
                observer.unobserve(element);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Property card hover animations and interactions
function initPropertyCardAnimations() {
    document.querySelectorAll('.property-card-modern').forEach(card => {
        const image = card.querySelector('.property-image');
        const overlay = card.querySelector('.property-overlay');
        const actionBtns = card.querySelectorAll('.action-btn');
        
        card.addEventListener('mouseenter', () => {
            if (image) {
                image.style.transform = 'scale(1.05)';
            }
            if (overlay) {
                overlay.style.opacity = '1';
            }
            actionBtns.forEach((btn, index) => {
                setTimeout(() => {
                    btn.style.transform = 'translateY(0) scale(1)';
                    btn.style.opacity = '1';
                }, index * 50);
            });
        });
        
        card.addEventListener('mouseleave', () => {
            if (image) {
                image.style.transform = 'scale(1)';
            }
            if (overlay) {
                overlay.style.opacity = '0';
            }
            actionBtns.forEach(btn => {
                btn.style.transform = 'translateY(10px) scale(0.8)';
                btn.style.opacity = '0';
            });
        });
    });
    
    // Favorite button functionality
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const icon = this.querySelector('i');
            if (icon.classList.contains('far')) {
                icon.classList.replace('far', 'fas');
                this.classList.add('favorited');
                
                // Add heart animation
                this.style.animation = 'heartBeat 0.6s ease-in-out';
                setTimeout(() => {
                    this.style.animation = '';
                }, 600);
            } else {
                icon.classList.replace('fas', 'far');
                this.classList.remove('favorited');
            }
        });
    });
}

// Count-up animation for stats
function initCountUpAnimations() {
    const countElements = document.querySelectorAll('.stat-number');
    
    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                const text = element.textContent;
                const number = parseFloat(text.replace(/[^0-9.]/g, ''));
                
                if (!isNaN(number)) {
                    animateCount(element, 0, number, 2000, text);
                }
                countObserver.unobserve(element);
            }
        });
    }, observerOptions);
    
    countElements.forEach(el => countObserver.observe(el));
}

function animateCount(element, start, end, duration, originalText) {
    const startTime = performance.now();
    const prefix = originalText.replace(/[0-9.,]/g, '').split(end.toString())[0] || '';
    const suffix = originalText.replace(/[0-9.,]/g, '').split(end.toString())[1] || '';
    
    function updateCount(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * easeOut;
        
        let displayValue;
        if (end >= 1000000) {
            displayValue = (current / 1000000).toFixed(1) + 'M';
        } else if (end >= 1000) {
            displayValue = (current / 1000).toFixed(0) + 'K';
        } else {
            displayValue = Math.floor(current).toLocaleString();
        }
        
        element.textContent = prefix + displayValue + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(updateCount);
        } else {
            element.textContent = originalText;
        }
    }
    
    requestAnimationFrame(updateCount);
}

// Parallax effects for background elements
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.hero-buildings .building');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        parallaxElements.forEach((element, index) => {
            const speed = (index + 1) * 0.1;
            element.style.transform = `translateY(${rate * speed}px)`;
        });
    });
}

// Search form animations
function initSearchFormAnimations() {
    const searchInputs = document.querySelectorAll('.search-input-modern');
    
    searchInputs.forEach(input => {
        const group = input.closest('.search-input-group');
        const label = group?.querySelector('label');
        
        input.addEventListener('focus', () => {
            group?.classList.add('focused');
            if (label) {
                label.style.transform = 'translateY(-20px) scale(0.8)';
                label.style.color = 'var(--warning-color)';
            }
        });
        
        input.addEventListener('blur', () => {
            if (!input.value) {
                group?.classList.remove('focused');
                if (label) {
                    label.style.transform = '';
                    label.style.color = '';
                }
            }
        });
        
        // Check if input has value on load
        if (input.value) {
            group?.classList.add('focused');
            if (label) {
                label.style.transform = 'translateY(-20px) scale(0.8)';
                label.style.color = 'var(--warning-color)';
            }
        }
    });
}

// Feature card hover effects
document.addEventListener('DOMContentLoaded', function() {
    const featureCards = document.querySelectorAll('.feature-card-modern');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
            
            const icon = this.querySelector('.feature-icon-modern');
            if (icon) {
                icon.style.transform = 'scale(1.1) rotate(5deg)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            
            const icon = this.querySelector('.feature-icon-modern');
            if (icon) {
                icon.style.transform = '';
            }
        });
    });
});

// Add smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading animations for images
function initImageLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initImageLoading);

// Add CSS animations keyframes dynamically
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes heartBeat {
        0% { transform: scale(1); }
        25% { transform: scale(1.2); }
        50% { transform: scale(1); }
        75% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .animate-on-scroll.animate-visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .property-image {
        transition: transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .action-btn {
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        transform: translateY(10px) scale(0.8);
        opacity: 0;
    }
    
    .feature-card-modern {
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    .feature-icon-modern {
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    img.loaded {
        opacity: 1;
        transition: opacity 0.3s ease-in-out;
    }
    
    img[data-src] {
        opacity: 0;
    }
`;
document.head.appendChild(styleSheet);
