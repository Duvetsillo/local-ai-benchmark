document.addEventListener('DOMContentLoaded', () => {
  const benchmarkKey = 'aetherion-benchmark-cache';
  localStorage.removeItem(benchmarkKey);

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

  document.querySelectorAll('.download-cta').forEach((link) => {
    link.addEventListener('click', () => {
      link.classList.remove('is-animating');
      void link.offsetWidth;
      link.classList.add('is-animating');
      window.setTimeout(() => link.classList.remove('is-animating'), 760);
    });
  });

  const resetBenchmarkBtn = document.getElementById('resetBenchmarkBtn');
  resetBenchmarkBtn?.addEventListener('click', () => {
    localStorage.removeItem(benchmarkKey);
    const state = document.getElementById('benchmarkState');
    state?.classList.add('benchmark-empty-state');
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
    const modelInterest = document.getElementById('modelInterest');
    const useCase = document.getElementById('useCase');
    const message = document.getElementById('message');
    const consent = document.getElementById('consent');
    const recipient = 'dayvermoreta21@gmail.com';

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

    const subject = encodeURIComponent(`AETHERION inquiry - ${name.value.trim()}`);
    const body = encodeURIComponent(
      [
        `Name: ${name.value.trim()}`,
        `Email: ${email.value.trim()}`,
        `Model of interest: ${modelInterest.value.trim() || 'Not specified'}`,
        `Use case: ${useCase.value || 'Not specified'}`,
        '',
        'Project details:',
        message.value.trim() || 'No additional details provided.'
      ].join('\n')
    );

    window.location.href = `mailto:${recipient}?subject=${subject}&body=${body}`;
    formStatus.textContent = 'Your request is being prepared in your email client.';
    contactForm.reset();
  });
});
