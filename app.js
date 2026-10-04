"use strict";
const initializePage = () => {
    const benchmarkKey = 'aetherion-benchmark-cache';
    try {
        localStorage.removeItem(benchmarkKey);
    }
    catch { /* Storage is optional. */ }
    document.querySelectorAll('.spotlight-card').forEach((card) => {
        card.addEventListener('pointermove', (event) => {
            const rect = card.getBoundingClientRect();
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;
            card.style.setProperty('--x', `${x}%`);
            card.style.setProperty('--y', `${y}%`);
        });
    });
    const cards = document.querySelectorAll('.model-card');
    cards.forEach((card) => {
        card.addEventListener('click', () => {
            cards.forEach((item) => item.classList.remove('selected'));
            card.classList.add('selected');
        });
        card.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                cards.forEach((item) => item.classList.remove('selected'));
                card.classList.add('selected');
            }
        });
    });
    const resetBenchmarkBtn = document.getElementById('resetBenchmarkBtn');
    resetBenchmarkBtn?.addEventListener('click', () => {
        try {
            localStorage.removeItem(benchmarkKey);
        }
        catch { /* Storage is optional. */ }
        const state = document.getElementById('benchmarkState');
        state?.classList.add('benchmark-empty-state');
    });
    const cookieBanner = document.getElementById('cookieBanner');
    const acceptCookiesButton = document.getElementById('acceptCookies');
    const rejectCookiesButton = document.getElementById('rejectCookies');
    const cookieKey = 'local-ai-benchmark-cookie-consent';
    const setConsent = (choice) => {
        if (!cookieBanner)
            return;
        try {
            localStorage.setItem(cookieKey, choice);
        }
        catch { /* Still allow dismissal in private sessions. */ }
        cookieBanner.classList.remove('visible');
    };
    if (cookieBanner) {
        let storedChoice = null;
        try {
            storedChoice = localStorage.getItem(cookieKey);
        }
        catch { /* Storage may be blocked. */ }
        if (!storedChoice) {
            cookieBanner.classList.add('visible');
        }
        acceptCookiesButton?.addEventListener('click', () => setConsent('accepted'));
        rejectCookiesButton?.addEventListener('click', () => setConsent('rejected'));
    }
    const contactForm = document.getElementById('contactForm');
    const formStatus = document.getElementById('formStatus');
    contactForm?.addEventListener('submit', (event) => {
        event.preventDefault();
        const fullName = document.getElementById('fullName');
        const email = document.getElementById('email');
        const modelInterest = document.getElementById('modelInterest');
        const useCase = document.getElementById('useCase');
        const message = document.getElementById('message');
        const consent = document.getElementById('consent');
        const recipient = 'dayvermoreta21@gmail.com';
        if (!fullName || !email || !formStatus) {
            return;
        }
        if (!fullName.value.trim() || !email.value.trim()) {
            formStatus.textContent = 'Please complete your name and email before sending your request.';
            (!fullName.value.trim() ? fullName : email).focus();
            return;
        }
        if (!email.validity.valid) {
            formStatus.textContent = 'Please enter a valid email address.';
            email.focus();
            return;
        }
        if (!consent || !consent.checked) {
            formStatus.textContent = 'Please accept the consent notice before submitting the form.';
            return;
        }
        const subject = encodeURIComponent(`AETHERION inquiry - ${fullName.value.trim()}`);
        const body = encodeURIComponent([
            `Name: ${fullName.value.trim()}`,
            `Email: ${email.value.trim()}`,
            `Model of interest: ${modelInterest?.value.trim() || 'Not specified'}`,
            `Use case: ${useCase?.value || 'Not specified'}`,
            '',
            'Project details:',
            message?.value.trim() || 'No additional details provided.'
        ].join('\n'));
        window.location.href = `mailto:${recipient}?subject=${subject}&body=${body}`;
        formStatus.textContent = 'Your request is being prepared in your email client.';
        // Keep the draft in the form if no mail application is configured.
    });
};
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
}
else {
    initializePage();
}
