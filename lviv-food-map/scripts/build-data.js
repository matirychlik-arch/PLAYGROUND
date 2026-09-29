#!/usr/bin/env node
/**
 * Regenerates derived data files from data/places.json:
 *   - data/places.js   (window.PLACES = [...]) so index.html works from file:// without a server
 *   - data/lviv-katsurin-ptushkin-map.csv  (Google My Maps import)
 * Run: node scripts/build-data.js
 */
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const src = path.join(root, 'data', 'places.json');
const places = JSON.parse(fs.readFileSync(src, 'utf8'));

// --- validation -------------------------------------------------------------
const CATEGORIES = ['restaurant','cafe','breakfast','streetfood','ukrainian','galician','finedining','bakery','bar','other'];
const errors = [];
const ids = new Set();
for (const p of places) {
  if (!p.id) errors.push(`missing id: ${p.name}`);
  if (ids.has(p.id)) errors.push(`duplicate id: ${p.id}`);
  ids.add(p.id);
  for (const k of ['name','name_uk','address','category','recommended_by','description','google_maps','sources','status','confidence']) {
    if (p[k] === undefined) errors.push(`${p.id}: missing ${k}`);
  }
  if (!CATEGORIES.includes(p.category)) errors.push(`${p.id}: bad category ${p.category}`);
  for (const t of p.tags || []) if (!CATEGORIES.includes(t)) errors.push(`${p.id}: bad tag ${t}`);
  if (!['open','closed','unknown'].includes(p.status)) errors.push(`${p.id}: bad status`);
  if (!['high','medium','low'].includes(p.confidence)) errors.push(`${p.id}: bad confidence`);
  if (!['visited','recommended','secondary','own'].includes(p.mention_type)) errors.push(`${p.id}: bad mention_type`);
  if ((p.lat == null) !== (p.lng == null)) errors.push(`${p.id}: lat/lng mismatch`);
  if (p.lat != null && (p.lat < 49.7 || p.lat > 50.0 || p.lng < 23.8 || p.lng > 24.2)) errors.push(`${p.id}: coordinates outside Lviv`);
  if (!p.sources.length) errors.push(`${p.id}: no sources`);
}
if (errors.length) { console.error('Validation errors:\n - ' + errors.join('\n - ')); process.exit(1); }

// --- places.js --------------------------------------------------------------
const js = '// GENERATED from data/places.json by scripts/build-data.js — do not edit by hand\n' +
  'window.PLACES = ' + JSON.stringify(places, null, 2) + ';\n';
fs.writeFileSync(path.join(root, 'data', 'places.js'), js);

// --- CSV --------------------------------------------------------------------
const BY = { katsurin: 'Katsurin', ptushkin: 'Ptushkin' };
const esc = v => {
  const s = v == null ? '' : String(v);
  return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};
const header = ['Name','Ukrainian Name','Address','Latitude','Longitude','Category','Recommended By','Recommended Dish','Description','Google Maps URL','Source URL','Status'];
const rows = places.map(p => [
  p.name,
  p.name_uk,
  p.address,
  p.lat == null ? '' : p.lat,
  p.lng == null ? '' : p.lng,
  p.category,
  p.recommended_by.length === 2 ? 'Both' : BY[p.recommended_by[0]],
  (p.recommended_items || []).join('; '),
  p.description,
  p.google_maps,
  p.sources[0] ? p.sources[0].url : '',
  p.status.toUpperCase()
].map(esc).join(','));
// BOM so Excel/Google detect UTF-8 (Cyrillic) correctly
fs.writeFileSync(path.join(root, 'data', 'lviv-katsurin-ptushkin-map.csv'), '﻿' + [header.join(',')].concat(rows).join('\r\n') + '\r\n');

const withCoords = places.filter(p => p.lat != null).length;
console.log(`OK: ${places.length} places (${withCoords} with coordinates) → data/places.js, data/lviv-katsurin-ptushkin-map.csv`);
