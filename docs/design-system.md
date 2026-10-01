# Design System

> **No design system exists in this project, and no UI has been built.** This document records only
> what is actually present in the repository. It does not describe a clinic design system, because
> none has been designed or implemented.

Related documents: [architecture.md](architecture.md) · [data-model.md](data-model.md)

---

## 1. What exists

### 1.1 Class design system — none

No Figma file, style guide, Storybook, component library, or design token file is referenced anywhere
in the repository. A search across `README.md`, `SETUP.md`, `API.md`, `frontend/index.html`,
`frontend/package.json`, and all CSS returns no match for Figma, design system, styleguide,
Storybook, Tailwind, Bootstrap, or Material.

**There is no class design system to link.** No URL can be given, because none was ever recorded in
the project.

### 1.2 Styling dependencies — none

`frontend/package.json` declares no CSS framework or styling library. Dependencies are `react`,
`react-dom`, and Vite/ESLint tooling only.

### 1.3 Screens — none

`frontend/src/App.jsx` (122 lines) is the unmodified Vite + React starter landing page: a `count`
state counter, `hero.png`, the React and Vite logos, and links to vite.dev, react.dev, GitHub,
Discord, X, and Bluesky. There are no clinic screens, no routing, no forms, no tables, and no data
display.

### 1.4 Screenshots — none

No screenshot image files exist in the repository. The only images present are Vite template assets:

| File | Size | Content |
| :--- | :--- | :--- |
| `frontend/src/assets/hero.png` | 13 KB | Vite logo graphic |
| `frontend/src/assets/react.svg` | 4 KB | React logo |
| `frontend/src/assets/vite.svg` | 8 KB | Vite logo |
| `frontend/public/favicon.svg` | 9 KB | Vite favicon |
| `frontend/public/icons.svg` | 5 KB | Vite template icon sprite |

No clinic iconography, logo, or product imagery exists.

---

## 2. The only implemented UI: Django Admin

Django Admin is the sole working user interface. It is framework-generated rather than custom-built,
configured in [`backend/clinic/admin.py`](../backend/clinic/admin.py):

* **`/admin/`** — searchable, filterable list and change pages for all four models
* **Student change page** — tabular inlines for `HealthRecordInline` (health_id, blood_type, weight,
  height, allergies) and `ConsultationInline` (consultation_id, visits, consultation), so staff can
  view and add child records without leaving the student page
* Grouped fieldsets per model: Student Identity; Vitals & Physical Stats; Medical Information;
  Consultation Information; Status Information; and collapsed Timestamps sections
* `raw_id_fields` on every foreign key, so staff pick students via an ID lookup rather than a
  dropdown
* Session-authenticated — requires an `is_staff` account

It follows Django's default admin styling. There is no custom CSS, theming, or branding.

---

## 3. Existing CSS

`frontend/src/index.css` and `frontend/src/App.css` are Vite starter boilerplate. They style only the
template landing page and will need replacing to build a clinic UI. The values are reproduced here
because they are what the codebase currently defines — note the purple accent is **Vite branding**,
not a clinic design decision.

Tokens in `frontend/src/index.css` (`:root`):

| Token | Light value | Purpose |
| :--- | :--- | :--- |
| `--text` | `#6b6375` | Body text |
| `--text-h` | `#08060d` | Headings |
| `--bg` | `#fff` | Page background |
| `--border` | `#e5e4e7` | Dividers, borders |
| `--code-bg` | `#f4f3ec` | Code / inline-code background |
| `--accent` | `#aa3bff` | Accent — Vite purple |
| `--accent-bg` | `rgba(170, 59, 255, 0.1)` | Accent surface |
| `--accent-border` | `rgba(170, 59, 255, 0.5)` | Accent border / hover |
| `--social-bg` | `rgba(244, 243, 236, 0.5)` | Button surface |
| `--shadow` | `rgba(0,0,0,0.1) 0 10px 15px -3px`, `rgba(0,0,0,0.05) 0 4px 6px -2px` | Elevation |
| `--sans` | `system-ui, 'Segoe UI', Roboto, sans-serif` | Body type |
| `--heading` | `system-ui, 'Segoe UI', Roboto, sans-serif` | Heading type (identical to body) |
| `--mono` | `ui-monospace, Consolas, monospace` | Monospace |

Dark-mode overrides exist under `@media (prefers-color-scheme: dark)` (`index.css:33-51`), restating
the same tokens with dark values (`--bg: #16171d`, `--accent: #c084fc`, `--border: #2e303a`,
`--text: #9ca3af`). Because the template sets `color-scheme: light dark`, browser UI follows
automatically.

Type scale:

| Element | Value | Location |
| :--- | :--- | :--- |
| `html` | `18px/145%`, dropping to `16px` at ≤1024px | `index.css:18` |
| `h1` | `56px` → `36px`, weight 500, letter-spacing `-1.68px` | `index.css:76` |
| `h2` | `24px` → `20px`, weight 500 | `index.css:85` |
| `code` | `15px/135%`, `--code-bg`, 4px radius | `index.css:106` |
| `.counter` | `16px`, 5px 10px padding, 5px radius | `App.css:1` |

Layout:

| Rule | Value | Location |
| :--- | :--- | :--- |
| `#root` width | `1126px`, `max-width: 100%`, centred | `index.css:58` |
| `#root` height | `min-height: 100svh`, flex column | `index.css:63` |
| `#root` border | `1px` inline `var(--border)` | `index.css:62` |
| Global alignment | `text-align: center` on `#root` | `index.css:61` |
| `.hero` | position context for stacked logos | `App.css:20` |
| `#next-steps` | two-column flex, stacks below 1024px | `App.css:73` |
| `#spacer` | 88px → 48px on small screens | `App.css:156` |
| `.ticks` | 5px triangular notches on a border | `App.css:164` |

Accessibility as it stands:

* `:focus-visible` outline (2px `var(--accent)`, 2px offset) is defined for `.counter` only
  (`App.css:14-17`) — no other interactive element has a focus style
* No `prefers-reduced-motion` handling anywhere
* `color-scheme: light dark` is declared, giving automatic dark-mode browser chrome
* Global `text-align: center` and the fixed `1126px` container suit a marketing landing page, not a
  data-dense clinical interface

---

## 4. Summary

| Required element | Status |
| :--- | :--- |
| Class design system link | **Absent** — no Figma file or equivalent is referenced anywhere |
| Module-specific UI details | **Absent** — no screens or components exist to document |
| Screenshots of main screens | **Absent** — no screenshots exist, and no screens exist to capture |
| Custom design tokens | **Absent** — only Vite template tokens |
| Clinic iconography / branding | **Absent** — only Vite template assets |
| Implemented UI | Django Admin only, framework-default styling |

Any clinic design system, screen specification, or screenshot would have to be created before this
document can describe them. It is left as a record of the actual current state rather than a
specification of intended work.