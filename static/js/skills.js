document.addEventListener('DOMContentLoaded', function() {
    const skillCards = document.querySelectorAll('.skill-card');

    skillCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove active class from all cards
            skillCards.forEach(c => c.classList.remove('active'));
            // Add active class to clicked card
            card.classList.add('active');
        });

        // Add hover animation for tags
        const tags = card.querySelectorAll('.skill-tag');
        tags.forEach(tag => {
            tag.addEventListener('mouseover', () => {
                tag.style.transform = 'scale(1.05)';
            });
            tag.addEventListener('mouseout', () => {
                tag.style.transform = 'scale(1)';
            });
        });
    });
});