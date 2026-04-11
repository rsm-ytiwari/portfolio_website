/* ═══════════════════════════════════════════════════════════════
   main.js — Yash Tiwari Portfolio

   EDIT THIS FILE to change any interactive behaviour.
   After editing, Quarto picks it up on next render.

   Contents:
     1. Theme toggle (dark / light mode)
     2. Typewriter animation (hero role line)
     3. Copy email to clipboard + toast notification
     4. Active nav link detection (auto, based on current URL)
═══════════════════════════════════════════════════════════════ */

/* ── 1. Theme Toggle ── */
const html       = document.documentElement;
const toggleBtn  = document.getElementById('theme-toggle');
const themeLabel = document.getElementById('theme-label');
const themeIcon  = document.getElementById('theme-icon');

const SUN  = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
const MOON = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;

if (toggleBtn) {
  toggleBtn.addEventListener('click', () => {
    html.classList.toggle('dark');
    const dark = html.classList.contains('dark');
    themeLabel.textContent = dark ? 'Dark' : 'Light';
    themeIcon.innerHTML    = dark ? MOON  : SUN;
  });
}

/* ── 2. Typewriter ──
   EDIT TW_TEXT to change the animated role line on the homepage. */
const TW_TEXT = 'MS Business Analytics · Builder · Agentic AI';
const twEl    = document.getElementById('typewriter');
let   twIdx   = 0;
function typeChar() {
  if (twIdx < TW_TEXT.length) {
    twEl.textContent += TW_TEXT.charAt(twIdx++);
    setTimeout(typeChar, 38);
  }
}
if (twEl) setTimeout(typeChar, 700);

/* ── 3. Copy Email + Toast ──
   EDIT the email string below if your address changes.         */
const copyBtn = document.getElementById('copy-btn');
const toast   = document.getElementById('toast');
let   tTimer, rTimer;

if (copyBtn && toast) {
  copyBtn.addEventListener('click', () => {
    const email = 'ytiwari@ucsd.edu';   // ← EDIT EMAIL HERE
    const write = () => {
      copyBtn.textContent = 'Copied ✓';
      toast.classList.add('show');
      clearTimeout(tTimer); clearTimeout(rTimer);
      tTimer = setTimeout(() => toast.classList.remove('show'), 2500);
      rTimer = setTimeout(() => { copyBtn.textContent = 'Copy email ↗'; }, 3000);
    };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(email).then(write).catch(write);
    } else { write(); }
  });
}

/* ── 4. Active Nav Link Detection ──
   Reads the current page filename and marks the matching
   .nav-link as .active automatically. No edits needed.        */
(function () {
  const path    = window.location.pathname;
  const current = (path.split('/').filter(Boolean).pop() || 'index').replace('.html', '');
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    const href     = link.getAttribute('href') || '';
    const linkPage = href.split('/').pop().replace('.html', '') || 'index';
    if (linkPage === current || (current === '' && linkPage === 'index')) {
      link.classList.add('active');
    }
  });
})();

/* ── 5. Cursor-reactive blob ──
   Blob follows cursor globally at 35% speed, capped at
   MAX_DRIFT px from origin. Returns to origin after 3 s
   of idle or on mouse leave.                                   */
(function() {
  const heroInner = document.querySelector('.hero-inner');
  if (!heroInner) return;

  let targetX = 0, targetY = 0;
  let currentX = 0, currentY = 0;
  let rafId = null;
  let idleTimer = null;
  const STRENGTH  = 0.35;
  const LERP      = 0.09;
  const MAX_DRIFT = 120;

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }
  function lerp(a, b, t)    { return a + (b - a) * t; }

  function animate() {
    currentX = lerp(currentX, targetX, LERP);
    currentY = lerp(currentY, targetY, LERP);

    heroInner.style.setProperty('--blob-x', currentX.toFixed(2) + 'px');
    heroInner.style.setProperty('--blob-y', currentY.toFixed(2) + 'px');

    if (
      Math.abs(currentX - targetX) > 0.05 ||
      Math.abs(currentY - targetY) > 0.05
    ) {
      rafId = requestAnimationFrame(animate);
    } else {
      rafId = null;
    }
  }

  function resetTarget() {
    targetX = 0;
    targetY = 0;
    if (!rafId) rafId = requestAnimationFrame(animate);
  }

  function scheduleIdle() {
    clearTimeout(idleTimer);
    idleTimer = setTimeout(resetTarget, 3000);
  }

  document.addEventListener('mousemove', function(e) {
    const rect = heroInner.getBoundingClientRect();
    const cx = rect.left + rect.width  / 2;
    const cy = rect.top  + rect.height / 2;

    const rawX = (e.clientX - cx) * STRENGTH;
    const rawY = (e.clientY - cy) * STRENGTH;

    targetX = clamp(rawX, -MAX_DRIFT, MAX_DRIFT);
    targetY = clamp(rawY, -MAX_DRIFT, MAX_DRIFT);

    if (!rafId) rafId = requestAnimationFrame(animate);
    scheduleIdle();
  });

  document.addEventListener('mouseleave', resetTarget);
})();
