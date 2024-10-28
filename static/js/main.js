// Global utility functions and event handlers

document.addEventListener('DOMContentLoaded', function() {
    initializeFlashMessages();
    initializeDropdowns();
    initializeFormValidation();
    initializeAutoRefresh();
    setupGlobalErrorHandling();
});

// Flash Messages
function initializeFlashMessages() {
    const flashMessages = document.querySelector('.flash-messages');
    if (!flashMessages) return;

    // Auto-hide messages after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Close button functionality
    document.querySelectorAll('.close-alert').forEach(button => {
        button.addEventListener('click', () => {
            const alert = button.closest('.alert');
            alert.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => alert.remove(), 300);
        });
    });
}

// Dropdown Menus
function initializeDropdowns() {
    document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            const menu = toggle.nextElementSibling;
            
            // Close other open dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                if (openMenu !== menu) {
                    openMenu.classList.remove('show');
                }
            });
            
            menu.classList.toggle('show');
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// Form Validation
function initializeFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    
    // Clear previous error messages
    form.querySelectorAll('.error-message').forEach(error => error.remove());
    
    // Validate required fields
    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        }
    });
    
    // Validate file inputs
    form.querySelectorAll('input[type="file"]').forEach(field => {
        if (field.hasAttribute('required') && !field.files.length) {
            showFieldError(field, 'Please select a file');
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    const error = document.createElement('div');
    error.className = 'error-message';
    error.textContent = message;
    field.parentNode.appendChild(error);
    field.classList.add('error');
}

// Auto-refresh functionality
function initializeAutoRefresh() {
    // Check for elements that need periodic updates
    const needsRefresh = document.querySelector('[data-refresh-interval]');
    if (!needsRefresh) return;

    const interval = parseInt(needsRefresh.dataset.refreshInterval) || 60000; // Default to 1 minute
    setInterval(() => refreshData(), interval);
}

async function refreshData() {
    try {
        // Update dashboard summary
        const summaryResponse = await fetch('/api/dashboard/summary');
        if (summaryResponse.ok) {
            const data = await summaryResponse.json();
            updateDashboardSummary(data);
        }

        // Update alerts
        const alertsResponse = await fetch('/api/alerts');
        if (alertsResponse.ok) {
            const data = await alertsResponse.json();
            updateAlerts(data);
        }
    } catch (error) {
        console.error('Error refreshing data:', error);
    }
}

// Error Handling
function setupGlobalErrorHandling() {
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showErrorNotification('An unexpected error occurred');
    });

    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showErrorNotification('An unexpected error occurred');
    });
}

// Utility Functions
function showErrorNotification(message) {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger';
    alert.innerHTML = `
        ${message}
        <button type="button" class="close-alert">&times;</button>
    `;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-US', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 2
    }).format(number);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(date));
}

// Export utilities for use in other scripts
window.utils = {
    formatNumber,
    formatDate,
    showErrorNotification
};
