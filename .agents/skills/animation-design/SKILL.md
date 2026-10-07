---
name: animation-design
description: Create smooth, performant animations with Framer Motion, CSS animations, and GSAP. Includes timing functions, choreography, performance optimization, and accessibility considerations.
tags: [animation, framer-motion, css, gsap, transitions, performance, accessibility]
version: 1.0.0
author: Enhanced from animation best practices)
---

# Animation Design

## Overview

Create smooth, purposeful animations that enhance user experience.

**Why animations matter:**
- **Feedback:** Confirm user actions
- **Guidance:** Direct attention
- **Continuity:** Smooth transitions
- **Delight:** Enhance experience
- **Hierarchy:** Show relationships

**Key principles:**
- **Purpose:** Every animation has a reason
- **Performance:** 60fps minimum
- **Accessibility:** Respect prefers-reduced-motion
- **Timing:** Natural, not robotic
- **Subtlety:** Enhance, don't distract

## When to Use

**Use for:**
- Button interactions
- Page transitions
- Loading states
- Micro-interactions
- Data visualization

**Critical for:**
- Modern web apps
- Mobile experiences
- Interactive dashboards
- E-commerce sites
- Portfolio sites

## The 5-Layer Animation Framework

```
┌─────────────────────────────────────────────────────────┐
│           ANIMATION FRAMEWORK                            │
└─────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │   LAYER 1    │  Purpose
    │   PURPOSE    │  - Why animate?
    │              │  - User benefit
    └──────┬───────┘  - Context
           │
           ▼
    ┌──────────────┐
    │   LAYER 2    │  Timing
    │   TIMING     │  - Duration
    │              │  - Easing
    └──────┬───────┘  - Delay
           │
           ▼
    ┌──────────────┐
    │   LAYER 3    │  Implementation
    │ IMPLEMENT    │  - CSS
    │              │  - Framer Motion
    └──────┬───────┘  - GSAP
           │
           ▼
    ┌──────────────┐
    │   LAYER 4    │  Performance
    │ PERFORMANCE  │  - 60fps
    │              │  - GPU acceleration
    └──────┬───────┘  - Will-change
           │
           ▼
    ┌──────────────┐
    │   LAYER 5    │  Accessibility
    │ ACCESSIBILITY│  - Reduced motion
    │              │  - Focus indicators
    └──────────────┘  - Screen readers
```

## Layer 1: Purpose & Principles

### Goal: Understand why you're animating

**Animation Purposes:**

```markdown
## 1. Feedback (Confirm actions)
- Button press
- Form submission
- Toggle switch
- Checkbox check

## 2. Guidance (Direct attention)
- Highlight new content
- Show next step
- Indicate errors
- Point to actions

## 3. Continuity (Smooth transitions)
- Page transitions
- Modal open/close
- Accordion expand
- Tab switching

## 4. Hierarchy (Show relationships)
- Parent-child connections
- Before/after states
- Cause and effect
- Spatial relationships

## 5. Delight (Enhance experience)
- Hover effects
- Loading animations
- Success celebrations
- Easter eggs
```

**12 Principles of Animation (Disney):**

```markdown
1. **Squash and Stretch** - Weight and flexibility
2. **Anticipation** - Prepare for action
3. **Staging** - Direct attention
4. **Straight Ahead vs Pose-to-Pose** - Animation technique
5. **Follow Through** - Overlapping action
6. **Slow In/Slow Out** - Easing
7. **Arc** - Natural motion paths
8. **Secondary Action** - Supporting details
9. **Timing** - Speed and rhythm
10. **Exaggeration** - Emphasis
11. **Solid Drawing** - Form and weight
12. **Appeal** - Engaging design
```

**Web Animation Principles:**

```markdown
1. **Performance First** - 60fps minimum
2. **Purposeful** - Every animation has a reason
3. **Subtle** - Enhance, don't distract
4. **Consistent** - Same timing/easing throughout
5. **Accessible** - Respect user preferences
6. **Responsive** - Adapt to screen size
7. **Interruptible** - User can cancel
```

---

## Layer 2: Timing & Easing

### Goal: Natural, smooth motion

**Duration Guidelines:**

```css
/* Micro-interactions (100-300ms) */
.button-hover { transition: 150ms; }
.checkbox-check { transition: 200ms; }
.tooltip-show { transition: 150ms; }

/* UI transitions (300-500ms) */
.modal-open { transition: 400ms; }
.dropdown-expand { transition: 350ms; }
.tab-switch { transition: 300ms; }

/* Page transitions (500-800ms) */
.page-enter { transition: 600ms; }
.slide-in { transition: 700ms; }

/* Complex animations (800ms+) */
.loading-sequence { transition: 1200ms; }
.celebration { transition: 1500ms; }
```

**Easing Functions:**

```css
/* Linear (robotic, avoid for most) */
transition-timing-function: linear;

/* Ease (default, good for most) */
transition-timing-function: ease;

/* Ease-in (slow start, fast end) */
transition-timing-function: ease-in;
/* Use for: Elements leaving screen */

/* Ease-out (fast start, slow end) */
transition-timing-function: ease-out;
/* Use for: Elements entering screen */

/* Ease-in-out (slow start and end) */
transition-timing-function: ease-in-out;
/* Use for: Elements moving on screen */

/* Cubic-bezier (custom) */
transition-timing-function: cubic-bezier(0.4, 0.0, 0.2, 1);

/* Material Design easing */
--ease-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
--ease-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);
--ease-accelerate: cubic-bezier(0.4, 0.0, 1, 1);

/* iOS easing */
--ease-ios: cubic-bezier(0.42, 0, 0.58, 1);

/* Bounce */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

**Timing Tokens:**

```css
:root {
  /* Duration */
  --duration-instant: 100ms;
  --duration-fast: 200ms;
  --duration-normal: 300ms;
  --duration-slow: 500ms;
  --duration-slower: 800ms;
  
  /* Easing */
  --ease-in: cubic-bezier(0.4, 0.0, 1, 1);
  --ease-out: cubic-bezier(0.0, 0.0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## Layer 3: Implementation

### Goal: Choose the right tool

**CSS Transitions (Simple state changes):**

```css
/* Button hover */
.button {
  background: #0066cc;
  color: white;
  transition: background 200ms ease-out, transform 200ms ease-out;
}

.button:hover {
  background: #0052a3;
  transform: translateY(-2px);
}

.button:active {
  transform: translateY(0);
}

/* Smooth color change */
.link {
  color: #0066cc;
  transition: color 150ms ease-out;
}

.link:hover {
  color: #0052a3;
}

/* Expand on hover */
.card {
  transform: scale(1);
  transition: transform 300ms ease-out, box-shadow 300ms ease-out;
}

.card:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}
```

**CSS Animations (Keyframe sequences):**

```css
/* Loading spinner */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}

/* Fade in */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 600ms ease-out;
}

/* Pulse */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}

/* Shake (error) */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-10px); }
  20%, 40%, 60%, 80% { transform: translateX(10px); }
}

.shake {
  animation: shake 500ms ease-in-out;
}

/* Bounce in */
@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    opacity: 1;
    transform: scale(1.05);
  }
  70% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
  }
}

.bounce-in {
  animation: bounceIn 600ms ease-out;
}
```

**Framer Motion (React animations):**

```tsx
import { motion } from 'framer-motion';

// Simple fade in
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.6 }}
>
  Content
</motion.div>

// Slide in from left
<motion.div
  initial={{ x: -100, opacity: 0 }}
  animate={{ x: 0, opacity: 1 }}
  transition={{ duration: 0.5, ease: 'easeOut' }}
>
  Content
</motion.div>

// Scale on hover
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ duration: 0.2 }}
>
  Click me
</motion.button>

// Stagger children
<motion.ul
  initial="hidden"
  animate="visible"
  variants={{
    visible: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  }}
>
  {items.map(item => (
    <motion.li
      key={item.id}
      variants={{
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0 },
      }}
    >
      {item.name}
    </motion.li>
  ))}
</motion.ul>

// Page transitions
import { AnimatePresence } from 'framer-motion';

<AnimatePresence mode="wait">
  <motion.div
    key={location.pathname}
    initial={{ opacity: 0, x: -100 }}
    animate={{ opacity: 1, x: 0 }}
    exit={{ opacity: 0, x: 100 }}
    transition={{ duration: 0.3 }}
  >
    <Routes />
  </motion.div>
</AnimatePresence>

// Drag
<motion.div
  drag
  dragConstraints={{ left: 0, right: 300, top: 0, bottom: 300 }}
  dragElastic={0.2}
>
  Drag me
</motion.div>

// Gesture animations
<motion.div
  whileHover={{ scale: 1.1 }}
  whileTap={{ scale: 0.9 }}
  whileFocus={{ scale: 1.05 }}
  whileDrag={{ scale: 1.2 }}
>
  Interactive
</motion.div>
```

**GSAP (Complex timelines):**

```javascript
import gsap from 'gsap';

// Simple tween
gsap.to('.box', {
  x: 100,
  duration: 1,
  ease: 'power2.out',
});

// From-to
gsap.fromTo('.box',
  { opacity: 0, y: 50 },
  { opacity: 1, y: 0, duration: 0.8, ease: 'back.out' }
);

// Timeline (sequence)
const tl = gsap.timeline();

tl.to('.box1', { x: 100, duration: 0.5 })
  .to('.box2', { x: 100, duration: 0.5 }, '-=0.2') // Overlap
  .to('.box3', { x: 100, duration: 0.5 }, '+=0.1'); // Delay

// Stagger
gsap.to('.box', {
  y: 100,
  duration: 0.5,
  stagger: 0.1, // 0.1s between each
  ease: 'power2.out',
});

// ScrollTrigger
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

gsap.to('.box', {
  scrollTrigger: {
    trigger: '.box',
    start: 'top center',
    end: 'bottom center',
    scrub: true, // Linked to scroll position
  },
  x: 500,
});

// Complex timeline
const tl = gsap.timeline({ repeat: -1, yoyo: true });

tl.to('.circle', {
  scale: 1.5,
  duration: 0.5,
  ease: 'power2.inOut',
})
.to('.circle', {
  rotation: 360,
  duration: 1,
  ease: 'none',
}, '-=0.5')
.to('.circle', {
  x: 200,
  duration: 0.8,
  ease: 'back.out',
});
```

---

## Layer 4: Performance

### Goal: Maintain 60fps

**GPU-Accelerated Properties (Fast):**

```css
/* ✅ Use these (GPU-accelerated) */
transform: translateX(100px);
transform: translateY(100px);
transform: scale(1.5);
transform: rotate(45deg);
opacity: 0.5;

/* ❌ Avoid these (CPU-bound, trigger layout) */
left: 100px;
top: 100px;
width: 200px;
height: 200px;
margin-left: 50px;
```

**Will-Change (Optimization hint):**

```css
/* Tell browser to optimize */
.animated-element {
  will-change: transform, opacity;
}

/* Remove after animation */
.animated-element.done {
  will-change: auto;
}

/* ⚠️ Don't overuse - memory cost */
/* Only use on elements that will animate soon */
```

**Performance Checklist:**

```markdown
## Before Animation
- [ ] Use transform instead of position
- [ ] Use opacity instead of visibility
- [ ] Add will-change for complex animations
- [ ] Reduce number of animated elements
- [ ] Use CSS animations for simple cases

## During Animation
- [ ] Monitor FPS (Chrome DevTools)
- [ ] Check for layout thrashing
- [ ] Verify GPU acceleration (Layers panel)
- [ ] Test on low-end devices
- [ ] Profile with Performance tab

## After Animation
- [ ] Remove will-change
- [ ] Clean up event listeners
- [ ] Cancel animations on unmount
- [ ] Test memory usage
- [ ] Verify no jank
```

**Measuring Performance:**

```javascript
// FPS counter
let lastTime = performance.now();
let frames = 0;

function measureFPS() {
  frames++;
  const currentTime = performance.now();
  
  if (currentTime >= lastTime + 1000) {
    const fps = Math.round((frames * 1000) / (currentTime - lastTime));
    console.log(`FPS: ${fps}`);
    frames = 0;
    lastTime = currentTime;
  }
  
  requestAnimationFrame(measureFPS);
}

measureFPS();

// Performance observer
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log('Animation duration:', entry.duration);
  }
});

observer.observe({ entryTypes: ['measure'] });
```

---

## Layer 5: Accessibility

### Goal: Respect user preferences

**Prefers-Reduced-Motion:**

```css
/* Default: full animations */
.animated {
  animation: slideIn 600ms ease-out;
}

/* Reduced motion: instant or subtle */
@media (prefers-reduced-motion: reduce) {
  .animated {
    animation: none;
    /* Or use instant transition */
    transition: none;
  }
  
  /* Or subtle fade only */
  .animated {
    animation: fadeIn 200ms ease-out;
  }
}
```

**React Implementation:**

```tsx
import { useReducedMotion } from 'framer-motion';

function AnimatedComponent() {
  const shouldReduceMotion = useReducedMotion();
  
  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: shouldReduceMotion ? 0.01 : 0.6,
      }}
    >
      Content
    </motion.div>
  );
}
```

**Custom Hook:**

```tsx
import { useEffect, useState } from 'react';

function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handleChange = () => {
      setPrefersReducedMotion(mediaQuery.matches);
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);
  
  return prefersReducedMotion;
}

// Usage
function Component() {
  const prefersReducedMotion = usePrefersReducedMotion();
  
  return (
    <div
      style={{
        transition: prefersReducedMotion ? 'none' : 'all 300ms',
      }}
    >
      Content
    </div>
  );
}
```

**Focus Indicators:**

```css
/* Ensure focus is visible during animations */
.button {
  transition: transform 200ms;
}

.button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
  /* Don't animate outline */
}

.button:hover {
  transform: scale(1.05);
}
```

**Screen Reader Announcements:**

```tsx
// Announce state changes
function LoadingButton() {
  const [loading, setLoading] = useState(false);
  
  return (
    <>
      <button
        onClick={() => setLoading(true)}
        aria-busy={loading}
      >
        {loading ? 'Loading...' : 'Submit'}
      </button>
      
      {/* Screen reader announcement */}
      <div
        role="status"
        aria-live="polite"
        className="sr-only"
      >
        {loading && 'Loading, please wait'}
      </div>
    </>
  );
}
```

---

## Common Animation Patterns

### 1. Button Interactions

```css
.button {
  background: #0066cc;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 200ms ease-out;
}

.button:hover {
  background: #0052a3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
}

.button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 102, 204, 0.2);
}

.button:focus-visible {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}
```

### 2. Modal Open/Close

```tsx
<AnimatePresence>
  {isOpen && (
    <>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.2 }}
        className="modal-backdrop"
        onClick={onClose}
      />
      
      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        transition={{ duration: 0.3, ease: 'easeOut' }}
        className="modal"
      >
        <h2>Modal Title</h2>
        <p>Modal content</p>
        <button onClick={onClose}>Close</button>
      </motion.div>
    </>
  )}
</AnimatePresence>
```

### 3. List Stagger

```tsx
<motion.ul
  initial="hidden"
  animate="visible"
  variants={{
    visible: {
      transition: {
        staggerChildren: 0.1,
      },
    },
  }}
>
  {items.map((item, index) => (
    <motion.li
      key={item.id}
      variants={{
        hidden: { opacity: 0, x: -20 },
        visible: { opacity: 1, x: 0 },
      }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      {item.name}
    </motion.li>
  ))}
</motion.ul>
```

### 4. Loading Spinner

```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top-color: #0066cc;
  border-radius: 50%;
  animation: spin 800ms linear infinite;
}
```

### 5. Skeleton Loading

```css
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 0%,
    #e0e0e0 50%,
    #f0f0f0 100%
  );
  background-size: 1000px 100%;
  animation: shimmer 2s infinite linear;
}
```

---

## Animation Checklist

**Planning:**
- [ ] Define purpose (feedback, guidance, continuity, etc.)
- [ ] Choose appropriate duration (100-800ms)
- [ ] Select easing function
- [ ] Consider accessibility

**Implementation:**
- [ ] Use GPU-accelerated properties (transform, opacity)
- [ ] Add will-change for complex animations
- [ ] Implement prefers-reduced-motion
- [ ] Test on low-end devices

**Performance:**
- [ ] Maintain 60fps
- [ ] No layout thrashing
- [ ] GPU acceleration verified
- [ ] Memory usage acceptable

**Accessibility:**
- [ ] Respects prefers-reduced-motion
- [ ] Focus indicators visible
- [ ] Screen reader announcements
- [ ] Keyboard accessible

---

## Common Animation Mistakes

### Mistake 1: Animating Layout Properties
**Problem:** `left`, `top`, `width`, `height` cause reflow

**Solution:** Use `transform` and `opacity`

### Mistake 2: Too Long
**Problem:** 2-second animations feel slow

**Solution:** Keep under 800ms for most UI

### Mistake 3: Ignoring Reduced Motion
**Problem:** Motion sickness for some users

**Solution:** Always implement prefers-reduced-motion

### Mistake 4: Too Many Elements
**Problem:** Animating 100+ elements at once

**Solution:** Stagger or limit visible animations

### Mistake 5: No Purpose
**Problem:** Animation for animation's sake

**Solution:** Every animation should have a clear purpose

---

## Integration with Other Skills

**Use before animating:**
- `component-library` - Component structure
- `responsive-design` - Responsive animations
- `accessibility-audit` - Accessibility requirements

**Use during development:**
- `performance-optimization` - Optimize animations
- `test-driven-development` - Test animation logic

**Use after implementation:**
- `requesting-code-review` - Review animation code
- `user-research` - Test with users

---

**Remember:** Animations should enhance, not distract. Keep them purposeful, performant, and accessible. When in doubt, less is more. Always respect prefers-reduced-motion.
