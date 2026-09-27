document.addEventListener('DOMContentLoaded', () => {
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

  const cookieBanner = document.getElementById('cookieBanner');
  const acceptCookiesButton = document.getElementById('acceptCookies');
  const rejectCookiesButton = document.getElementById('rejectCookies');

  const cookieKey = 'local-ai-benchmark-cookie-consent';

  const setConsent = (choice) => {
    if (!cookieBanner) return;
    localStorage.setItem(cookieKey, choice);
    cookieBanner.classList.remove('visible');
  };

  if (cookieBanner) {
    const storedChoice = localStorage.getItem(cookieKey);
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

    const name = document.getElementById('fullName');
    const email = document.getElementById('email');
    const consent = document.getElementById('consent');

    if (!name.value.trim() || !email.value.trim()) {
      formStatus.textContent = 'Please complete your name and email before sending your request.';
      return;
    }

    if (!email.value.includes('@')) {
      formStatus.textContent = 'Please enter a valid email address.';
      return;
    }

    if (!consent.checked) {
      formStatus.textContent = 'Please accept the consent notice before submitting the form.';
      return;
    }

    formStatus.textContent = 'Your request is ready to be sent. Connect this form to your preferred email or backend in production.';
    contactForm.reset();
  });
});
