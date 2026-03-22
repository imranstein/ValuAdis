<template>
  <div class="landing-page">

    <!-- ═══ NAV ═══ -->
    <nav :class="['nav-bar', { 'nav-scrolled': isScrolled }]">
      <div class="nav-inner">
        <NuxtLink to="/" class="brand-logo">
          <span class="brand-name">ValuAdis</span>
        </NuxtLink>
        <div class="nav-links">
          <NuxtLink to="/login">Properties</NuxtLink>
          <NuxtLink to="/login">Valuations</NuxtLink>
          <NuxtLink to="/login">GIS Maps</NuxtLink>
          <NuxtLink to="/login">Reports</NuxtLink>
        </div>
        <div class="nav-actions">
          <NuxtLink to="/login" class="btn-cta">New Valuation</NuxtLink>
        </div>
      </div>
    </nav>

    <main>
      <!-- ═══ HERO ═══ -->
      <section class="hero-section">
        <!-- Background -->
        <div class="hero-bg">
          <div class="hero-bg-gradient"></div>
        </div>

        <div class="hero-content">
          <!-- Left copy -->
          <div class="hero-copy">
            <div class="eyebrow-badge">B2G Certified Infrastructure</div>
            <h1 class="hero-headline">
              Digital Property Valuation
              <br />
              <em class="hero-headline-em">Made Simple</em>
            </h1>
            <p class="hero-sub">
              Transforming municipal asset management with Ethiopia's first
              editorial-grade property ledger. Accurate, transparent, and sovereign.
            </p>
            <div class="hero-btns">
              <NuxtLink to="/login" class="btn-primary">Start Valuation</NuxtLink>
              <button class="btn-ghost">
                <span class="play-ring">
                  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <path d="M8 5v14l11-7z"/>
                  </svg>
                </span>
                Watch Demo
              </button>
            </div>
          </div>

          <!-- Right visual -->
          <div class="hero-visual">
            <div class="hero-orb floating">
              <!-- Abstract gradient orb matching Stitch painterly-border style -->
              <div class="orb-inner">
                <div class="orb-gradient"></div>
                <!-- Floating glass cards -->
                <div class="glass-chip chip-top">
                  <svg class="chip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
                    <polyline points="9 22 9 12 15 12 15 22"/>
                  </svg>
                  <p class="chip-label">Properties</p>
                </div>
                <div class="glass-chip chip-bottom">
                  <svg class="chip-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="1" y="3" width="15" height="13" rx="2"/>
                    <path d="M16 8h4l3 3v5h-7V8z"/>
                    <circle cx="5.5" cy="18.5" r="2.5"/>
                    <circle cx="18.5" cy="18.5" r="2.5"/>
                  </svg>
                  <p class="chip-label">Vehicles</p>
                </div>
              </div>
              <!-- Amber pulse -->
              <div class="amber-pulse-ring"></div>
              <div class="amber-pulse-dot"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ FEATURES ═══ -->
      <section class="features-section">
        <div class="section-container">

          <!-- GIS Feature — full width -->
          <div class="feature-gis rv">
            <div class="feature-gis-copy">
              <svg class="feature-icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
                <circle cx="12" cy="9" r="2.5"/>
              </svg>
              <h3 class="feature-title-serif">Precision GIS Mapping</h3>
              <p class="feature-desc">
                Seamlessly integrate cadastral data with high-resolution satellite
                imagery for millimeter-accurate property boundary definitions.
              </p>
              <div class="feature-tags">
                <span><span class="dot-amber"></span> Topology validation</span>
                <span><span class="dot-amber"></span> Historical layering</span>
              </div>
            </div>
            <div class="feature-gis-visual">
              <div class="feature-img-wrap painterly">
                <div class="feature-img-inner"></div>
                <div class="feature-img-overlay"></div>
              </div>
            </div>
          </div>

          <!-- Two col features -->
          <div class="feature-row-2">
            <div class="feature-card rv">
              <svg class="feature-icon-md" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
              <h3 class="feature-card-title">Real-Time Compliance</h3>
              <p class="feature-card-desc">
                Every valuation report is instantly cross-referenced against federal
                taxation guidelines and legal statutes.
              </p>
              <div class="feature-card-footer">
                <span>Status: Certified</span>
                <span class="text-amber-deep">Shield Protocol</span>
              </div>
            </div>

            <div class="feature-card feature-card-white rv">
              <svg class="feature-icon-md feature-icon-sage" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M1 6l5.5 5.5L12 5l5.5 6.5L23 6"/>
                <path d="M1 18l5.5-5.5L12 19l5.5-6.5L23 18"/>
              </svg>
              <h3 class="feature-card-title">Mobile Offline Mode</h3>
              <p class="feature-card-desc">
                Field agents can perform full valuations in areas with zero
                connectivity. Data syncs automatically.
              </p>
              <div class="offline-bar">
                <div class="offline-bar-fill"></div>
              </div>
            </div>
          </div>

          <!-- Ledger dark banner -->
          <div class="ledger-banner rv">
            <div class="ledger-copy">
              <h3 class="ledger-title">Transparent Asset Ledger</h3>
              <p class="ledger-desc">
                A permanent, immutable record of all national assets, ensuring total
                accountability for government stakeholders.
              </p>
              <NuxtLink to="/login" class="btn-ledger">View Demo Ledger</NuxtLink>
            </div>
            <div class="ledger-lines" aria-hidden="true">
              <div class="ledger-line" style="width:100%;opacity:0.5"></div>
              <div class="ledger-line" style="width:80%;opacity:0.3"></div>
              <div class="ledger-line" style="width:100%;opacity:0.4"></div>
              <div class="ledger-line" style="width:75%;opacity:0.2"></div>
            </div>
          </div>

        </div>
      </section>

      <!-- ═══ STATS ═══ -->
      <section class="stats-section">
        <div class="section-container">
          <div class="stats-grid">
            <div class="stat-item rv" v-for="stat in stats" :key="stat.label">
              <span class="stat-value">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- ═══ CTA ═══ -->
      <section class="cta-section">
        <div class="cta-glow" aria-hidden="true"></div>
        <div class="section-container">
          <div class="cta-content rv">
            <h2 class="cta-headline">
              Ready to modernise your
              <br />
              <em class="cta-headline-em">property ledger?</em>
            </h2>
            <div class="cta-btns">
              <NuxtLink to="/login" class="btn-cta-dark">Get Started Now</NuxtLink>
              <button class="btn-cta-ghost">Request Consultation</button>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- ═══ FOOTER ═══ -->
    <footer class="site-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-logo">ValuAdis</span>
          <p class="footer-copy">© 2025 ValuAdis GovTech.<br />Digital Heritage Initiative.</p>
        </div>
        <div class="footer-links">
          <NuxtLink to="/login">Privacy Policy</NuxtLink>
          <NuxtLink to="/login">Terms of Service</NuxtLink>
          <NuxtLink to="/login">Compliance</NuxtLink>
          <NuxtLink to="/login">Contact Support</NuxtLink>
        </div>
        <div class="footer-socials">
          <button class="social-btn" aria-label="Website">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>
            </svg>
          </button>
          <button class="social-btn" aria-label="Email">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="18" height="18">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
          </button>
        </div>
      </div>
    </footer>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

definePageMeta({ layout: 'landing', middleware: 'guest' })

const isScrolled = ref(false)

const stats = [
  { value: '2,400+', label: 'Properties Valued' },
  { value: '12', label: 'Cities Covered' },
  { value: '100%', label: 'Compliance Rate' },
  { value: '< 2min', label: 'Avg. Valuation Time' },
]

function handleScroll() {
  isScrolled.value = window.scrollY > 60
}

function initReveal() {
  if (typeof IntersectionObserver === 'undefined') return
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('revealed')
          observer.unobserve(e.target)
        }
      })
    },
    { threshold: 0.1 }
  )
  document.querySelectorAll('.rv').forEach((el) => observer.observe(el))
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  setTimeout(initReveal, 50)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:ital,wght@0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&display=swap');

/* ── TOKENS ── */
:root {
  --earth-dark:  #2d2a26;
  --earth-clay:  #7c6a58;
  --earth-sand:  #d9d0c1;
  --earth-mist:  #f2eee9;
  --amber-glow:  #ffbf69;
  --amber-deep:  #b07d4b;
  --sage:        #8a9a5b;
}

/* ── BASE ── */
.landing-page {
  font-family: 'Lora', serif;
  background: var(--earth-mist);
  color: var(--earth-dark);
  line-height: 1.7;
  overflow-x: hidden;
}

/* ── REVEAL ANIMATION ── */
.rv {
  opacity: 0;
  transform: translateY(32px);
  transition: opacity 0.8s ease, transform 0.8s ease;
}
.rv.revealed {
  opacity: 1;
  transform: translateY(0);
}

/* ── NAV ── */
.nav-bar {
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 50;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 3rem;
  height: 6rem;
  transition: background 0.4s ease, backdrop-filter 0.4s ease, box-shadow 0.4s ease;
}
.nav-scrolled {
  background: rgba(242, 238, 233, 0.9);
  backdrop-filter: blur(16px);
  box-shadow: 0 1px 0 rgba(124, 106, 88, 0.12);
}
.nav-inner {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand-logo {
  text-decoration: none;
}
.brand-name {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 1.6rem;
  color: var(--earth-clay);
  letter-spacing: -0.02em;
}
.nav-links {
  display: flex;
  gap: 3rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 600;
}
.nav-links a {
  color: rgba(124, 106, 88, 0.8);
  text-decoration: none;
  transition: color 0.2s;
}
.nav-links a:hover { color: var(--amber-deep); }
.btn-cta {
  background: var(--earth-dark);
  color: var(--earth-mist);
  padding: 0.75rem 2rem;
  border-radius: 9999px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  border: none;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.4s ease, box-shadow 0.4s ease;
}
.btn-cta:hover {
  background: var(--amber-deep);
  box-shadow: 0 8px 24px rgba(176, 125, 75, 0.2);
}

/* ── HERO ── */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
}
.hero-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}
.hero-bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 70% 30%, rgba(255, 191, 105, 0.18) 0%, transparent 52%),
    radial-gradient(circle at 10% 80%, rgba(124, 106, 88, 0.12) 0%, transparent 42%);
}
.hero-content {
  position: relative;
  z-index: 10;
  max-width: 80rem;
  margin: 0 auto;
  padding: 7rem 2rem 4rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  width: 100%;
}
.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.eyebrow-badge {
  display: inline-block;
  padding: 0.35rem 1rem;
  border-radius: 9999px;
  border: 1px solid rgba(176, 125, 75, 0.3);
  background: rgba(255, 191, 105, 0.06);
  color: var(--amber-deep);
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  width: fit-content;
}
.hero-headline {
  font-family: 'Instrument Serif', serif;
  font-size: clamp(3.5rem, 7vw, 5.5rem);
  line-height: 0.92;
  color: var(--earth-dark);
  margin: 0;
}
.hero-headline-em {
  font-style: italic;
  color: var(--amber-deep);
}
.hero-sub {
  font-size: 1.2rem;
  color: rgba(124, 106, 88, 0.85);
  font-style: italic;
  font-weight: 300;
  max-width: 38rem;
  line-height: 1.75;
}
.hero-btns {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}
.btn-primary {
  background: var(--amber-deep);
  color: #fff;
  padding: 1.1rem 2.5rem;
  border-radius: 9999px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  border: none;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 8px 24px rgba(176, 125, 75, 0.22);
  transition: background 0.4s ease, transform 0.3s ease;
}
.btn-primary:hover {
  background: var(--earth-dark);
  transform: translateY(-2px);
}
.btn-ghost {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--earth-clay);
  transition: color 0.2s;
}
.btn-ghost:hover { color: var(--amber-deep); }
.play-ring {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 50%;
  border: 1px solid rgba(124, 106, 88, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s, border-color 0.3s;
}
.btn-ghost:hover .play-ring {
  background: rgba(255, 191, 105, 0.1);
  border-color: var(--amber-deep);
}

/* ── HERO VISUAL ── */
.hero-visual {
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}
.hero-orb {
  position: relative;
  width: 28rem;
  height: 28rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.orb-inner {
  width: 100%;
  height: 100%;
  border-radius: 60% 40% 70% 30% / 40% 50% 60% 70%;
  overflow: hidden;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.orb-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 191, 105, 0.25) 0%, rgba(138, 154, 91, 0.2) 100%);
}
.floating {
  animation: float 7s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
.glass-chip {
  position: absolute;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 1.25rem;
  border-radius: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  animation: pulse 3s ease-in-out infinite;
}
.chip-top {
  top: 20%;
  right: -2rem;
}
.chip-bottom {
  bottom: 22%;
  left: -2rem;
  animation-delay: 0.8s;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.04); }
}
.chip-icon {
  width: 1.5rem;
  height: 1.5rem;
  stroke: var(--amber-deep);
}
.chip-label {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.6rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 700;
  color: var(--earth-dark);
  opacity: 0.7;
  margin: 0;
}
.amber-pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background: rgba(255, 191, 105, 0.3);
  filter: blur(8px);
  animation: ping 2s ease-in-out infinite;
}
.amber-pulse-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: var(--amber-glow);
  box-shadow: 0 0 20px 4px rgba(255, 191, 105, 0.6);
}
@keyframes ping {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.6); opacity: 0; }
}

/* ── FEATURES ── */
.features-section {
  background: linear-gradient(to bottom, transparent, var(--earth-mist) 15%);
  padding: 5rem 0 6rem;
  margin-top: -6rem;
}
.section-container {
  max-width: 80rem;
  margin: 0 auto;
  padding: 0 2rem;
}

/* GIS feature */
.feature-gis {
  display: flex;
  flex-direction: column;
  gap: 4rem;
  margin-bottom: 4rem;
}
@media (min-width: 1024px) {
  .feature-gis {
    flex-direction: row;
    align-items: center;
  }
  .feature-gis-copy,
  .feature-gis-visual {
    flex: 1;
  }
}
.feature-gis-copy {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.feature-icon-lg {
  width: 3rem;
  height: 3rem;
  stroke: var(--amber-deep);
}
.feature-title-serif {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 2.8rem;
  color: var(--earth-dark);
  line-height: 1.1;
  margin: 0;
}
.feature-desc {
  font-size: 1.1rem;
  color: rgba(124, 106, 88, 0.85);
  font-weight: 300;
  line-height: 1.75;
}
.feature-tags {
  display: flex;
  gap: 2rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 700;
  color: var(--earth-clay);
}
.feature-tags span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.dot-amber {
  display: inline-block;
  width: 0.35rem;
  height: 0.35rem;
  border-radius: 50%;
  background: var(--amber-glow);
}
.feature-gis-visual {
  position: relative;
}
.feature-img-wrap {
  aspect-ratio: 4/3;
  background: var(--earth-sand);
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(45, 42, 38, 0.12);
}
.painterly {
  border-radius: 60% 40% 70% 30% / 40% 50% 60% 70%;
}
.feature-img-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(176, 125, 75, 0.15), rgba(138, 154, 91, 0.2));
  opacity: 0.8;
}
.feature-img-overlay {
  position: absolute;
  inset: 0;
  background: rgba(176, 125, 75, 0.08);
}

/* 2-col feature cards */
.feature-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 3rem;
}
@media (max-width: 768px) {
  .feature-row-2 { grid-template-columns: 1fr; }
}
.feature-card {
  padding: 3rem;
  border-radius: 4rem;
  background: linear-gradient(135deg, rgba(124, 106, 88, 0.05), rgba(255, 191, 105, 0.1));
  border: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.feature-card-white {
  background: #fff;
  box-shadow: 0 10px 40px rgba(45, 42, 38, 0.06);
  border-color: var(--earth-mist);
}
.feature-icon-md {
  width: 2.5rem;
  height: 2.5rem;
  stroke: var(--amber-deep);
}
.feature-icon-sage {
  stroke: var(--sage);
}
.feature-card-title {
  font-family: 'Instrument Serif', serif;
  font-size: 2rem;
  color: var(--earth-dark);
  margin: 0;
}
.feature-card-desc {
  font-size: 1rem;
  color: rgba(124, 106, 88, 0.85);
  font-style: italic;
  line-height: 1.7;
  margin: 0;
  flex: 1;
}
.feature-card-footer {
  padding-top: 1.5rem;
  border-top: 1px solid rgba(124, 106, 88, 0.1);
  display: flex;
  justify-content: space-between;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-weight: 700;
  color: rgba(124, 106, 88, 0.6);
}
.text-amber-deep { color: var(--amber-deep); }
.offline-bar {
  height: 0.5rem;
  width: 6rem;
  background: rgba(138, 154, 91, 0.2);
  border-radius: 9999px;
  overflow: hidden;
}
.offline-bar-fill {
  height: 100%;
  width: 50%;
  background: var(--sage);
  border-radius: 9999px;
}

/* Ledger dark banner */
.ledger-banner {
  border-radius: 5rem;
  background: var(--earth-dark);
  color: var(--earth-mist);
  padding: 5rem 6rem;
  display: flex;
  gap: 4rem;
  align-items: center;
  position: relative;
  overflow: hidden;
}
.ledger-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: relative;
  z-index: 1;
}
.ledger-title {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 3rem;
  line-height: 1.1;
  margin: 0;
}
.ledger-desc {
  font-size: 1.05rem;
  color: var(--earth-sand);
  font-weight: 300;
  line-height: 1.75;
  margin: 0;
}
.btn-ledger {
  display: inline-block;
  padding: 1rem 3rem;
  border: 1px solid rgba(217, 208, 193, 0.3);
  border-radius: 9999px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 700;
  color: var(--earth-mist);
  text-decoration: none;
  background: none;
  cursor: pointer;
  width: fit-content;
  transition: background 0.6s ease, color 0.6s ease;
}
.btn-ledger:hover {
  background: var(--amber-glow);
  color: var(--earth-dark);
  border-color: var(--amber-glow);
}
.ledger-lines {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  z-index: 1;
}
.ledger-line {
  height: 3px;
  background: rgba(255, 191, 105, 0.5);
  border-radius: 9999px;
}

/* ── STATS ── */
.stats-section {
  padding: 5rem 0;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
  border-top: 1px solid rgba(124, 106, 88, 0.15);
  padding-top: 3rem;
}
@media (max-width: 768px) {
  .stats-grid { grid-template-columns: 1fr 1fr; }
}
.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.stat-value {
  font-family: 'Instrument Serif', serif;
  font-size: 2.8rem;
  color: var(--earth-dark);
  line-height: 1;
}
.stat-label {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-weight: 600;
  color: var(--earth-clay);
}

/* ── CTA ── */
.cta-section {
  padding: 10rem 0;
  position: relative;
  overflow: hidden;
}
.cta-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  height: 500px;
  background: radial-gradient(ellipse at bottom, rgba(255, 191, 105, 0.12), transparent 70%);
  filter: blur(40px);
  pointer-events: none;
}
.cta-content {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  position: relative;
  z-index: 1;
}
.cta-headline {
  font-family: 'Instrument Serif', serif;
  font-size: clamp(3.5rem, 8vw, 7rem);
  line-height: 0.88;
  color: var(--earth-dark);
  margin: 0;
}
.cta-headline-em {
  font-style: italic;
  color: var(--amber-deep);
}
.cta-btns {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
}
.btn-cta-dark {
  background: var(--earth-dark);
  color: var(--earth-mist);
  padding: 1.25rem 3.5rem;
  border-radius: 9999px;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  border: none;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 12px 36px rgba(45, 42, 38, 0.2);
  transition: background 0.4s ease, transform 0.3s ease;
}
.btn-cta-dark:hover {
  background: var(--amber-deep);
  transform: scale(1.04);
}
.btn-cta-ghost {
  background: none;
  border: none;
  cursor: pointer;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: var(--earth-clay);
  text-decoration: underline;
  text-underline-offset: 8px;
  transition: color 0.2s;
}
.btn-cta-ghost:hover { color: var(--amber-deep); }

/* ── FOOTER ── */
.site-footer {
  background: var(--earth-mist);
  border-top: 1px solid rgba(124, 106, 88, 0.1);
  padding: 5rem 3rem;
}
.footer-inner {
  max-width: 80rem;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 4rem;
  flex-wrap: wrap;
}
.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.footer-logo {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 2.5rem;
  color: var(--earth-clay);
}
.footer-copy {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(124, 106, 88, 0.5);
  line-height: 1.7;
  margin: 0;
}
.footer-links {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem 4rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-weight: 700;
}
.footer-links a {
  color: var(--earth-clay);
  text-decoration: none;
  transition: color 0.2s;
}
.footer-links a:hover { color: var(--amber-deep); }
.footer-socials {
  display: flex;
  gap: 1rem;
}
.social-btn {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  border: 1px solid rgba(124, 106, 88, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  cursor: pointer;
  color: var(--earth-clay);
  transition: background 0.2s;
}
.social-btn:hover {
  background: rgba(255, 191, 105, 0.1);
}

/* ── RESPONSIVE ── */
@media (max-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    padding-top: 8rem;
  }
  .hero-visual { display: none; }
  .eyebrow-badge { margin: 0 auto; }
  .hero-btns { justify-content: center; }
  .ledger-banner {
    flex-direction: column;
    padding: 3rem 2rem;
    border-radius: 3rem;
  }
  .nav-links { display: none; }
}
@media (max-width: 640px) {
  .hero-headline { font-size: 3rem; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .feature-row-2 { grid-template-columns: 1fr; }
  .cta-headline { font-size: 3rem; }
  .nav-bar { padding: 0 1.5rem; }
  .site-footer { padding: 3rem 1.5rem; }
}
</style>
