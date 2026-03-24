# Design System Strategy: The Gilded Minimalist

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Digital Vault."** 

We are moving away from the "utility-first" aesthetic of standard admin dashboards toward a high-end, editorial experience that feels like a private Swiss bank or a luxury concierge service. To break the "template" look, we employ **Intentional Asymmetry**. Large-scale typography is often offset against dense data visualizations, creating a rhythmic tension between breathing room and information density. We don't just display data; we curate it.

The system relies on high-contrast typography scales and overlapping surfaces. By allowing certain "Glassmorphism" elements to bleed over container boundaries, we create a sense of three-dimensional depth that feels bespoke and premium.

---

## 2. Colors & Surface Philosophy
The palette is built on a foundation of obsidian and charcoal, punctuated by precision-engineered metallic accents.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning or layout containment. Structural separation must be achieved exclusively through:
- **Background Tonal Shifts:** Placing a `surface-container-high` card against a `surface` background.
- **Negative Space:** Using the Spacing Scale (specifically 8, 12, or 16 units) to create "invisible" boundaries.
- **Luminance Contrast:** Subtle variations between `surface-container-low` and `surface-container-highest`.

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of luxury materials. 
- **Base Layer:** `surface` (#131313).
- **Secondary Tier:** `surface-container` (#201f1f) for main content areas.
- **Floating Tier:** `surface-container-highest` (#353534) for interactive elements like modals or dropdowns.

### The "Glass & Gradient" Rule
To avoid a "flat" digital feel, use **Metallic Gradients** for Primary CTAs. Instead of a solid `#f2ca50`, use a linear gradient from `primary` (#f2ca50) to `primary-container` (#d4af37) at a 135-degree angle. This mimics the way light hits real gold. For floating navigation or top bars, use `surface-bright` at 60% opacity with a `20px` backdrop-blur to create a "Smoked Glass" effect.

---

## 3. Typography: Editorial Authority
We utilize a dual-typeface system to balance character with absolute legibility.

- **The Voice (Manrope):** Used for `display` and `headline` roles. Manrope’s geometric yet warm proportions provide an authoritative, modern-luxury feel. Use `headline-lg` (2rem) for page titles to establish clear hierarchy.
- **The Utility (Inter):** Used for `title`, `body`, and `label` roles. Inter is the workhorse for high-density data. It ensures that even at `body-sm` (0.75rem), financial figures and technical metrics remain crystal clear.

**Hierarchy Tip:** Always pair a `display-sm` headline with a `label-md` in `on-surface-variant` (muted gold/grey) to create the "Editorial Lead" look found in high-end magazines.

---

## 4. Elevation & Depth
Depth in this system is a result of **Tonal Layering**, not structural scaffolding.

- **The Layering Principle:** Place a `surface-container-lowest` (#0e0e0e) card on a `surface-container-low` (#1c1b1b) section. This "recessed" look is more sophisticated than a raised shadow.
- **Ambient Shadows:** Shadows should only be used for "True Overlays" (Modals/Popovers). Use a blur of `40px`, an opacity of `8%`, and a tint derived from `primary_container` (#d4af37) to simulate a golden glow reflecting off a dark surface.
- **The "Ghost Border" Fallback:** If a divider is functionally required, use `outline-variant` (#4d4635) at **15% opacity**. It should be felt, not seen.
- **Interactive Depth:** On hover, an element shouldn't just change color; it should "lift" by transitioning from `surface-container` to `surface-container-high`.

---

## 5. Components

### Buttons
- **Primary:** Gradient fill (`primary` to `primary-container`), black text (`on-primary`), `md` (0.375rem) corner radius.
- **Secondary:** `Ghost Border` (15% opacity `outline-variant`) with `primary` text.
- **Tertiary:** No background. Underline on hover using a 1px `primary` border-bottom with `2px` offset.

### Input Fields
- **Style:** Never use a 4-sided box. Use a "Soft Tray" approach: a `surface-container-highest` background with a slightly brighter bottom-border (`outline-variant`) that animates to `primary` (gold) on focus.
- **Label:** Always use `label-sm` in `on-surface-variant` positioned above the input.

### Cards & Lists
- **Prohibition:** Divider lines are strictly forbidden in lists.
- **The "Spatial Separation" Rule:** Use `spacing-4` (0.9rem) between list items. Use alternating background tints (`surface-container-low` vs `surface-container`) for long data tables to maintain horizontal tracking.

### Gold Status Chips
For "Active" or "Premium" statuses, use a semi-transparent `primary` background (10% opacity) with a solid `primary` text and a tiny 4px gold dot. This creates a "jeweled" indicator effect.

---

## 6. Do’s and Don’ts

### Do:
- **Use "Golden" White Space:** Be generous with margins. A high-end dashboard feels expensive because it isn't "cramped."
- **Use Metallic Textures Sparingly:** Only apply subtle noise or metallic grain to the `primary` gradient elements.
- **Leverage Asymmetry:** Place a large `display-md` metric on the left and three `body-sm` data points stacked on the right.

### Don’t:
- **No Pure White:** Never use #FFFFFF. Use `on-surface` (#e5e2e1) to prevent eye strain against the dark background.
- **No Harsh Shadows:** Avoid the standard `0 4px 6px rgba(0,0,0,0.1)`. It looks "cheap" and "SaaS-generic."
- **No 100% Opaque Borders:** High-contrast lines "trap" the eye. We want the user's gaze to flow across the data like liquid.
- **No "Default" Inter:** Avoid using Inter for headlines. Use the Manrope scale provided to maintain the editorial signature.