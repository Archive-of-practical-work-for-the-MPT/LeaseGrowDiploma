document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('leasingConfirmModal');
    const textNode = document.getElementById('leasingConfirmText');
    const submitButton = document.getElementById('leasingConfirmSubmit');
    if (!modal || !textNode || !submitButton) {
        return;
    }

    const forms = document.querySelectorAll('form[data-confirm-message]');
    if (!forms.length) {
        return;
    }

    let pendingForm = null;

    const closeModal = () => {
        modal.hidden = true;
        document.body.classList.remove('modal-open');
        pendingForm = null;
    };

    const openModal = (form) => {
        pendingForm = form;
        textNode.textContent = form.dataset.confirmMessage || 'Вы уверены, что хотите продолжить?';
        modal.hidden = false;
        document.body.classList.add('modal-open');
    };

    forms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (form.dataset.confirmed === 'true') {
                form.dataset.confirmed = 'false';
                return;
            }
            event.preventDefault();
            openModal(form);
        });
    });

    submitButton.addEventListener('click', () => {
        if (!pendingForm) {
            return;
        }
        pendingForm.dataset.confirmed = 'true';
        pendingForm.requestSubmit();
        closeModal();
    });

    modal.querySelectorAll('[data-confirm-close]').forEach((element) => {
        element.addEventListener('click', closeModal);
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && !modal.hidden) {
            closeModal();
        }
    });
});
