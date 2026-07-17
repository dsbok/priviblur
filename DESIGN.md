# Design System: Priviblur
**Project ID:** dsbok/priviblur

## 1. Visual Theme & Atmosphere
Priviblur uses a sleek, high-contrast dark mode to deliver a distraction-free Tumblr browsing experience. The design philosophy centers on content density, crisp typography, and fluid micro-transitions. It balances a clean, utilitarian aesthetic with premium, warm accents to make the browsing experience feel rich and modern.

## 2. Color Palette & Roles
The design relies on a curated HSL color palette to control contrast and visual weight:

* **Primary Background** (`#0b0a0a` / `hsl(41, 5%, 4%)`): Ultra-dark charcoal backdrop for the page to focus attention on timeline content.
* **Card & Post Container Background** (`#171615` / `hsl(41, 2%, 7%)`): Muted dark slate, providing structure and separating individual posts.
* **Secondary Highlight/Hover** (`#232120` / `hsl(41, 2%, 10.5%)`): Soft accent layer for hover states, active inputs, and dropdown options.
* **Primary Accent** (`#e6952e` / `hsl(36, 80%, 50%)`): Warm, vibrant golden-amber used for call-to-actions, the main navigation highlight, and branding.
* **Primary Text** (`#cccccc` / `hsl(41, 7%, 80%)`): Soft off-white to prevent eye strain while preserving high readability.
* **Secondary Text** (`#807c79` / `hsl(41, 3%, 50%)`): Dark gray for metadata, timestamp links, and footer info.

## 3. Typography Rules
* **Font Family:** Modern system-sans stack (`system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`) to ensure instant loading and consistent rendering across devices.
* **Weights:**
  * Bold (`700`): Used for headings, post titles, and branding.
  * Medium (`500`): Used for interactive tabs, button labels, and tags.
  * Regular (`400` / `450`): Used for post descriptions and body text.
* **Line Height:** Relaxed line height (`1.5`) for readable text blocks.

## 4. Component Stylings
* **Buttons:** Rectangular with clean, subtly rounded corners (`border-radius: 6px`). They use smooth opacity and background color transitions (`transition: all 0.2s ease-in-out`).
* **Cards/Containers:** Frameless with slight corner roundness (`border-radius: 10px`), clean borders (`1px solid hsl(41, 2%, 12%)`), and very subtle glow outlines instead of heavy shadows.
* **Inputs & Search Bars:** Rounded container inputs with inset backgrounds, clean outline-free focus rings utilizing the golden-amber primary accent color.

## 5. Layout Principles
* **Timeline Density:** Timelines are constrained to a maximum content width of `640px` to maintain a readable vertical reading flow.
* **Whitespace Strategy:** Tight but consistent margins (`16px` on mobile, `24px` on desktop) to optimize content density without feeling cluttered.
