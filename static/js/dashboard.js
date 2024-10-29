// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeDateRange();
    initializeCharts();
    initializeModals();
    initializeProjectForm();
});

function initializeDateRange() {
    const dateButtons = document.querySelectorAll('.date-range .btn-outline');
    dateButtons.forEach(button => {
        button.addEventListener('click', () => {
            dateButtons.forEach(b => b.classList.remove('active'));
            button.classList.add('active');
        });
    });
}

function initializeCharts() {
    // Add any chart initialization here
}

function initializeModals() {
    // Get modal elements
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const closeButtons = document.querySelectorAll('.close-modal');
    
    // Add click event to modal triggers
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            const modalId = trigger.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'flex';
            }
        });
    });
    
    // Close modal when clicking close button
    closeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

function initializeProjectForm() {
    const form = document.getElementById('newProjectForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    redirect: 'follow'
                });
                
                if (response.redirected) {
                    window.location.href = response.url;
                } else if (response.ok) {
                    const data = await response.json();
                    window.location.href = `/project/${data.project_id}`;
                } else {
                    const data = await response.json();
                    alert(data.error || 'Failed to create project');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to create project');
            }
        });
    }
}
