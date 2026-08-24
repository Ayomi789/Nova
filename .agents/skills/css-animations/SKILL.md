---
name: css-animations
description: "Web UI animation with CSS and light JS. Use when adding transitions, hover effects, keyframe animations, scroll-reveal, micro-interactions, page transitions, or loading shimmer to websites and apps."
---

# CSS Animations for Web UI

Motion that clarifies hierarchy and state - never decoration for its own sake.

## Choose the right tool

| Need | Use |
|---|---|
| State change (hover, focus, open/close) | `transition` |
| Multi-step or looping motion | `@keyframes` + `animation` |
| Enter/exit on scroll into view | IntersectionObserver + class toggle |
| Physics-y or interruptible UI motion | WAAPI (`element.animate`) or a tiny JS spring |
| Complex sequenced choreography | GSAP |

## Performance iron law

Only animate `transform` and `opacity`. They run on the compositor.
Never animate `width`, `height`, `top`, `left`, `margin`, or `box-shadow`
duration-wise - they force layout/paint every frame. For size changes use
`transform: scale()`, for reveals use `clip-path` or `opacity`.

Always promote intentionally:
```css
.card { will-change: transform; } /* only while animating */
```

## Duration and easing tokens

- Micro feedback (hover, press): 120-200ms
- Enter/exit transitions: 200-350ms
- Large surfaces / page moves: 350-600ms
- Nothing decorative over 700ms.

Easings:
```css
--ease-out:   cubic-bezier(0.16, 1, 0.3, 1);    /* entrances  */
--ease-in:    cubic-bezier(0.7, 0, 0.84, 0);    /* exits      */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* playful pop */
```
Entrances ease-out. Exits ease-in. Never linear (except loops/indeterminate).

## Core patterns

Fade-up on reveal:
```css
.reveal { opacity: 0; transform: translateY(16px); transition: opacity .5s var(--ease-out), transform .5s var(--ease-out); }
.reveal.is-visible { opacity: 1; transform: none; }
```

Stagger children via `transition-delay: calc(var(--i) * 60ms)` with `style="--i: n"`.

Hover lift:
```css
.card { transition: transform .2s var(--ease-out), box-shadow .2s; }
.card:hover { transform: translateY(-4px); }
```

Skeleton shimmer (compositor-safe):
```css
@keyframes shimmer { from { background-position: 200% 0; } to { background-position: -200% 0; } }
.skeleton { background: linear-gradient(90deg, #eee 25%, #f5f5f5 50%, #eee 75%) 0 0 / 200% 100%; animation: shimmer 1.4s linear infinite; }
```

Respect reduced motion - always:
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}
```

## Anti-slop rules

- One motion idea per component. No floating + pulsing + rotating at once.
- Animate the smallest element that communicates the change, not whole sections by default.
- No infinite ambient animations on marketing pages above the fold.
- Modals/sheets scale from their trigger direction, fade backdrop 150ms.
- Lists entering: stagger 40-80ms per item, cap total sequence under 600ms.
- Buttons confirm presses with 1px translate + slight darken, not bounce.
