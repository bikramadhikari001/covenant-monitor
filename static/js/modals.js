document.addEventListener('DOMContentLoaded', function() {
    // Show modal
    function showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            
            // Add animation class
            modal.querySelector('.modal-content').style.animation = 'modalSlideIn 0.3s ease forwards';
        }
    }

    // Hide modal
    function hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    // Close modal when clicking outside
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            hideModal(event.target.id);
        }
    });

    // Close modal when clicking close button
    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            hideModal(modal.id);
        });
    });

    // Show modal when clicking trigger buttons
    document.querySelectorAll('[data-modal]').forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.dataset.modal;
            showModal(modalId);
        });
    });

    // Close modal on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const visibleModal = document.querySelector('.modal[style*="flex"]');
            if (visibleModal) {
                hideModal(visibleModal.id);
            }
        }
    });
});
