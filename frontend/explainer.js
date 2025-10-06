document.addEventListener('DOMContentLoaded', () => {
    // A list of all the element IDs in the order they should appear
    const animationSequence = [
        'node-dev',
        'arrow1',
        'node-portal',
        'arrow2',
        'node-affiliate',
        'arrow3',
        'node-victim',
        'arrow4',
        'node-payout'
    ];

    // Function to reveal elements one by one
    function revealElements() {
        let delay = 500; // Start after 0.5 seconds
        
        animationSequence.forEach(id => {
            setTimeout(() => {
                const element = document.getElementById(id);
                if (element) {
                    element.classList.add('visible');
                }
            }, delay);
            
            // Increase the delay for the next element
            delay += 800; // Each element appears 0.8 seconds after the previous one
        });
    }

    // Start the animation when the page loads
    revealElements();
});