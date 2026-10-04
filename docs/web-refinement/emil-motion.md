# Aetherion motion and identity refinement

This pass applies `emil-design-eng` to the existing public website. The orbital star remains the identity: a four-point core, a central dot and orbital geometry. The former overlapping circular paths have been replaced with an open outer orbit and an inclined meridian. The same vector geometry is used in all eight page headers, the homepage footer and download section, and the favicon. `brand-symbol.svg` is the standalone vector source.

| Before | After | Why |
| --- | --- | --- |
| Legacy typing-intro controller, with no matching intro on the new homepage | A finite logo assembly and staggered hero entrance, finishing at approximately 630 ms | Introduce the identity without a blocking overlay or artificial progress |
| Category text changed abruptly | 180 ms opacity and 4 px translation on pointer selection | Make the changed content visible |
| Rapid changes could leave a previous animation running | Cancel the previous animation before applying the latest selection | Keep content and selected state consistent |
| Buttons lacked press feedback | 140 ms transform transition and a subtle press scale | Confirm pointer activation |
| Static mobile menu control | Icon morph and 180 ms entry from its top-right origin | Connect the menu to its trigger |
| Instant FAQ content and swapping plus/minus text | Native disclosure with a rotating plus and a 170 ms answer entrance | Preserve semantics while communicating expansion |
| Header, secondary pages and favicon had different logo geometry | One refined orbital-star vector | Make the identity coherent at small and large sizes |

## Motion decisions

The homepage entrance is a one-time sequence per applicable navigation. It is skipped on back/forward navigation, deep links, restored scroll positions, hidden tabs and reduced-motion preferences. The page stays usable while it runs. It has no perpetual loop.

Repeated interactions are short. Changing an already selected category does nothing. Keyboard-triggered category changes and navigation are immediate: keyboard input cancels running programmatic motion and disables CSS animations and transitions. Pointer input restores pointer feedback. Reduced-motion changes and hidden tabs also cancel active motion. Hover movement is restricted to fine pointers with hover capability.

Predetermined entry uses CSS; interruptible content and menu entry use the Web Animations API. Animated properties are transform and opacity. No motion library, animation of layout dimensions or frame-by-frame pointer tracking was added.

## Validation

- TypeScript compilation and JavaScript syntax checks passed.
- Eight public pages passed checks for heading count, duplicate IDs, local assets, same-page anchors and logo presence. Both SVG assets parsed as valid XML.
- Browser checks verified the completed entrance, four sequential category changes with exactly one selection, and an Enter-triggered category change with CSS transition duration `0s`.
- At 390 px, the logo measured 38 px; the menu opened from the top-right origin and closed with Escape. Pointer category changes restored pointer mode. FAQ opening by pointer and closing with Enter worked.
- No document-level horizontal overflow was found at 320 px, 390 px or the default desktop viewport.
- Reduced-motion branches were inspected in the CSS and JavaScript. The operating-system preference was not changed during verification; physical touch hardware was not tested.

The updated website remains local at `http://127.0.0.1:4173/`. No public deployment was performed.
