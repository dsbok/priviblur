# Design System: Priviblur (Apple HIG)
**Project ID:** dsbok/priviblur

## 1. Visual Theme & Atmosphere
Priviblur's visual theme follows the Apple Human Interface Guidelines (HIG) for macOS/iOS Dark Mode. The interface relies on pure black backdrop surfaces, flat nested containers with subtle border separation, system-level typography, and clean contrast. Spacing is comfortable, interactions are micro-animated, and frosted glass elements are used to convey layer depth.

## 2. Color Palette & Roles
Colors correspond to Apple's native Dark Mode system palette:

* **System Background** (`#000000` / `hsl(0, 0%, 0%)`): Pure black backdrop for absolute contrast and OLED power saving.
* **Secondary Grouped Background (Card BG)** (`#1c1c1e` / `hsl(240, 6%, 10%)`): Apple's system gray, used to group post content blocks.
* **Tertiary Grouped Background (Input BG)** (`#2c2c2e` / `hsl(240, 5%, 15%)`): Lighter system gray for search inputs and hover states.
* **System Blue (Primary Accent)** (`#0a84ff` / `hsl(211, 100%, 52%)`): Active navigation tabs, link indicators, and primary call-to-action buttons.
* **Label Primary** (`#ffffff` / `hsl(0, 0%, 100%)`): Pure white for body and primary text.
* **Label Secondary** (`#8e8e93` / `hsl(240, 2%, 56%)`): Apple system gray for secondary metadata, timestamps, and tag descriptions.

## 3. Typography Rules
* **Font Family:** Apple's system font stack (`-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", sans-serif`).
* **Weights:**
  * Semibold (`600`): Used for header typography, title metadata, and buttons.
  * Regular (`400`): Used for main body text, reblog comments, and descriptions.
* **Letter Spacing:** Balanced system tracking (`letter-spacing: -0.1px` on body and titles) to emulate SF Pro font characteristics.

## 4. Component Stylings
* **Buttons**: Rounded buttons with a clean corner radius (`border-radius: 8px`). Primary buttons use System Blue (`#0a84ff`) background with white text, and secondary buttons use System Gray (`#2c2c2e`).
* **Cards/Containers**: Apple-style nested containers with a corner radius (`border-radius: 12px`), minimal subtle border strokes (`1px solid rgba(255, 255, 255, 0.08)`), and flat elevation (no shadows).
* **Inputs & Search Bars**: Smooth pill-shaped/curved containers (`border-radius: 10px`) utilizing `#2c2c2e` backgrounds.

## 5. Layout Principles
* **Timeline Containment**: Constrained to a standard content width of `640px`.
* **Margins & Insets**: Consistent spacing margins (`16px` mobile, `24px` desktop) following standard Apple padding grids.
