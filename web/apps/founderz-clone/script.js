document.addEventListener('DOMContentLoaded', () => {
    // Interactive Level Selection Logic
    const levelCards = document.querySelectorAll('.level-card');
    const hiddenInput = document.getElementById('selectedLevel');

    levelCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove active class from all
            levelCards.forEach(c => c.classList.remove('active'));
            // Add active class to clicked
            card.classList.add('active');
            // Update hidden input
            hiddenInput.value = card.getAttribute('data-level');
        });
    });

    // Form Submission Handler
    const form = document.getElementById('signupForm');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.textContent;
        
        // Simple loading simulation
        btn.textContent = 'Processing...';
        btn.disabled = true;
        
        setTimeout(() => {
            btn.textContent = 'Registration Complete!';
            btn.style.backgroundColor = '#10B981'; // Success Green
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.backgroundColor = '';
                btn.disabled = false;
                form.reset();
                // Reset level selection to default
                levelCards.forEach(c => c.classList.remove('active'));
                levelCards[0].classList.add('active');
                hiddenInput.value = 'explorer';
            }, 3000);
        }, 1500);
    });

    // Intersection Observer for scroll animations (fade in up)
    const fadeElements = document.querySelectorAll('.fade-in-up');
    
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    fadeElements.forEach(el => observer.observe(el));
});
