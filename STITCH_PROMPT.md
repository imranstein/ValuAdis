# STITCH PROMPT: ValuAdis B2G Property Valuation Platform

## PROJECT OVERVIEW
Design a modern, professional B2G (Business-to-Government) GovTech SaaS platform for Ethiopian licensed property and vehicle valuers. The platform enables digital property assessments compliant with Proclamation 1365/2025, with offline-first capability, real-time GIS mapping, and compliance certificate generation.

**Target Users**: Licensed property valuers, government agencies
**Business Model**: SaaS subscription + per-certificate pricing model
**Key Requirement**: Blend Ethiopian cultural identity with modern professional design

---

## DESIGN SYSTEM

### COLOR PALETTE
- **Primary Green**: #059669 (main), #10b981 (light) — Ethiopian national identity
- **Secondary Indigo**: #4f46e5 — Professional trust & authority
- **Accent Gold**: #f59e0b — Cultural richness & premium feel
- **Neutrals**: #f9fafb (bg), #f3f4f6 (light), #d1d5db (border), #6b7280 (text), #111827 (dark)
- **Semantic Colors**:
  - Success: #10b981
  - Warning: #f59e0b
  - Error: #ef4444
  - Info: #3b82f6

### TYPOGRAPHY
- **Primary Font**: Inter (system fallback: system-ui) — clean, professional
- **Display Font**: Syne (700-800 weight) — bold, modern, distinctive
- **Monospace**: JetBrains Mono — for code snippets, VIN numbers, coordinates
- **Language Support**: Amharic characters with letter-spacing 0.05em for optimal readability

### DESIGN PATTERNS

#### 1. Glassmorphism
- `backdrop-filter: blur(10px)`
- Semi-transparent backgrounds (rgba with 0.8-0.95 opacity)
- Border: 1px solid rgba(255,255,255,0.2)
- Applied to cards, forms, dropdowns, modals

#### 2. Gradient Overlays
- Default: `linear-gradient(135deg, primary to secondary)`
- Card headers: `linear-gradient(135deg, #059669 to #4f46e5)`
- Stat cards: `linear-gradient(180deg, #f9fafb 0%, #f3f4f6 100%)`

#### 3. Modern Cards
- Border-radius: 16px (standard), 20px (hero elements)
- Box-shadow: `0 10px 30px rgba(0,0,0,0.1)`
- Hover state: `transform: translateY(-2px)` with enhanced shadow

#### 4. Button Styling
- Primary: Solid emerald green with gradient overlay
- Hover: Shimmer effect (animated left-to-right highlight)
- Secondary: Outlined with transparent background
- Disabled: 50% opacity, cursor: not-allowed

---

## LANDING PAGE DESIGN

### HERO SECTION
- **Layout**: Full-width (100vh), centered content with asymmetric design
- **Background**: Subtle gradient from #f9fafb → #f3f4f6 with grid pattern overlay (low opacity)
- **Content Split**:
  - **Left (60%)**: Hero text & CTA buttons
    - Headline: "Digital Property Valuation Made Simple" (Syne, 3.5rem, bold)
    - Subheadline: 1.25rem, text-gray-600, 2 sentences max
    - CTA Buttons:
      - Primary: "Start Valuation" (emerald, solid)
      - Secondary: "Watch Demo" (outlined, transparent)
  - **Right (40%)**: Isometric SVG city visualization

### ISOMETRIC 3D CITY VISUALIZATION
- **Technique**: Pure SVG (no Three.js) with isometric projection
- **Buildings**: 3 buildings at 30-60-90° angles
  - **Building 1** (Residential):
    - Base color: #0A3A1E (dark green)
    - Front face: #16542E
    - Side face: #0A3A1E with shadow
    - Roof: #1E6E3A
    - Windows: 4×4 grid, #C8860A (gold) with opacity 0.3-0.9
    - Building height: Takes 25% of SVG width
  - **Building 2** (Commercial): Similar structure, slightly taller
  - **Building 3** (Mixed-use): Tallest, gradient effect

- **Animated Beacon Antenna** (on Building 3):
  - SVG line element with animated circle pulse
  - Pulsing animation: `<animate attributeName="r" values="5;15;5" dur="2s" repeatCount="indefinite"/>`
  - Color: #f59e0b (gold) with fade effect
  - Represents "live valuations"

- **SVG Grain Overlay**:
  - `<filter id="grain-filter"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4"/></filter>`
  - Applied via CSS filter for vintage texture

- **Animation**:
  - Buildings float up/down gently (6s cycle)
  - Beacon pulses continuously
  - Opacity: 0 → 1 on page load (fade-in)

### FLOATING CARDS (over city visualization)
- **Card 1 - Properties**:
  - Position: Absolute, top-left of city
  - Content: "5,000+ Properties Valued"
  - Floating animation: Y-axis ±20px over 6s
  - Delay: 0s

- **Card 2 - Vehicles**:
  - Position: Top-right of city
  - Content: "1,200+ Vehicles Assessed"
  - Floating animation: Y-axis ±20px over 6s
  - Delay: 0.5s

- **Card 3 - Valuations** (highlighted):
  - Position: Bottom-center
  - Content: "Real-Time Compliance" with badge
  - Gradient background: Primary to secondary
  - Floating animation: Y-axis ±25px over 7s
  - Delay: 1s
  - Slightly larger scale, more prominent

### FEATURE SHOWCASE SECTIONS (below hero)
- **Section 1: GIS Mapping**
  - Left: Mock Leaflet map with property boundaries
  - Right: Text describing "Smart GIS Boundary Detection"
  - Checkbox: "Offline-capable"

- **Section 2: Real-Time Compliance**
  - Icon: Certificate badge (SVG)
  - Text: "Proclamation 1365/2025 Compliant"
  - Metrics: "99.9% accuracy"

- **Section 3: Mobile Offline**
  - Icon: Mobile device (SVG)
  - Text: "7-Day Offline Support"
  - Feature list: Download, sync, verify

### CALL-TO-ACTION SECTION
- Centered text
- Primary button: "Get Started Free" with shimmer hover
- Secondary text: "No credit card required"

---

## DASHBOARD DESIGN

### LAYOUT
- **Sidebar Navigation** (fixed, 250px):
  - Logo + app name at top
  - Menu items with icons (Properties, Vehicles, Valuations, Maps, Reports, Settings)
  - User profile dropdown at bottom
  - Smooth transitions on hover (translate 4px)

- **Main Content Area**:
  - Responsive grid layout
  - Mobile: Single column
  - Tablet: 2-column
  - Desktop: 3-4 column grid

### DASHBOARD HEADER
- Page title: "Dashboard" (Syne, 2rem)
- Breadcrumb navigation: "Home > Dashboard"
- Quick action buttons: "New Property", "New Valuation" (side-by-side)
- Date range picker: "Last 30 Days" (default)

### STAT CARDS (Row 1)
- **Layout**: 4 cards in desktop, 2 in tablet, 1 in mobile
- **Card Structure**:
  - Header: Gradient background (135deg, primary to secondary) with icon
  - Icon: Property, vehicle, valuation, or certificate SVG (white, 2rem)
  - Body:
    - Large number (2.5rem, bold)
    - Label below (1rem, gray)
    - Trend indicator: "↑ 12% vs. last month" (green text)
  - Hover effect: `transform: translateY(-2px)`, shadow enhancement
  - Glassmorphism applied to body section

**Cards**:
1. **Total Properties**: "1,234" with property icon
2. **Vehicles Valued**: "567" with vehicle icon
3. **Avg. Confidence**: "94.5%" with badge icon
4. **Pending Certs**: "23" with certificate icon (red badge on corner)

### CHARTS & VISUALIZATIONS (Row 2)
- **Left Column** (50%):
  - **Title**: "Valuations Trend" (last 30 days)
  - **Chart Type**: Line chart (Chart.js)
  - **Colors**: Primary green line, secondary blue as trend
  - **Height**: 300px
  - **Legend**: Bottom

- **Right Column** (50%):
  - **Title**: "Property Type Distribution"
  - **Chart Type**: Donut chart
  - **Colors**: Emerald, Indigo, Gold, muted variants
  - **Center Text**: Total count
  - **Height**: 300px

### PROPERTY INVENTORY TABLE (Row 3, Full Width)
- **Columns**: Address | Municipality | Type | Status | Valuation | Actions
- **Styling**:
  - Header: Gradient background (emerald to indigo)
  - Rows: Alternating white/light-gray background
  - Hover: Row highlight (light green), 2px left border accent
  - Pagination: Bottom, "Show 10/25/50 entries"

- **Status Badges**:
  - "Completed": Green
  - "In Progress": Blue
  - "Pending": Gray

- **Actions**: Edit button, View details icon, Download certificate link
- **Responsive**: Horizontal scroll on mobile, collapsible columns

### WIZARD WORKFLOW INDICATOR (Optional Panel)
- **Title**: "Active Workflows"
- **Cards** (2-3 per row):
  - Property address
  - Current step: "Step 3 of 7: Physical Features"
  - Progress bar: Visual indicator (60% filled, green gradient)
  - Time estimate: "~5 min remaining"
  - Button: "Continue Wizard"

### MAP PANEL (Optional, if pinned)
- **Title**: "Recent Valuations Map"
- **Content**: Leaflet map showing property pins
- **Height**: 400px
- **Pins**: Property locations with valuation markers
- **Zoom**: Auto-fit to all pins

---

## ANIMATIONS & INTERACTIONS

### CSS ANIMATIONS

```css
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

@keyframes slideInUp {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0% { r: 5px; }
  50% { r: 15px; }
  100% { r: 5px; }
}
```

### TIMING & EASING
- **Fast**: 150ms ease (button hovers, icons)
- **Default**: 250ms ease (card transitions, form inputs)
- **Slow**: 350ms ease (page transitions, modals)
- **SVG Animations**: 2-7s for continuous effects

### INTERACTIVE EFFECTS

#### 1. Button Hover
- Primary: Shimmer effect left-to-right (0.5s)
- Scale: 1.02× on hover
- Shadow: Enhanced

#### 2. Card Hover
- Lift: translateY(-2px)
- Shadow expansion: 0 20px 40px (vs. 0 10px 30px)
- Duration: 200ms

#### 3. Form Input Focus
- Border color: Primary green
- Box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1)
- Transition: 150ms

#### 4. Toast Notifications
- Slide in from top-right
- Duration: 0.3s ease-out
- Auto-dismiss after 4s
- Colors: Green (success), Red (error), Blue (info)

#### 5. Modal Dialogs
- Backdrop: Blur + semi-transparent dark overlay
- Content: Scale from 0.9 to 1.0 (250ms cubic-bezier)
- Dismiss: Reverse animation

#### 6. Parallax Floating
- Hero floating cards: Different Y offsets & delays
- Creates depth effect
- Continuous loop (infinite animation)

### LOADING STATES
- Spinner: Rotating SVG circle (1s linear)
- Skeleton screens: Pulsing placeholder cards
- Progress bars: Animated width change (smooth transition)

---

## RESPONSIVE DESIGN

### BREAKPOINTS
- **Mobile**: < 480px
- **Tablet**: 481px - 768px
- **Desktop**: 769px - 1024px
- **Large**: > 1024px

### MOBILE OPTIMIZATIONS
- Sidebar: Collapsible hamburger menu
- Dashboard: Stat cards stack vertically
- Charts: Full width, reduced height
- Tables: Horizontal scroll with sticky first column
- Landing page: Single-column hero (city visualization above text)
- Buttons: Full width (except inline actions)
- Font sizes: Scaled down (headlines 2rem instead of 3.5rem)

---

## TECHNICAL NOTES FOR IMPLEMENTATION

### TECH STACK
- **Frontend**: Vue.js 3 (Composition API), Nuxt.js 3
- **UI Framework**: PrimeVue 3.50+ (components)
- **Styling**: Tailwind CSS 3.4 + Custom CSS
- **Maps**: Leaflet.js + OpenStreetMap
- **Charts**: Chart.js
- **SVG**: Pure SVG for isometric graphics (no Three.js for performance)
- **Animations**: CSS-based (GPU-optimized) + Vue transitions

### PERFORMANCE
- Use CSS animations over JavaScript (better performance)
- Lazy-load chart libraries
- Optimize SVG file sizes (< 50KB for landing page)
- Defer non-critical animations on mobile

### ACCESSIBILITY
- ARIA labels on interactive elements
- Semantic HTML structure
- Color contrast: WCAG AA minimum
- Keyboard navigation support (Tab through buttons, forms)
- Amharic character support with proper fonts

---

## ADDITIONAL ASSETS TO CREATE

### SVG ICONS (2rem × 2rem)
- **Property types**: House, Apartment, Commercial, Industrial
- **Vehicles**: Car, Truck, Bus, Motorcycle
- **Status**: Pending, In Progress, Completed, Error
- **Actions**: Edit, Delete, Download, Share

### ILLUSTRATIONS
- Empty state graphics (no data found)
- Error page illustrations (404, 500)
- Success animations (certificate validation)

### PATTERNS
- Background grid (subtle, low opacity)
- Grain texture overlay (SVG or image)

---

## SUMMARY

This comprehensive prompt provides everything needed for designing the ValuAdis B2G property valuation platform. The design balances Ethiopian cultural identity with modern professional aesthetics, incorporating glassmorphism, gradient overlays, and smooth CSS-based animations. The isometric SVG city visualization on the landing page creates a unique visual identity, while the dashboard provides clear data visualization and workflow management for valuers conducting compliant property and vehicle assessments.
