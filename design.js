document.addEventListener('DOMContentLoaded', () => {
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const mobileNavigation = window.matchMedia('(max-width: 700px)');
  const activeAnimations = new Map();
  const easeOut = 'cubic-bezier(.23, 1, .32, 1)';
  const animate = (element, frames, duration) => {
    if (!element) return;
    activeAnimations.get(element)?.cancel();
    if (reducedMotion.matches || document.body.classList.contains('keyboard-input') || !element.animate) return;
    const animation = element.animate(frames, { duration, easing: easeOut });
    activeAnimations.set(element, animation);
    const forget = () => { if (activeAnimations.get(element) === animation) activeAnimations.delete(element); };
    animation.finished.then(forget, forget);
  };
  const stopMotion = () => {
    document.body.classList.remove('entry-motion');
    activeAnimations.forEach(animation => animation.cancel());
    activeAnimations.clear();
  };
  document.addEventListener('keydown', () => {
    document.body.classList.add('keyboard-input');
    stopMotion();
  }, { capture: true });
  document.addEventListener('pointerdown', () => document.body.classList.remove('keyboard-input'), { capture: true });
  reducedMotion.addEventListener('change', stopMotion);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopMotion(); });
  const navigationEntry = performance.getEntriesByType('navigation')[0];
  if (document.body.classList.contains('homepage') && !reducedMotion.matches && !document.hidden &&
      !window.location.hash && navigationEntry?.type !== 'back_forward' && window.scrollY < 20) {
    document.body.classList.add('entry-motion');
    document.querySelector('.machine-scene')?.addEventListener('animationend', event => {
      if (event.animationName === 'scene-arrive') document.body.classList.remove('entry-motion');
    });
  }
  const suites = {
    general: ['General / DNS explanation', 'Explain DNS in exactly two short sentences.', 'Sentence-count check', 'The validator checks for two sentence segments. It does not judge factual accuracy.'],
    coding: ['Coding / Duplicate files', 'Write only a Python function named find_duplicate_files that accepts a list of paths and returns duplicate SHA256 groups.', 'Python syntax check', 'The output must compile as Python and contain find_duplicate_files. The function is not executed; correctness is not fully tested.'],
    math: ['Math / Arithmetic', 'What is 37 * 24? Answer with the number only.', 'Expected-answer check', 'The validator looks for 888 as a standalone number. Extra text is not rejected by this check.'],
    json: ['Structured output / Profile', 'Return only valid JSON matching this schema: {"name": string, "age": integer, "skills": array}. Use name "Ada", age 36, and skills ["python"].', 'JSON parsing and values', 'The response must parse as JSON with name Ada, age 36 and skills ["python"].'],
    spanish: ['Spanish / Memory summary', 'En español y en una sola frase, resume que la memoria RAM guarda datos temporalmente para que la CPU acceda a ellos rápidamente.', 'Keyword check', 'The validator checks for memoria, datos or cpu. It does not fully evaluate language fluency or sentence count.']
  };
  document.querySelectorAll('[data-suite]').forEach(button => {
    button.addEventListener('click', event => {
      const suite = suites[button.dataset.suite];
      if (!suite || button.getAttribute('aria-pressed') === 'true') return;
      const preview = document.querySelector('.suite-preview');
      activeAnimations.get(preview)?.cancel();
      document.querySelectorAll('[data-suite]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      ['suite-name', 'suite-prompt', 'suite-check-title', 'suite-check'].forEach((id, index) => {
        const element = document.getElementById(id);
        if (element) element.textContent = suite[index];
      });
      if (event.detail > 0) animate(preview, [
        { opacity: .55, transform: 'translateY(4px)' },
        { opacity: 1, transform: 'translateY(0)' }
      ], 180);
    });
  });
  document.querySelectorAll('.faq-list details').forEach(details => {
    details.addEventListener('click', event => {
      if (!event.target.closest('summary')) return;
      const opening = !details.open;
      if (!opening || event.detail === 0) {
        activeAnimations.get(details.querySelector('p'))?.cancel();
        return;
      }
      // Native details keeps semantics and keyboard behavior; only its answer fades.
      requestAnimationFrame(() => {
        if (details.open) animate(details.querySelector('p'), [
          { opacity: 0, transform: 'translateY(-3px)' },
          { opacity: 1, transform: 'translateY(0)' }
        ], 170);
      });
    });
  });
  const header = document.querySelector('.topbar');
  if (!header) return;
  // Shared secondary pages get the same accessible mobile navigation.
  let menu = header.querySelector('.design-menu');
  const nav = header.querySelector('.nav');
  if (!nav) return;
  if (!menu) {
    nav.id = 'aetherion-navigation';
    menu = document.createElement('button');
    menu.type = 'button';
    menu.className = 'design-menu';
    menu.setAttribute('aria-label', 'Open navigation');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-controls', nav.id);
    menu.innerHTML = '<span></span><span></span>';
    header.append(menu);
  }
  document.body.classList.add('design-ready');
  const setMenu = (open, pointerInitiated = false) => {
    activeAnimations.get(nav)?.cancel();
    header.classList.toggle('navigation-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
    if (open && pointerInitiated && mobileNavigation.matches) animate(nav, [
      { opacity: 0, transform: 'translateY(-4px) scale(.985)' },
      { opacity: 1, transform: 'translateY(0) scale(1)' }
    ], 180);
  };
  menu.addEventListener('click', event => setMenu(menu.getAttribute('aria-expanded') !== 'true', event.detail > 0));
  header.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('click', event => { if (!header.contains(event.target)) setMenu(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && header.classList.contains('navigation-open')) { setMenu(false); menu.focus(); }
  });
  mobileNavigation.addEventListener('change', () => setMenu(false));
  const currentFile = window.location.pathname.split('/').pop() || 'index.html';
  nav.querySelectorAll('a').forEach(link => {
    if (link.getAttribute('href') === currentFile) link.setAttribute('aria-current', 'page');
  });
});
