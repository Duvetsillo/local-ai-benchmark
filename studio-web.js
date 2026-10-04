/* Real client imagery and one scroll narrative. No simulated live telemetry. */
document.addEventListener('DOMContentLoaded', () => {
  const image = document.getElementById('studio-image');
  const note = document.getElementById('studio-capture-note');
  const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  const views = {
    workspace: ['Aetherion Studio Workspace: six real local models and detected hardware', 'Implemented client · real hardware and local models'],
    models: ['Implemented Aetherion Studio model library with demonstration data', 'Implemented client · demonstration model data'],
    benchmark: ['Implemented Aetherion Studio benchmark configuration with demonstration data', 'Implemented client · demonstration configuration']
  };
  let imageAnimation;
  let imageRequest = 0;
  document.querySelectorAll('[data-studio-view]').forEach(button => {
    button.addEventListener('click', async event => {
      const key = button.dataset.studioView;
      if (!image || !note || !views[key] || button.getAttribute('aria-pressed') === 'true') return;
      const request = ++imageRequest;
      const next = new Image();
      next.src = `assets/studio/${key}.png`;
      imageAnimation?.cancel();
      try { await next.decode(); } catch {
        if (request === imageRequest) note.textContent = 'This screenshot could not load. Choose another view or try again.';
        return;
      }
      if (request !== imageRequest) return;
      document.querySelectorAll('[data-studio-view]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      image.src = next.src;
      image.alt = views[key][0];
      note.textContent = views[key][1];
      if (event.detail > 0 && !motionPreference.matches && image.animate) {
        imageAnimation = image.animate([{ opacity:.7 }, { opacity:1 }], { duration:180, easing:'cubic-bezier(.23,1,.32,1)' });
      }
    });
  });
  const strip = document.querySelector('.capability-strip');
  const pause = strip?.querySelector('.capability-pause');
  pause?.addEventListener('click', () => {
    const paused = strip.classList.toggle('paused');
    pause.setAttribute('aria-pressed', String(paused));
    pause.setAttribute('aria-label', paused ? 'Resume integrations animation' : 'Pause integrations animation');
    pause.querySelector('path')?.setAttribute('d', paused ? 'M8 5 19 12 8 19Z' : 'M9 6v12M15 6v12');
  });
  document.addEventListener('visibilitychange', () => {
    if (strip) strip.style.animationPlayState = document.hidden ? 'paused' : '';
    const track = strip?.querySelector('.capability-track');
    if (track) track.style.animationPlayState = document.hidden ? 'paused' : '';
  });
  // MatchMedia reverts every pin and inline style when motion is reduced or width changes.
  if (!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);
  const media = gsap.matchMedia();
  const setupMotion = () => {
    media.revert();
    if (document.hidden || document.body.classList.contains('keyboard-input')) return;
    media.add('(min-width: 1000px) and (prefers-reduced-motion: no-preference)', () => {
      const section = document.querySelector('.workflow-section');
      const intro = section?.querySelector('.section-intro');
      if (!section || !intro) return;
      const overflow = section.clientHeight - parseFloat(getComputedStyle(section).paddingTop) - parseFloat(getComputedStyle(section).paddingBottom) - intro.clientHeight;
      if (overflow > 80) ScrollTrigger.create({ trigger:intro, pin:true, start:'top 110px', end:() => `+=${Math.max(0, overflow)}`, pinSpacing:false, invalidateOnRefresh:true });
      section.querySelectorAll('.workflow-list p').forEach(paragraph => {
        gsap.fromTo(paragraph, { opacity:.75 }, { opacity:1, ease:'none', scrollTrigger:{ trigger:paragraph, start:'top 88%', end:'top 65%', scrub:true } });
      });
    });
  };
  document.fonts.ready.then(setupMotion);
  document.addEventListener('keydown', () => { media.revert(); imageAnimation?.cancel(); }, { capture:true });
  document.addEventListener('pointerdown', setupMotion);
  document.addEventListener('visibilitychange', setupMotion);
  motionPreference.addEventListener('change', () => { imageAnimation?.cancel(); setupMotion(); });
});
