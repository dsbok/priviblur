# Design System: Priviblur (Industrial Brutalist Minimalist)
**Project ID:** dsbok/priviblur

## 1. Visual Theme & Atmosphere
The layout follows an Industrial Brutalist Minimalist design. It features raw structural lines, sharp boxy geometry, flat offset mechanical shadows, and a high-contrast dark palette highlighted by safety warning yellow. The interface feels raw, heavy, and mechanical, optimizing for absolute responsiveness and zero-lag feedback.

## 2. Color Palette & Roles
Colors represent a raw, high-contrast industrial palette:

* **Backdrop Concrete** (`#0e0e10` / `hsl(240, 10%, 6%)`): Dark iron backdrop.
* **Structural Card BG** (`#16161a` / `hsl(240, 9%, 9%)`): Solid dark steel card container.
* **Brutalist Accent / Warning Highlight** (`#facc15` / `hsl(48, 96%, 53%)`): Safety warning yellow, used for primary interactions, active tabs, and logo accents.
* **Label Primary** (`#ffffff` / `hsl(0, 0%, 100%)`): Pure white text.
* **Label Secondary** (`#a1a1aa` / `hsl(240, 5%, 65%)`): Concrete gray for timestamps, tags, and secondary metadata.
* **Borders / Grid Lines** (`#ffffff` / `hsl(0, 0%, 100%)`): Solid white structural lines (`2px` thickness) to frame all cards, inputs, and buttons.

## 3. Typography Rules
* **Font Family:** Hybrid system monospace stack (`"SF Mono", "Fira Code", Menlo, Monaco, "Courier New", monospace`) combined with heavy sans-serif.
* **Weights:**
  * Heavy (`800`) and Black (`900`) for headers, branding, and titles.
  * Regular monospace (`400`) for post text.
* **Letter Spacing:** Standard spacing for monospace; no rounding or tracking adjustments.

## 4. Component Stylings
* **Buttons**: Sharp rectangular blocks (`border-radius: 0px`) with a `2px solid #ffffff` border and a flat offset shadow (`box-shadow: 3px 3px 0px #ffffff`). Hovering translates the button (`transform: translate(3px, 3px)`) and collapses the shadow (`box-shadow: 0px 0px 0px`) to simulate a mechanical click.
* **Cards/Containers**: Framed boxes (`border-radius: 0px`) with solid borders (`2px solid #ffffff`) and flat offset shadows (`box-shadow: 6px 6px 0px #ffffff`).
* **Inputs & Search**: Rectangular input boxes (`border-radius: 0px`) with solid white borders and high-contrast yellow backgrounds on focus.

## 5. Layout Principles
* **Timeline Width**: Constrained to `640px` with rigid vertical borders.
* **Mechanical Animations**: No smooth fades. Interactive elements use instant mechanical transitions (`transition: transform 0.1s ease, box-shadow 0.1s ease`).
