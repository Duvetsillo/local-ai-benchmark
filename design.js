document.addEventListener('DOMContentLoaded', () => {
  const lenses = {
    hardware: ['Start with your machine.', 'Profile the hardware before choosing a model. CPU, memory and available acceleration set the context.'],
    models: ['Choose the workload.', 'Compare local Ollama and GGUF models against the tasks you need them to perform.'],
    evidence: ['Read speed and quality together.', 'Review latency, throughput and validation. Keep reproducible results from your own hardware.']
  };
  document.querySelectorAll('[data-engine-lens]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-engine-lens]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    const [title, copy] = lenses[button.dataset.engineLens];
    document.getElementById('engine-lens-title').textContent = title;
    document.getElementById('engine-lens-copy').textContent = copy;
    document.querySelector('.engine-visual').dataset.lens = button.dataset.engineLens;
  }));
  const menu = document.querySelector('.design-menu');
  const header = document.querySelector('.topbar');
  if (!menu || !header) return;
  document.body.classList.add('design-ready');
  function setMenu(open) {
    header.classList.toggle('navigation-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  }
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  header.querySelectorAll('a').forEach(link => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('click', event => { if (!header.contains(event.target)) setMenu(false); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && header.classList.contains('navigation-open')) { setMenu(false); menu.focus(); }
  });
});
