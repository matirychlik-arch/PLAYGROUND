#!/usr/bin/env python3
"""Lint the creative-skills pack: frontmatter, required headings, referenced files, forbidden Higgsfield-isms, sizes."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQ = ["## When to use / when not", "## Inputs to collect", "## Workflow", "## Output format", "## Tool adapters", "## QA checklist", "## References"]
BAD = re.compile(r"media_upload|jobs_wait|generate_(image|video)\(|show_generation|execute_preset|use_unlim|\bcredits?\b|media_confirm|sandbox_exec", re.I)
ok = True
for name in sorted(os.listdir(ROOT)):
    d = os.path.join(ROOT, name)
    if name.startswith("_") or not os.path.isdir(d): continue
    sk = os.path.join(d, "SKILL.md")
    if not os.path.exists(sk): print(f"[{name}] missing SKILL.md"); ok = False; continue
    s = open(sk, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", s, re.S)
    if not m: print(f"[{name}] no frontmatter"); ok = False; continue
    fm = m.group(1)
    try:
        import yaml; meta = yaml.safe_load(fm)
    except Exception as e:
        print(f"[{name}] frontmatter YAML error: {str(e)[:80]}"); ok = False; meta = {}
    if meta.get("name") != name: print(f"[{name}] frontmatter name mismatch: {meta.get('name')}"); ok = False
    if len(str(meta.get("description", ""))) < 80: print(f"[{name}] description missing/short"); ok = False
    lines = s.count("\n")
    if lines > 420: print(f"[{name}] SKILL.md long: {lines} lines")
    for h in REQ:
        if not any(l.startswith(h) for l in s.splitlines()): print(f"[{name}] missing heading: {h}"); ok = False
    for ref in set(re.findall(r"(?:references|scripts|assets)/[\w./-]+\.(?:md|py|json|txt|mjs|js)", s)):
        if not os.path.exists(os.path.join(d, ref)): print(f"[{name}] referenced file missing: {ref}"); ok = False
    total = 0
    for r, _, fs in os.walk(d):
        for f in fs:
            p = os.path.join(r, f); total += os.path.getsize(p)
            t = open(p, encoding="utf-8", errors="replace").read()
            for mm in BAD.finditer(t):
                ln = t[:mm.start()].count("\n") + 1
                print(f"[{name}] forbidden term '{mm.group(0)}' in {os.path.relpath(p, d)}:{ln}"); ok = False
    print(f"[{name}] OK-ish, {lines} lines SKILL.md, {total//1024} KB total")
sys.exit(0 if ok else 1)
