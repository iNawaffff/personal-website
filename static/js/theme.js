// Theme toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-toggle');
    const body = document.body;

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        body.classList.toggle('light-theme', savedTheme === 'light');
        themeToggle.textContent = savedTheme === 'light' ? '🌙' : '☀️';
    }

    // Toggle theme
    themeToggle.addEventListener('click', (e) => {
        e.preventDefault();
        body.classList.toggle('light-theme');

        // Update moon/sun emoji
        const isLight = body.classList.contains('light-theme');
        themeToggle.textContent = isLight ? '🌙' : '☀️';

        // Save preference
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
    });
});