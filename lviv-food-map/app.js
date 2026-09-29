/* Lviv Food Map — Katsurin & Ptushkin
 * Plain JS + Leaflet. Data comes from data/places.js (generated from data/places.json).
 */
(function () {
  'use strict';

  // ---------------------------------------------------------------- config
  const CATEGORIES = [
    { key: 'all',        label: 'Wszystkie',           icon: '✦' },
    { key: 'restaurant', label: 'Restauracje',         icon: '🍽️' },
    { key: 'cafe',       label: 'Kawiarnie',           icon: '☕' },
    { key: 'breakfast',  label: 'Śniadania',           icon: '🍳' },
    { key: 'streetfood', label: 'Street food',         icon: '🌯' },
    { key: 'ukrainian',  label: 'Ukraińska',           icon: '🥟' },
    { key: 'galician',   label: 'Galicyjska / lwowska', icon: '🥧' },
    { key: 'finedining', label: 'Fine dining',         icon: '✨' },
    { key: 'bakery',     label: 'Bakery / słodkie',    icon: '🥐' },
    { key: 'bar',        label: 'Bary',                icon: '🍺' },
    { key: 'other',      label: 'Inne',                icon: '📍' }
  ];
  const CAT = Object.fromEntries(CATEGORIES.map(c => [c.key, c]));
  const CAT_COLOR = {
    restaurant: '#E4572E', cafe: '#8C5E3C', breakfast: '#F2A900', streetfood: '#FF7A00',
    ukrainian: '#2E86AB', galician: '#6C4AB6', finedining: '#1B1B1F', bakery: '#D9648E',
    bar: '#2D9C6B', other: '#6B7280'
  };
  const BY_LABEL = { katsurin: 'Katsurin', ptushkin: 'Ptushkin' };
  const MENTION_LABEL = { visited: 'odwiedzone osobiście', recommended: 'polecone', secondary: 'źródło wtórne', own: 'lokal własny Katsurina' };
  const STATUS_LABEL = { open: 'otwarte', closed: 'zamknięte', unknown: 'status nieznany' };
  const LVIV_CENTER = [49.8419, 24.0315];
  const SNAP = { peek: 0.22, half: 0.55, full: 0.92 };
  let sheetState = 'half';

  const places = (window.PLACES || []).map(p => ({ ...p, tags: p.tags || [] }));

  // ---------------------------------------------------------------- state
  const state = {
    category: 'all',
    by: 'all',
    status: 'all',
    visitedOnly: false,
    showClosed: false,
    showSecondary: false,
    query: '',
    selectedId: null
  };

  // ---------------------------------------------------------------- DOM
  const $ = s => document.querySelector(s);
  const listEl = $('#list');
  const chipsEl = $('#categoryChips');
  const detailEl = $('#detail');
  const detailBody = $('#detailBody');
  const panel = $('#panel');
  const resultCount = $('#resultCount');
  const isMobile = () => window.matchMedia('(max-width: 860px)').matches;

  // ---------------------------------------------------------------- map
  const map = L.map('map', { zoomControl: false, attributionControl: true }).setView(LVIV_CENTER, 14);
  L.control.zoom({ position: 'bottomright' }).addTo(map);
  const tiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    maxZoom: 20,
    subdomains: 'abcd',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
  }).addTo(map);
  map.attributionControl.setPrefix('');
  // Tile fallback: some hosts (e.g. sandboxed previews) block third-party images. Detect it and
  // switch to a schematic "paper" background with permanent labels so the map stays usable.
  (function watchTiles() {
    let loaded = 0, failed = 0, decided = false;
    const decide = () => {
      if (decided) return;
      if (loaded === 0 && failed > 0) { decided = true; document.body.classList.add('no-tiles'); const n = $('#tileNotice'); if (n) n.hidden = false; }
      else if (loaded > 0) decided = true;
    };
    tiles.on('tileload', () => { loaded++; decide(); });
    tiles.on('tileerror', () => { failed++; setTimeout(decide, 1500); });
    setTimeout(() => { if (loaded === 0) { failed++; decide(); } }, 6000);
  })();
  const syncZoomClass = () => document.body.classList.toggle('zoomed-in', map.getZoom() >= 15);
  map.on('zoomend', syncZoomClass); syncZoomClass();

  const markers = new Map(); // id -> L.Marker
  const layer = L.layerGroup().addTo(map);

  function markerIcon(p, selected) {
    const color = CAT_COLOR[p.category] || CAT_COLOR.other;
    const cls = ['pin', p.status === 'closed' ? 'pin-closed' : '', selected ? 'pin-selected' : ''].join(' ');
    return L.divIcon({
      className: cls,
      html: `<span class="pin-dot" style="--c:${color}"><span class="pin-ico">${CAT[p.category]?.icon || '📍'}</span></span><span class="pin-label">${escapeHtml(p.name_uk.split(' (')[0])}</span>`,
      iconSize: [36, 36],
      iconAnchor: [18, 36],
      popupAnchor: [0, -36]
    });
  }

  function buildMarkers() {
    for (const p of places) {
      if (p.lat == null || p.lng == null) continue;
      const m = L.marker([p.lat, p.lng], { icon: markerIcon(p, false), riseOnHover: true, keyboard: true, title: p.name_uk });
      m.on('click', () => select(p.id, { from: 'map' }));
      markers.set(p.id, m);
    }
  }

  // ---------------------------------------------------------------- filtering
  function matches(p) {
    if (state.category !== 'all' && p.category !== state.category && !p.tags.includes(state.category)) return false;
    if (state.by === 'both') { if (p.recommended_by.length < 2) return false; }
    else if (state.by !== 'all' && !p.recommended_by.includes(state.by)) return false;
    if (state.status !== 'all' && p.status !== state.status) return false;
    if (state.visitedOnly && !p.visited) return false;
    if (!state.showClosed && state.status === 'all' && p.status === 'closed') return false;
    if (!state.showSecondary && p.mention_type === 'secondary') return false;
    if (state.query) {
      const q = state.query.toLowerCase();
      const hay = [p.name, p.name_uk, p.address, p.description, ...(p.recommended_items || []), ...p.tags.map(t => CAT[t]?.label || t), CAT[p.category]?.label]
        .join(' ').toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  }

  function visiblePlaces() {
    return places.filter(matches).sort((a, b) => {
      const ord = { high: 0, medium: 1, low: 2 };
      if (a.visited !== b.visited) return a.visited ? -1 : 1;
      if (ord[a.confidence] !== ord[b.confidence]) return ord[a.confidence] - ord[b.confidence];
      return a.name_uk.localeCompare(b.name_uk, 'uk');
    });
  }

  // ---------------------------------------------------------------- render
  function render() {
    const vis = visiblePlaces();
    const visIds = new Set(vis.map(p => p.id));

    // markers
    layer.clearLayers();
    for (const [id, m] of markers) if (visIds.has(id)) m.addTo(layer);

    // list
    listEl.innerHTML = '';
    if (!vis.length) {
      listEl.innerHTML = '<li class="empty">Brak miejsc dla tych filtrów.<br><small>Włącz „historyczne / zamknięte” lub „źródła wtórne”, albo wyczyść wyszukiwanie.</small></li>';
    }
    for (const p of vis) listEl.appendChild(card(p));

    const n = vis.length;
    resultCount.textContent = `${n} ${plural(n, 'miejsce', 'miejsca', 'miejsc')}`;
    updateFilterBadge();
    renderChips();
    if (state.selectedId && !visIds.has(state.selectedId)) closeDetail();
  }

  function card(p) {
    const li = document.createElement('li');
    li.className = 'card' + (p.id === state.selectedId ? ' selected' : '') + (p.status === 'closed' ? ' closed' : '');
    li.dataset.id = p.id;
    li.setAttribute('role', 'option');
    li.tabIndex = 0;
    const color = CAT_COLOR[p.category] || CAT_COLOR.other;
    li.innerHTML = `
      <div class="card-ico" style="--c:${color}">${CAT[p.category]?.icon || '📍'}</div>
      <div class="card-body">
        <div class="card-top">
          <h3>${escapeHtml(p.name_uk.split(' (')[0])}</h3>
          ${confBadge(p.confidence)}
        </div>
        <div class="card-meta">${escapeHtml(CAT[p.category]?.label || p.category)} · ${escapeHtml(shortAddress(p.address))}</div>
        <div class="card-tags">
          ${byPill(p)}
          <span class="pill pill-${p.mention_type}">${MENTION_LABEL[p.mention_type]}</span>
          ${p.status !== 'open' ? `<span class="pill pill-status-${p.status}">${STATUS_LABEL[p.status]}</span>` : ''}
          ${p.lat == null ? '<span class="pill pill-nogeo">brak lokalizacji</span>' : ''}
        </div>
      </div>`;
    li.addEventListener('click', () => select(p.id, { from: 'list' }));
    li.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(p.id, { from: 'list' }); } });
    return li;
  }

  function renderDetail(p) {
    const color = CAT_COLOR[p.category] || CAT_COLOR.other;
    const items = (p.recommended_items || []);
    const srcs = p.sources || [];
    const primary = srcs[0];
    detailBody.innerHTML = `
      <div class="detail-head">
        <div class="detail-ico" style="--c:${color}">${CAT[p.category]?.icon || '📍'}</div>
        <div>
          <h2>${escapeHtml(p.name_uk)}</h2>
          ${p.name && p.name !== p.name_uk ? `<div class="detail-latin">${escapeHtml(p.name)}</div>` : ''}
        </div>
      </div>
      <dl class="detail-facts">
        <div><dt>Kategoria</dt><dd>${escapeHtml(CAT[p.category]?.label || p.category)}${p.tags.filter(t => t !== p.category).length ? ` <span class="muted">· ${p.tags.filter(t => t !== p.category).map(t => escapeHtml(CAT[t]?.label || t)).join(', ')}</span>` : ''}</dd></div>
        <div><dt>Adres</dt><dd>${escapeHtml(p.address)}</dd></div>
        <div><dt>Polecał</dt><dd>${byText(p)} <span class="muted">· ${MENTION_LABEL[p.mention_type]}</span></dd></div>
        <div><dt>Status</dt><dd><span class="dot dot-${p.status}"></span>${STATUS_LABEL[p.status]} <span class="muted">· pewność źródła: ${confBadge(p.confidence)}</span></dd></div>
      </dl>
      ${items.length ? `<section class="detail-sec"><h4>Co warto zamówić</h4><ul class="dish-list">${items.map(i => `<li>${escapeHtml(i)}</li>`).join('')}</ul></section>` : ''}
      <section class="detail-sec"><h4>Opis</h4><p>${escapeHtml(p.description)}</p>${p.notes ? `<p class="note">${escapeHtml(p.notes)}</p>` : ''}</section>
      <div class="detail-actions">
        <a class="btn primary" href="${p.google_maps}" target="_blank" rel="noopener">Open in Google Maps →</a>
        ${primary ? `<a class="btn" href="${primary.url}" target="_blank" rel="noopener">Źródło rekomendacji →</a>` : ''}
      </div>
      ${srcs.length ? `<section class="detail-sec"><h4>Źródła (${srcs.length})</h4><ul class="src-list">${srcs.map(s => `<li><a href="${s.url}" target="_blank" rel="noopener">${escapeHtml(s.title)}</a>${s.date ? ` <span class="muted">${escapeHtml(s.date)}</span>` : ''}</li>`).join('')}</ul></section>` : ''}
      ${(p.website || p.instagram) ? `<div class="detail-links">${p.website ? `<a href="${p.website}" target="_blank" rel="noopener">Strona lokalu</a>` : ''}${p.instagram ? `<a href="${p.instagram}" target="_blank" rel="noopener">Social</a>` : ''}</div>` : ''}
    `;
    detailEl.hidden = false;
    document.body.classList.add('detail-open');
    requestAnimationFrame(() => detailEl.classList.add('show'));
  }

  function closeDetail() {
    detailEl.classList.remove('show');
    document.body.classList.remove('detail-open');
    setTimeout(() => { if (!detailEl.classList.contains('show')) detailEl.hidden = true; }, 220);
    const prev = state.selectedId;
    state.selectedId = null;
    if (prev && markers.has(prev)) markers.get(prev).setIcon(markerIcon(placeById(prev), false));
    listEl.querySelectorAll('.card.selected').forEach(el => el.classList.remove('selected'));
  }

  // ---------------------------------------------------------------- selection
  function select(id, { from } = {}) {
    const p = placeById(id);
    if (!p) return;
    if (state.selectedId && state.selectedId !== id && markers.has(state.selectedId)) {
      markers.get(state.selectedId).setIcon(markerIcon(placeById(state.selectedId), false));
    }
    state.selectedId = id;
    if (markers.has(id)) {
      const m = markers.get(id);
      m.setIcon(markerIcon(p, true));
      m.setZIndexOffset(1000);
      if (from === 'list') {
        const targetZoom = Math.max(map.getZoom(), 16);
        if (isMobile()) {
          // keep the marker visible above the sheet: offset the center downwards
          const pt = map.project([p.lat, p.lng], targetZoom).add([0, window.innerHeight * 0.18]);
          map.flyTo(map.unproject(pt, targetZoom), targetZoom, { duration: 0.6 });
        } else {
          map.flyTo([p.lat, p.lng], targetZoom, { duration: 0.6 });
        }
      } else if (from === 'map') {
        map.panTo([p.lat, p.lng], { animate: true });
      }
    }
    // highlight list item
    listEl.querySelectorAll('.card').forEach(el => el.classList.toggle('selected', el.dataset.id === id));
    const el = listEl.querySelector(`.card[data-id="${CSS.escape(id)}"]`);
    if (el && from === 'map') el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    renderDetail(p);
    if (isMobile()) setSheet('peek');
  }

  // ---------------------------------------------------------------- chips & controls
  function renderChips() {
    chipsEl.innerHTML = '';
    for (const c of CATEGORIES) {
      const n = c.key === 'all' ? null : places.filter(p => (p.category === c.key || p.tags.includes(c.key)) && matchesIgnoring(p, 'category')).length;
      if (c.key !== 'all' && n === 0) continue;
      const b = document.createElement('button');
      b.className = 'chip' + (state.category === c.key ? ' on' : '');
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', String(state.category === c.key));
      b.innerHTML = `<span class="chip-ico">${c.icon}</span>${c.label}${n != null ? `<span class="chip-n">${n}</span>` : ''}`;
      b.addEventListener('click', () => { state.category = c.key; render(); });
      chipsEl.appendChild(b);
    }
  }
  function matchesIgnoring(p, field) {
    const saved = state[field];
    state[field] = 'all';
    const ok = matches(p);
    state[field] = saved;
    return ok;
  }

  function seg(el, attr, key) {
    el.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      state[key] = b.dataset[attr];
      el.querySelectorAll('button').forEach(x => { const on = x === b; x.classList.toggle('on', on); x.setAttribute('aria-checked', String(on)); });
      render();
    });
  }
  seg($('#bySeg'), 'by', 'by');
  seg($('#statusSeg'), 'status', 'status');

  $('#visitedOnly').addEventListener('change', e => { state.visitedOnly = e.target.checked; render(); });
  $('#showClosed').addEventListener('change', e => { state.showClosed = e.target.checked; render(); });
  $('#showSecondary').addEventListener('change', e => { state.showSecondary = e.target.checked; render(); });

  const searchEl = $('#search');
  let t;
  searchEl.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => { state.query = searchEl.value.trim(); render(); }, 120); });
  $('#searchClear').addEventListener('click', () => { searchEl.value = ''; state.query = ''; render(); searchEl.focus(); });
  searchEl.addEventListener('keydown', e => { if (e.key === 'Escape') { searchEl.value = ''; state.query = ''; render(); } });

  $('#resetBtn').addEventListener('click', () => {
    Object.assign(state, { category: 'all', by: 'all', status: 'all', visitedOnly: false, showClosed: false, showSecondary: false, query: '' });
    searchEl.value = '';
    ['#visitedOnly', '#showClosed', '#showSecondary'].forEach(s => { $(s).checked = false; });
    document.querySelectorAll('.seg').forEach(s => s.querySelectorAll('button').forEach((b, i) => { b.classList.toggle('on', i === 0); b.setAttribute('aria-checked', String(i === 0)); }));
    render();
  });

  function updateFilterBadge() {
    let n = 0;
    if (state.by !== 'all') n++;
    if (state.status !== 'all') n++;
    if (state.visitedOnly) n++;
    if (state.showClosed) n++;
    if (state.showSecondary) n++;
    const b = $('#activeFilterCount');
    b.hidden = n === 0; b.textContent = n;
  }

  $('#detailClose').addEventListener('click', closeDetail);
  $('#tileNoticeClose')?.addEventListener('click', () => { $('#tileNotice').hidden = true; });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !detailEl.hidden) closeDetail(); });
  map.on('click', () => { if (!detailEl.hidden) closeDetail(); });

  $('#locateBtn').addEventListener('click', () => fitAll(true));

  const about = $('#about');
  $('#aboutBtn').addEventListener('click', () => about.showModal());
  about.addEventListener('click', e => { if (e.target === about) about.close(); });

  // legend
  $('#legend').innerHTML = CATEGORIES.filter(c => c.key !== 'all' && places.some(p => p.category === c.key))
    .map(c => `<span><i style="background:${CAT_COLOR[c.key]}"></i>${c.label}</span>`).join('');

  // ---------------------------------------------------------------- mobile bottom sheet
  function setSheet(s) {
    sheetState = s;
    panel.dataset.sheet = s;
    panel.style.setProperty('--sheet-h', `${Math.round(SNAP[s] * 100)}svh`);
    setTimeout(() => map.invalidateSize(), 320);
  }
  (function initSheet() {
    const handle = $('#sheetHandle');
    let startY = 0, startH = 0, dragging = false;
    const vh = () => window.innerHeight;
    const onStart = y => { dragging = true; startY = y; startH = panel.getBoundingClientRect().height; panel.classList.add('dragging'); };
    const onMove = y => {
      if (!dragging) return;
      const h = Math.min(vh() * 0.95, Math.max(vh() * 0.12, startH + (startY - y)));
      panel.style.setProperty('--sheet-h', `${h}px`);
    };
    const onEnd = () => {
      if (!dragging) return;
      dragging = false; panel.classList.remove('dragging');
      const ratio = panel.getBoundingClientRect().height / vh();
      const nearest = Object.entries(SNAP).sort((a, b) => Math.abs(a[1] - ratio) - Math.abs(b[1] - ratio))[0][0];
      setSheet(nearest);
    };
    handle.addEventListener('touchstart', e => onStart(e.touches[0].clientY), { passive: true });
    window.addEventListener('touchmove', e => onMove(e.touches[0].clientY), { passive: true });
    window.addEventListener('touchend', onEnd);
    handle.addEventListener('mousedown', e => { onStart(e.clientY); e.preventDefault(); });
    window.addEventListener('mousemove', e => onMove(e.clientY));
    window.addEventListener('mouseup', onEnd);
    handle.addEventListener('click', () => setSheet(sheetState === 'half' ? 'full' : sheetState === 'full' ? 'peek' : 'half'));
    handle.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); handle.click(); } });
    if (isMobile()) setSheet('half');
    window.addEventListener('resize', () => { if (isMobile()) setSheet(sheetState); else { panel.style.removeProperty('--sheet-h'); map.invalidateSize(); } });
  })();

  // ---------------------------------------------------------------- helpers
  function placeById(id) { return places.find(p => p.id === id); }
  function escapeHtml(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
  function shortAddress(a) { return a.replace(/,\s*Львів$/, ''); }
  function plural(n, one, few, many) { const m10 = n % 10, m100 = n % 100; if (m10 === 1 && m100 !== 11) return one; if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few; return many; }
  function confBadge(c) { return `<span class="conf conf-${c}">${c.toUpperCase()}</span>`; }
  function byPill(p) {
    if (p.recommended_by.length === 2) return '<span class="pill pill-both">Katsurin + Ptushkin</span>';
    return `<span class="pill pill-${p.recommended_by[0]}">${BY_LABEL[p.recommended_by[0]]}</span>`;
  }
  function byText(p) { return p.recommended_by.length === 2 ? 'obaj (Katsurin i Ptushkin)' : BY_LABEL[p.recommended_by[0]]; }

  // ---------------------------------------------------------------- init
  buildMarkers();
  render();
  function fitAll(animate, { coreOnly = false } = {}) {
    let pts = visiblePlaces().filter(p => p.lat != null).map(p => [p.lat, p.lng]);
    if (coreOnly) {
      // initial view: focus on the Old Town cluster, leave far-out places (e.g. Briukhovychi) for the locate button
      const core = pts.filter(([la, ln]) => map.distance([la, ln], LVIV_CENTER) < 3000);
      if (core.length >= 2) pts = core;
    }
    if (!pts.length) { map.setView(LVIV_CENTER, 14); return; }
    const opts = isMobile()
      ? { paddingTopLeft: [24, 70], paddingBottomRight: [24, Math.round(window.innerHeight * SNAP[sheetState]) + 24] }
      : { paddingTopLeft: [parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sidebar-w')) + 60, 40], paddingBottomRight: [40, 60] };
    const b = L.latLngBounds(pts).pad(0.05);
    if (animate) map.flyToBounds(b, { ...opts, duration: 0.8 }); else map.fitBounds(b, opts);
  }
  fitAll(false, { coreOnly: true });

  // deep link ?place=id
  const qp = new URLSearchParams(location.search).get('place');
  if (qp && placeById(qp)) setTimeout(() => select(qp, { from: 'list' }), 400);
})();
