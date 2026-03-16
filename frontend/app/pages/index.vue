<template>
  <div class="landing">
    <canvas ref="particleCanvas" class="particle-canvas"></canvas>

    <nav class="nav" :class="{ scrolled: isScrolled }">
      <div class="nav-inner">
        <div class="logo">
          <span class="logo-mark">VA</span>
          <div><span class="logo-name">ValuAdis</span><span class="logo-sub">// PROPERTY INTELLIGENCE</span></div>
        </div>
        <div class="nav-links">
          <a href="#features" class="nav-link">Features</a>
          <a href="#trust" class="nav-link">Compliance</a>
          <NuxtLink to="/login" class="nav-cta">Launch App <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M1 6.5h11M6.5 1l5.5 5.5-5.5 5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></NuxtLink>
        </div>
      </div>
    </nav>

    <section class="hero">
      <div class="hero-glow glow-cyan"></div>
      <div class="hero-glow glow-violet"></div>
      <div class="hero-glow glow-gold"></div>

      <div class="hero-content">
        <div class="hero-badge"><span class="badge-dot"></span>// ETHIOPIAN PROPERTY INTELLIGENCE PLATFORM</div>
        <h1 class="hero-title">
          <span class="hl">Property</span>
          <span class="hl hl-accent">Valuation.</span>
          <span class="hl hl-ghost">Reimagined.</span>
        </h1>
        <p class="hero-sub">AI-powered valuations for properties &amp; vehicles across Ethiopia.<br>Proclamation 1365/2025 compliant. Audit-ready. Real-time.</p>
        <div class="hero-actions">
          <NuxtLink to="/login" class="btn-primary"><span>Get Started</span><svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M2 7.5h11M8 2l5 5.5L8 13" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></NuxtLink>
          <a href="#features" class="btn-ghost">Explore Features</a>
        </div>
        <div class="stats-ticker">
          <div class="tk"><span class="tk-val">2,400+</span><span class="tk-lbl">Properties Valued</span></div>
          <div class="tk-div"></div>
          <div class="tk"><span class="tk-val">12</span><span class="tk-lbl">Cities Covered</span></div>
          <div class="tk-div"></div>
          <div class="tk"><span class="tk-val">100%</span><span class="tk-lbl">Compliance Rate</span></div>
        </div>
      </div>

      <div class="hero-card-wrap" ref="heroCard">
        <div class="hero-card">
          <div class="hc-top"><span class="hc-tag">LIVE VALUATION</span><span class="hc-live"><span class="hc-dot"></span>Active</span></div>
          <div class="hc-addr">Bole Sub-City, Addis Ababa</div>
          <div class="hc-val">ETB 4,250,000</div>
          <div class="hc-meta">Residential · 280m² · Grade A</div>
          <div class="hc-bar-row"><span>Market Confidence</span><span>94%</span></div>
          <div class="hc-bar"><div class="hc-fill" style="width:94%"></div></div>
          <div class="hc-foot"><span class="hc-badge">✓ Proclamation Compliant</span><span class="hc-time">Just now</span></div>
        </div>
        <div class="card-reflection"></div>
      </div>
      <div class="scroll-line"></div>
    </section>

    <section id="features" class="features">
      <div class="sw">
        <div class="sec-label">// CAPABILITIES</div>
        <h2 class="sec-title">Everything to <span class="accent-text">Value with Confidence</span></h2>
        <div class="feat-grid">
          <div v-for="(f,i) in features" :key="f.title" class="feat-card" :style="`--delay:${i*0.12}s;--c:${f.color}`">
            <div class="feat-icon"><i :class="f.icon"></i></div>
            <h3>{{ f.title }}</h3>
            <p>{{ f.desc }}</p>
            <div class="feat-shine"></div>
          </div>
        </div>
      </div>
    </section>

    <section id="trust" class="trust">
      <div class="trust-card">
        <div class="trust-icon"><i class="pi pi-shield"></i></div>
        <div class="trust-body">
          <h2>Proclamation 1365/2025 <span class="accent-text">Compliant</span></h2>
          <p>All valuations follow Ethiopian government regulations with complete traceability and zero compliance issues.</p>
          <div class="trust-badges">
            <span class="tb">✓ 100% Audit Ready</span>
            <span class="tb">✓ Tax Compliant</span>
            <span class="tb">✓ Zero Issues</span>
          </div>
        </div>
        <div class="trust-nums">
          <div class="tn"><span class="tn-v">25%</span><span class="tn-l">Tax Rate</span></div>
          <div class="tn"><span class="tn-v">100%</span><span class="tn-l">Audit Ready</span></div>
          <div class="tn"><span class="tn-v">0</span><span class="tn-l">Issues</span></div>
        </div>
      </div>
    </section>

    <section class="cta-sec">
      <div class="cta-glow"></div>
      <div class="sec-label">// GET STARTED</div>
      <h2 class="sec-title">Ready to Streamline<br><span class="accent-text">Your Valuations?</span></h2>
      <p class="cta-sub">Join valuation professionals who trust ValuAdis for accuracy, compliance, and speed.</p>
      <NuxtLink to="/login" class="btn-primary btn-lg"><span>Launch ValuAdis</span><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 8h12M8 2l6 6-6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg></NuxtLink>
    </section>

    <footer class="footer">
      <div class="foot-in">
        <div><span class="logo-name">ValuAdis</span><span class="logo-sub"> // PROPERTY INTELLIGENCE</span></div>
        <p class="foot-copy">© {{ new Date().getFullYear() }} ValuAdis · Ethiopian Property Valuation Platform</p>
        <NuxtLink to="/login" class="foot-link">Sign In →</NuxtLink>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
definePageMeta({ layout: 'landing', middleware: 'guest' })

const isScrolled = ref(false)
const particleCanvas = ref<HTMLCanvasElement | null>(null)
const heroCard = ref<HTMLElement | null>(null)

const features = [
  { icon: 'pi pi-building', title: 'Property Valuation', color: '#00d4ff', desc: 'AI-assisted residential, commercial, and mixed-use property valuations with full audit trails and spatial context.' },
  { icon: 'pi pi-car', title: 'Vehicle Valuation', color: '#e8a020', desc: 'Comprehensive vehicle assessments with market data, depreciation curves, and compliance-ready documentation.' },
  { icon: 'pi pi-file-pdf', title: 'Audit-Ready Reports', color: '#7b2fff', desc: 'Generate professional PDF certificates that meet Proclamation 1365/2025 requirements instantly.' },
  { icon: 'pi pi-map', title: 'Geographic Intelligence', color: '#00e676', desc: 'Interactive map visualization with heatmaps, spatial analytics, and location-aware pricing models.' },
]

let animFrame: number
function handleScroll() { isScrolled.value = window.scrollY > 50 }

function initParticles() {
  const canvas = particleCanvas.value; if (!canvas) return
  const ctx = canvas.getContext('2d')!
  let W = canvas.width = window.innerWidth
  let H = canvas.height = document.body.scrollHeight || window.innerHeight * 3
  const clrs = ['#00d4ff','#7b2fff','#e8a020','#00e676']
  const pts = Array.from({ length: 100 }, () => ({
    x: Math.random()*W, y: Math.random()*H,
    vx: (Math.random()-.5)*.5, vy: (Math.random()-.5)*.5,
    r: Math.random()*1.6+.4, a: Math.random()*.5+.15,
    c: clrs[Math.floor(Math.random()*clrs.length)]
  }))
  function draw() {
    ctx.clearRect(0,0,W,H)
    ctx.strokeStyle='rgba(0,212,255,0.04)'; ctx.lineWidth=1
    for (let x=0;x<W;x+=80){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,H);ctx.stroke()}
    for (let y=0;y<H;y+=80){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(W,y);ctx.stroke()}
    for (let i=0;i<pts.length;i++) for(let j=i+1;j<pts.length;j++){
      const d=Math.hypot(pts[i].x-pts[j].x,pts[i].y-pts[j].y)
      if(d<120){ctx.beginPath();ctx.strokeStyle=`rgba(0,212,255,${.1*(1-d/120)})`;ctx.lineWidth=.5;ctx.moveTo(pts[i].x,pts[i].y);ctx.lineTo(pts[j].x,pts[j].y);ctx.stroke()}
    }
    pts.forEach(p=>{ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=p.c;ctx.globalAlpha=p.a;ctx.fill();ctx.globalAlpha=1;p.x+=p.vx;p.y+=p.vy;if(p.x<0)p.x=W;if(p.x>W)p.x=0;if(p.y<0)p.y=H;if(p.y>H)p.y=0})
    animFrame=requestAnimationFrame(draw)
  }
  draw()
  window.addEventListener('resize',()=>{W=canvas.width=window.innerWidth;H=canvas.height=document.body.scrollHeight})
}

function initTilt() {
  const card = heroCard.value; if (!card) return
  document.addEventListener('mousemove',(e)=>{
    const r=card.getBoundingClientRect()
    const rx=((e.clientY-r.top-r.height/2)/r.height)*14
    const ry=((e.clientX-r.left-r.width/2)/r.width)*-14
    card.style.transform=`perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) translateY(-6px)`
  })
  document.addEventListener('mouseleave',()=>{ card.style.transform='perspective(900px) rotateX(6deg) rotateY(-8deg)' })
}

onMounted(()=>{ window.addEventListener('scroll',handleScroll,{passive:true}); initParticles(); initTilt() })
onUnmounted(()=>{ window.removeEventListener('scroll',handleScroll); cancelAnimationFrame(animFrame) })
</script>

<style scoped>
.landing{--void:#06060f;--surf:#0d0d1a;--cyan:#00d4ff;--gold:#e8a020;--vio:#7b2fff;--grn:#00e676;--txt:#e2e8f0;--mut:#64748b;--fh:'Syne',sans-serif;--fm:'JetBrains Mono',monospace;--fb:'DM Sans',sans-serif;background:var(--void);color:var(--txt);font-family:var(--fb);overflow-x:hidden;min-height:100vh}
.particle-canvas{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.9}

/* NAV */
.nav{position:fixed;top:0;left:0;right:0;z-index:100;padding:1.2rem 2.5rem;transition:background .4s,border .4s;border-bottom:1px solid transparent}
.nav.scrolled{background:rgba(6,6,15,.9);backdrop-filter:blur(20px);border-color:rgba(0,212,255,.12)}
.nav-inner{max-width:1280px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{display:flex;align-items:center;gap:.75rem}
.logo-mark{width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,var(--cyan),var(--vio));display:grid;place-items:center;font-family:var(--fh);font-weight:800;font-size:.8rem;color:#fff;box-shadow:0 0 20px rgba(0,212,255,.4);flex-shrink:0}
.logo-name{font-family:var(--fh);font-weight:800;font-size:1.15rem;color:#fff;display:block}
.logo-sub{font-family:var(--fm);font-size:.55rem;color:var(--cyan);letter-spacing:.15em;display:block}
.nav-links{display:flex;align-items:center;gap:2.5rem}
.nav-link{color:var(--mut);font-size:.88rem;text-decoration:none;transition:color .2s;font-family:var(--fb)}
.nav-link:hover{color:var(--txt)}
.nav-cta{display:inline-flex;align-items:center;gap:.5rem;padding:.5rem 1.15rem;background:rgba(0,212,255,.08);border:1px solid var(--cyan);color:var(--cyan);font-size:.85rem;text-decoration:none;border-radius:6px;font-family:var(--fb);font-weight:500;transition:all .3s}
.nav-cta:hover{background:var(--cyan);color:var(--void);box-shadow:0 0 25px rgba(0,212,255,.45)}

/* HERO */
.hero{min-height:100vh;display:flex;align-items:center;padding:7rem 2.5rem 5rem;position:relative;overflow:hidden;z-index:1}
.hero-glow{position:absolute;border-radius:50%;filter:blur(100px);animation:gfloat 10s ease-in-out infinite}
.glow-cyan{width:600px;height:600px;background:rgba(0,212,255,.1);top:-100px;left:-150px}
.glow-violet{width:500px;height:500px;background:rgba(123,47,255,.13);top:5%;right:-50px;animation-delay:-4s}
.glow-gold{width:350px;height:350px;background:rgba(232,160,32,.09);bottom:0;left:35%;animation-delay:-7s}
@keyframes gfloat{0%,100%{transform:scale(1) translate(0,0);opacity:.8}33%{transform:scale(1.1) translate(15px,-25px);opacity:1}66%{transform:scale(.95) translate(-10px,15px);opacity:.7}}

.hero-content{position:relative;z-index:3;flex:1;max-width:620px;animation:fadeUp .9s cubic-bezier(.4,0,.2,1) both}
.hero-badge{display:inline-flex;align-items:center;gap:.6rem;padding:.4rem 1rem;background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.25);border-radius:99px;margin-bottom:2rem;font-family:var(--fm);font-size:.68rem;color:var(--cyan);letter-spacing:.1em}
.badge-dot{width:7px;height:7px;border-radius:50%;background:var(--cyan);box-shadow:0 0 10px var(--cyan);animation:dpulse 2s ease-in-out infinite;flex-shrink:0}
@keyframes dpulse{0%,100%{opacity:1;box-shadow:0 0 8px var(--cyan)}50%{opacity:.4;box-shadow:0 0 3px var(--cyan)}}

.hero-title{font-family:var(--fh);font-weight:800;line-height:1.04;margin-bottom:1.5rem;display:flex;flex-direction:column}
.hl{font-size:clamp(3rem,7vw,5.5rem);color:#fff;display:block;animation:slideIn .8s cubic-bezier(.4,0,.2,1) both}
.hl-accent{background:linear-gradient(90deg,var(--cyan) 0%,var(--vio) 70%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;animation-delay:.1s}
.hl-ghost{color:transparent;-webkit-text-stroke:1.5px rgba(255,255,255,.18);animation-delay:.22s}
@keyframes slideIn{from{opacity:0;transform:translateY(45px)}to{opacity:1;transform:translateY(0)}}

.hero-sub{font-size:1.05rem;color:var(--mut);line-height:1.75;margin-bottom:2.5rem;max-width:500px}
.hero-actions{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:3rem}
.btn-primary{display:inline-flex;align-items:center;gap:.55rem;padding:.85rem 1.9rem;background:linear-gradient(135deg,var(--cyan),#0090cc);color:var(--void);font-weight:700;font-size:.95rem;border-radius:8px;text-decoration:none;font-family:var(--fb);box-shadow:0 0 30px rgba(0,212,255,.35),0 4px 15px rgba(0,0,0,.3);transition:all .3s;letter-spacing:.01em}
.btn-primary:hover{transform:translateY(-3px);box-shadow:0 0 55px rgba(0,212,255,.6),0 8px 25px rgba(0,0,0,.3)}
.btn-primary.btn-lg{padding:1.05rem 2.4rem;font-size:1.05rem}
.btn-ghost{display:inline-flex;align-items:center;gap:.5rem;padding:.85rem 1.75rem;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.14);color:var(--txt);font-size:.95rem;border-radius:8px;text-decoration:none;font-family:var(--fb);transition:all .3s}
.btn-ghost:hover{background:rgba(255,255,255,.09);border-color:rgba(255,255,255,.3)}

.stats-ticker{display:inline-flex;align-items:center;gap:1.75rem;padding:1.1rem 1.75rem;background:rgba(255,255,255,.03);border:1px solid rgba(0,212,255,.12);border-radius:12px;backdrop-filter:blur(12px)}
.tk{text-align:center}
.tk-val{display:block;font-family:var(--fm);font-size:1.45rem;font-weight:600;color:var(--cyan);text-shadow:0 0 20px rgba(0,212,255,.5);line-height:1}
.tk-lbl{font-size:.68rem;color:var(--mut);letter-spacing:.06em;text-transform:uppercase;margin-top:4px;display:block}
.tk-div{width:1px;height:38px;background:rgba(0,212,255,.15)}

/* 3D HERO CARD */
.hero-card-wrap{position:relative;z-index:3;flex-shrink:0;margin-left:4rem;transform:perspective(900px) rotateX(6deg) rotateY(-8deg);transition:transform .12s ease-out;animation:cardIn 1s .4s cubic-bezier(.4,0,.2,1) both}
@keyframes cardIn{from{opacity:0;transform:perspective(900px) rotateX(18deg) rotateY(-18deg) translateY(60px)}to{opacity:1;transform:perspective(900px) rotateX(6deg) rotateY(-8deg) translateY(0)}}
.hero-card{width:310px;padding:1.6rem;background:rgba(10,10,22,.92);border:1px solid rgba(0,212,255,.28);border-radius:16px;backdrop-filter:blur(24px);box-shadow:0 30px 80px rgba(0,0,0,.65),0 0 50px rgba(0,212,255,.07),inset 0 1px 0 rgba(255,255,255,.06)}
.card-reflection{position:absolute;bottom:-30px;left:5%;right:5%;height:30px;background:rgba(0,212,255,.06);filter:blur(20px);border-radius:50%}
.hc-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.1rem}
.hc-tag{font-family:var(--fm);font-size:.62rem;color:var(--cyan);letter-spacing:.15em}
.hc-live{display:flex;align-items:center;gap:.4rem;font-size:.7rem;color:var(--grn);font-family:var(--fm)}
.hc-dot{width:6px;height:6px;border-radius:50%;background:var(--grn);box-shadow:0 0 8px var(--grn);animation:dpulse 2s infinite}
.hc-addr{font-size:.8rem;color:var(--mut);margin-bottom:.4rem}
.hc-val{font-family:var(--fh);font-size:1.65rem;font-weight:800;color:#fff;margin-bottom:.35rem;letter-spacing:-.01em}
.hc-meta{font-size:.72rem;color:var(--mut);margin-bottom:1.1rem}
.hc-bar-row{display:flex;justify-content:space-between;font-size:.7rem;color:var(--mut);margin-bottom:.4rem}
.hc-bar{height:4px;background:rgba(255,255,255,.07);border-radius:99px;overflow:hidden;margin-bottom:1.1rem}
.hc-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--cyan),var(--vio));box-shadow:0 0 10px rgba(0,212,255,.6);animation:barGrow 1.5s 1s ease-out both}
@keyframes barGrow{from{width:0 !important}}
.hc-foot{display:flex;justify-content:space-between;align-items:center}
.hc-badge{font-size:.66rem;color:var(--grn);background:rgba(0,230,118,.1);border:1px solid rgba(0,230,118,.2);padding:.22rem .6rem;border-radius:99px}
.hc-time{font-size:.66rem;color:var(--mut);font-family:var(--fm)}
.scroll-line{position:absolute;bottom:0;left:50%;width:1px;height:70px;background:linear-gradient(to bottom,rgba(0,212,255,.5),transparent);transform:translateX(-50%);animation:scrlFade 2s ease-in-out infinite;z-index:3}
@keyframes scrlFade{0%,100%{opacity:0}50%{opacity:1}}

/* FEATURES */
.features{padding:8rem 2.5rem;position:relative;z-index:2;background:linear-gradient(to bottom,transparent,rgba(13,13,26,.7),transparent)}
.sw{max-width:1200px;margin:0 auto}
.sec-label{font-family:var(--fm);font-size:.7rem;color:var(--cyan);letter-spacing:.2em;margin-bottom:1rem}
.sec-title{font-family:var(--fh);font-size:clamp(2rem,4vw,3rem);font-weight:800;color:#fff;margin-bottom:4rem;line-height:1.12}
.accent-text{background:linear-gradient(90deg,var(--cyan),var(--vio));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.feat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem}
.feat-card{padding:2rem;border-radius:14px;background:rgba(13,13,26,.75);border:1px solid rgba(255,255,255,.06);backdrop-filter:blur(14px);position:relative;overflow:hidden;transition:transform .3s,border-color .3s,box-shadow .3s;animation:fadeUp .7s var(--delay) cubic-bezier(.4,0,.2,1) both}
.feat-card:hover{transform:translateY(-7px);border-color:color-mix(in srgb,var(--c) 40%,transparent);box-shadow:0 20px 50px rgba(0,0,0,.4),0 0 30px color-mix(in srgb,var(--c) 10%,transparent)}
.feat-card:hover .feat-shine{opacity:1}
.feat-shine{position:absolute;inset:0;border-radius:14px;opacity:0;transition:opacity .3s;pointer-events:none;background:radial-gradient(circle at 50% 0%,color-mix(in srgb,var(--c) 10%,transparent) 0%,transparent 65%)}
.feat-icon{width:48px;height:48px;border-radius:10px;display:grid;place-items:center;background:color-mix(in srgb,var(--c) 14%,transparent);border:1px solid color-mix(in srgb,var(--c) 28%,transparent);color:var(--c);font-size:1.25rem;margin-bottom:1.2rem;box-shadow:0 0 18px color-mix(in srgb,var(--c) 18%,transparent)}
.feat-card h3{font-family:var(--fh);font-size:1.1rem;font-weight:700;color:#fff;margin-bottom:.55rem}
.feat-card p{font-size:.86rem;color:var(--mut);line-height:1.65}

/* TRUST */
.trust{padding:6rem 2.5rem;position:relative;z-index:2}
.trust-card{max-width:1100px;margin:0 auto;display:flex;align-items:flex-start;gap:2.5rem;padding:2.75rem;background:rgba(13,13,26,.85);border:1px solid rgba(232,160,32,.22);border-radius:20px;backdrop-filter:blur(20px);box-shadow:0 0 60px rgba(232,160,32,.04)}
.trust-icon{width:60px;height:60px;flex-shrink:0;border-radius:12px;background:linear-gradient(135deg,var(--gold),#c07010);display:grid;place-items:center;color:#000;font-size:1.6rem;box-shadow:0 0 30px rgba(232,160,32,.4)}
.trust-body{flex:1}
.trust-body h2{font-family:var(--fh);font-size:1.6rem;font-weight:800;color:#fff;margin-bottom:.65rem}
.trust-body p{color:var(--mut);line-height:1.65;font-size:.93rem;margin-bottom:1.1rem}
.trust-badges{display:flex;flex-wrap:wrap;gap:.6rem}
.tb{display:inline-flex;padding:.3rem .8rem;background:rgba(0,230,118,.08);border:1px solid rgba(0,230,118,.2);color:var(--grn);font-size:.76rem;border-radius:99px}
.trust-nums{display:flex;flex-direction:column;gap:1.1rem;flex-shrink:0}
.tn{text-align:right}
.tn-v{display:block;font-family:var(--fm);font-size:1.5rem;font-weight:600;color:var(--gold);text-shadow:0 0 20px rgba(232,160,32,.5)}
.tn-l{font-size:.7rem;color:var(--mut);text-transform:uppercase;letter-spacing:.08em}

/* CTA */
.cta-sec{padding:9rem 2.5rem;position:relative;z-index:2;text-align:center;overflow:hidden}
.cta-glow{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:600px;height:400px;border-radius:50%;background:radial-gradient(ellipse,rgba(0,212,255,.07) 0%,transparent 70%);filter:blur(40px);pointer-events:none}
.cta-sec .sec-label,.cta-sec .sec-title{position:relative;z-index:2}
.cta-sub{color:var(--mut);font-size:1.05rem;margin-bottom:2.25rem;position:relative;z-index:2}

/* FOOTER */
.footer{padding:2.25rem;position:relative;z-index:2;border-top:1px solid rgba(0,212,255,.07);background:rgba(6,6,15,.7);backdrop-filter:blur(10px)}
.foot-in{max-width:1200px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.foot-copy{font-size:.78rem;color:var(--mut)}
.foot-link{font-size:.84rem;color:var(--cyan);text-decoration:none;transition:color .2s}
.foot-link:hover{color:#fff}

/* SHARED */
@keyframes fadeUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}

/* RESPONSIVE */
@media(max-width:1024px){.hero{flex-direction:column;text-align:center;padding-top:8rem}.hero-card-wrap{margin-left:0;margin-top:3rem}.stats-ticker{margin:0 auto}}
@media(max-width:640px){.nav-link{display:none}.hero-card-wrap{display:none}.trust-card{flex-direction:column}.trust-nums{flex-direction:row}.foot-in{flex-direction:column;text-align:center}}
</style>
