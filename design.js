document.addEventListener('DOMContentLoaded', () => {
  const suites = {
    general: ['General / DNS explanation', 'Explain DNS in exactly two short sentences.', 'Sentence-count check', 'The validator checks for two sentence segments. It does not judge factual accuracy.'],
    coding: ['Coding / Duplicate files', 'Write only a Python function named find_duplicate_files that accepts a list of paths and returns duplicate SHA256 groups.', 'Python syntax check', 'The output must compile as Python and contain find_duplicate_files. The function is not executed; correctness is not fully tested.'],
    math: ['Math / Arithmetic', 'What is 37 * 24? Answer with the number only.', 'Expected-answer check', 'The validator looks for 888 as a standalone number. Extra text is not rejected by this check.'],
    json: ['Structured output / Profile', 'Return only valid JSON matching this schema: {"name": string, "age": integer, "skills": array}. Use name "Ada", age 36, and skills ["python"].', 'JSON parsing and values', 'The response must parse as JSON with name Ada, age 36 and skills ["python"].'],
    spanish: ['Spanish / Memory summary', 'En español y en una sola frase, resume que la memoria RAM guarda datos temporalmente para que la CPU acceda a ellos rápidamente.', 'Keyword check', 'The validator checks for memoria, datos or cpu. It does not fully evaluate language fluency or sentence count.']
  };
  document.querySelectorAll('[data-suite]').forEach(button => {
    button.addEventListener('click', () => {
      const suite = suites[button.dataset.suite];
      if (!suite) return;
      document.querySelectorAll('[data-suite]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      ['suite-name', 'suite-prompt', 'suite-check-title', 'suite-check'].forEach((id, index) => {
        const element = document.getElementById(id);
        if (element) element.textContent = suite[index];
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
  const setMenu = open => {
    header.classList.toggle('navigation-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  };
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  header.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('click', event => { if (!header.contains(event.target)) setMenu(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && header.classList.contains('navigation-open')) { setMenu(false); menu.focus(); }
  });
  const currentFile = window.location.pathname.split('/').pop() || 'index.html';
  nav.querySelectorAll('a').forEach(link => {
    if (link.getAttribute('href') === currentFile) link.setAttribute('aria-current', 'page');
  });
});
