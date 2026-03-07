<template>
  <div class="luxury-landing">
    <!-- Navigation -->
    <nav class="luxury-nav" :class="{ scrolled: isScrolled }">
      <div class="nav-inner">
        <div class="logo">
          <span class="logo-text">ValuAdis</span>
          <span class="logo-tagline">Valuation Excellence</span>
        </div>
        <div class="nav-links">
          <a href="#features" class="nav-link">Features</a>
          <a href="#trust" class="nav-link">Compliance</a>
          <NuxtLink to="/login" class="nav-cta">
            <span class="cta-text">Sign In</span>
            <i class="pi pi-arrow-right cta-icon"></i>
          </NuxtLink>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg">
        <div class="hero-gradient"></div>
        <div class="hero-pattern"></div>
        <div class="hero-glow hero-glow-1"></div>
        <div class="hero-glow hero-glow-2"></div>
      </div>
      <div class="hero-content">
        <p class="hero-eyebrow animate-fade-up">Ethiopian Property & Vehicle Valuation</p>
        <h1 class="hero-title animate-fade-up animate-delay-1">
          Precision Valuation.<br />
          <span class="hero-title-accent">Ethiopian Excellence.</span>
        </h1>
        <p class="hero-subtitle animate-fade-up animate-delay-2">
          Trusted valuation platform for properties and vehicles. 
          Proclamation 1365/2025 compliant. Audit-ready reports.
        </p>
        <div class="hero-actions animate-fade-up animate-delay-3">
          <NuxtLink to="/login" class="btn-luxury btn-primary">
            <span>Get Started</span>
            <i class="pi pi-arrow-right"></i>
          </NuxtLink>
          <a href="#features" class="btn-luxury btn-outline">Learn More</a>
        </div>
      </div>
      <div class="hero-scroll">
        <div class="scroll-indicator"></div>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="features">
      <div class="section-inner">
        <p class="section-eyebrow">What We Offer</p>
        <h2 class="section-title">Comprehensive Valuation Solutions</h2>
        <div class="features-grid">
          <div 
            v-for="(feature, i) in features" 
            :key="feature.title"
            class="feature-card"
            :style="{ animationDelay: `${i * 0.1}s` }"
          >
            <div class="feature-icon">
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
        <div class="trust-card">
          <div class="trust-icon">
            <i class="pi pi-shield"></i>
          </div>
          <div class="trust-content">
            <h2>Proclamation 1365/2025 Compliant</h2>
            <p>All valuations follow Ethiopian government regulations. Fully audit-ready with complete traceability.</p>
            <div class="trust-badges">
              <span class="trust-badge">100% Audit Ready</span>
              <span class="trust-badge">Tax Compliant</span>
              <span class="trust-badge">Zero Compliance Issues</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="section-inner">
        <h2 class="cta-title">Ready to streamline your valuations?</h2>
        <p class="cta-subtitle">Join professionals who trust ValuAdis for accurate, compliant property and vehicle valuations.</p>
        <NuxtLink to="/login" class="btn-luxury btn-primary btn-large">
          <span>Sign In to Dashboard</span>
          <i class="pi pi-arrow-right"></i>
        </NuxtLink>
      </div>
    </section>

    <!-- Footer -->
    <footer class="luxury-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <span class="logo-text">ValuAdis</span>
          <p>Ethiopian Property Valuation Platform</p>
        </div>
        <div class="footer-links">
          <NuxtLink to="/login">Sign In</NuxtLink>
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
/* Luxury Design Tokens */
.luxury-landing {
  --luxury-black: #0a0a0a;
  --luxury-cream: #f5f0e8;
  --luxury-ivory: #fffff5;
  --luxury-gold: #d4af37;
  --luxury-gold-light: #e8c547;
  --luxury-rose: #b76e79;
  --luxury-navy: #1a1a2e;
  --luxury-charcoal: #1c1c1c;
  --luxury-muted: rgba(245, 240, 232, 0.7);
}

/* Navigation */
.luxury-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 1.5rem 2rem;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.luxury-nav.scrolled {
  background: rgba(10, 10, 10, 0.92);
  backdrop-filter: blur(12px);
  box-shadow: 0 1px 0 rgba(212, 175, 55, 0.1);
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-text {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--luxury-ivory);
  letter-spacing: 0.08em;
}

.logo-tagline {
  display: block;
  font-size: 0.65rem;
  color: var(--luxury-gold);
  letter-spacing: 0.2em;
  text-transform: uppercase;
  margin-top: 2px;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2.5rem;
}

.nav-link {
  color: var(--luxury-muted);
  font-size: 0.9rem;
  text-decoration: none;
  letter-spacing: 0.05em;
  transition: color 0.3s ease;
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  width: 0;
  height: 1px;
  background: var(--luxury-gold);
  transition: width 0.3s ease;
}

.nav-link:hover {
  color: var(--luxury-ivory);
}

.nav-link:hover::after {
  width: 100%;
}

.nav-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  background: transparent;
  border: 1px solid var(--luxury-gold);
  color: var(--luxury-gold);
  text-decoration: none;
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  transition: all 0.3s ease;
}

.nav-cta:hover {
  background: var(--luxury-gold);
  color: var(--luxury-black);
}

.cta-icon {
  font-size: 0.75rem;
  transition: transform 0.3s ease;
}

.nav-cta:hover .cta-icon {
  transform: translateX(4px);
}

/* Hero */
.hero {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
  background: var(--luxury-black);
}

.hero-bg {
  position: absolute;
  inset: 0;
}

.hero-gradient {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% 0%, rgba(26, 26, 46, 0.9) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(212, 175, 55, 0.08) 0%, transparent 50%);
}

.hero-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(212, 175, 55, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(212, 175, 55, 0.03) 1px, transparent 1px);
  background-size: 60px 60px;
}

.hero-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: glow-pulse 8s ease-in-out infinite;
}

.hero-glow-1 {
  width: 400px;
  height: 400px;
  background: var(--luxury-gold);
  top: -100px;
  right: -100px;
}

.hero-glow-2 {
  width: 300px;
  height: 300px;
  background: var(--luxury-rose);
  bottom: -50px;
  left: -50px;
  animation-delay: -4s;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.1); }
}

.hero-content {
  position: relative;
  z-index: 2;
  text-align: center;
  padding: 0 2rem;
  max-width: 800px;
}

.hero-eyebrow {
  font-size: 0.8rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--luxury-gold);
  margin-bottom: 1.5rem;
}

.hero-title {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 500;
  line-height: 1.15;
  color: var(--luxury-ivory);
  margin-bottom: 1.5rem;
}

.hero-title-accent {
  color: var(--luxury-gold);
  font-style: italic;
}

.hero-subtitle {
  font-size: 1.1rem;
  color: var(--luxury-muted);
  line-height: 1.7;
  margin-bottom: 2.5rem;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-luxury {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1rem 2rem;
  font-size: 0.9rem;
  letter-spacing: 0.08em;
  text-decoration: none;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border: none;
}

.btn-luxury.btn-primary {
  background: linear-gradient(135deg, var(--luxury-gold) 0%, #c9a227 100%);
  color: var(--luxury-black);
  box-shadow: 0 4px 20px rgba(212, 175, 55, 0.3);
}

.btn-luxury.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(212, 175, 55, 0.4);
}

.btn-luxury.btn-primary i {
  transition: transform 0.3s ease;
}

.btn-luxury.btn-primary:hover i {
  transform: translateX(4px);
}

.btn-luxury.btn-outline {
  background: transparent;
  border: 1px solid rgba(245, 240, 232, 0.4);
  color: var(--luxury-cream);
}

.btn-luxury.btn-outline:hover {
  border-color: var(--luxury-gold);
  color: var(--luxury-gold);
}

.btn-luxury.btn-large {
  padding: 1.2rem 2.5rem;
  font-size: 1rem;
}

.hero-scroll {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
}

.scroll-indicator {
  width: 24px;
  height: 40px;
  border: 2px solid rgba(212, 175, 55, 0.5);
  border-radius: 12px;
  position: relative;
  animation: scroll-bounce 2s ease-in-out infinite;
}

.scroll-indicator::before {
  content: '';
  position: absolute;
  top: 8px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 8px;
  background: var(--luxury-gold);
  border-radius: 2px;
}

@keyframes scroll-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8px); }
}

/* Animations */
.animate-fade-up {
  opacity: 0;
  transform: translateY(24px);
  animation: fade-up 0.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.animate-delay-1 { animation-delay: 0.1s; }
.animate-delay-2 { animation-delay: 0.2s; }
.animate-delay-3 { animation-delay: 0.3s; }

@keyframes fade-up {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Features */
.features {
  padding: 8rem 2rem;
  background: var(--luxury-charcoal);
}

.section-inner {
  max-width: 1200px;
  margin: 0 auto;
}

.section-eyebrow {
  font-size: 0.75rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--luxury-gold);
  margin-bottom: 0.75rem;
}

.section-title {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 500;
  color: var(--luxury-ivory);
  margin-bottom: 4rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 2rem;
}

.feature-card {
  padding: 2rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(212, 175, 55, 0.15);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fade-up 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
  opacity: 0;
}

.feature-card:hover {
  border-color: rgba(212, 175, 55, 0.4);
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feature-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(212, 175, 55, 0.05) 100%);
  color: var(--luxury-gold);
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
}

.feature-title {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: 1.35rem;
  font-weight: 500;
  color: var(--luxury-ivory);
  margin-bottom: 0.75rem;
}

.feature-desc {
  font-size: 0.95rem;
  color: var(--luxury-muted);
  line-height: 1.6;
}

/* Trust */
.trust {
  padding: 6rem 2rem;
  background: var(--luxury-black);
}

.trust-card {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 2.5rem;
  padding: 3rem;
  background: rgba(26, 26, 46, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.trust-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--luxury-gold) 0%, #c9a227 100%);
  color: var(--luxury-black);
  font-size: 2rem;
  flex-shrink: 0;
}

.trust-content h2 {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: 1.75rem;
  font-weight: 500;
  color: var(--luxury-ivory);
  margin-bottom: 0.75rem;
}

.trust-content p {
  color: var(--luxury-muted);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.trust-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.trust-badge {
  padding: 0.4rem 1rem;
  background: rgba(212, 175, 55, 0.15);
  color: var(--luxury-gold);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
}

/* CTA */
.cta {
  padding: 8rem 2rem;
  background: var(--luxury-charcoal);
  text-align: center;
}

.cta-title {
  font-family: 'Cormorant Garamond', 'Georgia', serif;
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 500;
  color: var(--luxury-ivory);
  margin-bottom: 0.75rem;
}

.cta-subtitle {
  color: var(--luxury-muted);
  margin-bottom: 2rem;
  font-size: 1.1rem;
}

/* Footer */
.luxury-footer {
  padding: 3rem 2rem;
  background: var(--luxury-black);
  border-top: 1px solid rgba(212, 175, 55, 0.1);
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-brand .logo-text {
  font-size: 1.25rem;
}

.footer-brand p {
  font-size: 0.85rem;
  color: var(--luxury-muted);
  margin-top: 0.25rem;
}

.footer-links {
  margin: 1.5rem 0;
}

.footer-links a {
  color: var(--luxury-gold);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: var(--luxury-gold-light);
}

.footer-copy {
  font-size: 0.8rem;
  color: var(--luxury-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .nav-links {
    gap: 1.5rem;
  }

  .nav-link {
    display: none;
  }

  .trust-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
