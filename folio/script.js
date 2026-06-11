// ========================================== //
// 6.1 DARK MODE TOGGLE                       //
// ========================================== //

// FIND the button by its id
const themeToggle = document.querySelector('#theme-toggle');

// LISTEN for a click
themeToggle.addEventListener('click', () => {
    // CHANGE: flip the 'dark' class on <body>
    document.body.classList.toggle('dark');
    
    // Swap the icon to match the mode
    const isDark = document.body.classList.contains('dark');
    themeToggle.textContent = isDark ? '☀️' : '🌙'; // Real emoji icons used here
});


// ========================================== //
// 6.2 BACK-TO-TOP BUTTON                     //
// ========================================== //

const toTop = document.querySelector('#to-top');

// LISTEN for scrolling; show the button past 300px down
window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        toTop.classList.add('show');
    } else {
        toTop.classList.remove('show');
    }
});

// Click -> glide back to the top
toTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});


// ========================================== //
// 6.3 SCROLL REVEAL — ELEMENTS FADE IN       //
// ========================================== //

// FIND every element marked with class "reveal"
const revealItems = document.querySelectorAll('.reveal');

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {                  // When it enters the screen
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target);        // Animate once, then stop
        }
    });
}, { threshold: 0.15 });

revealItems.forEach((item) => observer.observe(item));
// ========================================== //
// SUPPLEMENTARY TASK: PROJECT FILTER SYSTEM   //
// ========================================== //
const filterButtons = document.querySelectorAll('.filter-btn');
const projectCards = document.querySelectorAll('.projects-grid .card');
const counterNum = document.querySelector('#count-num');

if (filterButtons.length > 0 && projectCards.length > 0 && counterNum) {
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Highlight the active pill button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const filterValue = button.getAttribute('data-filter');
            let visibleCount = 0;
            
            projectCards.forEach(card => {
                const cardCategory = card.getAttribute('data-category');
                
                // Show matching cards, hide the rest
                if (filterValue === 'all' || filterValue === cardCategory) {
                    card.classList.remove('hide-card');
                    visibleCount++;
                } else {
                    card.classList.add('hide-card');
                }
            });
            
            // Dynamically update the live display counter text
            counterNum.textContent = visibleCount;
        });
    });
}