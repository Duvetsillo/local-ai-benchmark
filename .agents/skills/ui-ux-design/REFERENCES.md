# UI/UX Design References

Optional implementation values and design heuristics. Use this file to pick a direction quickly, not to copy a canned style system.

## Table of Contents

- [Aesthetic Directions](#aesthetic-directions)
- [Color System](#color-system)
- [Typography](#typography)
- [Spacing & Layout](#spacing--layout)
- [Component Patterns](#component-patterns)
- [Motion & Accessibility](#motion--accessibility)
- [External Resources](#external-resources)

---

## Aesthetic Directions

Choose one strong direction that matches the product context. Do not mix several unless the user explicitly wants a more eclectic result.

### Minimalism

- generous whitespace
- restrained palette
- typography and layout carry most of the visual weight
- best for productivity tools, portfolios, internal dashboards

### Glassmorphism

- layered surfaces with blur and translucency
- stronger contrast between background and content panes
- best for dashboards, visual tooling, experimental product surfaces

### Neubrutalism

- hard shadows, thick borders, bold contrast
- playful and intentionally non-neutral
- best for creative tools, startups, brand-forward marketing pages

### Editorial

- strong type hierarchy
- clear columns and rhythm
- image and copy composition matter more than chrome
- best for content-heavy pages, publications, story-led landing pages

### Organic

- rounded shapes, warmer colors, softer contrast transitions
- approachable and less mechanical
- best for consumer apps, wellness, education, community products

### Dark Mode

- use when the product already supports it or the user explicitly asks
- lower overall brightness, but keep hierarchy strong
- avoid washed-out gray-on-gray text

---

## Color System

Use a semantic color system first. Pick an accent that matches the product tone and keep the rest neutral.

### Neutral Foundation

```css
:root {
  --gray-50: #fafafa;
  --gray-100: #f4f4f5;
  --gray-200: #e4e4e7;
  --gray-300: #d4d4d8;
  --gray-400: #a1a1aa;
  --gray-500: #71717a;
  --gray-600: #52525b;
  --gray-700: #3f3f46;
  --gray-800: #27272a;
  --gray-900: #18181b;
}
```

### Accessible Accent Options

Use one primary accent and map it semantically.

```css
:root {
  --blue-600: #2563eb;
  --blue-700: #1d4ed8;
  --green-600: #16a34a;
  --amber-600: #d97706;
  --red-600: #dc2626;
  --teal-600: #0d9488;
}
```

### Semantic Mapping

```css
:root {
  --color-primary: var(--blue-600);
  --color-primary-hover: var(--blue-700);
  --color-success: var(--green-600);
  --color-warning: var(--amber-600);
  --color-error: var(--red-600);
  --color-text-primary: var(--gray-900);
  --color-text-secondary: var(--gray-600);
  --color-text-muted: var(--gray-500);
  --color-border: var(--gray-200);
  --color-border-strong: var(--gray-300);
}
```

### Dark Surface Baseline

```css
:root[data-theme="dark"] {
  --background: #0a0a0b;
  --surface: #141416;
  --surface-elevated: #1c1c1f;
  --border: #27272a;
  --text-primary: #fafafa;
  --text-secondary: #a1a1aa;
}
```

Guidelines:

- avoid purple as a default accent unless it fits the product
- reserve bright accents for action and emphasis, not every surface
- ensure color is never the only signal for state

---

## Typography

Pick a pairing that reinforces the chosen direction. Use project fonts if the repo already has a typography system.

### Reliable Pairings

- Modern product: `Geist` or `IBM Plex Sans` with `JetBrains Mono` or `IBM Plex Mono`
- Editorial: `Playfair Display` or another high-contrast serif with a quieter serif or sans body
- Friendly consumer: `DM Sans` or `Nunito` with a clean mono for code-like details
- Bold brand-forward: `Cabinet Grotesk` or `Satoshi` with a calmer sans body

### Type Tokens

```css
:root {
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --text-3xl: 1.875rem;
  --text-4xl: 2.25rem;

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.625;

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

Guidelines:

- body copy should usually stay at `16px` equivalent or above
- headings need contrast in both size and weight
- avoid defaulting to Inter/Roboto/system fonts unless the project already uses them

---

## Spacing & Layout

Use a consistent spacing scale and a clear container strategy.

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 16px;
  --space-4: 24px;
  --space-5: 32px;
  --space-6: 48px;
  --space-7: 64px;

  --container-sm: 640px;
  --container-md: 768px;
  --container-lg: 1024px;
  --container-xl: 1280px;

  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-full: 9999px;
}
```

Layout heuristics:

- let spacing create hierarchy before adding extra borders or shadows
- use tighter spacing in dense productivity UIs, looser spacing in editorial and marketing work
- mobile layouts should collapse gracefully before they merely scale down

---

## Component Patterns

Use these as implementation checks, not rigid templates.

### Button

- clear primary vs secondary hierarchy
- visible hover, focus, active, disabled states
- minimum touch target of `44x44px`
- icon-only buttons need accessible labels

### Input

- every input has a visible label
- placeholder text is not the only source of meaning
- error state includes both styling and explanatory text
- use `16px` text on mobile inputs to avoid iOS zoom issues

### Card / Panel

- cards should only be interactive when the whole surface behaves like a control
- use border, elevation, and spacing intentionally; do not stack all three at maximum intensity
- distinguish informational cards from actionable cards

### Empty / Loading / Error States

- empty states should explain what is missing and what to do next
- loading states should preserve layout stability
- error states should state what failed and how the user can recover

### Helpful Snippets

```css
.focus-ring:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## Motion & Accessibility

Motion should support hierarchy and feedback, not decorate everything.

### Motion Tokens

```css
:root {
  --duration-fast: 150ms;
  --duration-normal: 250ms;
  --duration-slow: 400ms;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
}
```

Guidelines:

- animate opacity, transform, and shadow before layout-affecting properties
- reserve larger entrance animations for page-level or section-level moments
- keep repeated UI interactions subtle and fast

Always support reduced motion:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

Accessibility reminders:

- target WCAG AA contrast as the default floor
- preserve visible focus states
- do not rely on hover-only disclosure for essential actions
- pair color changes with icon, text, or layout cues

---

## External Resources

Use these only when needed for verification or asset sourcing.

| Resource | Use For |
|----------|---------|
| [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker) | Contrast validation |
| [Google Fonts](https://fonts.google.com) | Widely available web fonts |
| [Fontshare](https://fontshare.com) | Free distinctive font options |
| [Coolors](https://coolors.co) | Palette exploration |
| [Heroicons](https://heroicons.com) | Clean SVG icon set |
| [Lucide](https://lucide.dev) | Open source icon set |

---

> **License:** MIT
