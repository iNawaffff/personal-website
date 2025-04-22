function copyEmail() {
    navigator.clipboard.writeText('nawafkm01@gmail.com');
    const btn = document.querySelector('.copy-btn');
    const originalText = btn.querySelector('.btn-text').textContent;
    btn.querySelector('.btn-text').textContent = 'Email copied!';
    setTimeout(() => {
        btn.querySelector('.btn-text').textContent = originalText;
    }, 2000);
}

function toggleForm() {
    const form = document.getElementById('contact-form');
    form.classList.toggle('hidden');

    // clear all the error messages when toggling
    clearAllErrors();
}

function clearAllErrors() {

    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(el => el.remove());


    const inputs = document.querySelectorAll('.input-error');
    inputs.forEach(input => input.classList.remove('input-error'));
}

function validateEmail(email) {

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showError(field, message) {

    let errorElement = field.parentElement.querySelector('.error-message');

    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        field.parentElement.appendChild(errorElement);
    }


    field.classList.add('input-error');


    errorElement.textContent = message;
}

function clearError(field) {

    const errorElement = field.parentElement.querySelector('.error-message');
    if (errorElement) {
        errorElement.remove();
    }


    field.classList.remove('input-error');
}

function validateForm(form) {
    let isValid = true;


    const nameInput = form.querySelector('input[name="name"]');
    const emailInput = form.querySelector('input[name="email"]');
    const messageInput = form.querySelector('textarea[name="message"]');


    clearAllErrors();


    if (nameInput.value.trim() === '') {
        showError(nameInput, 'Please enter your name');
        isValid = false;
    }


    if (emailInput.value.trim() === '') {
        showError(emailInput, 'Please enter your email address');
        isValid = false;
    } else if (!validateEmail(emailInput.value)) {
        showError(emailInput, 'Please enter a valid email address');
        isValid = false;
    }


    if (messageInput.value.trim() === '') {
        showError(messageInput, 'Please enter your message');
        isValid = false;
    } else if (messageInput.value.trim().length < 10) {
        showError(messageInput, 'Message must be at least 10 characters long');
        isValid = false;
    }

    return isValid;
}

function submitForm(event) {
    event.preventDefault();
    const form = event.target;


    if (!validateForm(form)) {
        return; // stop the submission if validation fails
    }

    const formData = new FormData(form);


    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i data-lucide="loader" class="w-4 h-4 animate-spin"></i> Sending...';
    submitBtn.disabled = true;

    fetch('/send-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(Object.fromEntries(formData)),
    })
    .then(response => response.json())
    .then(data => {

        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;

        if (data.success) {

            const successMessage = document.createElement('div');
            successMessage.className = 'success-message';
            successMessage.textContent = 'Message sent successfully!';
            form.appendChild(successMessage);


            form.reset();


            setTimeout(() => {
                successMessage.remove();
                toggleForm();
            }, 3000);
        } else {
            throw new Error(data.error || 'Failed to send message');
        }
    })
    .catch(error => {

        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;

        console.error('Error:', error);


        const serverError = document.createElement('div');
        serverError.className = 'error-message server-error';
        serverError.textContent = 'Error sending message. Please try again.';
        form.appendChild(serverError);


        setTimeout(() => {
            serverError.remove();
        }, 5000);
    });
}