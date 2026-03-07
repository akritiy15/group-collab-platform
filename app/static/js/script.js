// Main Script for FunCollab

console.log('✨ FunCollab script loaded! ✨');

document.addEventListener('DOMContentLoaded', () => {
    // Hover animation (SAFE)
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            const rot = Math.random() * 4 - 2;
            card.style.transform = `translate(-2px, -2px) rotate(${rot}deg)`;
            card.style.boxShadow = '10px 10px 0px #000';
        });
        card.addEventListener('mouseleave', () => {
            card.style.boxShadow = '6px 6px 0px #000';
        });
    });
});