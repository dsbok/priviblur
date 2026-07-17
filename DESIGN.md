# Design System: Priviblur (Minimalist Monochrome Brutalist)
**Project ID:** dsbok/priviblur

## 1. Visual Theme & Atmosphere
The layout follows a Minimalist Monochrome Brutalist theme. The design features flat, symmetric, sharp borders with zero box shadows, ensuring all card outlines are identical in thickness. Color is eliminated, relying purely on a high-contrast black, white, and gray scale. Spacing is structural, and interactions are clean and instant.

## 2. Color Palette & Roles
Colors are strictly monochrome:

* **System Canvas** (`#0e0e10` / `hsl(240, 10%, 6%)`): Dark iron canvas background.
* **Card & Post BG** (`#16161a` / `hsl(240, 9%, 9%)`): Solid dark steel card container.
* **Secondary Highlight / Active BG** (`#27272a` / `hsl(240, 5%, 15%)`): Grouped gray for input focus, active tabs, and hover states.
* **Accent Highlight** (`#ffffff` / `hsl(0, 0%, 100%)`): Pure white, used for primary highlights, logo branding, and active tab highlights.
* **Label Primary** (`#ffffff` / `hsl(0, 0%, 100%)`): High-contrast white for text.
* **Label Secondary** (`#a1a1aa` / `hsl(240, 5%, 65%)`): Concrete gray for timestamps, tags, and metadata.
* **Structural Borders** (`#ffffff` / `hsl(0, 0%, 100%)`): Solid white lines (`2px` thickness) framing all cards, buttons, and input fields. Zero box-shadows are used to maintain perfect symmetry.

## 3. Typography Rules
* **Font Family:** System monospace stack (`"SF Mono", "Fira Code", Menlo, Monaco, "Courier New", monospace`).
* **Weights:**
  * Heavy (`800`) and Bold (`700`) for headers, branding, and titles.
  * Regular (`400`) for post body copy.

## 4. Component Stylings
* **Buttons**: Sharp rectangular blocks (`border-radius: 0px`) with a `2px solid #ffffff` border and zero box-shadow. Primary buttons use a solid white background with black text (`#000000`). Secondary buttons use a dark gray background (`rgba(255, 255, 255, 0.08)`) with white text.
* **Cards/Containers**: Flat containers (`border-radius: 0px`) with `2px solid #ffffff` borders all around.
* **Inputs & Search**: Boxy inputs (`border-radius: 0px`) with a `2px solid #ffffff` border, changing background to `#27272a` on focus.

## 5. Layout Principles
* **Timeline Containment**: Constrained to `640px` with symmetric frames.
* **Zero Decoration**: All decorative blurs, gradients, and drop shadows are removed for a raw, high-contrast structural aesthetic.
