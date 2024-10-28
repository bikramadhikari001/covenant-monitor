// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeDateRange();
    initializeCharts();
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
