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
}

function submitForm(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    fetch('/send-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(Object.fromEntries(formData)),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Message sent successfully!');
            form.reset();
            toggleForm();
        } else {
            alert('Error sending message. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error sending message. Please try again.');
    });
}