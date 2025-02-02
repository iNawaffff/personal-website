document.addEventListener('DOMContentLoaded', function() {
    initBinaryStream();
});

function initBinaryStream() {
    const streamElement = document.getElementById('binary-stream');
    if (!streamElement) return;

    // Create two streams for seamless scrolling
    const createStream = () => {
        const stream = document.createElement('div');
        stream.className = 'binary-content';

        // Create enough digits to fill the container
        const streamLength = 50;
        for (let i = 0; i < streamLength; i++) {
            const digit = Math.random() < 0.5 ? '0' : '1';
            const span = document.createElement('span');
            span.className = 'binary-digit';
            span.textContent = digit;
            stream.appendChild(span);
        }

        return stream;
    };
    // Add two identical streams
    streamElement.appendChild(createStream());
    streamElement.appendChild(createStream());

    // Animation function
    function animate() {
        const streams = streamElement.querySelectorAll('.binary-content');
        streams.forEach(stream => {
            // Move each stream
            let currentPosition = parseFloat(stream.style.transform.replace('translateX(', '')) || 0;
            if (currentPosition <= -100) {
                currentPosition = 100; // Reset position
            }
            stream.style.transform = `translateX(${currentPosition - 0.5}%)`; // Adjust speed here
        });

        requestAnimationFrame(animate);
    }

    // Start animation
    animate();

    // Keep the hover effect
    streamElement.addEventListener('mousemove', (e) => {
        const digits = streamElement.getElementsByClassName('binary-digit');
        const rect = streamElement.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;

        Array.from(digits).forEach((digit) => {
            const digitRect = digit.getBoundingClientRect();
            const digitCenter = digitRect.left + digitRect.width / 2 - rect.left;
            const distance = Math.abs(mouseX - digitCenter);

            if (distance < 50) {
                digit.classList.add('gap');
            } else {
                digit.classList.remove('gap');
            }
        });
    });

    streamElement.addEventListener('mouseleave', () => {
        const digits = streamElement.getElementsByClassName('binary-digit');
        Array.from(digits).forEach(digit => digit.classList.remove('gap'));
    });
}