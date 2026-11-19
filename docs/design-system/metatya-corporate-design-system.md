# METATYA Corporate Design System

**Status:** Canonical design reference for corporate pages  
**Source of truth:** `docs/metatya-company.css` and the approved corporate homepage `docs/metatya.html`

## 1. Purpose and boundaries

This system makes corporate inner pages visually consistent with the approved METATYA corporate homepage. It is a reusable layer for company, product, capability, and information pages.

- Keep METATYA Academy as a separate website experience. Do not replace its page structure or visual identity with this system.
- Keep each product's data, business logic, permissions, and domain-specific experience independent.
- Do not copy the older shared-capabilities visual system as a second corporate theme.
- Do not change the canonical homepage appearance without explicit approval.
- This design guide describes presentation conventions; it does not claim that a product capability is implemented.

## 2. Brand tokens

The canonical tokens live in `docs/metatya-company.css`. Reuse them; do not introduce competing palette values in page-level styles.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#050807` | Deep black-green page background |
| `--panel` | `#0b1210` | Main panel |
| `--panel2` | `#101b17` | Elevated panel |
| `--green` | `#00ff9d` | Electric-green accent and primary action |
| `--green-dim` | `rgba(0,255,157,.1)` | Soft green surfaces |
| `--silver` | `#c5d0ca` | Secondary emphasis |
| `--muted` | `#9baaa2` | Supporting text |
| `--text` | `#f1f7f3` | Primary text |
| `--line` | `rgba(255,255,255,.09)` | Fine borders |
| `--gold` | `#c9a85d` | Restrained tertiary accent |
| `--width` | `1180px` | Content maximum width |

Visual rules: deep black base, electric green as a controlled accent, silver for secondary hierarchy, restrained gold only where already used, rounded cards, fine borders, subtle glow, and uncluttered typography. Avoid gradients or glow effects that compete with the content.

## 3. Canonical assets

- Stylesheet: `docs/metatya-company.css`
- Shared behavior: `docs/metatya-company.js`
- Corporate homepage: `docs/metatya.html`
- Copy-ready page scaffold: `docs/design-system/metatya-corporate-page-template.html`

A page in `docs/` references the stylesheet and script as `metatya-company.css` and `metatya-company.js`. A template in `docs/design-system/` uses `../metatya-company.css` and `../metatya-company.js`. Keep relative paths correct after copying a template.

## 4. Page shell

Every corporate page should use:

1. `<!doctype html>`, `<html lang="fa" dir="rtl">`, UTF-8 and responsive viewport metadata.
2. A descriptive title and page-specific description.
3. The Vazirmatn font link and canonical stylesheet.
4. A visible-on-focus skip link to `#main`.
5. A shared `.site-header` with brand, desktop navigation, CTA, and accessible mobile toggle.
6. Exactly one primary `<main id="main">`.
7. A shared `.site-footer` with company, Academy, and contact routes as appropriate.
8. The canonical script with `defer`.

Do not duplicate IDs. Every in-page navigation target must exist. Keep the menu button's `aria-controls` synchronized with the mobile navigation ID and its `aria-expanded` state.

## 5. Component catalogue

| Component | Classes | Intended use |
|---|---|---|
| Content frame | `.container` | Centered responsive width |
| Header | `.site-header .nav-wrap .brand .desktop-nav` | Shared company navigation |
| Mobile navigation | `.menu-toggle .mobile-nav` | Accessible compact navigation |
| Skip link | `.skip-link` | Keyboard access to main content |
| Eyebrow | `.eyebrow .pulse` | Small section label |
| Hero | `.hero .hero-copy .hero-art` | Page title, lead, actions, visual |
| Actions | `.hero-actions .button` | Primary and quiet CTAs |
| Intro strip | `.intro-strip .intro-grid` | Short framing statement |
| Section heading | `.section .section-heading` | Section title and supporting copy |
| Cards | `.product-grid .product-card` | Repeated products, capabilities, or topics |
| Status | `.status` with `.status-build`, `.status-plan`, `.status-separate` | Explicit and evidence-based state |
| Foundation | `.foundation-section .foundation-layout` | Shared architecture or explanatory content |
| Capability tiles | `.capability-grid` | Compact feature descriptions |
| Principles | `.principle-grid` | Engineering or governance principles |
| Founder / profile | `.founder-section .founder-layout` | Approved company profile content |
| Closing CTA | `.closing-cta` | Centered final action |
| Footer | `.site-footer .footer-main .footer-bottom` | Consistent close and navigation |

Use only components needed by the page. A page may omit the visual hero artwork, foundation section, or founder section when they do not add value; do not add filler merely to match the homepage length.

## 6. Status and content integrity

- Use `در حال توسعه` only when development is actually in progress.
- Use `مسیر محصول` or `در برنامه` for a planned direction, not an implemented feature.
- Use `پروژه مستقل` only when the project is in fact independently governed.
- Distinguish architectural intent from tested, deployed, and operational capability.
- Put a transparency note near product or capability cards whenever status could be misunderstood.
- Do not publish customer data, internal secrets, credentials, or unsupported performance claims.
- Confirm every external destination and every local link before release.

## 7. Responsive behavior

The canonical stylesheet already defines breakpoints at 980px, 720px, and 480px. Use its existing grid and spacing behavior. Do not add page-specific breakpoints unless a verified layout issue requires them.

- Desktop: use multi-column hero and card layouts where content supports them.
- Tablet: reduce navigation density and card columns.
- Mobile: use the accessible menu, single-column hero, and stacked actions/cards.
- Keep tap targets readable and avoid horizontal overflow.

## 8. Accessibility and motion

- Preserve RTL language metadata and logical reading order.
- Give navigation landmarks accessible labels.
- Use semantic headings in order and meaningful link text.
- Keep keyboard focus visible; do not remove `:focus-visible`.
- Keep the skip link.
- Ensure decorative graphics are hidden from assistive technology or have a useful accessible description when meaningful.
- Preserve the `prefers-reduced-motion: reduce` rules in the canonical stylesheet.
- Do not communicate status through color alone; retain visible status text.

## 9. Safe page creation workflow

1. Copy `metatya-corporate-page-template.html` to a new page under `docs/`.
2. Fix relative asset paths after copying (remove the leading `../` from stylesheet and script paths).
3. Replace all sample titles, copy, status labels, card text, and CTA destinations.
4. Remove unused sections rather than leaving empty placeholders.
5. Verify all IDs, local links, external links, responsive behavior, and accessibility.
6. Run `node scripts/test-metatya-company.mjs`.
7. Review the rendered page at desktop and mobile widths.
8. Submit the page through a feature branch and pull request. Do not merge or publish without approval.

## 10. Change control

The homepage and its visual identity are the reference implementation. Any change to the palette, typography, core spacing, component geometry, animation behavior, or global navigation requires explicit approval before changing the canonical CSS or homepage. Product-specific content changes do not authorize global visual changes.
