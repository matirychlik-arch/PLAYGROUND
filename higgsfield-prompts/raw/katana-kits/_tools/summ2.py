import json,sys,os
slug=sys.argv[1]; a=json.load(open(f'an/{slug}/analysis/analysis.json'))
an=a.get('analysed',{}); cv=a.get('canvas',{}); sm=a.get('summary',{}); lk=a.get('look',{})
fps=None
for c in a.get('cuts',[]):
    fps=c.get('cadence',{}).get('src_fps'); 
    if fps: break
o=[]
o.append(f"# Katana reference edit map: {slug}")
o.append(f"Generated 2026-10-09 with Higgsfield katana workflow `analyze_ref.py` over the preset's reference video (frames {an.get('frames')}, crop {json.dumps(an.get('crop'))}, src_fps {fps}). Detector proposals, not confirmed cuts.")
o.append(f"Totals: cuts {sm.get('cuts')}, bursts {sm.get('bursts')}, flashes {sm.get('flashes')}, solids {sm.get('solids')}, inverts {sm.get('inverts')}; cadence patterns: " + ", ".join(f"{k}={len(v)}" for k,v in (sm.get('cadence_patterns') or {}).items()))
o.append(f"Global look: bw={lk.get('bw')} accent_only={lk.get('accent_only')} threshold={lk.get('threshold_look')} luma_mean={lk.get('luma_mean')} contrast={lk.get('contrast_p5_p95')} sat={lk.get('sat_mean')} colorful={lk.get('colorful_share')} warmth={lk.get('warmth')} hue={lk.get('dominant_hue_name')}({lk.get('dominant_hue_share')}) bars={json.dumps(lk.get('bars'))}")
if cv.get('window') or cv.get('letterbox'): o.append(f"Canvas: kind={cv.get('kind')} window={json.dumps(cv.get('window'))} letterbox={json.dumps(cv.get('letterbox'))}")
o.append("\n## Cuts (id f0-f1 | t0-t1 s | dur | kind/sub_cuts | conf | cadence | motion move/energy/zoom/pan | look bw/luma/sat/hue | flashes/inverts/text)")
for c in a.get('cuts',[]):
    cad=c.get('cadence',{}); mo=c.get('motion',{}); l=c.get('look',{})
    sub=f" sub{c.get('sub_cuts')}" if c.get('sub_cuts') else ''
    fl=''
    if c.get('flashes'): fl+=f" flashes={len(c['flashes'])}"
    if c.get('inverts'): fl+=f" inv={len(c['inverts'])}"
    if c.get('text_candidates'): fl+=f" text={len(c['text_candidates'])}"
    o.append(f"- {c.get('id')} f{c.get('f0')}-{c.get('f1')} | {c.get('t0',0):.2f}-{c.get('t1',0):.2f}s | {c.get('dur_s',0):.2f}s | {c.get('kind','')}{sub} | {c.get('conf_label','')} | {cad.get('pattern','')} holds={cad.get('holds','')} | {mo.get('move','')} e={mo.get('energy','')} z={mo.get('zoom','')} pan=({mo.get('pan_x','')},{mo.get('pan_y','')}) | {'BW ' if l.get('bw') else ''}L{l.get('luma_mean','')} S{l.get('sat_mean','')} {l.get('dominant_hue_name','')}{fl}")
fls=a.get('flashes') or []
if fls:
    o.append("\n## Flashes (f0-f1 type note)")
    o.append("; ".join(f"f{x.get('f0')}-{x.get('f1')} {x.get('type')} {x.get('note','')}".strip() for x in fls))
so=a.get('solids') or []
if so:
    o.append("\n## Solids (f0-f1 kind color)")
    o.append("; ".join(f"f{x.get('f0')}-{x.get('f1')} {x.get('kind')} {x.get('color')}" for x in so))
iv=a.get('inverts') or []
if iv: o.append("\n## Inverts\n"+json.dumps(iv)[:800])
az=a.get('activity_zones') or []
if az: o.append("\n## Activity zones\n"+json.dumps(az)[:600])
mb=a.get('maybes') or []
if mb: o.append(f"\n## Maybe-cuts (unconfirmed): "+", ".join(str(x.get('f',x)) if isinstance(x,dict) else str(x) for x in mb)[:600])
s='\n'.join(o)+'\n'
open(f'an/{slug}/summary.md','w').write(s); print(slug,len(s))
