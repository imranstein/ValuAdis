<template>
  <div class="nf-landing">
    <!-- Navigation -->
    <nav class="nf-nav" :class="{ scrolled: isScrolled }">
      <div class="nav-inner">
        <div class="logo">
          <span class="logo-text">ValuAdis</span>
        </div>
        <div class="nav-links">
          <a href="#features" class="nav-link">Features</a>
          <a href="#trust" class="nav-link">Compliance</a>
          <NuxtLink to="/login" class="nav-cta">
            <span>Sign In</span>
            <i class="pi pi-arrow-right cta-icon"></i>
          </NuxtLink>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg">
        <div class="dot-grid"></div>
        <div class="hero-glow hero-glow-cyan"></div>
        <div class="hero-glow hero-glow-violet"></div>
      </div>
      <div class="hero-content">
        <p class="hero-eyebrow animate-fade-up">// ETHIOPIAN PROPERTY INTELLIGENCE</p>
        <h1 class="hero-title animate-fade-up animate-delay-1">
          Property Valuation.<br />
          <span class="hero-title-gold">Reimagined.</span>
        </h1>
        <p class="hero-subtitle animate-fade-up animate-delay-2">
          Next-generation valuation platform built for Ethiopia's property market.
          Proclamation 1365/2025 compliant. Audit-ready in minutes.
        </p>
        <div class="hero-actions animate-fade-up animate-delay-3">
          <NuxtLink to="/login" class="btn-primary-glow">
            <span>Get Started</span>
            <i class="pi pi-arrow-right"></i>
          </NuxtLink>
          <a href="#features" class="btn-glass">Learn More</a>
        </div>

        <div class="hero-stats animate-fade-up animate-delay-4">
          <div class="stat-item">
            <span class="stat-value">2,400+</span>
            <span class="stat-label">Properties Valued</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">12</span>
            <span class="stat-label">Cities Covered</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">100%</span>
            <span class="stat-label">Compliant Reports</span>
          </div>
        </div>
      </div>

      <div class="hero-scroll">
        <div class="scroll-line"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features">
      <div class="section-inner">
        <p class="section-eyebrow">// CAPABILITIES</p>
        <h2 class="section-title">Built for Precision. <span class="title-accent">Engineered for Ethiopia.</span></h2>
        <div class="features-grid">
          <div
            v-for="(feature, i) in features"
            :key="feature.title"
            class="feature-card"
            :style="{ animationDelay: `${i * 0.12}s` }"
          >
            <div class="feature-icon-wrap">
              <i :class="feature.icon"></i>
            </div>
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-desc">{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Trust / Compliance Section -->
    <section id="trust" class="trust">
      <div class="section-inner">
        <div class="trust-card-wrap">
          <div class="trust-card">
            <div class="trust-card-inner">
              <div class="trust-shield">
                <i class="pi pi-shield"></i>
              </div>
              <h2 class="trust-heading">Proclamation 1365/2025 Compliant</h2>
              <p class="trust-desc">
                All valuations adhere to Ethiopian government regulations with complete
                traceability, full audit trails, and stakeholder-ready documentation.
              </p>
              <div class="trust-badges">
                <span class="trust-badge">
                  <i class="pi pi-check-circle"></i> 100% Audit Ready
                </span>
                <span class="trust-badge">
                  <i class="pi pi-check-circle"></i> Tax Compliant
                </span>
                <span class="trust-badge">
                  <i class="pi pi-check-circle"></i> Zero Compliance Issues
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Strip -->
    <section class="stats-strip">
      <div class="section-inner">
        <div class="stats-row">
          <div class="big-stat">
            <span class="big-stat-value">2,400+</span>
            <span class="big-stat-label">Properties Valued</span>
          </div>
          <div class="stats-vdivider"></div>
          <div class="big-stat">
            <span class="big-stat-value">12</span>
            <span class="big-stat-label">Cities in Ethiopia</span>
          </div>
          <div class="stats-vdivider"></div>
          <div class="big-stat">
            <span class="big-stat-value">100%</span>
            <span class="big-stat-label">Regulatory Compliance</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-glow-bg"></div>
      <div class="section-inner cta-inner">
        <h2 class="cta-heading">Ready to streamline your valuations?</h2>
        <p class="cta-sub">
          Join professionals who trust ValuAdis for accurate, compliant property valuations.
        </p>
        <NuxtLink to="/login" class="btn-primary-glow btn-large">
          <span>Sign In to Dashboard</span>
          <i class="pi pi-arrow-right"></i>
        </NuxtLink>
      </div>
    </section>

    <!-- Footer -->
    <footer class="nf-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="footer-logo">ValuAdis</span>
          <p class="footer-tagline">Ethiopian Property Valuation Platform</p>
        </div>
        <div class="footer-links">
          <NuxtLink to="/login" class="footer-link">Sign In</NuxtLink>
          <a href="#features" class="footer-link">Features</a>
          <a href="#trust" class="footer-link">Compliance</a>
        </div>
        <p class="footer-copy">© {{ new Date().getFullYear() }} ValuAdis. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

definePageMeta({
  layout: 'landing',
  middleware: 'guest'
})

const isScrolled = ref(false)

const features = [
  {
    icon: 'pi pi-building',
    title: 'Property Valuation',
    desc: 'Accurate residential, commercial, and mixed-use property valuations with AI-assisted estimates and full audit trails.'
  },
  {
    icon: 'pi pi-car',
    title: 'Vehicle Valuation',
    desc: 'Comprehensive vehicle valuations with market data, depreciation models, and compliance-ready documentation.'
  },
  {
    icon: 'pi pi-file-pdf',
    title: 'Audit-Ready Reports',
    desc: 'Generate professional PDF reports that meet regulatory requirements and stakeholder expectations.'
  },
  {
    icon: 'pi pi-map',
    title: 'Geographic Intelligence',
    desc: 'Map-based property visualization with location analytics and spatial context for informed decisions.'
  }
]

function handleScroll() {
  isScrolled.value = window.scrollY > 50
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@400;500&display=swap');

/* ── Design Tokens ── */
.nf-landing {
  --void: #08080f;
  --surface: #0f0f1a;
  --cyan: #00d4ff;
  --gold: #e8a020;
  --violet: #7b2fff;
  --text: #e2e8f0;
  --muted: #64748b;
  --cyan-dim: rgba(0, 212, 255, 0.15);
  --cyan-glow: rgba(0, 212, 255, 0.25);
  --gold-dim: rgba(232, 160, 32, 0.15);
  --violet-dim: rgba(123, 47, 255, 0.2);

  font-family: 'DM Sans', sans-serif;
  background: var(--void);
  color: var(--text);
  scroll-behavior: smooth;
}

/* ── Navigation ── */
.nf-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 200;
  padding: 1.25rem 2rem;
  background: transparent;
  transition: background 0.4s ease, border-color 0.4s ease;
  border-bottom: 1px solid transparent;
}

.nf-nav.scrolled {
  background: rgba(8, 8, 15, 0.8);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom-color: rgba(0, 212, 255, 0.2);
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-text {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 1.5rem;
  color: var(--text);
  letter-spacing: 0.04em;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.nav-link {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.9rem;
  color: var(--muted);
  text-decoration: none;
  letter-spacing: 0.03em;
  transition: color 0.25s ease;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -3px;
  left: 0;
  width: 0;
  height: 1px;
  background: var(--cyan);
  transition: width 0.3s ease;
}

.nav-link:hover {
  color: var(--cyan);
}

.nav-link:hover::after {
  width: 100%;
}

.nav-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.2rem;
  border: 1px solid var(--cyan);
  color: var(--cyan);
  text-decoration: none;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem;
  letter-spacing: 0.04em;
  transition: all 0.3s ease;
  background: transparent;
}

.nav-cta:hover {
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 0 0 16px rgba(0, 212, 255, 0.3);
}

.cta-icon {
  font-size: 0.72rem;
  transition: transform 0.3s ease;
}

.nav-cta:hover .cta-icon {
  transform: translateX(3px);
}

/* ── Hero ── */
.hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: var(--void);
}

.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.dot-grid {
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(0, 212, 255, 0.18) 1px, transparent 1px);
  background-size: 32px 32px;
  animation: dot-grid-pulse 6s ease-in-out infinite;
}

@keyframes dot-grid-pulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.7; }
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  animation: glow-float 10s ease-in-out infinite;
}

.hero-glow-cyan {
  width: 500px;
  height: 500px;
  background: rgba(0, 212, 255, 0.12);
  top: -120px;
  right: -120px;
}

.hero-glow-violet {
  width: 400px;
  height: 400px;
  background: rgba(123, 47, 255, 0.15);
  bottom: -80px;
  left: -80px;
  animation-delay: -5s;
}

@keyframes glow-float {
  0%, 100% { transform: scale(1) translate(0, 0); opacity: 0.8; }
  33% { transform: scale(1.08) translate(10px, -15px); opacity: 1; }
  66% { transform: scale(0.95) translate(-8px, 10px); opacity: 0.7; }
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 0 2rem;
  max-width: 860px;
}

.hero-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.78rem;
  letter-spacing: 0.2em;
  color: var(--cyan);
  margin-bottom: 1.75rem;
}

.hero-title {
  font-family: 'Syne', sans-serif;
  font-weight: 800;
  font-size: clamp(3rem, 7vw, 5.5rem);
  line-height: 1.1;
  color: var(--text);
  margin-bottom: 1.5rem;
  letter-spacing: -0.01em;
}

.hero-title-gold {
  background: linear-gradient(135deg, var(--gold) 0%, #f5c842 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.1rem;
  color: var(--muted);
  line-height: 1.7;
  max-width: 540px;
  margin: 0 auto 2.5rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 4rem;
}

.btn-primary-glow {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.9rem 2rem;
  background: linear-gradient(135deg, var(--cyan) 0%, #0099cc 100%);
  color: var(--void);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  font-weight: 500;
  text-decoration: none;
  border: none;
  cursor: pointer;
  box-shadow: 0 0 24px rgba(0, 212, 255, 0.4), 0 4px 16px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.btn-primary-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 36px rgba(0, 212, 255, 0.6), 0 8px 24px rgba(0, 0, 0, 0.4);
}

.btn-primary-glow i {
  font-size: 0.85rem;
  transition: transform 0.3s ease;
}

.btn-primary-glow:hover i {
  transform: translateX(4px);
}

.btn-glass {
  display: inline-flex;
  align-items: center;
  padding: 0.9rem 2rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(226, 232, 240, 0.2);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.95rem;
  text-decoration: none;
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.btn-glass:hover {
  border-color: var(--cyan);
  color: var(--cyan);
  background: rgba(0, 212, 255, 0.05);
}

.btn-large {
  padding: 1.1rem 2.5rem;
  font-size: 1rem;
}

/* Hero Stats Strip */
.hero-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  background: rgba(15, 15, 26, 0.7);
  border: 1px solid rgba(0, 212, 255, 0.15);
  backdrop-filter: blur(12px);
  padding: 1.5rem 2.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 2.5rem;
}

.stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.6rem;
  font-weight: 600;
  color: var(--cyan);
  line-height: 1;
  margin-bottom: 0.3rem;
}

.stat-label {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem;
  color: var(--muted);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(0, 212, 255, 0.2);
}

/* Scroll Indicator */
.hero-scroll {
  position: absolute;
  bottom: 2.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scroll-line {
  width: 1px;
  height: 60px;
  background: linear-gradient(to bottom, var(--cyan), transparent);
  animation: scroll-pulse 2s ease-in-out infinite;
}

@keyframes scroll-pulse {
  0%, 100% { opacity: 0.3; transform: scaleY(1); }
  50% { opacity: 1; transform: scaleY(1.1); }
}

/* ── Animations ── */
.animate-fade-up {
  opacity: 0;
  transform: translateY(28px);
  animation: fade-up 0.85s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.animate-delay-1 { animation-delay: 0.12s; }
.animate-delay-2 { animation-delay: 0.24s; }
.animate-delay-3 { animation-delay: 0.36s; }
.animate-delay-4 { animation-delay: 0.52s; }

@keyframes fade-up {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── Features ── */
.features {
  padding: 9rem 2rem;
  background: var(--surface);
}

.section-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.section-eyebrow {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.76rem;
  letter-spacing: 0.18em;
  color: var(--cyan);
  margin-bottom: 1rem;
}

.section-title {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 3rem);
  color: var(--text);
  margin-bottom: 4rem;
  line-height: 1.2;
}

.title-accent {
  color: var(--cyan);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(0, 212, 255, 0.15);
  backdrop-filter: blur(10px);
  transition: border-color 0.35s ease, box-shadow 0.35s ease, transform 0.35s ease;
  animation: fade-up 0.7s cubic-bezier(0.4, 0, 0.2, 1) both;
}

.feature-card:hover {
  border-color: rgba(0, 212, 255, 0.5);
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.1);
  transform: translateY(-4px);
}

.feature-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid rgba(0, 212, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--cyan);
  font-size: 1.2rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 0 12px rgba(0, 212, 255, 0.2);
  transition: box-shadow 0.3s ease;
}

.feature-card:hover .feature-icon-wrap {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.feature-title {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 1.15rem;
  color: var(--text);
  margin-bottom: 0.75rem;
}

.feature-desc {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.93rem;
  color: var(--muted);
  line-height: 1.65;
}

/* ── Trust Section ── */
.trust {
  padding: 8rem 2rem;
  background: var(--void);
}

.trust-card-wrap {
  position: relative;
  max-width: 700px;
  margin: 0 auto;
  padding: 2px;
  border-radius: 4px;
  background: linear-gradient(
    135deg,
    rgba(0, 212, 255, 0.6),
    rgba(123, 47, 255, 0.6),
    rgba(232, 160, 32, 0.6),
    rgba(0, 212, 255, 0.6)
  );
  background-size: 300% 300%;
  animation: border-spin 5s linear infinite;
}

@keyframes border-spin {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.trust-card {
  background: var(--surface);
  border-radius: 3px;
  padding: 3.5rem;
  text-align: center;
}

.trust-card-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.trust-shield {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(232, 160, 32, 0.12);
  border: 2px solid rgba(232, 160, 32, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gold);
  font-size: 2rem;
  margin-bottom: 1.75rem;
  box-shadow: 0 0 24px rgba(232, 160, 32, 0.2);
}

.trust-heading {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: clamp(1.4rem, 3vw, 2rem);
  color: var(--text);
  margin-bottom: 1rem;
}

.trust-desc {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.98rem;
  color: var(--muted);
  line-height: 1.7;
  max-width: 480px;
  margin: 0 auto 2rem;
}

.trust-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem;
}

.trust-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1.1rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(232, 160, 32, 0.25);
  color: var(--gold);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  letter-spacing: 0.03em;
  backdrop-filter: blur(6px);
}

.trust-badge i {
  font-size: 0.78rem;
}

/* ── Stats Strip ── */
.stats-strip {
  padding: 5rem 2rem;
  background: var(--surface);
  border-top: 1px solid rgba(0, 212, 255, 0.08);
  border-bottom: 1px solid rgba(0, 212, 255, 0.08);
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
}

.big-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 4rem;
}

.big-stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 600;
  color: var(--cyan);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.big-stat-label {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem;
  color: var(--muted);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.stats-vdivider {
  width: 1px;
  height: 64px;
  background: rgba(0, 212, 255, 0.15);
}

/* ── CTA Section ── */
.cta-section {
  position: relative;
  padding: 9rem 2rem;
  background: var(--void);
  text-align: center;
  overflow: hidden;
}

.cta-glow-bg {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: rgba(0, 212, 255, 0.05);
  filter: blur(100px);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.cta-inner {
  position: relative;
  z-index: 2;
}

.cta-heading {
  font-family: 'Syne', sans-serif;
  font-weight: 800;
  font-size: clamp(2rem, 4.5vw, 3.5rem);
  color: var(--text);
  margin-bottom: 1rem;
  line-height: 1.15;
}

.cta-sub {
  font-family: 'DM Sans', sans-serif;
  font-size: 1.05rem;
  color: var(--muted);
  max-width: 520px;
  margin: 0 auto 2.5rem;
  line-height: 1.7;
}

/* ── Footer ── */
.nf-footer {
  padding: 3rem 2rem;
  background: var(--void);
  border-top: 1px solid rgba(0, 212, 255, 0.1);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}

.footer-logo {
  font-family: 'Syne', sans-serif;
  font-weight: 700;
  font-size: 1.3rem;
  color: var(--text);
  text-shadow: 0 0 16px rgba(0, 212, 255, 0.4);
}

.footer-tagline {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  color: var(--muted);
  margin-top: 0.25rem;
}

.footer-links {
  display: flex;
  gap: 2rem;
}

.footer-link {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.88rem;
  color: var(--cyan);
  text-decoration: none;
  opacity: 0.75;
  transition: opacity 0.25s ease;
}

.footer-link:hover {
  opacity: 1;
}

.footer-copy {
  font-family: 'DM Sans', sans-serif;
  font-size: 0.78rem;
  color: var(--muted);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .nav-link {
    display: none;
  }

  .nav-links {
    gap: 1rem;
  }

  .hero-stats {
    flex-direction: column;
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .stat-divider {
    width: 60px;
    height: 1px;
  }

  .stats-row {
    flex-direction: column;
    gap: 2.5rem;
  }

  .stats-vdivider {
    width: 60px;
    height: 1px;
  }

  .big-stat {
    padding: 0;
  }

  .trust-card {
    padding: 2rem 1.5rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: clamp(2.5rem, 9vw, 3.5rem);
  }

  .hero-stats {
    width: 100%;
  }

  .stat-item {
    padding: 0;
  }
}
</style>
