document.addEventListener('DOMContentLoaded', function() {
    initializeStatCounters();
    initializeModals();
    initializeDemoForm();
});

// Animated stat counters
function initializeStatCounters() {
    const stats = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const stat = entry.target;
                const value = parseFloat(stat.dataset.value);
                const format = stat.dataset.format;
                
                animateValue(stat, 0, value, 2000, format);
                observer.unobserve(stat);
            }
        });
    }, observerOptions);
    
    stats.forEach(stat => observer.observe(stat));
}

function animateValue(element, start, end, duration, format) {
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        element.textContent = formatValue(current, format);
    }, 16);
}

function formatValue(value, format) {
    switch (format) {
        case 'percentage':
            return `${Math.round(value)}%`;
        case 'plus':
            return `${Math.round(value)}+`;
        default:
            return Math.round(value);
    }
}

// Modal handling
function initializeModals() {
    const demoModal = document.getElementById('demoModal');
    const scheduleModal = document.getElementById('scheduleModal');
    const watchDemoBtn = document.getElementById('watchDemoBtn');
    const scheduleDemoBtn = document.getElementById('scheduleDemoBtn');
    
    // Watch Demo button
    if (watchDemoBtn && demoModal) {
        watchDemoBtn.addEventListener('click', () => {
            demoModal.style.display = 'block';
            // Load video only when modal is opened
            const iframe = demoModal.querySelector('iframe');
            if (iframe.getAttribute('src') === 'about:blank') {
                iframe.setAttribute('src', iframe.dataset.src);
            }
        });
    }
    
    // Schedule Demo button
    if (scheduleDemoBtn && scheduleModal) {
        scheduleDemoBtn.addEventListener('click', () => {
            scheduleModal.style.display = 'block';
        });
    }
    
    // Close buttons
    document.querySelectorAll('.modal .close').forEach(closeBtn => {
        closeBtn.addEventListener('click', () => {
            closeBtn.closest('.modal').style.display = 'none';
            // Stop video when closing demo modal
            if (closeBtn.closest('#demoModal')) {
                const iframe = demoModal.querySelector('iframe');
                iframe.setAttribute('src', iframe.getAttribute('src'));
            }
        });
    });
    
    // Click outside modal to close
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
            // Stop video if demo modal
            if (e.target.id === 'demoModal') {
                const iframe = demoModal.querySelector('iframe');
                iframe.setAttribute('src', iframe.getAttribute('src'));
            }
        }
    });
}

// Demo form handling
function initializeDemoForm() {
    const demoForm = document.getElementById('demoForm');
    if (!demoForm) return;
    
    demoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = demoForm.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        
        const formData = new FormData(demoForm);
        const data = Object.fromEntries(formData.entries());
        
        try {
            const response = await fetch('/api/schedule-demo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                showSuccess('Thank you! We will contact you shortly.');
                demoForm.reset();
                setTimeout(() => {
                    document.getElementById('scheduleModal').style.display = 'none';
                }, 2000);
            } else {
                throw new Error('Failed to submit form');
            }
        } catch (error) {
            showError('Failed to submit form. Please try again.');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Submit Request';
        }
    });
}

// Utility functions
function showSuccess(message) {
    const container = document.querySelector('.flash-messages') || createFlashContainer();
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-success';
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

function showError(message) {
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
