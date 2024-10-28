console.log('Modal script loaded');

function showNewProjectModal() {
    console.log('showNewProjectModal called');
    const modal = document.getElementById('newProjectModal');
    console.log('Modal element:', modal);
    if (modal) {
        modal.style.display = 'flex';
    }
}

function hideNewProjectModal() {
    console.log('hideNewProjectModal called');
    const modal = document.getElementById('newProjectModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    console.log('Click event:', e.target);
    if (e.target.classList.contains('modal')) {
        hideNewProjectModal();
    }
});
