# Design

> Captured from the existing single-file implementation
> (`4138-theory-corrector.html`). This is the current visual system, not an
> aspirational one. Regenerate with `/impeccable document` after significant UI
> changes.

## Theme

A professional legal/advocacy tool with a deep-navy and gold identity. Light working
surface (cool slate gradient) with white cards; the navy carries authority in the
chrome (header, document preview header) and gold is the single deliberate accent for
primary actions and active state. Serif typesetting in the document preview evokes a
formal legal filing; the working UI uses a clean humanist sans. The register is
**product** — design serves the practitioner's task and the fidelity of the generated
filing.

## Color

Defined as CSS custom properties on `:root`. (sRGB hex as authored; migrate to OKLCH
if the palette is reworked.)

**Navy (authority / chrome / primary text)**
- `--navy-900` `#0a1628` — header gradient start, preview header, document headings
- `--navy-800` `#1a2744` — body text, primary buttons (nav-next), citation selected
- `--navy-700` `#2a3a5a`
- `--navy-600` `#3d4f6f`

**Slate (working surface / neutrals)**
- `--slate-100` `#f1f5f9` — body bg gradient start, inset panels
- `--slate-200` `#e2e8f0` — body bg gradient end, borders, secondary buttons
- `--slate-300` `#cbd5e1` — input borders, progress track
- `--slate-400` `#94a3b8` — placeholder text, empty-state icon
- `--slate-500` `#64748b` — help text, muted labels

**Gold (single accent — primary action + active state)**
- `--gold-400` `#d4a853` — primary buttons, active step, focus ring, logo mark
- `--gold-500` `#b8923d` — hover
- `--gold-600` `#9a7a30` — text on tinted gold backgrounds

**Status**
- `--success` `#16a34a` · `--warning` `#ca8a04` · `--error` `#dc2626` (also the
  required-field asterisk and destructive "Clear All")
- `--white` `#ffffff`

**Surfaces**
- Body: `linear-gradient(135deg, slate-100, slate-200)`
- Cards/panels: white, elevated with layered shadows
- Header & preview header: `linear-gradient(135deg, navy-900, navy-800)`

Contrast note (per PRODUCT.md, no formal target, but baseline matters): help text in
`--slate-500` on white passes for normal text; `--slate-400` placeholders are the
likeliest weak spot — keep placeholder contrast in mind if accessibility is formalized.

## Typography

Three families, paired on a real contrast axis (serif + two distinct sans/mono):
- `--font-serif`: **Source Serif 4** (Georgia fallback) — document preview body and
  headings; signals a formal legal statement.
- `--font-sans`: **IBM Plex Sans** — all working UI (labels, inputs, buttons, nav).
- `--font-mono`: **IBM Plex Mono** — legal citations and file/SSN-style values.

Base `16px`, line-height `1.6` (UI) and `1.75` (document preview). Section headings
~`1.375rem` serif 600; logo title `1.5rem` serif 600 with `-0.02em` tracking. Loaded
from Google Fonts via `<link preconnect>` (the tool's only external resource).

## Layout & Spacing

- App shell: sticky navy header → privacy-notice bar → two-column `main-container`
  (`grid-template-columns: 1fr 1fr`, `gap: 2rem`, `max-width: 1400px`).
- Left column: form panel with a 5-step progress indicator (Claim Info → Condition →
  VSR Request → Evidence → Questions); one section visible at a time.
- Right column: sticky live document preview (`position: sticky; top: 100px`).
- Responsive: collapses to a single column at `≤1024px`; form rows collapse at
  `≤600px`; header stacks at `≤768px`.
- Radii scale: inputs/buttons `6px`, inset entries `8px`, panels `12px`, pills `20px`,
  step/letter badges `50%`.
- Shadow scale: `--shadow-sm/md/lg/xl`, tinted with navy alpha rather than pure black.

## Components

- **Buttons**: `.btn` base; `.btn-primary` (gold), `.btn-secondary` (translucent on
  navy), `.btn-danger` (error red), nav variants (`.btn-nav-prev` slate /
  `.btn-nav-next` navy). Hover lifts primary by `translateY(-1px)`.
- **Inputs / selects / textareas**: full-width, `1.5px` slate border, gold focus ring
  (`box-shadow: 0 0 0 3px rgba(212,168,83,.15)`); custom SVG chevron on selects.
- **Progress steps**: numbered circles with connecting track; active = gold halo,
  completed = success green.
- **Citation tags**: mono pills, toggle to navy-filled when selected.
- **Evidence entries / question boxes**: slate-100 inset blocks with remove controls.
- **Document preview**: serif "paper", `.legal-cite` (mono chip) and `.placeholder`
  (dashed gold) inline styles; print stylesheet hides all chrome and prints only the
  document.
- **Feedback**: toast (`.copy-notification`), `.alert-info` / `.alert-success`, and a
  confirm `.modal-overlay` for destructive Clear All.

## Motion

- `fadeIn` (opacity + 10px rise) on section change; `0.2s ease` on interactive hovers;
  `0.3s ease` on modal/toast. Curves are simple eases — no bounce/elastic.
- `prefers-reduced-motion`: **not yet handled** — a known gap. Add a reduced-motion
  fallback (crossfade/instant) when the UI is next touched.

## Iconography

Inline stroke SVGs (1.5–2px), `currentColor`, ~16px in UI / 64px for the empty state.
No icon font, no external icon dependency.

## Constraints / Conventions

- **Single-file, no-build.** Everything (HTML/CSS/JS) lives in
  `4138-theory-corrector.html`. Preserve this — no bundler, no framework, runs from
  `file://`.
- **Local-only & private.** No data leaves the browser; the only network calls are the
  Google Fonts stylesheet. Keep it that way (see PRODUCT.md principle 2).
- State persists to `localStorage` under the key `va4138Draft`.
