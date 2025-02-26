# Malaysian Design System Guidelines

This document summarizes the Malaysian Design System (MYDS) guidelines for use by frontend web developers.

## Grid System (12-8-4)

MYDS uses a responsive 12-8-4 grid system to ensure layouts adapt well to different screen sizes.

**Breakpoints:**

- **Desktop:**  Screens ≥ 1024px width
- **Tablet:** Screens 768px - 1023px width
- **Mobile:** Screens ≤ 767px width

**Grid Specifications:**

| Screen Size | Grid Columns | Column Gap | Edge Padding | Max Content Width |
|---|---|---|---|---|
| **Desktop (≥1024px)** | 12 Columns | 24px | Yes | 1280px |
| **Tablet (768px - 1023px)** | 8 Columns | 24px | Yes | N/A (Adapts to screen) |
| **Mobile (≤767px)** | 4 Columns | 18px | Yes | N/A (Adapts to screen) |

**Container Types and Width Behavior:**

- **Content:** Flexible container for general content layouts, adapts to the grid system.
- **Article:** Container for long-form text, maximum width of 640px for comfortable reading.
- **Images & Interactive Charts:** Can span article width (640px) or extend up to 740px for more visual impact.

## Radius

MYDS uses consistent corner radii to create a modern and unified look.

**Radius Specifications:**

| Name          | Size  | Usage Examples              |
|---------------|-------|------------------------------|
| **Extra Small** | `4px` | Context Menu Item            |
| **Small**       | `6px` | Small Button                 |
| **Medium**      | `8px` | Button, CTA, Context Menu     |
| **Large**       | `12px`| Content Card                 |
| **Extra Large** | `14px`| Context Menu with Search field |

## Shadow

Shadows are used to add depth and visual hierarchy to UI elements.

**Shadow Specifications:**

| Name           | CSS `box-shadow` Value                                    |
|----------------|------------------------------------------------------------|
| **Button**       | `0px 1px 3px 0px rgba(0, 0, 0, 0.07)`                    |
| **Card**         | `0px 2px 6px 0px rgba(0, 0, 0, 0.05),`<br>`0px 6px 24px 0px rgba(0, 0, 0, 0.05)` |
| **Context Menu** | `0px 2px 6px 0px rgba(0, 0, 0, 0.05),`<br>`0px 12px 50px 0px rgba(0, 0, 0, 0.10)` |

## Spacing

Consistent spacing is crucial for creating visually balanced and harmonious layouts. MYDS defines specific spacing values to be used across components.

**Spacing Sizes and Usage Examples:**

| Size  | Usage Examples                                |
|-------|------------------------------------------------|
| **4px**   |                                                |
| **8px**   | Gap in button groups, fields and labels        |
| **12px**  |                                                |
| **16px**  |                                                |
| **20px**  |                                                |
| **24px**  | Gap between subsections, cards              |
| **32px**  | Gap between main sections                     |
| **40px**  |                                                |
| **48px**  |                                                |
| **64px**  |                                                |