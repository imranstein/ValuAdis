<template>
  <main class="landing-page">
    <nav class="landing-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="landing-brand">
        <span class="landing-mark">V</span>
        <span>ValuAdis</span>
      </NuxtLink>
      <div class="landing-links">
        <a href="#operating-desk">Operating desk</a>
        <a href="#workflow">Workflow</a>
        <a href="#assurance">Assurance</a>
      </div>
      <NuxtLink to="/login" class="landing-login">Sign in</NuxtLink>
    </nav>

    <section class="landing-hero">
      <div class="hero-copy">
        <p class="page-kicker">Municipal valuation infrastructure</p>
        <h1>ValuAdis</h1>
        <p class="hero-lede">
          A civic ledger for Ethiopian valuation teams: property evidence, jurisdiction records,
          AI-assisted estimates, approvals, and exportable audit packs in one operating desk.
        </p>
        <div class="hero-actions">
          <NuxtLink to="/login" class="btn-primary">Enter workspace</NuxtLink>
        </div>
      </div>

      <div class="hero-stage" aria-label="ValuAdis operating preview">
        <img src="/images/valuadis-civic-ledger-hero.png" alt="" class="hero-image" />
        <div class="case-file">
          <div class="case-file-head">
            <span>Case file</span>
            <strong>AA-BOL-0427</strong>
          </div>
          <dl>
            <div>
              <dt>Jurisdiction</dt>
              <dd>Bole Sub-City</dd>
            </div>
            <div>
              <dt>Asset class</dt>
              <dd>Mixed-use parcel</dd>
            </div>
            <div>
              <dt>Review state</dt>
              <dd>Valuer approved</dd>
            </div>
          </dl>
        </div>
        <div class="map-ledger" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div class="hero-ledger" aria-label="Platform capabilities">
        <div>
          <span>Records</span>
          <strong>Property / vehicle</strong>
        </div>
        <div>
          <span>Review path</span>
          <strong>Draft to approved</strong>
        </div>
        <div>
          <span>Export formats</span>
          <strong>PDF / CSV</strong>
        </div>
      </div>
    </section>

    <section id="operating-desk" class="landing-band desk-band">
      <div class="section-head">
        <p class="page-kicker">Operating desk</p>
        <h2>Built around the record, not the presentation.</h2>
      </div>

      <div class="desk-grid">
        <article class="desk-panel primary-panel">
          <div class="panel-meta">
            <span>Registry intake</span>
            <strong>Evidence complete</strong>
          </div>
          <h3>Property files stay connected to location, valuation, and approval history.</h3>
          <p>
            Municipal teams can review parcel data, ownership evidence, comparable signals, and
            generated reports without moving between disconnected files.
          </p>
        </article>

        <article class="desk-panel metric-panel">
          <span>Taxable value</span>
          <strong>25% rule</strong>
          <p>Valuation output follows the configured proclamation calculation contract.</p>
        </article>

        <article class="desk-panel table-panel">
          <div class="ledger-row">
            <span>Residential parcels</span>
            <strong>Ready</strong>
          </div>
          <div class="ledger-row">
            <span>Commercial blocks</span>
            <strong>Review</strong>
          </div>
          <div class="ledger-row">
            <span>Vehicle asset files</span>
            <strong>Synced</strong>
          </div>
          <div class="ledger-row">
            <span>Audit exports</span>
            <strong>Queued</strong>
          </div>
        </article>
      </div>
    </section>

    <section id="workflow" class="workflow-band">
      <div class="section-head">
        <p class="page-kicker">Workflow</p>
        <h2>One disciplined path from intake to certificate.</h2>
      </div>

      <ol class="workflow-list">
        <li>
          <span>01</span>
          <div>
            <h3>Capture</h3>
            <p>Register property, vehicle, spatial, and ownership evidence with clear jurisdiction context.</p>
          </div>
        </li>
        <li>
          <span>02</span>
          <div>
            <h3>Estimate</h3>
            <p>Run valuation logic and compare the AI estimate against the record before approval.</p>
          </div>
        </li>
        <li>
          <span>03</span>
          <div>
            <h3>Approve</h3>
            <p>Move records through review states with audit history attached to every material decision.</p>
          </div>
        </li>
        <li>
          <span>04</span>
          <div>
            <h3>Export</h3>
            <p>Generate valuation reports, certificates, and operational CSVs for municipal reporting.</p>
          </div>
        </li>
      </ol>
    </section>

    <section id="assurance" class="assurance-band">
      <div class="assurance-copy">
        <p class="page-kicker">Assurance</p>
        <h2>Controls that make public-sector review defensible.</h2>
        <p>
          ValuAdis keeps role access, workflow state, valuation evidence, and export history visible
          so administrators can prove how a figure moved from draft to approved record.
        </p>
      </div>
      <div class="assurance-ledger" aria-label="Assurance controls">
        <div>
          <span>Protected routes</span>
          <strong>Role gated</strong>
        </div>
        <div>
          <span>Reports</span>
          <strong>Traceable</strong>
        </div>
        <div>
          <span>Configuration</span>
          <strong>Environment scoped</strong>
        </div>
      </div>
    </section>

    <footer class="landing-footer">
      <span>ValuAdis civic valuation ledger</span>
      <NuxtLink to="/login">Workspace sign in</NuxtLink>
    </footer>
  </main>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'landing' })
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  overflow-x: hidden;
  background:
    linear-gradient(rgba(23, 26, 23, 0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(23, 26, 23, 0.025) 1px, transparent 1px),
    var(--canvas);
  background-size: 56px 56px, 56px 56px, auto;
  color: var(--ink);
}

.landing-nav {
  position: fixed;
  inset: 0 0 auto;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
  height: 72px;
  border-bottom: 1px solid rgba(215, 221, 212, 0.84);
  background: rgba(246, 247, 244, 0.92);
  padding: 0 clamp(18px, 5vw, 64px);
  backdrop-filter: blur(14px);
}

.landing-brand,
.landing-links,
.landing-login,
.btn-primary {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
}

.landing-brand {
  gap: 10px;
  color: var(--ink);
  font-family: var(--display);
  font-size: 24px;
  font-weight: 750;
}

.landing-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
}

.landing-links {
  gap: 26px;
}

.landing-links a,
.landing-login {
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  transition: color 160ms var(--ease), border-color 160ms var(--ease), background-color 160ms var(--ease);
}

.landing-links a:hover,
.landing-login:hover {
  color: var(--ink);
}

.landing-login {
  min-height: 38px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 14px;
}

.landing-login:active,
.btn-primary:active {
  transform: scale(0.98);
}

.landing-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(420px, 1.1fr);
  gap: clamp(28px, 5vw, 74px);
  min-height: 94vh;
  align-items: center;
  padding: 122px clamp(18px, 5vw, 64px) 132px;
  border-bottom: 1px solid var(--line);
}

.hero-copy {
  position: relative;
  z-index: 2;
  max-width: 760px;
}

.page-kicker {
  margin: 0 0 16px;
  color: var(--green);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero-copy h1 {
  margin: 0;
  font-family: var(--display);
  font-size: clamp(76px, 12vw, 164px);
  font-weight: 760;
  letter-spacing: 0;
  line-height: 0.84;
}

.hero-lede {
  max-width: 660px;
  margin: 28px 0 0;
  color: var(--ink-soft);
  font-size: clamp(18px, 2vw, 23px);
  line-height: 1.55;
}

.hero-actions {
  display: flex;
  margin-top: 32px;
}

.btn-primary {
  min-height: 46px;
  justify-content: center;
  border-radius: var(--radius);
  background: var(--green);
  padding: 0 18px;
  color: var(--surface);
  font-weight: 850;
  transition: transform 160ms var(--ease), background-color 160ms var(--ease);
}

.btn-primary:hover {
  background: var(--green-dark);
}

.hero-stage {
  position: relative;
  min-height: min(68vh, 680px);
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--surface);
  overflow: hidden;
  box-shadow: var(--shadow);
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  opacity: 0.82;
  filter: saturate(0.8) contrast(0.98);
}

.hero-stage::after {
  position: absolute;
  inset: 0;
  content: "";
  background:
    linear-gradient(180deg, rgba(252, 252, 250, 0.06), rgba(23, 26, 23, 0.18)),
    linear-gradient(90deg, rgba(252, 252, 250, 0.82) 0%, rgba(252, 252, 250, 0.28) 44%, rgba(23, 26, 23, 0.16) 100%);
}

.case-file {
  position: absolute;
  left: 24px;
  bottom: 24px;
  z-index: 2;
  width: min(360px, calc(100% - 48px));
  border: 1px solid rgba(215, 221, 212, 0.92);
  border-radius: var(--radius);
  background: rgba(252, 252, 250, 0.92);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(12px);
}

.case-file-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--line);
  padding: 14px 16px;
}

.case-file-head span,
.case-file dt,
.hero-ledger span,
.metric-panel span,
.assurance-ledger span {
  color: var(--muted);
  font-size: 11px;
  font-weight: 850;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.case-file-head strong,
.case-file dd,
.hero-ledger strong,
.metric-panel strong,
.ledger-row strong,
.assurance-ledger strong {
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
}

.case-file dl {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 16px;
}

.case-file dl div {
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.case-file dd {
  margin: 0;
  color: var(--ink);
  font-size: 12px;
  text-align: right;
}

.map-ledger {
  position: absolute;
  top: 24px;
  right: 24px;
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 0.8fr;
  gap: 8px;
  width: min(220px, 42%);
  aspect-ratio: 1.2;
  opacity: 0.82;
}

.map-ledger span {
  border: 1px solid rgba(31, 107, 79, 0.44);
  background: rgba(223, 233, 227, 0.62);
}

.map-ledger span:nth-child(1) {
  grid-row: span 2;
}

.map-ledger span:nth-child(3) {
  margin-left: 22px;
}

.hero-ledger {
  position: absolute;
  right: clamp(18px, 5vw, 64px);
  bottom: 34px;
  left: clamp(18px, 5vw, 64px);
  display: grid;
  grid-template-columns: 1.1fr 0.9fr 0.8fr;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: rgba(252, 252, 250, 0.94);
  box-shadow: var(--shadow-sm);
}

.hero-ledger div {
  min-width: 0;
  padding: 17px 18px;
  border-right: 1px solid var(--line);
}

.hero-ledger div:last-child {
  border-right: 0;
}

.hero-ledger strong {
  display: block;
  margin-top: 8px;
  color: var(--ink);
  font-size: clamp(18px, 2vw, 27px);
  line-height: 1.1;
}

.landing-band,
.workflow-band,
.assurance-band {
  padding: clamp(64px, 8vw, 108px) clamp(18px, 5vw, 64px);
}

.section-head {
  max-width: 820px;
  margin-bottom: 30px;
}

.section-head h2,
.assurance-copy h2 {
  margin: 0;
  font-family: var(--display);
  font-size: clamp(40px, 6vw, 76px);
  font-weight: 760;
  letter-spacing: 0;
  line-height: 0.98;
}

.desk-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(260px, 0.58fr);
  grid-template-areas:
    "primary metric"
    "primary table";
  gap: 14px;
}

.desk-panel {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
}

.primary-panel {
  grid-area: primary;
  min-height: 470px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: clamp(24px, 4vw, 44px);
}

.primary-panel h3 {
  max-width: 830px;
  margin: 0;
  font-family: var(--display);
  font-size: clamp(34px, 5vw, 68px);
  font-weight: 740;
  line-height: 1;
}

.primary-panel p {
  max-width: 720px;
  margin: 24px 0 0;
  color: var(--muted);
  font-size: 17px;
  line-height: 1.62;
}

.panel-meta {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 850;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.panel-meta strong {
  color: var(--green);
}

.metric-panel {
  grid-area: metric;
  min-height: 190px;
  padding: 24px;
}

.metric-panel strong {
  display: block;
  margin-top: 18px;
  font-size: clamp(32px, 4vw, 50px);
  line-height: 1;
}

.metric-panel p {
  margin: 16px 0 0;
  color: var(--muted);
}

.table-panel {
  grid-area: table;
  overflow: hidden;
}

.ledger-row {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 20px;
  border-bottom: 1px solid var(--line);
}

.ledger-row:last-child {
  border-bottom: 0;
}

.ledger-row span {
  min-width: 0;
  color: var(--ink-soft);
  font-weight: 740;
}

.ledger-row strong {
  color: var(--green);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.workflow-band {
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  background: var(--surface-2);
}

.workflow-list {
  display: grid;
  grid-template-columns: 0.82fr 1.08fr;
  gap: 1px;
  margin: 0;
  padding: 0;
  list-style: none;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.workflow-list li {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr);
  gap: 20px;
  min-height: 190px;
  background: var(--surface);
  padding: 24px;
}

.workflow-list li:nth-child(2),
.workflow-list li:nth-child(3) {
  background: var(--canvas);
}

.workflow-list span {
  color: var(--green);
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 850;
}

.workflow-list h3 {
  margin: 0 0 14px;
  font-family: var(--display);
  font-size: 34px;
  font-weight: 740;
}

.workflow-list p {
  max-width: 520px;
  margin: 0;
  color: var(--muted);
  line-height: 1.58;
}

.assurance-band {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(360px, 1.1fr);
  gap: clamp(30px, 6vw, 92px);
  align-items: end;
}

.assurance-copy p:not(.page-kicker) {
  max-width: 640px;
  margin: 24px 0 0;
  color: var(--muted);
  font-size: 17px;
  line-height: 1.62;
}

.assurance-ledger {
  display: grid;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.assurance-ledger div {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 22px 24px;
  border-bottom: 1px solid var(--line);
}

.assurance-ledger div:last-child {
  border-bottom: 0;
}

.assurance-ledger strong {
  color: var(--green);
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

.landing-footer {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  border-top: 1px solid var(--line);
  padding: 28px clamp(18px, 5vw, 64px);
  color: var(--muted);
  font-size: 13px;
  font-weight: 760;
}

.landing-footer a {
  color: var(--green);
  text-decoration: none;
  transition: color 160ms var(--ease);
}

.landing-footer a:hover {
  color: var(--green-dark);
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 1ms !important;
  }
}

@media (max-width: 980px) {
  .landing-links {
    display: none;
  }

  .landing-hero,
  .desk-grid,
  .workflow-list,
  .assurance-band {
    grid-template-columns: 1fr;
  }

  .landing-hero {
    padding-bottom: 28px;
  }

  .hero-stage {
    min-height: 440px;
  }

  .hero-ledger {
    position: static;
    grid-template-columns: 1fr;
    margin-top: 0;
  }

  .hero-ledger div {
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .hero-ledger div:last-child {
    border-bottom: 0;
  }

  .desk-grid {
    grid-template-areas:
      "primary"
      "metric"
      "table";
  }

  .primary-panel {
    min-height: 360px;
  }
}

@media (max-width: 640px) {
  .landing-nav {
    height: 64px;
  }

  .landing-brand {
    font-size: 21px;
  }

  .landing-login {
    min-height: 36px;
  }

  .landing-hero {
    padding-top: 104px;
  }

  .hero-stage {
    min-height: 360px;
  }

  .case-file {
    left: 14px;
    right: 14px;
    bottom: 14px;
    width: auto;
  }

  .map-ledger {
    top: 14px;
    right: 14px;
    width: 46%;
  }

  .case-file dl div,
  .case-file-head,
  .assurance-ledger div,
  .ledger-row {
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }

  .case-file dd {
    text-align: left;
  }

  .workflow-list li {
    grid-template-columns: 1fr;
    min-height: 0;
  }

  .landing-footer {
    flex-direction: column;
  }
}
</style>
