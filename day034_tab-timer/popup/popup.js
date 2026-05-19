'use strict';

// ─── time formatting ────────────────────────────────────────────────────────

function formatTime(totalSeconds) {
  if (totalSeconds < 60) return `${totalSeconds}秒`;
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  if (h > 0) return `${h}時間${m}分`;
  return s > 0 ? `${m}分${s}秒` : `${m}分`;
}

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

// ─── favicon ────────────────────────────────────────────────────────────────

function faviconUrl(domain) {
  return `https://www.google.com/s2/favicons?sz=32&domain=${domain}`;
}

function createFaviconEl(domain) {
  const img = document.createElement('img');
  img.className = 'favicon';
  img.src = faviconUrl(domain);
  img.alt = '';
  img.onerror = () => {
    const fb = document.createElement('div');
    fb.className = 'favicon-fallback';
    fb.textContent = domain.charAt(0).toUpperCase();
    img.replaceWith(fb);
  };
  return img;
}

// ─── render ─────────────────────────────────────────────────────────────────

function render(domains, active) {
  const listEl   = document.getElementById('list');
  const emptyEl  = document.getElementById('empty');
  const totalEl  = document.getElementById('total-time');
  const dateEl   = document.getElementById('date-label');

  dateEl.textContent = todayKey();

  // Merge active elapsed time into display copy (not persisted here)
  const display = { ...domains };
  if (active && active.domain && active.startTime) {
    const elapsed = Math.round((Date.now() - active.startTime) / 1000);
    display[active.domain] = (display[active.domain] || 0) + elapsed;
  }

  const sorted = Object.entries(display).sort((a, b) => b[1] - a[1]);
  const totalSec = sorted.reduce((s, [, v]) => s + v, 0);

  totalEl.textContent = totalSec > 0 ? formatTime(totalSec) : '—';

  listEl.innerHTML = '';

  if (sorted.length === 0) {
    emptyEl.classList.remove('hidden');
    return;
  }
  emptyEl.classList.add('hidden');

  const maxSec = sorted[0]?.[1] ?? 1;

  sorted.forEach(([domain, secs], i) => {
    const isActive = active?.domain === domain;

    const item = document.createElement('div');
    item.className = 'domain-item';

    // Rank
    const rank = document.createElement('span');
    rank.className = 'rank';
    rank.textContent = `${i + 1}`;

    // Favicon
    const fav = createFaviconEl(domain);

    // Info (name + bar)
    const info = document.createElement('div');
    info.className = 'domain-info';

    const name = document.createElement('div');
    name.className = 'domain-name';
    name.textContent = domain;

    const barWrap = document.createElement('div');
    barWrap.className = 'bar-wrap';
    const bar = document.createElement('div');
    bar.className = 'bar';
    bar.style.width = `${Math.round((secs / maxSec) * 100)}%`;
    barWrap.appendChild(bar);

    info.append(name, barWrap);

    // Time
    const time = document.createElement('span');
    time.className = `domain-time${isActive ? ' active' : ''}`;
    time.textContent = formatTime(secs);

    // Active dot
    if (isActive) {
      const dot = document.createElement('div');
      dot.className = 'active-dot';
      item.append(rank, fav, info, time, dot);
    } else {
      item.append(rank, fav, info, time);
    }

    listEl.appendChild(item);
  });
}

// ─── main ────────────────────────────────────────────────────────────────────

function load() {
  chrome.storage.local.get(['today', 'domains', 'active'], data => {
    const today = todayKey();
    const storedToday = data.today;
    const domains = storedToday === today ? (data.domains || {}) : {};
    render(domains, data.active ?? null);
  });
}

// Reload every 5 seconds while popup is open
load();
setInterval(load, 5000);

// Reset button
document.getElementById('reset-btn').addEventListener('click', () => {
  if (!confirm('今日のデータをリセットしますか？')) return;
  chrome.storage.local.set({ today: todayKey(), domains: {}, active: null }, load);
});
