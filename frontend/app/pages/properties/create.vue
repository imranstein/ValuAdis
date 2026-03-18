<template>
  <div class="create-property-page">
    <div class="page-header">
      <div class="header-content">
        <h1>Register Property</h1>
        <p>Complete the 7-step wizard to register a new property</p>
      </div>
      <Button
        label="Back to Properties"
        icon="pi pi-arrow-left"
        severity="secondary"
        outlined
        @click="router.push('/properties')"
      />
    </div>

    <PropertyWizard />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import PropertyWizard from '~/components/property/PropertyWizard.vue'

const router = useRouter()
</script>

<style scoped>
/* Design System Variables */
.create-property-page {
  /* Colors - Ethiopian Brand Palette */
  --primary: #078160;
  --primary-dark: #065043;
  --primary-light: #10b981;
  --cyan: #00d4ff;
  --cyan-dim: rgba(0, 212, 255, 0.15);
  --gold: #F59E0B;
  --violet: #1E3A8A;
  --success: #00e676;
  --error: #ff4444;
  --warning: #F59E0B;

  /* Text Colors */
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --text-light: #e2e8f0;

  /* Backgrounds */
  --bg-primary: #ffffff;
  --bg-secondary: #f8fafc;
  --bg-tertiary: #f1f5f9;
  --bg-dark: #0f172a;

  /* Borders */
  --border: rgba(7, 129, 96, 0.12);
  --border-light: rgba(0, 0, 0, 0.06);

  /* Typography */
  --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-display: 'Syne', 'Inter', sans-serif;
  --font-weight-light: 300;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --font-weight-extrabold: 800;

  /* Spacing Scale */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;

  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;

  /* Shadows */
  --shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.08);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.12);
  --shadow-lg: 0 4px 24px rgba(0, 0, 0, 0.15), 0 0 0 1px var(--border);
  --shadow-xl: 0 8px 40px rgba(0, 0, 0, 0.2);
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.25);
  --shadow-hover: 0 8px 40px rgba(0, 0, 0, 0.25);

  /* Transitions */
  --transition-fast: 0.15s ease;
  --transition-base: 0.25s ease;
  --transition-slow: 0.35s ease;

  max-width: 960px;
  margin: 0 auto;
  padding: 0 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  font-family: var(--font-family-base);
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
  min-height: 100vh;
}

/* Header Styling */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 2rem 2.5rem;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  border-radius: var(--radius-lg);
  color: var(--text-light);
  box-shadow: var(--shadow-lg), 0 0 30px rgba(7, 129, 96, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.05) 50%, transparent 70%);
  pointer-events: none;
}

.header-content {
  position: relative;
  z-index: 1;
  flex: 1;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: var(--font-weight-extrabold);
  letter-spacing: -0.5px;
  margin: 0 0 0.5rem;
  font-family: var(--font-family-display);
}

.header-content p {
  font-size: 1rem;
  font-weight: var(--font-weight-normal);
  opacity: 0.9;
  margin: 0;
  letter-spacing: 0.3px;
}

/* Button Styling in Header */
:deep(.page-header .p-button) {
  background: rgba(255, 255, 255, 0.15) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  color: var(--text-light) !important;
  transition: all var(--transition-base);
  backdrop-filter: blur(8px);
}

:deep(.page-header .p-button:hover) {
  background: rgba(255, 255, 255, 0.25) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.2);
}

@media (max-width: 768px) {
  .create-property-page {
    padding: 0 0.75rem 2rem;
  }

  .page-header {
    padding: 1.5rem 1.5rem;
    flex-direction: column;
    text-align: center;
  }

  .header-content h1 {
    font-size: 1.5rem;
  }

  .header-content p {
    font-size: 0.9rem;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 1.25rem 1rem;
  }

  .header-content h1 {
    font-size: 1.25rem;
  }
}
</style>
