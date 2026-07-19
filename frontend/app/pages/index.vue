<template>
  <main class="landing-page">
    <nav class="landing-nav" aria-label="Public navigation">
      <NuxtLink to="/" class="landing-brand">
        <span class="landing-mark" aria-hidden="true">V</span>
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
        <p class="hero-kicker">Municipal valuation infrastructure</p>
        <h1>
          A civic ledger for
          <em>Ethiopian valuation</em>
          work.
        </h1>
        <p class="hero-lede">
          Property and vehicle evidence, jurisdiction records, AI-assisted estimates, review
          approvals, and exportable audit packs — kept together in one operating desk.
        </p>
        <div class="hero-actions">
          <NuxtLink to="/login" class="btn-primary">Enter workspace</NuxtLink>
          <a href="#workflow" class="hero-secondary">See the workflow</a>
        </div>
      </div>

      <div class="hero-stage" aria-label="ValuAdis operating preview">
        <img
          src="/images/valuadis-civic-ledger-hero.png"
          alt=""
          class="hero-image"
          width="1200"
          height="900"
        />
        <div class="case-file">
          <div class="case-file-head">
            <span>Specimen record</span>
            <strong>Case file</strong>
          </div>
          <dl>
            <div>
              <dt>Jurisdiction</dt>
              <dd>Sub-city registry</dd>
            </div>
            <div>
              <dt>Asset class</dt>
              <dd>Mixed-use parcel</dd>
            </div>
            <div>
              <dt>Review state</dt>
              <dd>Draft &rarr; approved</dd>
            </div>
          </dl>
        </div>
        <div class="parcel-motif" aria-hidden="true">
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
        <p class="section-kicker">Operating desk</p>
        <h2>Built around the record, not the presentation.</h2>
      </div>

      <div class="desk-grid">
        <article class="desk-panel primary-panel">
          <div class="panel-meta">
            <span>Registry intake</span>
            <strong>Evidence stays connected</strong>
          </div>
          <h3>Property files keep location, valuation, and approval history in one dossier.</h3>
          <p>
            Municipal teams review parcel data, ownership evidence, comparable signals, and
            generated reports without moving between disconnected files.
          </p>
        </article>

        <article class="desk-panel metric-panel">
          <span>Taxable value</span>
          <strong>25% rule</strong>
          <p>Valuation output follows the configured proclamation calculation contract.</p>
        </article>

        <article class="desk-panel ledger-panel">
          <div class="ledger-row">
            <span>Residential parcels</span>
            <strong>Registry</strong>
          </div>
          <div class="ledger-row">
            <span>Commercial blocks</span>
            <strong>Review</strong>
          </div>
          <div class="ledger-row">
            <span>Vehicle asset files</span>
            <strong>Valuation</strong>
          </div>
          <div class="ledger-row">
            <span>Audit exports</span>
            <strong>Reporting</strong>
          </div>
        </article>
      </div>
    </section>

    <section id="workflow" class="workflow-band">
      <div class="section-head">
        <p class="section-kicker">Workflow</p>
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
        <p class="section-kicker">Assurance</p>
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
      <span>ValuAdis &mdash; civic valuation ledger</span>
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
    linear-gradient(rgba(27, 35, 29, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(27, 35, 29, 0.03) 1px, transparent 1px),
    var(--canvas);
  background-size: 56px 56px, 56px 56px, auto;
  color: var(--ink);
}

/* --- Navigation --- */
.landing-nav {
  position: fixed;
  inset: 0 0 auto;
  z-index: var(--z-sticky);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-5);
  height: 72px;
  border-bottom: 1px solid rgba(222, 216, 198, 0.85);
  background: rgba(246, 243, 234, 0.92);
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
  gap: var(--space-3);
  color: var(--ink);
  font-family: var(--serif);
  font-size: 26px;
  font-weight: 600;
}

.landing-mark {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: var(--radius);
  background: var(--green);
  color: var(--surface);
  font-size: 20px;
}

.landing-links {
  gap: var(--space-5);
}

.landing-links a,
.landing-login {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  transition: color var(--duration-normal) var(--ease), border-color var(--duration-normal) var(--ease), background-color var(--duration-normal) var(--ease);
}

.landing-links a:hover,
.landing-login:hover {
  color: var(--ink);
}

.landing-login {
  min-height: 40px;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  background: var(--surface);
  padding: 0 var(--space-4);
}

.landing-login:hover {
  border-color: var(--green);
  color: var(--green);
}

.landing-login:active,
.btn-primary:active {
  transform: scale(0.98);
}

/* --- Hero --- */
.landing-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(400px, 0.95fr);
  gap: clamp(28px, 5vw, 74px);
  min-height: 94vh;
  align-items: center;
  padding: 128px clamp(18px, 5vw, 64px) 148px;
  border-bottom: 1px solid var(--line);
}

.hero-copy {
  position: relative;
  z-index: 2;
  max-width: 760px;
  animation: rise 640ms var(--ease) both;
}

.hero-kicker,
.section-kicker {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin: 0 0 var(--space-4);
  color: var(--gold);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.hero-kicker::before,
.section-kicker::before {
  content: "";
  width: 34px;
  height: 2px;
  background: var(--gold-bright);
}

.hero-copy h1 {
  margin: 0;
  font-family: var(--serif);
  font-size: clamp(52px, 8vw, 108px);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 0.98;
}

.hero-copy h1 em {
  color: var(--green);
  font-style: italic;
  font-weight: 500;
}

.hero-lede {
  max-width: 620px;
  margin: var(--space-5) 0 0;
  color: var(--ink-soft);
  font-size: clamp(17px, 2vw, 20px);
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  margin-top: var(--space-6);
}

.btn-primary {
  min-height: 48px;
  justify-content: center;
  border-radius: var(--radius);
  background: var(--green);
  padding: 0 var(--space-5);
  color: var(--surface);
  font-weight: 700;
  transition: transform var(--duration-fast) var(--ease), background-color var(--duration-normal) var(--ease);
}

.btn-primary:hover {
  background: var(--green-dark);
}

.hero-secondary {
  color: var(--ink-soft);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-decoration: none;
  text-transform: uppercase;
  border-bottom: 2px solid var(--gold-bright);
  padding-bottom: 3px;
  transition: color var(--duration-normal) var(--ease);
}

.hero-secondary:hover {
  color: var(--green);
}

.hero-stage {
  position: relative;
  min-height: min(64vh, 640px);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius-lg);
  background: var(--surface);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  animation: rise 640ms var(--ease) 120ms both;
}

.hero-image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  opacity: 0.82;
  filter: saturate(0.78) contrast(0.98) sepia(0.06);
}

.hero-stage::after {
  position: absolute;
  inset: 0;
  content: "";
  background:
    linear-gradient(180deg, rgba(252, 250, 243, 0.05), rgba(19, 31, 24, 0.22)),
    linear-gradient(90deg, rgba(252, 250, 243, 0.8) 0%, rgba(252, 250, 243, 0.24) 44%, rgba(19, 31, 24, 0.18) 100%);
}

.case-file {
  position: absolute;
  left: var(--space-5);
  bottom: var(--space-5);
  z-index: 2;
  width: min(360px, calc(100% - 48px));
  border: 1px solid rgba(222, 216, 198, 0.92);
  border-radius: var(--radius);
  background: rgba(252, 250, 243, 0.94);
  box-shadow: var(--shadow-sm);
  backdrop-filter: blur(12px);
}

.case-file-head {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  border-bottom: 1px solid var(--line);
  padding: var(--space-3) var(--space-4);
}

.case-file-head span,
.case-file dt,
.hero-ledger span,
.metric-panel span,
.assurance-ledger span {
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.case-file-head span {
  color: var(--gold);
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
  gap: var(--space-3);
  margin: 0;
  padding: var(--space-4);
}

.case-file dl div {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
}

.case-file dd {
  margin: 0;
  color: var(--ink);
  font-size: 12px;
  text-align: right;
}

/* Cadastral parcel motif */
.parcel-motif {
  position: absolute;
  top: var(--space-5);
  right: var(--space-5);
  z-index: 2;
  display: grid;
  grid-template-columns: 1fr 0.8fr;
  gap: var(--space-2);
  width: min(220px, 42%);
  aspect-ratio: 1.2;
  opacity: 0.85;
}

.parcel-motif span {
  border: 1px solid rgba(199, 154, 62, 0.72);
  background: rgba(243, 233, 208, 0.4);
}

.parcel-motif span:nth-child(1) {
  grid-row: span 2;
  border-color: rgba(35, 92, 67, 0.55);
  background: rgba(223, 232, 221, 0.5);
}

.parcel-motif span:nth-child(3) {
  margin-left: 22px;
}

.hero-ledger {
  position: absolute;
  right: clamp(18px, 5vw, 64px);
  bottom: 40px;
  left: clamp(18px, 5vw, 64px);
  display: grid;
  grid-template-columns: 1.1fr 0.9fr 0.8fr;
  border: 1px solid var(--line-strong);
  border-top: 2px solid var(--gold-bright);
  border-radius: var(--radius);
  background: rgba(252, 250, 243, 0.95);
  box-shadow: var(--shadow-sm);
  animation: rise 640ms var(--ease) 240ms both;
}

.hero-ledger div {
  min-width: 0;
  padding: var(--space-4) var(--space-4);
  border-right: 1px solid var(--line);
}

.hero-ledger div:last-child {
  border-right: 0;
}

.hero-ledger strong {
  display: block;
  margin-top: var(--space-2);
  color: var(--green);
  font-size: clamp(15px, 1.6vw, 20px);
  font-weight: 600;
  line-height: 1.2;
}

/* --- Bands --- */
.landing-band,
.workflow-band,
.assurance-band {
  padding: clamp(64px, 8vw, 108px) clamp(18px, 5vw, 64px);
}

.section-head {
  max-width: 860px;
  margin-bottom: var(--space-6);
}

.section-head h2,
.assurance-copy h2 {
  margin: 0;
  font-family: var(--serif);
  font-size: clamp(38px, 5.4vw, 68px);
  font-weight: 600;
  letter-spacing: -0.005em;
  line-height: 1.02;
}

.desk-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(260px, 0.58fr);
  grid-template-areas:
    "primary metric"
    "primary table";
  gap: var(--space-4);
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
  font-family: var(--serif);
  font-size: clamp(32px, 4.6vw, 58px);
  font-weight: 600;
  line-height: 1.04;
}

.primary-panel p {
  max-width: 720px;
  margin: var(--space-5) 0 0;
  color: var(--muted);
  font-size: 17px;
  line-height: 1.62;
}

.panel-meta {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.panel-meta strong {
  color: var(--green);
}

.metric-panel {
  grid-area: metric;
  min-height: 190px;
  border-top: 2px solid var(--gold-bright);
  padding: var(--space-5);
}

.metric-panel strong {
  display: block;
  margin-top: var(--space-4);
  color: var(--green);
  font-size: clamp(30px, 3.6vw, 44px);
  font-weight: 600;
  line-height: 1;
}

.metric-panel p {
  margin: var(--space-4) 0 0;
  color: var(--muted);
}

.ledger-panel {
  grid-area: table;
  overflow: hidden;
}

.ledger-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--line);
}

.ledger-row:last-child {
  border-bottom: 0;
}

.ledger-row span {
  min-width: 0;
  color: var(--ink-soft);
  font-weight: 600;
}

.ledger-row strong {
  color: var(--gold);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  white-space: nowrap;
}

/* --- Workflow --- */
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
  background: var(--line-strong);
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  overflow: hidden;
}

.workflow-list li {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr);
  gap: var(--space-4);
  min-height: 190px;
  background: var(--surface);
  padding: var(--space-5);
}

.workflow-list li:nth-child(2),
.workflow-list li:nth-child(3) {
  background: var(--canvas);
}

.workflow-list span {
  color: var(--gold);
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
}

.workflow-list h3 {
  margin: 0 0 var(--space-3);
  font-family: var(--serif);
  font-size: 34px;
  font-weight: 600;
}

.workflow-list p {
  max-width: 520px;
  margin: 0;
  color: var(--muted);
  line-height: 1.58;
}

/* --- Assurance --- */
.assurance-band {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(360px, 1.1fr);
  gap: clamp(30px, 6vw, 92px);
  align-items: end;
}

.assurance-copy p:not(.section-kicker) {
  max-width: 640px;
  margin: var(--space-5) 0 0;
  color: var(--muted);
  font-size: 17px;
  line-height: 1.62;
}

.assurance-ledger {
  display: grid;
  border: 1px solid var(--line);
  border-top: 2px solid var(--gold-bright);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.assurance-ledger div {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-5) var(--space-5);
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

/* --- Footer --- */
.landing-footer {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  border-top: 1px solid var(--line);
  padding: var(--space-6) clamp(18px, 5vw, 64px);
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
}

.landing-footer a {
  color: var(--green);
  text-decoration: none;
  transition: color var(--duration-normal) var(--ease);
}

.landing-footer a:hover {
  color: var(--green-dark);
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(14px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* --- Responsive --- */
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
    font-size: 22px;
  }

  .landing-login {
    min-height: 40px;
  }

  .landing-hero {
    padding-top: 104px;
  }

  .hero-stage {
    min-height: 360px;
  }

  .hero-actions {
    align-items: flex-start;
    flex-direction: column;
    gap: var(--space-4);
  }

  .case-file {
    left: var(--space-3);
    right: var(--space-3);
    bottom: var(--space-3);
    width: auto;
  }

  .parcel-motif {
    top: var(--space-3);
    right: var(--space-3);
    width: 46%;
  }

  .case-file dl div,
  .case-file-head,
  .assurance-ledger div,
  .ledger-row {
    align-items: flex-start;
    flex-direction: column;
    gap: var(--space-1);
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
