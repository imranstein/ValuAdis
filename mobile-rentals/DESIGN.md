# Design System: ValuAdis Rent

The consumer-facing companion to the ValuAdis civic ledger. Where the admin web is a
dense green-charcoal operator console, this app is its warm, public-facing sibling: a
citizen holds it one-handed, in daylight, deciding where to live or whether to trust a
price. It must feel like a trustworthy government service that a designer actually loved.

This file is the single source of truth for the app's visual language. Screens are built
to it, not around it.

## 1. Visual Theme & Atmosphere

**Warm civic paper, not corporate dashboard.** Surfaces are tinted parchment (a warm
off-white with a faint green undertone), never clinical `#fff`. The deep ValuAdis green is
the identity color, used with restraint as the primary action and the "verified" signal.
Gold is the trust accent, reserved for the valuation-certified mark and premium moments,
never as decoration.

- **Density: 4 (Daily-app balanced).** Generous vertical rhythm, room to breathe around the
  hero surfaces (listing cards, band range). Never cockpit-dense.
- **Variance: 5 (offset asymmetric).** Listing cards lead with imagery and an overlaid price;
  detail pages break the uniform-card reflex with a full-bleed header, a summary strip, and a
  distinct band panel.
- **Motion: 6 (fluid, purposeful).** Micro-interactions with intent: hero-to-detail continuity,
  band slider haptic-like feedback, status transitions, staggered list reveals, skeleton loads.
  Never gratuitous, never on rapidly repeated actions.

**Dark mode is first-class**, not an afterthought. It derives from the admin shell's dark
green-charcoal (`#131f18` family): a renter checking listings at night gets a calm, low-glare
surface, gold and light-green accents lifting off near-black green.

## 2. Color Palette & Roles

All values are OKLCH-considered hex derived from `frontend/design-tokens.json` (civic-ledger),
warmed for consumer surfaces. Neutrals are tinted toward the brand green, never pure black/white.

### Light (default — daylight use)
- **Canvas** `#F6F3EA` — app background, warm parchment
- **Surface** `#FCFAF3` — cards, sheets, elevated fills
- **Surface Sunken** `#EEEADD` — recessed wells, skeleton base, input fill
- **Ink** `#1B231D` — primary text (green-tinted charcoal, never `#000`)
- **Ink Secondary** `#39443B` — subheads, body
- **Ink Muted** `#5C665D` — metadata, captions
- **Border** `#DED8C6` / **Border Strong** `#C2BBA4` — 1px structural lines
- **Green (Primary)** `#235C43` — primary CTA, verified/published, active nav
- **Green Deep** `#163C2B` — pressed primary, headings on light
- **Green Light** `#5C8A70` — secondary fills, in-band track
- **Green Soft** `#DFE8DD` — tonal chips, success wash
- **Gold (Accent)** `#8A5F14` — certified mark text, premium; **Gold Bright** `#C79A3E` — on-dark gold
- **Gold Wash** `#FAF4E4` — certified badge background

### Dark (night use — derived from admin shell)
- **Canvas** `#101A14` — near-black green
- **Surface** `#16241B` (raised `#1C2B21`, active `#23392C`)
- **Ink** `#F1EEE0` / **Secondary** `#C3CFC5` / **Muted** `#9DB0A0`
- **Border** `#26382C` / strong `#31473A`
- **Green** `#5C8A70` (lifts off dark) / **Green Soft** `#23392C`
- **Gold** `#D3A94C`

### Semantic (both themes)
- **Success** = Green family. **Warning** `#8A5F14`/gold. **Danger** `#9B2F2F` (light) / `#E08A8A` (dark).
- Status pills map to muted tonal washes, never saturated blocks: pending (gold wash),
  published/accepted (green soft), rejected/withdrawn (neutral/danger wash).

**Banned:** pure `#000`/`#fff`, neon/glow shadows, purple/blue "AI" gradients, gradient text,
side-stripe accent borders, oversaturated fills.

## 3. Typography

Roles mirror the civic-ledger contract. Loaded via `google_fonts` (cached; degrades to
system if offline).

- **Serif display — Cormorant Garamond.** Brand moments ONLY: welcome/onboarding, the app
  wordmark, the rent-index headline, empty-state headlines. Large, tracked-tight, weight 500–600.
  This is the single serif; it carries the "official register" gravitas.
- **Body / UI — DM Sans.** Everything functional: nav, labels, buttons, list text, forms.
  Hierarchy by weight (400/500/600/700) and scale, ratio ≥1.25 between steps. Body ≤ ~40em line.
- **Mono — JetBrains Mono.** Ledger figures: ETB rent amounts, band bounds, contract numbers
  (`AA-RNT-2026-000123`), Fayda IDs, dates in registry contexts. Money is mono, always.

Type scale (logical px): Display 34/28 · Title 22 · Headline 18 · Body 15 · Label 13 · Caption 11.

## 4. Component Behaviors

- **Buttons.** Filled green primary; ghost/tonal secondary; text tertiary. Press = `scale(0.97)`
  over 120ms ease-out-quart with subtle opacity dip. 44px min height. No glow. One primary per view.
- **Listing card (hero surface).** Photography-forward: a 16:10 image zone at the top. Because the
  public API exposes no photos yet, the zone renders an honest branded placeholder — a deterministic
  green→gold tonal gradient keyed to the listing id with a property-type glyph and a small "Photo
  pending" note — never a stock photo posing as the real unit. Rent (mono) overlays bottom-left;
  the gold **Certified** mark sits top-right. Below: address, sub-city, a compact bed/bath/area
  meta row, and the **band range bar**.
- **Band range bar (signature element).** A horizontal track from band-min to band-max with the
  suggested rent marked, both bounds labeled in mono ETB. On the apply sheet it becomes an
  interactive slider clamped to `[band_min, band_max]` with live in/out-of-band validation and a
  value bubble. This is the product's core honesty gesture, visualized.
- **Certified badge.** Gold wash pill, shield/seal glyph, "Valuation Certified". Real signal
  (`has_valuation_certificate`), never shown when false.
- **Status pill.** Tonal wash + dot + label. Consistent mapping across applications, listings,
  contracts.
- **Inputs.** Label above, helper/error below. Filled sunken surface, 1px border, green focus ring.
  Sub-city and property fields are selects with real Addis sub-city values (Bole, Yeka pilot first).
- **Loaders.** Skeleton shimmer matching the real layout (card silhouettes, list rows). No spinners
  for content; a small progress indicator only for in-flight actions (apply, submit).
- **Empty / honest states.** Composed, serif-headline states for: no listings match, no data for an
  index district (small-sample suppression is honest, not hidden), no applications yet,
  owner-verification-pending (explains what happens next), and offline. Never a bare "No data".

## 5. Layout Principles

- Single column, mobile-first; nothing overflows horizontally. Max content measure respected on
  tablets via centered constraint.
- Vary spacing for rhythm (8/12/16/24/32). Not the same padding everywhere.
- Cards only where elevation earns it (listings, contract summaries). No nested cards. Section
  dividers and negative space over card-in-card.
- Role-scoped bottom navigation: renters get Browse / Applications / Index / Profile; owners get
  Listings / Applications / Contracts / Profile. The shell is one component, the tabs are data.
- Full-height sheets use safe-area insets; the apply sheet is a draggable bottom sheet, not a modal
  reflex.

## 6. Motion & Interaction

Curves (Flutter `Cubic`): `easeOutQuart (0.25,1,0.5,1)`, `easeOutQuint (0.22,1,0.36,1)`,
`easeOutExpo (0.16,1,0.3,1)`. No bounce, no elastic. Animate transform/opacity only.

- **Hero moment:** listing image + price share a `Hero` tag from card to detail; detail content
  fades/slides up (easeOutQuint, ~360ms).
- **Feedback:** every pressable scales to 0.97 (120ms). Apply slider snaps and pulses its value
  bubble as it crosses band bounds.
- **Transitions:** status changes cross-fade the pill; list items stagger in (40–60ms steps, capped).
  Skeleton→content cross-fades with a faint blur bridge.
- **Durations:** feedback 100–160ms, sheets/nav 200–320ms, hero ~360ms. All UI motion < 400ms.
- **Respect `prefers-reduced-motion`** (`MediaQuery.disableAnimations`): drop movement, keep opacity
  fades that aid comprehension. Provide non-animated fallbacks.

## 7. Anti-Patterns (Banned)

- No emojis in UI. No pure `#000`/`#fff`. No neon/outer-glow shadows. No gradient text.
- No side-stripe accent borders. No identical 3-up card grids. No modal-first thinking.
- No fake/stock photos posing as real listing units, no invented owner names, no fabricated metrics
  or round-number stats. Honest empty/pending/offline states everywhere.
- No `ease-in` on entrances, no `transition: all` equivalents, no animating layout properties.
- No AI-copy clichés ("Seamless", "Elevate", "Unleash"). No em dashes in copy.
