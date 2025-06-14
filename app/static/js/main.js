/**
 * NextProperty AI - Main JavaScript File
 * Contains global functionality and utilities
 */

// =====================================================
// GLOBAL VARIABLES
// =====================================================
window.NextProperty = {
    config: {
        apiBaseUrl: '/api',
        mapTileUrl: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        mapAttribution: '© OpenStreetMap contributors',
        animationDuration: 300,
        toastTimeout: 5000
    },
    state: {
        currentUser: null,
        favoriteProperties: [],
        watchlistProperties: [],
        notifications: []
    },
    utils: {},
    ui: {},
    maps: {},
    charts: {}
};

// =====================================================
// UTILITY FUNCTIONS
// =====================================================
NextProperty.utils = {
    /**
     * Format currency values
     */
    formatCurrency: function(amount, currency = 'CAD') {
        return new Intl.NumberFormat('en-CA', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    },

    /**
     * Format numbers with commas
     */
    formatNumber: function(number) {
        return new Intl.NumberFormat('en-CA').format(number);
    },

    /**
     * Format dates
     */
    formatDate: function(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        return new Intl.DateTimeFormat('en-CA', {...defaultOptions, ...options}).format(new Date(date));
    },

    /**
     * Debounce function
     */
    debounce: function(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },

    /**
     * Throttle function
     */
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    /**
     * Generate random ID
     */
    generateId: function() {
        return Math.random().toString(36).substr(2, 9);
    },

    /**
     * Validate email
     */
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    /**
     * Calculate investment metrics
     */
    calculateROI: function(initialInvestment, annualIncome, appreciation = 0) {
        return ((annualIncome + appreciation) / initialInvestment) * 100;
    },

    calculateCapRate: function(noi, propertyValue) {
        return (noi / propertyValue) * 100;
    },

    calculateCashFlow: function(monthlyIncome, monthlyExpenses) {
        return monthlyIncome - monthlyExpenses;
    },

    /**
     * Local storage helpers
     */
    storage: {
        set: function(key, value) {
            try {
                localStorage.setItem(key, JSON.stringify(value));
                return true;
            } catch (e) {
                console.error('Error saving to localStorage:', e);
                return false;
            }
        },

        get: function(key, defaultValue = null) {
            try {
                const item = localStorage.getItem(key);
                return item ? JSON.parse(item) : defaultValue;
            } catch (e) {
                console.error('Error reading from localStorage:', e);
                return defaultValue;
            }
        },

        remove: function(key) {
            try {
                localStorage.removeItem(key);
                return true;
            } catch (e) {
                console.error('Error removing from localStorage:', e);
                return false;
            }
        }
    }
};

// =====================================================
// UI COMPONENTS
// =====================================================
NextProperty.ui = {
    /**
     * Show toast notification
     */
    showToast: function(message, type = 'info', duration = null) {
        const toastId = NextProperty.utils.generateId();
        const toastContainer = this.getToastContainer();
        
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" 
                 role="alert" aria-live="assertive" aria-atomic="true" 
                 id="toast-${toastId}">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${this.getToastIcon(type)} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        
        const toastElement = document.getElementById(`toast-${toastId}`);
        const toast = new bootstrap.Toast(toastElement, {
            delay: duration || NextProperty.config.toastTimeout
        });
        
        toast.show();
        
        // Remove element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
        
        return toast;
    },

    /**
     * Get or create toast container
     */
    getToastContainer: function() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1055';
            document.body.appendChild(container);
        }
        return container;
    },

    /**
     * Get icon for toast type
     */
    getToastIcon: function(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    },

    /**
     * Show loading spinner
     */
    showLoading: function(element, message = 'Loading...') {
        const loadingHtml = `
            <div class="loading-overlay d-flex flex-column align-items-center justify-content-center">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted">${message}</p>
            </div>
        `;
        
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        element.style.position = 'relative';
        element.insertAdjacentHTML('beforeend', loadingHtml);
        
        // Style the overlay
        const overlay = element.querySelector('.loading-overlay');
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            z-index: 1000;
            backdrop-filter: blur(2px);
        `;
    },

    /**
     * Hide loading spinner
     */
    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    },

    /**
     * Show confirmation modal
     */
    showConfirmModal: function(title, message, onConfirm, onCancel = null) {
        const modalId = NextProperty.utils.generateId();
        const modalHtml = `
            <div class="modal fade" id="modal-${modalId}" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${message}</p>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="confirm-${modalId}">Confirm</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const modalElement = document.getElementById(`modal-${modalId}`);
        const modal = new bootstrap.Modal(modalElement);
        
        // Handle confirm button
        document.getElementById(`confirm-${modalId}`).addEventListener('click', () => {
            modal.hide();
            if (onConfirm) onConfirm();
        });
        
        // Handle cancel
        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
            if (onCancel) onCancel();
        });
        
        modal.show();
        return modal;
    },

    /**
     * Initialize tooltips
     */
    initTooltips: function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },

    /**
     * Initialize popovers
     */
    initPopovers: function() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
};

// =====================================================
// API HELPERS
// =====================================================
NextProperty.api = {
    /**
     * Make API request
     */
    request: function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        // Add CSRF token if available
        const csrfToken = document.querySelector('meta[name="csrf-token"]');
        if (csrfToken) {
            finalOptions.headers['X-CSRFToken'] = csrfToken.getAttribute('content');
        }
        
        return fetch(NextProperty.config.apiBaseUrl + url, finalOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            });
    },

    /**
     * GET request
     */
    get: function(url, params = {}) {
        const urlParams = new URLSearchParams(params);
        const fullUrl = urlParams.toString() ? `${url}?${urlParams}` : url;
        return this.request(fullUrl);
    },

    /**
     * POST request
     */
    post: function(url, data = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     */
    put: function(url, data = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    /**
     * DELETE request
     */
    delete: function(url) {
        return this.request(url, {
            method: 'DELETE'
        });
    }
};

// =====================================================
// PROPERTY FUNCTIONS
// =====================================================
NextProperty.properties = {
    /**
     * Add property to watchlist
     */
    addToWatchlist: function(propertyId) {
        return NextProperty.api.post(`/watchlist/${propertyId}`)
            .then(response => {
                if (response.success) {
                    NextProperty.ui.showToast('Property added to watchlist', 'success');
                    this.updateWatchlistState(propertyId, true);
                } else {
                    throw new Error(response.message || 'Failed to add to watchlist');
                }
                return response;
            })
            .catch(error => {
                NextProperty.ui.showToast('Error adding to watchlist', 'error');
                throw error;
            });
    },

    /**
     * Remove property from watchlist
     */
    removeFromWatchlist: function(propertyId) {
        return NextProperty.api.delete(`/watchlist/${propertyId}`)
            .then(response => {
                if (response.success) {
                    NextProperty.ui.showToast('Property removed from watchlist', 'info');
                    this.updateWatchlistState(propertyId, false);
                } else {
                    throw new Error(response.message || 'Failed to remove from watchlist');
                }
                return response;
            })
            .catch(error => {
                NextProperty.ui.showToast('Error removing from watchlist', 'error');
                throw error;
            });
    },

    /**
     * Update watchlist state
     */
    updateWatchlistState: function(propertyId, isWatchlisted) {
        const buttons = document.querySelectorAll(`[data-property-id="${propertyId}"] .watchlist-btn`);
        buttons.forEach(button => {
            const icon = button.querySelector('i');
            if (isWatchlisted) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                button.classList.add('active');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                button.classList.remove('active');
            }
        });
        
        // Update state
        if (isWatchlisted) {
            NextProperty.state.watchlistProperties.push(propertyId);
        } else {
            const index = NextProperty.state.watchlistProperties.indexOf(propertyId);
            if (index > -1) {
                NextProperty.state.watchlistProperties.splice(index, 1);
            }
        }
    },

    /**
     * Get property analysis
     */
    getAnalysis: function(propertyId) {
        return NextProperty.api.get(`/properties/${propertyId}/analysis`);
    },

    /**
     * Search properties
     */
    search: function(filters = {}) {
        return NextProperty.api.get('/properties/search', filters);
    }
};

// =====================================================
// SCROLL FUNCTIONS
// =====================================================
NextProperty.scroll = {
    /**
     * Initialize back to top button
     */
    initBackToTop: function() {
        const backToTopBtn = document.getElementById('backToTop');
        if (!backToTopBtn) return;
        
        const toggleVisibility = NextProperty.utils.throttle(() => {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        }, 100);
        
        window.addEventListener('scroll', toggleVisibility);
        
        backToTopBtn.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    },

    /**
     * Smooth scroll to element
     */
    scrollToElement: function(selector, offset = 0) {
        const element = document.querySelector(selector);
        if (element) {
            const elementPosition = element.offsetTop - offset;
            window.scrollTo({
                top: elementPosition,
                behavior: 'smooth'
            });
        }
    }
};

// =====================================================
// FORM HELPERS
// =====================================================
NextProperty.forms = {
    /**
     * Validate form
     */
    validate: function(form) {
        const errors = [];
        const formData = new FormData(form);
        
        // Get validation rules from data attributes
        const fields = form.querySelectorAll('[data-required], [data-email], [data-min], [data-max]');
        
        fields.forEach(field => {
            const value = formData.get(field.name) || '';
            
            // Required validation
            if (field.hasAttribute('data-required') && !value.trim()) {
                errors.push(`${field.name} is required`);
                this.showFieldError(field, 'This field is required');
            }
            
            // Email validation
            if (field.hasAttribute('data-email') && value && !NextProperty.utils.validateEmail(value)) {
                errors.push(`${field.name} must be a valid email`);
                this.showFieldError(field, 'Please enter a valid email address');
            }
            
            // Min length validation
            if (field.hasAttribute('data-min')) {
                const min = parseInt(field.getAttribute('data-min'));
                if (value.length < min) {
                    errors.push(`${field.name} must be at least ${min} characters`);
                    this.showFieldError(field, `Must be at least ${min} characters`);
                }
            }
            
            // Max length validation
            if (field.hasAttribute('data-max')) {
                const max = parseInt(field.getAttribute('data-max'));
                if (value.length > max) {
                    errors.push(`${field.name} must be no more than ${max} characters`);
                    this.showFieldError(field, `Must be no more than ${max} characters`);
                }
            }
        });
        
        return errors;
    },

    /**
     * Show field error
     */
    showFieldError: function(field, message) {
        // Remove existing error
        this.clearFieldError(field);
        
        // Add error class
        field.classList.add('is-invalid');
        
        // Add error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    },

    /**
     * Clear field error
     */
    clearFieldError: function(field) {
        field.classList.remove('is-invalid');
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
    },

    /**
     * Clear all form errors
     */
    clearAllErrors: function(form) {
        const fields = form.querySelectorAll('.is-invalid');
        fields.forEach(field => this.clearFieldError(field));
    }
};

// =====================================================
// INITIALIZATION
// =====================================================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    NextProperty.ui.initTooltips();
    NextProperty.ui.initPopovers();
    
    // Initialize scroll functions
    NextProperty.scroll.initBackToTop();
    
    // Initialize form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            NextProperty.forms.clearAllErrors(form);
            const errors = NextProperty.forms.validate(form);
            
            if (errors.length === 0) {
                // Form is valid, submit it
                this.submit();
            } else {
                NextProperty.ui.showToast('Please fix the errors below', 'error');
            }
        });
    });
    
    // Initialize watchlist buttons
    const watchlistBtns = document.querySelectorAll('.watchlist-btn');
    watchlistBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const propertyId = this.closest('[data-property-id]').getAttribute('data-property-id');
            const isWatchlisted = this.classList.contains('active');
            
            if (isWatchlisted) {
                NextProperty.properties.removeFromWatchlist(propertyId);
            } else {
                NextProperty.properties.addToWatchlist(propertyId);
            }
        });
    });
    
    // Initialize auto-save for forms
    const autoSaveForms = document.querySelectorAll('form[data-auto-save]');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('change', NextProperty.utils.debounce(() => {
                // Auto-save logic here
                console.log('Auto-saving form data...');
            }, 1000));
        });
    });
    
    // Load user state if logged in
    const userDataElement = document.getElementById('user-data');
    if (userDataElement) {
        try {
            NextProperty.state.currentUser = JSON.parse(userDataElement.textContent);
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
    
    console.log('NextProperty AI initialized successfully');
});

// =====================================================
// EXPORT FOR GLOBAL ACCESS
// =====================================================
window.NextProperty = NextProperty;
