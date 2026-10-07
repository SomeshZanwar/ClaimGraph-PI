# ClaimGraph PI Design System

## 1. Design Direction

ClaimGraph PI should feel like a serious investigation and operational analytics product.

The visual system should communicate:

- precision
- evidence
- seriousness
- readability
- operational clarity

It should not resemble a generic AI startup landing page, consumer wellness app, crypto dashboard, or template marketplace dashboard.

## 2. Theme

Primary theme: dark-neutral operational interface with warm off-white content surfaces where needed.

Avoid pure white and pure black as dominant backgrounds.

### Base palette

- App background: #16191D
- Elevated surface: #1D2126
- Secondary surface: #24292F
- Light content surface: #F3F0E8
- Primary text on dark: #F2EFE7
- Secondary text on dark: #B5BAC1
- Primary text on light: #202327
- Muted text on light: #626A73
- Border dark: #343A40
- Border light: #D2CEC4

### Primary CTA

Single CTA color:

- CTA: #A65304
- CTA hover: #884303
- CTA text: #FFF8ED

No other high-saturation color should compete with the CTA.

### Semantic colors

Use restrained semantic colors only where meaning requires them:

- Critical: #B94A48
- High risk: #C86B32
- Warning: #B08A2E
- Informational: #4D7C8A
- Success/cleared: #4E7A5B
- Neutral: #6B727A

Risk communication must use label + iconography or text, not color alone.

## 3. Typography

Avoid Inter, Geist, and Space Grotesk.

Preferred family:

- UI and body: IBM Plex Sans
- Technical/tabular values: IBM Plex Mono

Fallbacks:

- sans-serif system fallback
- monospace system fallback

### Type scale

- Display: 42/48, 600
- H1: 34/40, 600
- H2: 26/32, 600
- H3: 20/26, 600
- Body large: 17/26, 400
- Body: 15/23, 400
- Small: 13/19, 400
- Label: 12/16, 600 with limited letter spacing
- Table values: 14/20

Avoid oversized marketing typography.

## 4. Layout

### Desktop

- persistent left navigation only when application density justifies it
- max readable content width for narrative pages
- investigator workspace may use wider bounded layouts
- tables and graph views may use full available width
- primary actions remain visible without excessive sticky UI

### Tablet

- navigation collapses
- two-column investigative layouts collapse intentionally
- no forced desktop-width tables
- filters may move to drawers or stacked regions

### Mobile

- dedicated mobile navigation
- one primary content column
- tables become responsive lists, horizontal-safe grids, or selectively scrollable data regions only when unavoidable
- no page-level horizontal scrolling
- graphs use constrained viewport with clear zoom controls
- buttons meet touch-target requirements

## 5. Spacing

Use a consistent spacing scale:

- 4
- 8
- 12
- 16
- 24
- 32
- 48
- 64

Dense analytical screens may use tighter internal spacing, but page structure should remain calm.

## 6. Corners and Borders

Avoid overly soft generic SaaS cards.

Recommended:

- 2px to 6px radius depending on component
- many containers may use square or near-square corners
- use borders and spacing rather than shadows

No drop shadows.

## 7. Navigation

Application navigation should prioritize workflows:

- Queue
- Providers
- Network
- Analytics
- Support

Administrative navigation appears only for authorized roles.

Rules:

- logo is clickable
- active location is obvious
- no unused links
- mobile menu required
- navigation labels are concrete
- no decorative icon-only navigation unless accessible labels exist

## 8. Page Patterns

### Investigation Queue

Primary content:

- case ID
- provider
- claim/payment exposure
- risk level
- strongest signal
- age/status
- assigned investigator

Filters should be functional, not decorative.

Do not present queue rows as oversized cards.

### Case Detail

Suggested structure:

1. case identity and status
2. financial exposure
3. evidence summary
4. deterministic signals
5. peer comparison
6. model signal
7. graph/network signals
8. source lineage
9. investigation notes
10. audit history

Evidence source types must remain visually distinct.

### Provider Profile

Show:

- provider identity
- peer group
- volume
- charge/utilization distribution
- top procedures
- peer deviations
- historical risk signals
- linked cases
- network relationships

### Graph Explorer

Graph is analytical, not decorative.

Requirements:

- legend
- node/edge counts
- filters
- relationship detail panel
- reset view
- bounded default expansion
- keyboard-accessible controls where technically practical
- explanatory text for graph metrics

### Public Product Page

Avoid generic SaaS landing-page formulas.

Preferred structure:

- concise product statement
- actual investigation workflow
- real interface screenshots or live demo entry
- architecture/data methodology
- limitations and responsible-use statement
- links to documentation and repository

No fake testimonials, fake logos, fake customer counts, or decorative pricing.

## 9. Forms

- labels always visible
- placeholder text is supplemental only
- inline field validation
- server errors shown near the relevant action
- disabled state only when reason is understandable
- success messages after mutations
- no silent submission
- password fields support appropriate visibility toggle if implemented
- required fields explicitly indicated

## 10. Buttons

Button hierarchy:

### Primary
Single CTA color.

Use for one dominant action per local context.

### Secondary
Neutral border or surface treatment.

### Tertiary
Text-style action for low-priority interactions.

### Destructive
Reserved semantic treatment, never the primary CTA color.

Rules:

- no gradient buttons
- no pill buttons by default
- no animated arrows
- no excessive hover motion
- no broken or decorative buttons

## 11. Tables

Tables are important to this product.

Requirements:

- readable column hierarchy
- sticky header only where useful
- sortable columns only when sorting actually works
- pagination
- empty states
- loading state
- error state
- accessible row actions
- responsive adaptation
- numeric alignment
- no unnecessary zebra rainbow coloring

## 12. Charts

Charts must answer a specific analytical question.

Use muted categorical palettes.

Avoid:

- rainbow scales unless mathematically necessary
- 3D charts
- chart junk
- gradients
- decorative area fills
- misleading axes

Every chart requires:

- clear title
- units
- readable labels
- accessible text alternative or contextual summary
- source/time-period context where relevant

## 13. Graph Visualization

Node colors must be semantic by entity type and restrained.

Example mapping:

- provider: muted rust
- member: muted blue-gray
- facility: muted green-gray
- address: muted ochre
- procedure: muted steel

Selection may use the primary CTA color.

Do not use neon graph styling.

## 14. Icons

Use icons sparingly.

Do not build the UI around Lucide-style icon decoration.

Prefer:

- text labels
- small inline SVGs where an icon materially improves comprehension
- consistent stroke/weight if custom icons are needed

No sparkle icons.

## 15. Loading States

Do not default to skeleton loaders.

Preferred:

- fast data fetch
- small progress indicator
- text status for long-running operations
- explicit job progress where background work is meaningful

## 16. Motion

Motion is optional.

If used:

- brief
- functional
- reduced-motion aware

Avoid:

- hover animation for decoration
- animated arrows
- floating elements
- radial/orb motion
- liquid effects

## 17. Accessibility

Target WCAG 2.2 AA principles.

Required:

- sufficient contrast
- semantic HTML
- logical tab order
- visible focus
- keyboard-operable controls
- form labels
- error association
- non-color-only status communication
- responsive text
- descriptive page titles

## 18. Public-Site SEO Presentation

Every public page must have:

- meaningful title
- meaningful meta description
- single H1
- proper heading hierarchy
- canonical URL where applicable
- social preview metadata
- favicon
- alt text
- internal links

## 19. Legal and Support Pages

Legal pages must use the same visual system as the main product.

Required:

- Privacy Policy
- Terms of Service
- Contact/Support
- Bug Report

Cookie controls appear only if required by the configured tracking/consent behavior.

## 20. Custom 404

The 404 page should:

- clearly state the page was not found
- provide a route back to the product
- provide a route to the investigation queue for authenticated users
- preserve the main navigation where appropriate
- avoid jokes, emojis, or gimmicks

## 21. Images

- compress before shipping
- use modern web formats where appropriate
- size images for actual display
- meaningful alt text
- no stock imagery unless it adds genuine explanatory value
- product screenshots must depict the real product
- social preview image should use the product's actual visual identity

## 22. Responsive QA Matrix

Every major page must be checked at representative widths for:

- mobile
- tablet
- laptop
- desktop

Required QA:

- no page horizontal overflow
- no clipped controls
- no hidden primary actions
- readable tables
- usable graph controls
- correct mobile navigation
- usable forms
- footer integrity
