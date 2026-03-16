<template>
  <div class="landing">

    <!-- SVG Grain filter (hidden) -->
    <svg style="position:fixed;width:0;height:0;overflow:hidden" aria-hidden="true">
      <defs>
        <filter id="grain-filter">
          <feTurbulence type="fractalNoise" baseFrequency="0.72" numOctaves="4" stitchTiles="stitch"/>
          <feColorMatrix type="saturate" values="0"/>
        </filter>
      </defs>
    </svg>
    <div class="grain-overlay" aria-hidden="true"></div>

    <!-- ═══ NAV ═══ -->
    <nav class="nav" :class="{ 'nav--solid': isScrolled }">
      <div class="container nav-inner">
        <NuxtLink to="/" class="logo">
          <div class="logo-mark">V</div>
          <div class="logo-text">
            <span class="logo-name">ValuAdis</span>
            <span class="logo-sub">Property Intelligence</span>
          </div>
        </NuxtLink>
        <div class="nav-links">
          <a href="#capabilities">Capabilities</a>
          <a href="#solutions">Solutions</a>
          <a href="#compliance">Compliance</a>
        </div>
        <NuxtLink to="/login" class="nav-cta">Get Started →</NuxtLink>
      </div>
    </nav>

    <!-- ═══ HERO ═══ -->
    <section class="hero">
      <div class="hero-bg-number" aria-hidden="true">2,400</div>
      <div class="hero-gold-circle c1" aria-hidden="true"></div>
      <div class="hero-gold-circle c2" aria-hidden="true"></div>

      <div class="container hero-layout">
        <!-- Left: Copy -->
        <div class="hero-copy">
          <div class="eyebrow">
            <span class="eyebrow-dot"></span>
            Ethiopian Property Intelligence Platform
          </div>
          <h1>
            <span class="hl hl-1">Property</span>
            <span class="hl hl-2"><em>Valuation.</em></span>
            <span class="hl hl-3">Elevated.</span>
          </h1>
          <p class="hero-desc">
            AI-powered valuations for properties and vehicles across Ethiopia.
            Proclamation 1365/2025 compliant. Audit-ready. Real-time.
          </p>
          <div class="hero-actions">
            <NuxtLink to="/login" class="btn-primary">Start Valuing</NuxtLink>
            <a href="#capabilities" class="btn-ghost">Explore Platform</a>
          </div>
          <div class="hero-stats">
            <div class="hs">
              <span class="hs-val">2,400+</span>
              <span class="hs-lbl">Properties Valued</span>
            </div>
            <div class="hs-div"></div>
            <div class="hs">
              <span class="hs-val">12</span>
              <span class="hs-lbl">Cities Covered</span>
            </div>
            <div class="hs-div"></div>
            <div class="hs">
              <span class="hs-val">100%</span>
              <span class="hs-lbl">Compliance Rate</span>
            </div>
          </div>
        </div>

        <!-- Right: 3D Visual -->
        <div class="hero-visual">
          <!-- Isometric SVG City -->
          <div class="iso-scene">
            <svg class="city-svg" viewBox="0 0 300 360" xmlns="http://www.w3.org/2000/svg">
              <!-- Ground shadow -->
              <ellipse cx="155" cy="332" rx="130" ry="18" fill="rgba(13,40,24,0.1)"/>

              <!-- Building 3 — back left, short -->
              <polygon points="42,248 84,270 84,190 42,168" fill="#0A3A1E"/>
              <polygon points="84,270 106,259 106,179 84,190" fill="#16542E"/>
              <polygon points="42,168 84,190 106,179 64,157" fill="#1E6E3A"/>
              <rect x="48" y="174" width="7" height="9" fill="#C8860A" opacity="0.6"/>
              <rect x="60" y="174" width="7" height="9" fill="#C8860A" opacity="0.3"/>
              <rect x="72" y="174" width="7" height="9" fill="#C8860A" opacity="0.8"/>
              <rect x="48" y="190" width="7" height="9" fill="#C8860A" opacity="0.4"/>
              <rect x="60" y="190" width="7" height="9" fill="#C8860A" opacity="0.7"/>
              <rect x="72" y="190" width="7" height="9" fill="#C8860A" opacity="0.5"/>
              <rect x="48" y="206" width="7" height="9" fill="#C8860A" opacity="0.9"/>
              <rect x="60" y="206" width="7" height="9" fill="#C8860A" opacity="0.3"/>
              <rect x="72" y="206" width="7" height="9" fill="#C8860A" opacity="0.6"/>
              <rect x="48" y="222" width="7" height="9" fill="#C8860A" opacity="0.5"/>
              <rect x="60" y="222" width="7" height="9" fill="#C8860A" opacity="0.8"/>
              <rect x="72" y="222" width="7" height="9" fill="#C8860A" opacity="0.4"/>

              <!-- Building 2 — back right, medium -->
              <polygon points="178,272 224,295 224,188 178,165" fill="#0A3A1E"/>
              <polygon points="224,295 250,282 250,175 224,188" fill="#16542E"/>
              <polygon points="178,165 224,188 250,175 204,152" fill="#1E6E3A"/>
              <rect x="184" y="173" width="7" height="10" fill="#C8860A" opacity="0.7"/>
              <rect x="197" y="173" width="7" height="10" fill="#C8860A" opacity="0.4"/>
              <rect x="210" y="173" width="7" height="10" fill="#C8860A" opacity="0.9"/>
              <rect x="184" y="191" width="7" height="10" fill="#C8860A" opacity="0.5"/>
              <rect x="197" y="191" width="7" height="10" fill="#C8860A" opacity="0.8"/>
              <rect x="210" y="191" width="7" height="10" fill="#C8860A" opacity="0.3"/>
              <rect x="184" y="209" width="7" height="10" fill="#C8860A" opacity="0.9"/>
              <rect x="197" y="209" width="7" height="10" fill="#C8860A" opacity="0.6"/>
              <rect x="210" y="209" width="7" height="10" fill="#C8860A" opacity="0.4"/>
              <rect x="184" y="227" width="7" height="10" fill="#C8860A" opacity="0.7"/>
              <rect x="197" y="227" width="7" height="10" fill="#C8860A" opacity="0.3"/>
              <rect x="210" y="227" width="7" height="10" fill="#C8860A" opacity="0.8"/>
              <rect x="184" y="245" width="7" height="10" fill="#C8860A" opacity="0.5"/>
              <rect x="197" y="245" width="7" height="10" fill="#C8860A" opacity="0.9"/>
              <rect x="210" y="245" width="7" height="10" fill="#C8860A" opacity="0.4"/>

              <!-- Main building — tallest, center-front -->
              <!-- Front face -->
              <polygon points="88,305 160,340 160,110 88,75" fill="#0D2818"/>
              <!-- Right face -->
              <polygon points="160,340 214,315 214,85 160,110" fill="#1A4A30"/>
              <!-- Top face -->
              <polygon points="88,75 160,110 214,85 142,50" fill="#2A6A45"/>

              <!-- Main building windows — front face (clip) -->
              <clipPath id="mf">
                <polygon points="88,305 160,340 160,110 88,75"/>
              </clipPath>
              <g clip-path="url(#mf)">
                <rect x="95"  y="92"  width="10" height="13" fill="#C8860A" opacity="0.8"/>
                <rect x="111" y="92"  width="10" height="13" fill="#C8860A" opacity="0.4"/>
                <rect x="127" y="92"  width="10" height="13" fill="#C8860A" opacity="0.9"/>
                <rect x="143" y="92"  width="10" height="13" fill="#C8860A" opacity="0.6"/>
                <rect x="95"  y="114" width="10" height="13" fill="#C8860A" opacity="0.5"/>
                <rect x="111" y="114" width="10" height="13" fill="#C8860A" opacity="0.9"/>
                <rect x="127" y="114" width="10" height="13" fill="#C8860A" opacity="0.3"/>
                <rect x="143" y="114" width="10" height="13" fill="#C8860A" opacity="0.7"/>
                <rect x="95"  y="136" width="10" height="13" fill="#C8860A" opacity="0.6"/>
                <rect x="111" y="136" width="10" height="13" fill="#C8860A" opacity="0.4"/>
                <rect x="127" y="136" width="10" height="13" fill="#C8860A" opacity="0.8"/>
                <rect x="143" y="136" width="10" height="13" fill="#C8860A" opacity="0.5"/>
                <rect x="95"  y="158" width="10" height="13" fill="#C8860A" opacity="0.9"/>
                <rect x="111" y="158" width="10" height="13" fill="#C8860A" opacity="0.3"/>
                <rect x="127" y="158" width="10" height="13" fill="#C8860A" opacity="0.7"/>
                <rect x="143" y="158" width="10" height="13" fill="#C8860A" opacity="0.9"/>
                <rect x="95"  y="180" width="10" height="13" fill="#C8860A" opacity="0.4"/>
                <rect x="111" y="180" width="10" height="13" fill="#C8860A" opacity="0.8"/>
                <rect x="127" y="180" width="10" height="13" fill="#C8860A" opacity="0.6"/>
                <rect x="143" y="180" width="10" height="13" fill="#C8860A" opacity="0.3"/>
                <rect x="95"  y="202" width="10" height="13" fill="#C8860A" opacity="0.7"/>
                <rect x="111" y="202" width="10" height="13" fill="#C8860A" opacity="0.5"/>
                <rect x="127" y="202" width="10" height="13" fill="#C8860A" opacity="0.9"/>
                <rect x="143" y="202" width="10" height="13" fill="#C8860A" opacity="0.4"/>
                <rect x="95"  y="224" width="10" height="13" fill="#C8860A" opacity="0.8"/>
                <rect x="111" y="224" width="10" height="13" fill="#C8860A" opacity="0.3"/>
                <rect x="127" y="224" width="10" height="13" fill="#C8860A" opacity="0.6"/>
                <rect x="143" y="224" width="10" height="13" fill="#C8860A" opacity="0.9"/>
                <rect x="95"  y="246" width="10" height="13" fill="#C8860A" opacity="0.5"/>
                <rect x="111" y="246" width="10" height="13" fill="#C8860A" opacity="0.8"/>
                <rect x="127" y="246" width="10" height="13" fill="#C8860A" opacity="0.4"/>
                <rect x="143" y="246" width="10" height="13" fill="#C8860A" opacity="0.7"/>
              </g>

              <!-- Main building windows — right face (clip) -->
              <clipPath id="mr">
                <polygon points="160,340 214,315 214,85 160,110"/>
              </clipPath>
              <g clip-path="url(#mr)">
                <rect x="163" y="122" width="9" height="12" fill="#C8860A" opacity="0.25"/>
                <rect x="177" y="122" width="9" height="12" fill="#C8860A" opacity="0.4"/>
                <rect x="163" y="142" width="9" height="12" fill="#C8860A" opacity="0.35"/>
                <rect x="177" y="142" width="9" height="12" fill="#C8860A" opacity="0.2"/>
                <rect x="163" y="162" width="9" height="12" fill="#C8860A" opacity="0.45"/>
                <rect x="177" y="162" width="9" height="12" fill="#C8860A" opacity="0.3"/>
                <rect x="163" y="182" width="9" height="12" fill="#C8860A" opacity="0.2"/>
                <rect x="177" y="182" width="9" height="12" fill="#C8860A" opacity="0.4"/>
                <rect x="163" y="202" width="9" height="12" fill="#C8860A" opacity="0.3"/>
                <rect x="177" y="202" width="9" height="12" fill="#C8860A" opacity="0.25"/>
              </g>

              <!-- Antenna + beacon -->
              <line x1="142" y1="50" x2="142" y2="20" stroke="#C8860A" stroke-width="1.5" stroke-linecap="round"/>
              <circle cx="142" cy="18" r="3" fill="#C8860A"/>
              <circle cx="142" cy="18" r="7" fill="#C8860A" opacity="0.2">
                <animate attributeName="r" values="5;12;5" dur="2.4s" repeatCount="indefinite"/>
                <animate attributeName="opacity" values="0.3;0;0.3" dur="2.4s" repeatCount="indefinite"/>
              </circle>

              <!-- Gold ground line -->
              <line x1="20" y1="348" x2="280" y2="348" stroke="#C8860A" stroke-width="0.8" opacity="0.35"/>
            </svg>
          </div>

          <!-- Floating valuation card -->
          <div class="float-card val-card">
            <div class="fc-header">
              <span class="fc-tag">Live Valuation</span>
              <span class="fc-live"><span class="live-dot"></span>Active</span>
            </div>
            <div class="fc-address">Bole Sub-City, Addis Ababa</div>
            <div class="fc-value">ETB 4,250,000</div>
            <div class="fc-meta">Residential · 280m² · Grade A</div>
            <div class="fc-bar-row">
              <span>Market Confidence</span>
              <span class="fc-pct">94%</span>
            </div>
            <div class="fc-bar-bg">
              <div class="fc-bar-fill"></div>
            </div>
          </div>

          <!-- Floating vehicle badge -->
          <div class="float-card veh-badge">
            <span class="vb-icon">🚙</span>
            <div class="vb-info">
              <span class="vb-model">LC 200 · 2022</span>
              <span class="vb-val">ETB 3.8M</span>
            </div>
            <span class="vb-check">✓</span>
          </div>
        </div>
      </div>

      <!-- Scroll cue -->
      <div class="scroll-cue" aria-hidden="true">
        <div class="sc-line"></div>
        <span>scroll</span>
      </div>
    </section>

    <!-- ═══ FEATURES ═══ -->
    <section id="capabilities" class="features">
      <div class="container">
        <div class="sec-hd">
          <span class="sec-label">Capabilities</span>
          <h2 class="sec-title rv">Everything to <em>Value with Confidence</em></h2>
          <div class="sec-rule"></div>
        </div>
        <div class="feat-grid">
          <div
            v-for="(f, i) in features"
            :key="f.title"
            class="feat-card rv"
            :style="`--i:${i}`"
          >
            <span class="feat-num">{{ String(i + 1).padStart(2, '0') }}</span>
            <span class="feat-emoji">{{ f.emoji }}</span>
            <h3>{{ f.title }}</h3>
            <p>{{ f.desc }}</p>
            <span class="feat-arrow">→</span>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ SHOWCASE ═══ -->
    <section id="solutions" class="showcase">
      <div class="showcase-bg-text" aria-hidden="true">VALUATE</div>
      <div class="container">
        <div class="sec-hd centered">
          <span class="sec-label">Solutions</span>
          <h2 class="sec-title rv">Built for Every <em>Asset Class</em></h2>
        </div>
        <div class="showcase-grid">

          <!-- Property card -->
          <div class="show-card rv" style="--i:0">
            <div class="show-img-wrap">
              <img
                src="https://images.unsplash.com/photo-1486325212027-8081e485255e?w=640&q=85&fit=crop"
                alt="Modern property in Addis Ababa"
                loading="lazy"
                class="show-img"
              />
              <div class="show-img-overlay">
                <span class="show-type-tag">Real Estate</span>
              </div>
            </div>
            <div class="prop-data-strip">
              <div class="pds-item">
                <span>Est. Value</span>
                <strong>ETB 8.2M</strong>
              </div>
              <div class="pds-item">
                <span>Land Area</span>
                <strong>450m²</strong>
              </div>
              <div class="pds-item">
                <span>Grade</span>
                <span class="grade-badge">Grade A</span>
              </div>
            </div>
            <div class="show-body">
              <h3>Real Estate Valuation</h3>
              <p>Precise valuations for residential and commercial properties across all 12 major Ethiopian cities, with automated grade classification.</p>
              <NuxtLink to="/login" class="show-link">Start valuing →</NuxtLink>
            </div>
          </div>

          <!-- Vehicle card -->
          <div class="show-card rv" style="--i:1">
            <div class="show-img-wrap">
              <img
                src="https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=640&q=85&fit=crop"
                alt="Vehicle valuation — Land Cruiser"
                loading="lazy"
                class="show-img"
              />
              <div class="show-img-overlay">
                <span class="show-type-tag">Vehicles</span>
              </div>
            </div>
            <div class="veh-data-strip">
              <div class="vds-model">Toyota Land Cruiser 200</div>
              <div class="vds-meta">2022 · 45,000 km</div>
              <div class="vds-value">ETB 3,850,000</div>
              <div class="vds-bar-wrap">
                <div class="vds-bar"><div class="vds-fill"></div></div>
                <span>12% depreciation</span>
              </div>
            </div>
            <div class="show-body">
              <h3>Vehicle Valuation</h3>
              <p>Accurate market valuations for all vehicle types with mileage, condition, and Ethiopian customs duty factored in.</p>
              <NuxtLink to="/login" class="show-link">Start valuing →</NuxtLink>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- ═══ COMPLIANCE ═══ -->
    <section id="compliance" class="compliance">
      <div class="comp-glow" aria-hidden="true"></div>
      <div class="container">
        <div class="comp-grid rv">
          <div class="comp-seal">
            <div class="seal-ring r1"></div>
            <div class="seal-ring r2"></div>
            <div class="seal-ring r3"></div>
            <span class="seal-icon">⚖</span>
          </div>
          <div class="comp-body">
            <span class="sec-label" style="color:var(--gold-light)">Regulatory Compliance</span>
            <h2>Proclamation 1365/2025<br><em>Fully Compliant</em></h2>
            <p>Every valuation follows Ethiopian government regulations with complete audit trails, 25% capital gains tax calculation, and zero compliance issues to date.</p>
            <div class="comp-badges">
              <span>✓ Audit Ready</span>
              <span>✓ Tax Compliant</span>
              <span>✓ Proclamation 1365/2025</span>
              <span>✓ Zero Issues</span>
            </div>
          </div>
          <div class="comp-nums">
            <div class="cn">
              <span class="cn-v">25%</span>
              <span class="cn-l">Capital Gains Rate</span>
            </div>
            <div class="cn">
              <span class="cn-v">100%</span>
              <span class="cn-l">Audit Ready</span>
            </div>
            <div class="cn">
              <span class="cn-v">0</span>
              <span class="cn-l">Compliance Issues</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══ CTA ═══ -->
    <section class="cta-sec">
      <div class="cta-ring r1" aria-hidden="true"></div>
      <div class="cta-ring r2" aria-hidden="true"></div>
      <div class="container">
        <div class="cta-inner rv">
          <span class="sec-label">Get Started Today</span>
          <h2>Ready to Elevate<br><em>Your Valuations?</em></h2>
          <p>Join valuation professionals who trust ValuAdis for accuracy, compliance, and speed.</p>
          <NuxtLink to="/login" class="btn-primary btn-lg">Launch ValuAdis →</NuxtLink>
        </div>
      </div>
    </section>

    <!-- ═══ FOOTER ═══ -->
    <footer class="footer">
      <div class="container">
        <div class="foot-top">
          <div class="foot-brand">
            <div class="logo foot-logo">
              <div class="logo-mark gold-mark">V</div>
              <div class="logo-text">
                <span class="logo-name" style="color:white">ValuAdis</span>
                <span class="logo-sub" style="color:rgba(255,255,255,0.4)">Property Intelligence</span>
              </div>
            </div>
            <p>Ethiopian Property Intelligence Platform.<br>Proclamation 1365/2025 compliant.</p>
          </div>
          <div class="foot-nav">
            <div class="fn-col">
              <span class="fn-title">Platform</span>
              <a href="#">Properties</a>
              <a href="#">Vehicles</a>
              <a href="#">Reports</a>
            </div>
            <div class="fn-col">
              <span class="fn-title">Legal</span>
              <a href="#">Compliance</a>
              <a href="#">Privacy</a>
              <a href="#">Terms</a>
            </div>
          </div>
        </div>
        <div class="foot-bottom">
          <span>© 2026 ValuAdis. All rights reserved.</span>
          <span>Addis Ababa, Ethiopia</span>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

definePageMeta({ layout: 'landing', middleware: 'guest' })

const isScrolled = ref(false)

const features = [
  {
    emoji: '🏢',
    title: 'Property Valuation',
    desc: 'AI-assisted residential, commercial, and mixed-use property valuations with full audit trails and spatial context.',
  },
  {
    emoji: '🚗',
    title: 'Vehicle Valuation',
    desc: 'Comprehensive vehicle assessments with market data, depreciation curves, and compliance-ready documentation.',
  },
  {
    emoji: '📋',
    title: 'Audit-Ready Reports',
    desc: 'Generate professional PDF certificates that meet Proclamation 1365/2025 requirements in seconds.',
  },
  {
    emoji: '🗺️',
    title: 'Geographic Intelligence',
    desc: 'Interactive map visualization with heatmaps, spatial analytics, and location-aware pricing models.',
  },
]

function handleScroll() {
  isScrolled.value = window.scrollY > 50
}

function initReveal() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('revealed')
          observer.unobserve(e.target)
        }
      })
    },
    { threshold: 0.12 }
  )
  document.querySelectorAll('.rv').forEach((el) => observer.observe(el))
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  initReveal()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600;1,700&family=Sora:wght@300;400;500;600&display=swap');

/* ══ TOKENS ══ */
:root {
  --cream:        #FAF8F4;
  --cream2:       #F3F0E8;
  --forest:       #0D2818;
  --forest-mid:   #1A4A30;
  --forest-light: #2A6A45;
  --gold:         #C8860A;
  --gold-light:   #E8A020;
  --gold-pale:    #FDF3DC;
  --ink:          #1A1200;
  --muted:        #7A7060;
  --border:       rgba(13, 40, 24, 0.10);
  --border-gold:  rgba(200, 134, 10, 0.25);
  --ease:         cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

/* ══ BASE ══ */
.landing {
  font-family: 'Sora', -apple-system, sans-serif;
  background: var(--cream);
  color: var(--ink);
  overflow-x: hidden;
  position: relative;
}

/* Grain overlay */
.grain-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.55;
  filter: url('#grain-filter');
  background: rgba(120, 100, 60, 0.04);
}

/* ══ CONTAINER ══ */
.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 48px;
}

/* ══ NAV ══ */
.nav {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 200;
  padding: 28px 0;
  transition: padding 0.35s var(--ease), background 0.35s var(--ease), box-shadow 0.35s var(--ease);
}
.nav--solid {
  background: rgba(250, 248, 244, 0.96);
  backdrop-filter: blur(24px);
  border-bottom: 1px solid var(--border);
  padding: 16px 0;
  box-shadow: 0 2px 32px rgba(13, 40, 24, 0.07);
}
.nav-inner {
  display: flex;
  align-items: center;
  gap: 40px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-mark {
  width: 38px; height: 38px;
  background: var(--forest);
  color: var(--cream);
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 22px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  letter-spacing: -0.5px;
  transition: background 0.25s;
}
.nav--solid .logo-mark { background: var(--gold); }
.gold-mark { background: var(--gold) !important; }
.logo-name {
  display: block;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 21px; font-weight: 700;
  color: var(--forest);
  letter-spacing: -0.3px;
  line-height: 1;
}
.logo-sub {
  display: block;
  font-size: 9px; font-weight: 500;
  color: var(--muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-top: 2px;
}
.nav-links {
  display: flex;
  gap: 36px;
  margin-left: auto;
}
.nav-links a {
  text-decoration: none;
  color: var(--muted);
  font-size: 14px; font-weight: 500;
  letter-spacing: 0.02em;
  transition: color 0.2s;
}
.nav-links a:hover { color: var(--forest); }
.nav-cta {
  padding: 10px 24px;
  background: var(--forest);
  color: var(--cream);
  text-decoration: none;
  font-size: 14px; font-weight: 600;
  border-radius: 6px;
  letter-spacing: 0.02em;
  transition: background 0.25s, transform 0.25s, box-shadow 0.25s;
  white-space: nowrap;
}
.nav-cta:hover {
  background: var(--gold);
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(200, 134, 10, 0.3);
}

/* ══ HERO ══ */
.hero {
  min-height: 100vh;
  padding: 130px 0 80px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
  background: var(--cream);
}

.hero-bg-number {
  position: absolute;
  right: -40px; top: 50%;
  transform: translateY(-50%);
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(140px, 18vw, 260px);
  font-weight: 700;
  color: transparent;
  -webkit-text-stroke: 1px rgba(13, 40, 24, 0.055);
  pointer-events: none;
  user-select: none;
  line-height: 1;
  animation: bgNumDrift 18s ease-in-out infinite;
}
@keyframes bgNumDrift {
  0%, 100% { transform: translateY(-50%) translateX(0); }
  50%       { transform: translateY(-52%) translateX(-8px); }
}

.hero-gold-circle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
}
.hero-gold-circle.c1 {
  width: 600px; height: 600px;
  top: -180px; right: -100px;
  background: radial-gradient(circle, rgba(200,134,10,0.08) 0%, transparent 70%);
  animation: circleBreath 8s ease-in-out infinite;
}
.hero-gold-circle.c2 {
  width: 400px; height: 400px;
  bottom: -120px; left: -100px;
  background: radial-gradient(circle, rgba(13,40,24,0.06) 0%, transparent 70%);
  animation: circleBreath 10s ease-in-out infinite reverse;
}
@keyframes circleBreath {
  0%, 100% { transform: scale(1); }
  50%       { transform: scale(1.08); }
}

.hero-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  position: relative;
  z-index: 1;
}

/* Hero copy */
.hero-copy {
  animation: slideUp 0.7s 0.05s ease both;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 11px; font-weight: 600;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 28px;
}
.eyebrow-dot {
  width: 6px; height: 6px;
  background: var(--gold);
  border-radius: 50%;
  animation: dotPulse 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes dotPulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(0.7); }
}

h1 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(58px, 6.5vw, 92px);
  font-weight: 700;
  line-height: 1.0;
  letter-spacing: -0.03em;
  color: var(--forest);
  margin: 0 0 28px;
}
.hl { display: block; }
.hl-1 { animation: slideUp 0.6s 0.1s ease both; }
.hl-2 { animation: slideUp 0.6s 0.2s ease both; }
.hl-2 em { font-style: italic; color: var(--gold); }
.hl-3 {
  animation: slideUp 0.6s 0.3s ease both;
  -webkit-text-stroke: 2px var(--forest);
  color: transparent;
}

.hero-desc {
  font-size: 16px;
  line-height: 1.75;
  color: var(--muted);
  max-width: 440px;
  margin: 0 0 36px;
  animation: slideUp 0.6s 0.35s ease both;
}

.hero-actions {
  display: flex;
  gap: 14px;
  margin-bottom: 52px;
  animation: slideUp 0.6s 0.4s ease both;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 30px;
  background: var(--forest);
  color: var(--cream);
  text-decoration: none;
  font-size: 15px; font-weight: 600;
  border-radius: 6px;
  letter-spacing: 0.01em;
  transition: background 0.3s, transform 0.3s, box-shadow 0.3s;
  position: relative;
  overflow: hidden;
}
.btn-primary::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(200,134,10,0.18), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.btn-primary:hover {
  background: var(--forest-mid);
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(13, 40, 24, 0.28);
}
.btn-primary:hover::after { opacity: 1; }
.btn-primary.btn-lg { padding: 18px 44px; font-size: 17px; }

.btn-ghost {
  display: inline-flex;
  align-items: center;
  padding: 14px 26px;
  color: var(--forest);
  text-decoration: none;
  font-size: 15px; font-weight: 500;
  border: 1.5px solid rgba(13, 40, 24, 0.2);
  border-radius: 6px;
  transition: border-color 0.25s, background 0.25s, color 0.25s;
}
.btn-ghost:hover {
  border-color: var(--forest);
  background: var(--forest);
  color: var(--cream);
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 28px;
  animation: slideUp 0.6s 0.45s ease both;
}
.hs { text-align: left; }
.hs-val {
  display: block;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 34px; font-weight: 700;
  color: var(--forest);
  line-height: 1;
  letter-spacing: -0.02em;
}
.hs-lbl {
  display: block;
  font-size: 11px; font-weight: 500;
  color: var(--muted);
  letter-spacing: 0.04em;
  margin-top: 4px;
}
.hs-div {
  width: 1px; height: 38px;
  background: rgba(13, 40, 24, 0.14);
}

/* Hero visual */
.hero-visual {
  position: relative;
  height: 520px;
  animation: slideUp 0.8s 0.15s ease both;
}

.iso-scene {
  position: absolute;
  top: 0; left: 0; right: 0;
  display: flex;
  justify-content: center;
}
.city-svg {
  width: 300px; height: 360px;
  filter: drop-shadow(0 28px 56px rgba(13,40,24,0.16));
  animation: cityFloat 7s ease-in-out infinite;
}
@keyframes cityFloat {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-18px); }
}

/* Floating cards */
.float-card {
  position: absolute;
  background: white;
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(13,40,24,0.11), 0 4px 16px rgba(13,40,24,0.06);
  border: 1px solid rgba(13,40,24,0.07);
}

.val-card {
  bottom: 50px; left: -30px;
  width: 248px;
  padding: 20px;
  animation: floatA 6s ease-in-out infinite;
}
@keyframes floatA {
  0%, 100% { transform: rotate(-1.5deg) translateY(0); }
  50%       { transform: rotate(-1.5deg) translateY(-10px); }
}
.fc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.fc-tag {
  font-size: 9px; font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
}
.fc-live {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; font-weight: 600;
  color: #059669;
}
.live-dot {
  width: 6px; height: 6px;
  background: #059669;
  border-radius: 50%;
  animation: livePulse 1.6s ease-in-out infinite;
}
@keyframes livePulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(5,150,105,0.5); }
  50%       { box-shadow: 0 0 0 5px rgba(5,150,105,0); }
}
.fc-address { font-size: 12px; color: var(--muted); margin-bottom: 6px; }
.fc-value {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 24px; font-weight: 700;
  color: var(--forest);
  letter-spacing: -0.02em;
  margin-bottom: 4px;
}
.fc-meta { font-size: 11px; color: var(--muted); margin-bottom: 14px; }
.fc-bar-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--muted);
  margin-bottom: 6px;
}
.fc-pct { font-weight: 700; color: var(--forest); }
.fc-bar-bg {
  height: 4px;
  background: var(--cream2);
  border-radius: 2px;
  overflow: hidden;
}
.fc-bar-fill {
  height: 100%; width: 94%;
  background: linear-gradient(90deg, var(--gold), var(--forest-light));
  border-radius: 2px;
  transform-origin: left;
  animation: barLoad 1.8s 0.6s ease both;
}
@keyframes barLoad {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}

.veh-badge {
  top: 40px; right: -16px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  animation: floatB 5.5s ease-in-out infinite;
}
@keyframes floatB {
  0%, 100% { transform: rotate(1.5deg) translateY(0); }
  50%       { transform: rotate(1.5deg) translateY(-12px); }
}
.vb-icon { font-size: 26px; }
.vb-model { display: block; font-size: 12px; font-weight: 700; color: var(--forest); }
.vb-val   { display: block; font-size: 11px; color: var(--muted); margin-top: 2px; }
.vb-check {
  width: 26px; height: 26px;
  background: #DCFCE7;
  color: #059669;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700;
  margin-left: auto;
  flex-shrink: 0;
}

/* Scroll cue */
.scroll-cue {
  position: absolute;
  bottom: 36px; left: 50%;
  transform: translateX(-50%);
  display: flex; flex-direction: column;
  align-items: center; gap: 8px;
  animation: fadeIn 1s 1.2s ease both;
}
.sc-line {
  width: 1px; height: 40px;
  background: linear-gradient(to bottom, transparent, var(--muted));
  animation: lineGrow 2s ease-in-out infinite;
}
@keyframes lineGrow {
  0%   { opacity: 0; transform: scaleY(0); transform-origin: top; }
  50%  { opacity: 1; transform: scaleY(1); transform-origin: top; }
  100% { opacity: 0; transform: scaleY(1); transform-origin: top; }
}
.scroll-cue span {
  font-size: 9px; font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
}

/* ══ SHARED ANIMATIONS ══ */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* Scroll-reveal */
.rv {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.7s var(--ease), transform 0.7s var(--ease);
  transition-delay: calc(var(--i, 0) * 0.1s);
}
.rv.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* ══ FEATURES ══ */
.features {
  padding: 128px 0;
  background: var(--cream);
  border-top: 1px solid var(--border);
}
.sec-hd { margin-bottom: 60px; }
.sec-hd.centered { text-align: center; }
.sec-label {
  display: inline-block;
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 16px;
  padding-left: 18px;
  position: relative;
}
.sec-label::before {
  content: '';
  position: absolute;
  left: 0; top: 50%;
  transform: translateY(-50%);
  width: 10px; height: 1px;
  background: var(--gold);
}
.sec-hd.centered .sec-label { padding-left: 0; }
.sec-hd.centered .sec-label::before { display: none; }
.sec-title {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(38px, 4.5vw, 58px);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.025em;
  color: var(--forest);
  margin: 0;
}
.sec-title em { font-style: italic; color: var(--gold); }
.sec-rule {
  width: 56px; height: 2px;
  background: var(--gold);
  margin-top: 20px;
}
.sec-hd.centered .sec-rule { margin: 20px auto 0; }

.feat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
}
.feat-card {
  background: var(--cream);
  padding: 40px 32px;
  position: relative;
  overflow: hidden;
  transition: background 0.3s;
  cursor: default;
}
.feat-card::before {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 2px;
  background: var(--gold);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s var(--ease);
}
.feat-card:hover { background: var(--cream2); }
.feat-card:hover::before { transform: scaleX(1); }
.feat-num {
  display: block;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 12px; font-weight: 600;
  color: var(--muted);
  margin-bottom: 18px;
  letter-spacing: 0.06em;
}
.feat-emoji {
  font-size: 34px;
  display: block;
  margin-bottom: 16px;
  transition: transform 0.3s;
}
.feat-card:hover .feat-emoji { transform: scale(1.12) rotate(3deg); }
.feat-card h3 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 21px; font-weight: 700;
  color: var(--forest);
  margin: 0 0 10px;
  letter-spacing: -0.01em;
}
.feat-card p {
  font-size: 13px; line-height: 1.7;
  color: var(--muted);
  margin: 0 0 18px;
}
.feat-arrow {
  display: block;
  font-size: 18px;
  color: var(--gold);
  opacity: 0;
  transform: translateX(-8px);
  transition: opacity 0.3s, transform 0.3s;
}
.feat-card:hover .feat-arrow { opacity: 1; transform: translateX(0); }

/* ══ SHOWCASE ══ */
.showcase {
  padding: 128px 0;
  background: var(--cream2);
  border-top: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}
.showcase-bg-text {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 18vw; font-weight: 700;
  color: transparent;
  -webkit-text-stroke: 1px rgba(13,40,24,0.04);
  white-space: nowrap;
  pointer-events: none; user-select: none;
}
.showcase-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
  margin-top: 64px;
}
.show-card {
  background: white;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4px 24px rgba(13,40,24,0.06);
  border: 1px solid var(--border);
  transition: transform 0.4s var(--ease), box-shadow 0.4s var(--ease);
}
.show-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 28px 72px rgba(13,40,24,0.13);
}
.show-img-wrap {
  position: relative;
  height: 240px;
  overflow: hidden;
}
.show-img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.6s var(--ease);
}
.show-card:hover .show-img { transform: scale(1.05); }
.show-img-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, transparent 35%, rgba(13,40,24,0.55));
  display: flex; align-items: flex-end;
  padding: 20px;
}
.show-type-tag {
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: white;
  background: var(--gold);
  padding: 4px 10px;
  border-radius: 4px;
}

/* Property data strip */
.prop-data-strip {
  display: flex;
  gap: 0;
  margin: 0;
  border-bottom: 1px solid var(--border);
}
.pds-item {
  flex: 1;
  padding: 14px 20px;
  display: flex; flex-direction: column; gap: 4px;
  border-right: 1px solid var(--border);
}
.pds-item:last-child { border-right: none; }
.pds-item span { font-size: 11px; color: var(--muted); }
.pds-item strong { font-size: 14px; font-weight: 700; color: var(--forest); }
.grade-badge {
  font-size: 11px !important;
  font-weight: 700 !important;
  color: var(--gold) !important;
  background: var(--gold-pale);
  padding: 3px 8px;
  border-radius: 4px;
  display: inline-block;
}

/* Vehicle data strip */
.veh-data-strip {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}
.vds-model {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 20px; font-weight: 700;
  color: var(--forest);
  margin-bottom: 3px;
}
.vds-meta { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
.vds-value {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 26px; font-weight: 700;
  color: var(--gold);
  letter-spacing: -0.02em;
  margin-bottom: 10px;
}
.vds-bar-wrap {
  display: flex; align-items: center; gap: 10px;
}
.vds-bar {
  flex: 1; height: 4px;
  background: var(--cream2);
  border-radius: 2px; overflow: hidden;
}
.vds-fill {
  width: 88%; height: 100%;
  background: linear-gradient(90deg, var(--forest), var(--gold));
  border-radius: 2px;
}
.vds-bar-wrap span { font-size: 11px; color: var(--muted); }

.show-body { padding: 24px; }
.show-body h3 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 26px; font-weight: 700;
  color: var(--forest);
  margin: 0 0 10px;
  letter-spacing: -0.01em;
}
.show-body p {
  font-size: 14px; line-height: 1.7;
  color: var(--muted);
  margin: 0 0 16px;
}
.show-link {
  font-size: 13px; font-weight: 700;
  color: var(--gold);
  text-decoration: none;
  letter-spacing: 0.03em;
  transition: color 0.2s;
}
.show-link:hover { color: var(--forest); }

/* ══ COMPLIANCE ══ */
.compliance {
  padding: 110px 0;
  background: var(--forest);
  color: white;
  position: relative;
  overflow: hidden;
}
.comp-glow {
  position: absolute;
  top: -200px; right: -200px;
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(200,134,10,0.14) 0%, transparent 70%);
  pointer-events: none;
}
.comp-grid {
  display: grid;
  grid-template-columns: 100px 1fr auto;
  gap: 64px;
  align-items: center;
}
.comp-seal {
  position: relative;
  width: 100px; height: 100px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.seal-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(200,134,10,0.3);
}
.r1 { width: 100%; height: 100%; animation: spin 20s linear infinite; }
.r2 { width: 72%;  height: 72%;  animation: spin 14s linear infinite reverse; }
.r3 { width: 44%;  height: 44%;  animation: spin 9s  linear infinite; }
@keyframes spin {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}
.seal-icon { font-size: 34px; position: relative; z-index: 1; }
.comp-body .sec-label::before { background: var(--gold-light); }
.comp-body h2 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(30px, 3.2vw, 46px);
  font-weight: 700;
  color: white;
  line-height: 1.2;
  letter-spacing: -0.02em;
  margin: 0 0 16px;
}
.comp-body h2 em { font-style: italic; color: var(--gold-light); }
.comp-body p {
  font-size: 15px; line-height: 1.75;
  color: rgba(255,255,255,0.58);
  margin: 0 0 24px;
}
.comp-badges {
  display: flex; flex-wrap: wrap; gap: 8px;
}
.comp-badges span {
  font-size: 12px; font-weight: 600;
  padding: 6px 14px;
  border: 1px solid rgba(200,134,10,0.4);
  border-radius: 100px;
  color: var(--gold-light);
  letter-spacing: 0.03em;
}
.comp-nums {
  display: flex; flex-direction: column; gap: 28px;
  flex-shrink: 0;
}
.cn-v {
  display: block;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 44px; font-weight: 700;
  color: var(--gold-light);
  letter-spacing: -0.03em;
  line-height: 1;
}
.cn-l {
  display: block;
  font-size: 11px;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.06em;
  margin-top: 4px;
}

/* ══ CTA ══ */
.cta-sec {
  padding: 150px 0;
  background: var(--cream);
  text-align: center;
  position: relative;
  overflow: hidden;
}
.cta-ring {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  border: 1px solid var(--border-gold);
  pointer-events: none;
}
.cta-ring.r1 { width: 500px; height: 500px; animation: ringPulse 6s ease-in-out infinite; }
.cta-ring.r2 { width: 740px; height: 740px; animation: ringPulse 6s ease-in-out infinite 1s; opacity: 0.5; }
@keyframes ringPulse {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50%       { opacity: 1;   transform: translate(-50%, -50%) scale(1.02); }
}
.cta-inner {
  position: relative;
  z-index: 1;
}
.cta-inner h2 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: clamp(48px, 5.5vw, 76px);
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.03em;
  color: var(--forest);
  margin: 16px 0 20px;
}
.cta-inner h2 em { font-style: italic; color: var(--gold); }
.cta-inner p {
  font-size: 16px; line-height: 1.7;
  color: var(--muted);
  margin: 0 auto 44px;
  max-width: 380px;
}

/* ══ FOOTER ══ */
.footer {
  background: var(--forest);
  padding: 68px 0 0;
}
.foot-top {
  display: flex;
  gap: 80px;
  padding-bottom: 60px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.foot-brand { flex: 1; }
.foot-logo { margin-bottom: 18px; }
.foot-brand p {
  font-size: 13px; line-height: 1.7;
  color: rgba(255,255,255,0.38);
  max-width: 260px;
}
.foot-nav { display: flex; gap: 60px; }
.fn-col { display: flex; flex-direction: column; gap: 12px; }
.fn-title {
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.35);
  margin-bottom: 4px;
}
.fn-col a {
  font-size: 14px;
  color: rgba(255,255,255,0.58);
  text-decoration: none;
  transition: color 0.2s;
}
.fn-col a:hover { color: var(--gold-light); }
.foot-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 0;
  font-size: 12px;
  color: rgba(255,255,255,0.28);
  letter-spacing: 0.03em;
}

/* ══ RESPONSIVE ══ */
@media (max-width: 1024px) {
  .hero-layout { grid-template-columns: 1fr; gap: 60px; }
  .hero-visual  { height: 420px; }
  .hero-bg-number { font-size: 120px; right: -10px; }
  .feat-grid    { grid-template-columns: repeat(2, 1fr); }
  .showcase-grid { grid-template-columns: 1fr; }
  .comp-grid    { grid-template-columns: 1fr; gap: 40px; text-align: center; }
  .comp-nums    { flex-direction: row; justify-content: center; }
  .comp-seal    { margin: 0 auto; }
  .foot-top     { flex-direction: column; gap: 40px; }
}

@media (max-width: 768px) {
  .container    { padding: 0 20px; }
  .nav-links    { display: none; }
  .hero-visual  { display: none; }
  h1            { font-size: 50px; }
  .feat-grid    { grid-template-columns: 1fr; }
  .comp-nums    { flex-direction: column; }
  .foot-nav     { gap: 32px; }
}
</style>
