# AETHERION — BEYOND THE KNOWN.

## Direction

A compact technical studio with a calm desktop hierarchy. The navigation layer is a quiet translucent material, task surfaces are heavier and readable, and the accent identifies action/selection. No decorative telemetry, random gradients, neon glow or panels without a task.

The UI/UX Pro Max search for `benchmark data dashboard` confirmed the relevance of readable metrics and accessible comparisons. Its broad Glassmorphism/commercial-landing result was not adopted as a layout. Apple Design guidance informs material weight, selective blur, instant pressed feedback and interruptible transitions. The existing web identity supplies the orbital mark and silicon vocabulary.

## Tokens and scale

| Role | Value |
| --- | --- |
| Canvas | #080A0F |
| Surface | #11151E |
| Elevated | #1A2030 |
| Primary text | #F5F7FA |
| Secondary text | #A0A8B8 |
| Quiet text | #929AAA |
| Accent | #8BA8FF |
| Success / warning / error | #9BE0B5 / #F2C879 / #FF9292 |
| Font | Bundled Inter, weights 400–600 |
| Body / supporting text | 13 / 12 logical px |
| Section / page / feature | 19 / 30 / 35 logical px |
| Surface / control radius | 16 / 9 logical px |
| Main gutter / panel inset | 30 / 24 logical px |
| Spacing rhythm | 6, 8, 12, 16, 20, 24, 30 |
| Mouse/keyboard action height | 40–44 logical px |
| Page / hover / progress motion | 200 / 200 / 250 ms, ease-out cubic |

These are device-independent units. Windows display scaling is handled by Qt with a PerMonitorV2 manifest. All persistent text remains native text; charts/icons/brand geometry are vectors. Temporary fade effects are removed after the animation so ordinary content does not stay rasterized. Reduced motion follows the Windows preference unless the user saves an override.

## Interaction and information

Model status and validation always include text. Fit is explicitly estimated, and the recommendation is withheld when memory telemetry is unavailable or no model passes the compatibility heuristic. Throughput uses saved measured values only; charts label units and warn that task suites may differ. Empty states explain the next action and contain no pretend activity.

Ctrl+1–7 selects sections. Ctrl+K opens searchable commands. Ctrl+F focuses the current library/records search. Ctrl+Enter starts a configured benchmark from the lab. Enter/Space activates buttons; Escape closes sheets. Errors stay until dismissed; settings persist locally. Downloads are cancellable, staged into a partial file and moved into the library only when complete.

The only background blur is used for modal focus. It is a static capture behind the sheet, not a continuously blurred whole application. Larger surfaces use subtle alpha, an inner highlight and depth. A material preference supplies an opaque alternative.
