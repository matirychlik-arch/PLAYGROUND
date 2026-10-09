# rr.sh - katana sandbox helpers. Source it at the start of EVERY sandbox_exec command.
#
# Pre-deploy bootstrap (first line of every sandbox_exec command while the bundle is not deployed;
# RR_BUNDLE_URL = permanent URL of the trusted bundle .zip: either katana/ at its root
# (install package) or scripts/ and references/ at its root (runtime package)).
# Deployed bundle wins, then a cached bootstrap from an earlier call, else download + unzip:
#
#   RR_BUNDLE_URL='<trusted bundle .zip url>'; source "${HF_WORKFLOWS:-/nonexistent}/katana/scripts/rr.sh" 2>/dev/null || { if [ ! -f /home/user/.rr/katana/scripts/rr.sh ] && [ ! -f /home/user/.rr/scripts/rr.sh ]; then mkdir -p /home/user/.rr && curl -sfL --retry 3 -o /home/user/.rr/b.zip "$RR_BUNDLE_URL" && unzip -q -o /home/user/.rr/b.zip -d /home/user/.rr; fi; if [ -f /home/user/.rr/katana/scripts/rr.sh ]; then source /home/user/.rr/katana/scripts/rr.sh; else source /home/user/.rr/scripts/rr.sh; fi; }
#   (The Higgsfield general-file store refuses .tgz (VERIFIED live 2026-10-08): ship the bundle as a .zip.)
#
# (Force a fresh bundle: prefix `rm -rf /home/user/.rr/scripts /home/user/.rr/katana/scripts;`.)
#
# Sandbox gotchas (VERIFIED live 2026-10-08):
#   - NEVER pipe rr_ws / rr_restore / rr_load into another command (`rr_restore s '<url>' | tail -3`):
#     a pipeline runs them in a subshell, so W, the cd and the exports are lost and every later command
#     of the chain runs outside the workspace. Let them print, or redirect: `rr_restore s '<url>' >/dev/null`.
#   - Keep each foreground sandbox_exec under ~45 s: a call that waited ~100 s (`rr_wait ... 100`) made the
#     MCP connector fail with "server isn't responding". rr_wait therefore caps at 45 s; poll again with a
#     new short call. Long work runs with background:true inside rr_bg.
#   - Every rr_save / rr_put burns one single-use media_upload slot: reserve all slots of a stage in ONE
#     media_upload files[] call before the stage.
#
# Exports: RR (this scripts dir), RR_HOME, RR_ROOT (workspaces), RR_PYLIB, RR_CACHE, PY, CHROME,
#          PYTHONPATH (+$RR_PYLIB +$RR), PATH (+$RR_PYLIB/bin), W (after rr_ws)
# Functions (all return non-zero on failure; see references/sandbox.md):
#   rr_ws <slug>                  create/enter workspace $W=$RR_ROOT/<slug> with the standard subdirs
#   rr_get <url> [dest]           download with retries (dest dir or file; default basename of url)
#   rr_put <file> <url> [mime]    presigned PUT (Content-Type + If-None-Match: *), prints "HTTP <code>"
#   rr_save <upload_url> [content_type]
#                                 LEAN tar.gz of the workspace and PUT it: no caches, comp/frames*, comp/stills,
#                                 huge files, ref/src.* (the downloaded original) or rebuildable frame
#                                 sequences (render.py prep JPEGs in plates/<id>/, PNG mattes in mattes/<id>/,
#                                 image dumps in cuts/<id>/); every .mp4/.json/.md stays. .rr_excluded.txt lists
#                                 what was left out, with a REBUILD command per sequence. RR_SAVE_FULL=1 keeps
#                                 sequences and ref/src.* (the old 78-184 MB archives). Reserve the slot as
#                                 '<slug>_vN_state.tar.gz' (media_upload, general file) and pass the content_type
#                                 from its reply (default application/octet-stream, which is what media_upload
#                                 returns for .tar.gz/.tar/.zip general files); then media_confirm and keep the
#                                 URL as the state URL
#   rr_load <state_url> [slug]    download a state tarball, unpack it into $W, print what to rebuild
#   rr_restore <slug> <state_url> rr_ws + rr_load only if the workspace has no saved state yet; either way
#                                 prints the frame folders that still need a rebuild
#   rr_rebuild [--dry]            run the pending REBUILD lines of .rr_excluded.txt from $W (render.py prep;
#                                 seconds per clip; many clips -> inside rr_bg with background:true)
#   rr_chrome                     print a working Chrome/Chromium binary path
#   rr_pip <pkg...>               use installed packages; missing packages require a hashed
#                                 RR_REQUIREMENTS_LOCK and install through Socket only
#   rr_bg <log> <cmd...>          run cmd with log + <log>.status (waits; use inside background:true)
#   rr_kill <log>                 stop an rr_bg job including its child processes
#   rr_status <log> [n]           print job state + last n log lines (rc 0 done,1 failed,3 running,4 missing,5 died)
#   rr_wait <log> [secs]          poll rr_status until done or secs (default 20, max 45) elapsed
#   rr_mime <file>                MIME type by extension
#   rr_info                       environment + workspaces + running jobs (shared-sandbox check)
#   rr_du                         workspace size per subdir
# Portable: bash 3.2+ (macOS) and bash 5 (Debian sandbox); no GNU-only flags, no bc.

RR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
export RR
export RR_VERSION="1"

if [ -z "${RR_HOME:-}" ]; then
  if [ -d /home/user ] && [ -w /home/user ]; then RR_HOME=/home/user; else RR_HOME="$HOME"; fi
fi
export RR_HOME
export RR_ROOT="${RR_ROOT:-$RR_HOME/rr}"
export RR_PYLIB="${RR_PYLIB:-$RR_HOME/pylib}"
export RR_CACHE="${RR_CACHE:-$RR_HOME/.rr/cache}"
export RR_TMP="${RR_TMP:-${TMPDIR:-/tmp}}"
export PY="${PY:-python3}"
export W="${W:-}"

case ":${PYTHONPATH:-}:" in *":$RR_PYLIB:"*) ;; *) PYTHONPATH="$RR_PYLIB${PYTHONPATH:+:$PYTHONPATH}" ;; esac
case ":${PYTHONPATH}:" in *":$RR:"*) ;; *) PYTHONPATH="$PYTHONPATH:$RR" ;; esac
export PYTHONPATH
case ":${PATH}:" in *":$RR_PYLIB/bin:"*) ;; *) PATH="$RR_PYLIB/bin:$PATH" ;; esac
export PATH

_rr_err() { echo "$*" >&2; }
_rr_size() { [ -f "$1" ] && wc -c < "$1" | tr -d ' ' || echo 0; }
_rr_lower() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }

# ---------------------------------------------------------------------------------------------
rr_ws() {
  local slug="${1:-}" d
  if [ -z "$slug" ]; then
    if [ -n "${W:-}" ] && [ -d "$W" ]; then cd "$W" && echo "$W"; return 0; fi
    _rr_err "usage: rr_ws <slug>   (existing: $(ls "$RR_ROOT" 2>/dev/null | tr '\n' ' '))"; return 2
  fi
  case "$slug" in
    *[!A-Za-z0-9._-]*|.*) _rr_err "rr_ws: slug must be [A-Za-z0-9._-] and not start with '.': '$slug'"; return 2 ;;
  esac
  W="$RR_ROOT/$slug"
  for d in ref analysis sheets plan gen plates mattes faces comp out qa logs; do
    mkdir -p "$W/$d" || { _rr_err "rr_ws: cannot create $W/$d"; return 1; }
  done
  export W
  cd "$W" || return 1
  echo "$W"
}

# ---------------------------------------------------------------------------------------------
rr_get() {
  local url="${1:-}" dest="${2:-}" base
  [ -n "$url" ] || { _rr_err "usage: rr_get <url> [dest_file_or_dir/]"; return 2; }
  base="$(basename "${url%%\?*}")"
  [ -n "$base" ] && [ "$base" != "/" ] || base="download"
  if [ -z "$dest" ]; then dest="$base"
  elif [ -d "$dest" ]; then dest="${dest%/}/$base"
  else case "$dest" in */) mkdir -p "$dest"; dest="$dest$base" ;; esac
  fi
  mkdir -p "$(dirname "$dest")" || return 1
  if curl -fL -sS --retry 4 --retry-delay 2 --retry-connrefused --connect-timeout 20 -o "$dest.part" "$url"; then
    mv -f "$dest.part" "$dest" || return 1
    echo "rr_get: $dest ($(_rr_size "$dest") bytes)"
  else
    local rc=$?
    rm -f "$dest.part"
    _rr_err "rr_get: FAILED (curl rc=$rc) ${url%%\?*}"
    return 1
  fi
}

# ---------------------------------------------------------------------------------------------
rr_mime() {
  local f; f="$(_rr_lower "${1:-}")"
  case "$f" in
    *.mp4|*.m4v) echo video/mp4 ;; *.mov) echo video/quicktime ;; *.webm) echo video/webm ;;
    *.mkv) echo video/x-matroska ;; *.jpg|*.jpeg) echo image/jpeg ;; *.png) echo image/png ;;
    *.webp) echo image/webp ;; *.gif) echo image/gif ;; *.mp3) echo audio/mpeg ;;
    *.wav) echo audio/wav ;; *.m4a) echo audio/mp4 ;; *.aac) echo audio/aac ;; *.ogg|*.opus) echo audio/ogg ;;
    *.flac) echo audio/flac ;; *.json) echo application/json ;; *.txt|*.log|*.md) echo text/plain ;;
    *.csv) echo text/csv ;; *.html) echo text/html ;; *.tar.gz|*.tgz|*.gz) echo application/gzip ;;
    *.tar) echo application/x-tar ;; *.zip) echo application/zip ;; *.pdf) echo application/pdf ;;
    *) echo application/octet-stream ;;
  esac
}

# rr_put <file> <upload_url> [mime]  - PUT to a media_upload presigned URL. The slot is single-use and
# signs Content-Type + If-None-Match, so: never PUT an empty file, and pass the exact content_type
# media_upload reported when it differs from the extension default.
rr_put() {
  local f="${1:-}" url="${2:-}" mime="${3:-}" code="" prev="" i errf rc
  [ -n "$f" ] && [ -n "$url" ] || { _rr_err "usage: rr_put <file> <upload_url> [mime]"; return 2; }
  [ -s "$f" ] || { _rr_err "rr_put: '$f' is missing or empty - NOT uploading (a PUT would burn the single-use slot)"; return 1; }
  [ -n "$mime" ] || mime="$(rr_mime "$f")"
  errf="$(mktemp "$RR_TMP/rr_put.XXXXXX")"
  for i in 1 2 3 4; do
    code="$(curl -sS -f -X PUT -H "Content-Type: $mime" -H "If-None-Match: *" --upload-file "$f" \
             --connect-timeout 20 -o /dev/null -w '%{http_code}' "$url" 2>"$errf")"
    rc=$?
    case "$code" in
      200|201|204)
        echo "HTTP $code $f ($(_rr_size "$f") bytes, $mime)"; rm -f "$errf"; return 0 ;;
      412)
        if [ -n "$prev" ]; then
          echo "HTTP 412 $f - slot already written after a failed attempt ($prev): probably uploaded; media_confirm will tell"
          rm -f "$errf"; return 0
        fi
        echo "HTTP 412 $f - slot already used (presigned URLs are single-use: request a new one with media_upload)"
        rm -f "$errf"; return 1 ;;
      000|408|429|5??)
        prev="$code"; sleep $((i * 2)) ;;
      *)
        echo "HTTP $code $f - FAILED (curl rc=$rc: $(tail -c 300 "$errf" | tr '\n' ' '))"
        [ "$code" = 403 ] && echo "  hint: 403 usually means Content-Type '$mime' differs from the one media_upload signed, or the URL expired"
        rm -f "$errf"; return 1 ;;
    esac
  done
  echo "HTTP $code $f - FAILED after 4 attempts ($(tail -c 300 "$errf" | tr '\n' ' '))"
  rm -f "$errf"; return 1
}

# ---------------------------------------------------------------------------------------------
# State: everything in $W except caches, rendered frame dumps (comp/frames, comp/frames_preview,
# comp/frames_unused, comp/stills: recreated by the next render) and files > RR_SAVE_MAX_MB (default 150).
# Extra exclusions: RR_SAVE_EXCLUDE="./gen/raw ./plates/*.mov" (find -path patterns relative to $W).
# Lean by default (RR_SAVE_FULL=1 turns it off): ./ref/src.* and the image files of every REBUILDABLE frame
# sequence stay out: plates/<id>/ and mattes/<id>/ whose clip.json names a source that is itself in the state
# (render.py prep rebuilds them from gen/*.mp4 in seconds), and cuts/<id>/ image dumps. A sequence that cannot
# be rebuilt (no clip.json, source outside $W or not saved) is kept whole. VERIFIED live 2026-10-08: the
# archives were 78-184 MB, almost all ref/src.* plus prep JPEG/PNG sequences.
_RR_SEQ_NAMES="jpg jpeg png webp bmp tif tiff"

# _rr_lean_scan <dirs_out>  (cwd = $W) - prints the .rr_excluded.txt lines of the sequences it leaves out
# (one per dir, a REBUILD command on the first dir of each clip) and writes those dirs, one per line, to
# <dirs_out>. Python stdlib; on any error nothing is left out (safe) and a warning goes to stderr.
_rr_lean_scan() {
  local out="$1"
  : > "$out" || return 1
  if "$PY" -I - "$W" "$out" "${RR_SAVE_MAX_MB:-150}" "${RR_SAVE_EXCLUDE:-}" "$_RR_SEQ_NAMES" <<'PY'
import fnmatch, json, os, re, shlex, sys
W, out, maxmb, excl, exts = sys.argv[1:6]
W = os.path.realpath(W)
maxb = float(maxmb) * 1048576
excl = excl.split()
IMG = tuple("." + e for e in exts.split())
PRUNE = {"frames_cache", "__pycache__", "node_modules", "tmp", ".tmp"}
JUNK = ("*.part", "*.raw", "*.y4m", "*.yuv", ".*.tmp", ".DS_Store")
NAME = re.compile(r"[A-Za-z0-9._-]+\Z")


def seq(dp):
    n = b = 0
    ext = set()
    for root, ds, fs in os.walk(dp):
        ds[:] = [d for d in ds if d not in PRUNE]
        for f in fs:
            e = os.path.splitext(f)[1].lower()
            if e in IMG:
                try:
                    sz = os.path.getsize(os.path.join(root, f))
                except OSError:
                    continue
                if sz <= maxb:
                    n, b = n + 1, b + sz
                    ext.add(e)
    return n, b, ext


def rel_in_w(p):
    """clip.json src -> path relative to W, or None when it lies outside W."""
    if not p:
        return None
    a = os.path.realpath(p if os.path.isabs(p) else os.path.join(W, p))
    return os.path.relpath(a, W) if a.startswith(W + os.sep) else None


def saved(rel):
    """(True, '') when rr_save puts this file into the state, else (False, why)."""
    if rel is None:
        return False, "source outside the workspace"
    full = os.path.join(W, rel)
    if not os.path.isfile(full):
        return False, "source missing"
    parts = rel.split(os.sep)
    if any(x in PRUNE for x in parts[:-1]) or rel.startswith(("comp" + os.sep + "frames", "comp" + os.sep + "stills")):
        return False, "source in a pruned folder"
    if fnmatch.fnmatchcase("./" + rel, "./ref/src.*"):
        return False, "source is ref/src.* (not saved)"
    if any(fnmatch.fnmatchcase(parts[-1], j) for j in JUNK):
        return False, "source matches a junk pattern"
    if os.path.getsize(full) > maxb:
        return False, f"source larger than RR_SAVE_MAX_MB={maxmb}"
    for pat in excl:
        for k in range(1, len(parts) + 1):
            if fnmatch.fnmatchcase("./" + "/".join(parts[:k]), pat):
                return False, f"source excluded by RR_SAVE_EXCLUDE {pat}"
    return True, ""


def clip_json(d):
    try:
        with open(os.path.join(d, "clip.json"), encoding="utf-8") as f:
            j = json.load(f)
        return j if isinstance(j, dict) else None
    except (OSError, ValueError):
        return None


def mb(b):
    return f"{b / 1048576:.1f} MB"


def ids(top):
    base = os.path.join(W, top)
    try:
        names = sorted(os.listdir(base))
    except OSError:
        return []
    return [d for d in names if os.path.isdir(os.path.join(base, d)) and not os.path.islink(os.path.join(base, d))]


lines, dirs, kept = [], [], []
q = shlex.quote
for cid in sorted(set(ids("plates")) | set(ids("mattes"))):
    pd, md = os.path.join(W, "plates", cid), os.path.join(W, "mattes", cid)
    pn, pb, pe = seq(pd) if os.path.isdir(pd) else (0, 0, set())
    mn, mbytes, me = seq(md) if os.path.isdir(md) else (0, 0, set())
    if not pn and not mn:
        continue
    if not NAME.match(cid):
        kept.append(f"# kept: ./plates|mattes/{cid}/ (clip id has characters rr_save does not pattern-match)")
        continue
    pj, mj = clip_json(pd), clip_json(md)
    src = rel_in_w((pj or {}).get("src"))
    ok, why = saved(src) if pj else (False, "no plates/" + cid + "/clip.json")
    if not ok:
        for d, n in (("plates", pn), ("mattes", mn)):
            if n:
                kept.append(f"# kept: ./{d}/{cid}/ {n} images (not rebuildable: {why})")
        continue
    args = pj.get("prep_args")
    if not isinstance(args, list) or not args or not all(isinstance(v, str) for v in args):
        for d, n in (("plates", pn), ("mattes", mn)):
            if n:
                kept.append(f"# kept: ./{d}/{cid}/ {n} images (no exact prep_args; re-run prep before a lean save)")
        continue
    if any("\n" in v or "\r" in v for v in args):
        for d, n in (("plates", pn), ("mattes", mn)):
            if n:
                kept.append(f"# kept: ./{d}/{cid}/ {n} images (multiline prep_args cannot use the line-based rebuild manifest)")
        continue
    if "--mask" in args:
        mi = args.index("--mask") + 1
        mok, mwhy = saved(rel_in_w(args[mi])) if mi < len(args) else (False, "missing mask argument")
        if not mok:
            for d, n in (("plates", pn), ("mattes", mn)):
                if n:
                    kept.append(f"# kept: ./{d}/{cid}/ {n} images (prep mask not rebuildable: {mwhy})")
            continue
    cmd = ["python3", "$RR/comp/render.py", "prep", "$W"] + args
    use_m = False
    if mn:
        msrc = rel_in_w((mj or {}).get("src"))
        mok, mwhy = saved(msrc) if mj else (False, "no mattes/" + cid + "/clip.json")
        if mok and "--mask" in args:
            use_m = True
        else:
            if mok:
                mwhy = "prep_args has no mask operation"
            kept.append(f"# kept: ./mattes/{cid}/ {mn} images (not rebuildable: {mwhy})")
    sh = " ".join(f'"{x}"' if x in ("$RR/comp/render.py", "$W") else q(x) for x in cmd)
    first = True
    for d, n, b, e, use in (("plates", pn, pb, pe, True), ("mattes", mn, mbytes, me, use_m)):
        if not n or not use:
            continue
        head = f"./{d}/{cid}/ {n} x {'/'.join(sorted(e))} {mb(b)}"
        lines.append(f"{head}  REBUILD: {sh}" if first else f"{head}  (rebuilt by the REBUILD line of ./plates/{cid}/)")
        dirs.append(f"./{d}/{cid}")
        first = False

for cid in ids("cuts"):
    cd = os.path.join(W, "cuts", cid)
    n, b, e = seq(cd)
    if not n:
        continue
    if not NAME.match(cid):
        kept.append(f"# kept: ./cuts/{cid}/ (name has characters rr_save does not pattern-match)")
        continue
    lines.append(f"./cuts/{cid}/ {n} x {'/'.join(sorted(e))} {mb(b)}  (frame dump; frames.py export re-creates cuts/<id>.mp4 if needed)")
    dirs.append(f"./cuts/{cid}")

with open(out, "w", encoding="utf-8") as f:
    f.write("".join(d + "\n" for d in dirs))
print("\n".join(lines + kept))
PY
  then
    return 0
  else
    _rr_err "rr_save: lean scan failed - frame sequences kept in the state"
    : > "$out"
  fi
}

_rr_state_find() {  # $1 = include|exclude, $2 = file of lean sequence dirs (from _rr_lean_scan; may be empty)
  local mode="$1" dirsf="${2:-}" max="${RR_SAVE_MAX_MB:-150}" p d e
  local -a prune junk pats lean dpat ipat
  lean=(); dpat=(); ipat=()
  prune=( -type d \( -name frames_cache -o -name __pycache__ -o -name node_modules -o -name tmp -o -name .tmp -o -path './comp/frames*' -o -path ./comp/stills \) )
  set -f; pats=( ${RR_SAVE_EXCLUDE:-} ); set +f   # patterns stay literal (no globbing here)
  if [ ${#pats[@]} -gt 0 ]; then for p in "${pats[@]}"; do prune=( "${prune[@]}" -o -path "$p" ); done; fi
  junk=( -name '*.part' -o -name '*.raw' -o -name '*.y4m' -o -name '*.yuv' -o -name '.*.tmp' -o -name '.DS_Store' -o -size +"${max}"M )
  if [ "${RR_SAVE_FULL:-0}" != 1 ]; then
    lean=( -path './ref/src.*' )
    if [ -n "$dirsf" ] && [ -s "$dirsf" ]; then
      while IFS= read -r d; do
        [ -n "$d" ] || continue
        if [ ${#dpat[@]} -gt 0 ]; then dpat=( "${dpat[@]}" -o -path "$d/*" ); else dpat=( -path "$d/*" ); fi
      done < "$dirsf"
      for e in $_RR_SEQ_NAMES; do
        if [ ${#ipat[@]} -gt 0 ]; then ipat=( "${ipat[@]}" -o -iname "*.$e" ); else ipat=( -iname "*.$e" ); fi
      done
      if [ ${#dpat[@]} -gt 0 ]; then lean=( "${lean[@]}" -o \( \( "${dpat[@]}" \) \( "${ipat[@]}" \) \) ); fi
    fi
  fi
  if [ "$mode" = include ]; then
    if [ ${#lean[@]} -gt 0 ]; then
      find . \( \( "${prune[@]}" \) -prune \) -o \( -type f \( "${junk[@]}" \) \) -o \( -type f \( "${lean[@]}" \) \) \
        -o \( -type f -print0 \)
    else
      find . \( \( "${prune[@]}" \) -prune \) -o \( -type f \( "${junk[@]}" \) \) -o \( -type f -print0 \)
    fi
  elif [ ${#lean[@]} -gt 0 ]; then  # sequences are summarised per folder by _rr_lean_scan: only ref/src.* here
    find . \( \( "${prune[@]}" \) -prune -print \) -o \( -type f \( "${junk[@]}" \) -print \) \
      -o \( -type f -path './ref/src.*' -print \) \
      | sed 's|^\(\./ref/src\.[^/]*\)$|\1  (downloaded original; ref/ref.mp4 preserves the original media bytes)|'
  else
    find . \( \( "${prune[@]}" \) -prune -print \) -o \( -type f \( "${junk[@]}" \) -print \)
  fi
}

# rr_save <upload_url> [content_type]  - slot reserved with media_upload (general file) as
# '<slug>_vN_state.tar.gz'; pass the content_type the reply echoed (the PUT signature covers it).
rr_save() {
  local url="${1:-}" mime="${2:-application/octet-stream}" slug list tarf n bytes nex dirsf rep nseq
  [ -n "$url" ] || { _rr_err "usage: rr_save <upload_url> [content_type]   (media_upload slot '<slug>_vN_state.tar.gz', type file; content_type from its reply)"; return 2; }
  [ -n "${W:-}" ] && [ -d "$W" ] || { _rr_err "rr_save: no workspace - run rr_ws <slug> first"; return 1; }
  slug="$(basename "$W")"
  list="$(mktemp "$RR_TMP/rr_list.XXXXXX")"
  dirsf="$(mktemp "$RR_TMP/rr_lean.XXXXXX")"
  rep="$(mktemp "$RR_TMP/rr_rep.XXXXXX")"
  tarf="$RR_TMP/rr_state_${slug}_$$.tar.gz"
  (
    cd "$W" || exit 1
    printf '%s\n' "$slug" > .rr_slug
    if [ "${RR_SAVE_FULL:-0}" != 1 ]; then _rr_lean_scan "$dirsf" > "$rep"; fi
    {
      if [ "${RR_SAVE_FULL:-0}" = 1 ]; then
        echo "# rr_save FULL state (RR_SAVE_FULL=1): only caches, frame dumps and huge files are left out."
      else
        echo "# rr_save lean state: these paths are NOT in the archive (RR_SAVE_FULL=1 keeps sequences and ref/src.*)."
        echo "# Run the REBUILD lines from \$W before rendering (rr_rebuild does it; rr_restore lists the pending ones)."
      fi
      _rr_state_find exclude "$dirsf" 2>/dev/null
      cat "$rep"
    } > .rr_excluded.txt
    printf '{"slug":"%s","saved_at":"%s","saved_epoch":%s,"rr_version":"%s","max_file_mb":%s,"lean":%s}\n' \
      "$slug" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(date +%s)" "$RR_VERSION" "${RR_SAVE_MAX_MB:-150}" \
      "$([ "${RR_SAVE_FULL:-0}" = 1 ] && echo false || echo true)" > .rr_state.json
    _rr_state_find include "$dirsf" > "$list"
    [ -s "$list" ] || exit 3
    tar -czf "$tarf" --null -T "$list"
  ) || { _rr_err "rr_save: tar failed (or empty workspace)"; rm -f "$list" "$tarf" "$dirsf" "$rep"; return 1; }
  n="$(tr -cd '\000' < "$list" | wc -c | tr -d ' ')"
  nex="$(grep -vc '^#' "$W/.rr_excluded.txt" 2>/dev/null || true)"
  nseq="$(grep -c . "$dirsf" 2>/dev/null || true)"
  bytes="$(_rr_size "$tarf")"
  echo "rr_save: $slug -> $n files, $bytes bytes (excluded ${nex:-0} paths, ${nseq:-0} rebuildable frame folders: see .rr_excluded.txt)"
  rr_put "$tarf" "$url" "$mime"
  local rc=$?
  rm -f "$list" "$tarf" "$dirsf" "$rep"
  [ $rc -eq 0 ] && echo "rr_save: OK - now media_confirm(type='file') and keep the returned URL as the state URL"
  return $rc
}

# _rr_pending  (needs $W) - REBUILD lines of .rr_excluded.txt whose folder has no images on disk yet
_rr_pending() {
  local f="$W/.rr_excluded.txt" line d e has
  [ -s "$f" ] || return 0
  grep '  REBUILD: ' "$f" | while IFS= read -r line; do
    d="${line%% *}"; has=""
    for e in $_RR_SEQ_NAMES; do
      if [ -n "$(find "$W/$d" -type f -iname "*.$e" 2>/dev/null | head -n 1)" ]; then has=1; break; fi
    done
    [ -n "$has" ] || printf '%s\n' "$line"
  done
}

_rr_print_pending() {  # $1 = prefix
  local pend
  pend="$(_rr_pending)"
  [ -n "$pend" ] || return 0
  echo "$1: REBUILD before rendering - $(printf '%s\n' "$pend" | grep -c .) frame folder(s) left out of the lean state (run rr_rebuild, or each command from \$W):"
  printf '%s\n' "$pend" | sed 's/^/  /'
}

rr_load() {
  local url="${1:-}" slug="${2:-}" tmp n
  [ -n "$url" ] || { _rr_err "usage: rr_load <state_url> [slug]"; return 2; }
  tmp="$(mktemp "$RR_TMP/rr_state.XXXXXX")"
  rr_get "$url" "$tmp" >/dev/null || { rm -f "$tmp"; return 1; }
  if [ -z "$slug" ] && [ -z "${W:-}" ]; then
    slug="$(tar -xOf "$tmp" ./.rr_slug 2>/dev/null | head -n 1)"
  fi
  if [ -n "$slug" ]; then rr_ws "$slug" >/dev/null || { rm -f "$tmp"; return 1; }; fi
  [ -n "${W:-}" ] || { _rr_err "rr_load: no slug given and none in the tarball"; rm -f "$tmp"; return 1; }
  tar -xf "$tmp" -C "$W" || { _rr_err "rr_load: untar failed (not a state tarball?)"; rm -f "$tmp"; return 1; }
  n="$(tar -tf "$tmp" | grep -vc '/$' || true)"
  rm -f "$tmp"
  cd "$W" || return 1
  echo "rr_load: $n files -> $W"
  if [ -s "$W/.rr_excluded.txt" ] && grep -v '^#' "$W/.rr_excluded.txt" | grep -vq '  REBUILD: \|(rebuilt by the REBUILD line'; then
    echo "rr_load: NOT in the state (re-fetch or re-create if needed):"
    grep -v '^#' "$W/.rr_excluded.txt" | grep -v '  REBUILD: \|(rebuilt by the REBUILD line' | head -n 20 | cut -c1-200 | sed 's/^/  /'
  fi
  _rr_print_pending rr_load
}

rr_restore() {
  local slug="${1:-}" url="${2:-}"
  [ -n "$slug" ] && [ -n "$url" ] || { _rr_err "usage: rr_restore <slug> <state_url>"; return 2; }
  rr_ws "$slug" >/dev/null || return 1
  if [ -f "$W/.rr_state.json" ]; then
    echo "rr_restore: $W already present (sandbox still warm) - not reloading"
    _rr_print_pending rr_restore
  else
    rr_load "$url" "$slug"
  fi
}

# rr_rebuild [--dry]  - run every pending REBUILD line of $W/.rr_excluded.txt (folders that have no images
# yet), from $W, as a validated argument vector for the trusted prep helper (never shell code).
# Returns non-zero when one fails.
rr_rebuild() {
  local dry="" pend line cmd d rc=0 k=0
  [ "${1:-}" = --dry ] && dry=1
  [ -n "${W:-}" ] && [ -d "$W" ] || { _rr_err "rr_rebuild: no workspace - run rr_ws/rr_restore first"; return 1; }
  pend="$(_rr_pending)"
  [ -n "$pend" ] || { echo "rr_rebuild: nothing to rebuild"; return 0; }
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    d="${line%% *}"; cmd="${line#*  REBUILD: }"
    k=$((k + 1))
    if [ -n "$dry" ]; then echo "rr_rebuild: would run ($d): $cmd"; continue; fi
    echo "rr_rebuild: $d"
    if "$PY" -I - "$RR/comp/render.py" "$W" "$cmd" "$PY" <<'PY'
import os, shlex, subprocess, sys
script, workspace, command, python = sys.argv[1:]
try:
    args = shlex.split(command, comments=True)
    if args[:4] != ["python3", "$RR/comp/render.py", "prep", "$W"] or len(args) < 7:
        raise ValueError("expected the trusted render.py prep command")
    args = args[4:]
    if args[1] != "--clip" or args[2] in (".", ".."):
        raise ValueError("invalid prep clip arguments")
    paths = [args[0]]
    allowed = {"--clip", "--width", "--height", "--quality", "--start", "--count", "--mask", "--mask-mode", "--mask-width", "--thr", "--close", "--vf"}
    i = 1
    while i < len(args):
        flag = args[i]
        if flag == "--native":
            i += 1
            continue
        if flag not in allowed or i + 1 >= len(args):
            raise ValueError("unsupported or incomplete prep option")
        if flag == "--mask":
            paths.append(args[i + 1])
        i += 2
    root = os.path.realpath(workspace)
    for path in paths:
        resolved = os.path.realpath(os.path.join(root, path))
        if not resolved.startswith(root + os.sep) or not os.path.isfile(resolved):
            raise ValueError("prep input must be a saved file inside the workspace")
except (ValueError, IndexError) as exc:
    print(f"rr_rebuild: invalid REBUILD entry: {exc}", file=sys.stderr)
    sys.exit(2)
sys.exit(subprocess.run([python, script, "prep", root] + args, cwd=root).returncode)
PY
    then :
    else _rr_err "rr_rebuild: FAILED for $d: $cmd"; rc=1
    fi
  done <<EOF
$pend
EOF
  [ -n "$dry" ] || echo "rr_rebuild: $k folder(s) processed$([ $rc -ne 0 ] && echo ', with failures')"
  return $rc
}

# ---------------------------------------------------------------------------------------------
rr_chrome() {
  local c found=""
  if [ -n "${CHROME:-}" ] && [ -x "$CHROME" ]; then echo "$CHROME"; return 0; fi
  for c in /ms-playwright/chromium-*/chrome-linux64/chrome /ms-playwright/chromium-*/chrome-linux/chrome; do
    [ -x "$c" ] && found="$c"
  done
  if [ -z "$found" ]; then
    for c in /ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell \
             /ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell; do
      [ -x "$c" ] && found="$c"
    done
  fi
  if [ -z "$found" ]; then
    for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
             "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
      [ -x "$c" ] && { found="$c"; break; }
    done
  fi
  if [ -z "$found" ]; then
    for c in chromium chromium-browser google-chrome google-chrome-stable chrome; do
      if command -v "$c" >/dev/null 2>&1; then found="$(command -v "$c")"; break; fi
    done
  fi
  [ -n "$found" ] || { _rr_err "rr_chrome: no Chrome/Chromium found (set CHROME=/path/to/chrome)"; return 1; }
  echo "$found"
}

# ---------------------------------------------------------------------------------------------
rr_pip() {
  [ $# -gt 0 ] || { _rr_err "usage: rr_pip <pkg> [pkg...]"; return 2; }
  local check_rc
  if "$PY" - "$@" <<'PY'
import importlib.metadata as metadata
import re
import sys
missing = []
for spec in sys.argv[1:]:
    match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9_.-]*)(?:==([A-Za-z0-9][A-Za-z0-9_.+!-]*))?", spec)
    if not match:
        print("rr_pip: only package names or exact name==version requests are supported", file=sys.stderr)
        sys.exit(2)
    name, required = match.groups()
    try:
        installed = metadata.version(name)
    except metadata.PackageNotFoundError:
        installed = None
    if installed is None or (required is not None and installed != required):
        missing.append(spec)
if missing:
    print("rr_pip: missing pinned runtime dependencies: " + ", ".join(missing), file=sys.stderr)
    sys.exit(10)
PY
  then check_rc=0; else check_rc=$?; fi
  [ "$check_rc" -eq 0 ] && { echo "rr_pip: available ($*)"; return 0; }
  [ "$check_rc" -eq 10 ] || return "$check_rc"
  [ -n "${RR_REQUIREMENTS_LOCK:-}" ] && [ -f "$RR_REQUIREMENTS_LOCK" ] || {
    _rr_err "rr_pip: unavailable dependency; deployment has no RR_REQUIREMENTS_LOCK. No install attempted."
    return 1
  }
  # A deployment-owned lock includes every transitive dependency. Reject indexes, URLs,
  # editable/local inputs and loose versions rather than passing options through to pip.
  if "$PY" - "$RR_REQUIREMENTS_LOCK" "$@" <<'PY'
from pathlib import Path
import re
import sys
normalize = lambda name: re.sub(r"[-_.]+", "-", name).lower()
pins = {}
try:
    content = Path(sys.argv[1]).read_text(encoding="utf-8").replace("\\\n", " ")
    for raw in content.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        match = re.fullmatch(r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9][A-Za-z0-9_.+!-]*)(?:\s+--hash=sha256:[0-9a-fA-F]{64})+", line)
        if not match:
            raise ValueError("lock must contain only exact version pins with SHA-256 hashes")
        name, version = match.groups()
        key = normalize(name)
        if key in pins:
            raise ValueError("duplicate package in lock")
        pins[key] = version
    for spec in sys.argv[2:]:
        name, sep, version = spec.partition("==")
        locked = pins.get(normalize(name))
        if locked is None or (sep and locked != version):
            raise ValueError("requested package/version is absent from the deployment lock")
except (OSError, ValueError) as exc:
    print("rr_pip: " + str(exc), file=sys.stderr)
    sys.exit(2)
PY
  then check_rc=0; else check_rc=$?; fi
  [ "$check_rc" -eq 0 ] || return "$check_rc"
  mkdir -p "$RR_PYLIB" || return 1
  (
    # Ignore inherited pip options and all config files, including extra requirements,
    # alternate indexes and dry-run. Retain unrelated proxy/certificate settings.
    for rr_pip_env_name in "${!PIP_@}"; do unset "$rr_pip_env_name"; done
    export PIP_CONFIG_FILE=/dev/null
    "$PY" -m pip install --index-url https://socket-firewall.higgsfield.xyz/pypi/simple \
      --require-hashes --no-deps --only-binary=:all: --requirement "$RR_REQUIREMENTS_LOCK" \
      --target "$RR_PYLIB" --upgrade -q --disable-pip-version-check --no-warn-script-location
  ) || return $?
  if "$PY" - "$@" <<'PY'
import importlib.metadata as metadata
import sys
for spec in sys.argv[1:]:
    name, sep, version = spec.partition("==")
    try:
        actual = metadata.version(name)
    except metadata.PackageNotFoundError:
        print("rr_pip: dependency still unavailable after installation: " + name, file=sys.stderr)
        sys.exit(1)
    if sep and actual != version:
        print("rr_pip: installed version does not match request: " + name, file=sys.stderr)
        sys.exit(1)
PY
  then echo "rr_pip: verified deployment dependencies through Socket -> $RR_PYLIB"
  else return $?
  fi
}

# ---------------------------------------------------------------------------------------------
# rr_bg <log> <cmd...>   Runs cmd with stdout+stderr -> log, SIGHUP ignored (nohup semantics), and
# writes <log>.status: "state=running start=..." then "state=done|failed rc=N start= end= secs=".
# Waits for the command (exit code = command's), which is what a sandbox_exec background:true call
# needs (the platform keeps the lease while the command runs). A single argument is run as a bash
# string: rr_bg logs/x.log "python3 a.py && python3 b.py". RR_BG_DETACH=1 returns immediately
# (local use only: a detached child does not outlive a foreground sandbox call).
rr_bg() {
  local log="${1:-}" st start pid
  [ -n "$log" ] && [ $# -ge 2 ] || { _rr_err "usage: rr_bg <logfile> <cmd...>   or   rr_bg <logfile> \"shell string\""; return 2; }
  shift
  case "$log" in /*) ;; *) log="$PWD/$log" ;; esac
  mkdir -p "$(dirname "$log")" || return 1
  st="$log.status"
  start="$(date +%s)"
  : > "$log"
  # the recorded command never keeps URL query strings (presigned signatures)
  printf 'state=running start=%s cmd=%s\n' "$start" \
    "$(printf '%s ' "$@" | tr '\n' ' ' | sed 's/?[^ ]*/?<q>/g' | cut -c1-200)" > "$st"
  (
    trap '' HUP
    if [ $# -eq 1 ]; then bash -c "$1"; else "$@"; fi < /dev/null >> "$log" 2>&1
    rc=$?
    end="$(date +%s)"
    if [ $rc -eq 0 ]; then s=done; else s=failed; fi
    echo "[rr_bg] $s rc=$rc after $((end - start))s" >> "$log"
    printf 'state=%s rc=%s start=%s end=%s secs=%s\n' "$s" "$rc" "$start" "$end" "$((end - start))" > "$st.tmp" \
      && mv -f "$st.tmp" "$st"
    exit $rc
  ) < /dev/null > /dev/null 2>&1 &
  pid=$!
  echo "$pid" > "$log.pid"
  echo "rr_bg: pid $pid log $log"
  if [ "${RR_BG_DETACH:-0}" = 1 ]; then disown "$pid" 2>/dev/null; return 0; fi
  wait "$pid"
}

_rr_children() {  # direct children of pid $1 (pgrep, else /proc scan on Linux)
  if command -v pgrep >/dev/null 2>&1; then pgrep -P "$1" 2>/dev/null; return 0; fi
  local f
  for f in /proc/[0-9]*/stat; do
    [ -r "$f" ] || continue
    set -- "$1" $(sed 's/^.*) //' "$f" 2>/dev/null)
    [ "${3:-}" = "$1" ] && { f="${f#/proc/}"; echo "${f%/stat}"; }
  done
}

_rr_tree() {  # pid $1 and all its descendants, parents first
  local c
  echo "$1"
  for c in $(_rr_children "$1"); do _rr_tree "$c"; done
}

# rr_kill <log>  - stop an rr_bg job and everything it started (a plain `kill <pid>` of the
# wrapper would orphan the real command). The wrapper then records state=failed rc=143.
rr_kill() {
  local log="${1:-}" pid c kids=""
  [ -n "$log" ] || { _rr_err "usage: rr_kill <logfile>"; return 2; }
  case "$log" in /*) ;; *) log="$PWD/$log" ;; esac
  pid="$(cat "$log.pid" 2>/dev/null)"
  [ -n "$pid" ] || { _rr_err "rr_kill: no pid file for $log"; return 1; }
  kill -0 "$pid" 2>/dev/null || { echo "rr_kill: pid $pid already gone"; return 0; }
  for c in $(_rr_children "$pid"); do kids="$kids $(_rr_tree "$c" | tr '\n' ' ')"; done
  if [ -n "${kids// /}" ]; then
    # freeze the whole subtree first so no shell in it can run its next command, then terminate;
    # the wrapper itself survives long enough to write state=failed rc=143
    kill -STOP $kids 2>/dev/null; kill -TERM $kids 2>/dev/null; kill -CONT $kids 2>/dev/null
  fi
  sleep 1
  kill -0 "$pid" 2>/dev/null && kill -TERM "$pid" 2>/dev/null
  echo "rr_kill: stopped job $pid ($log)"
}

_rr_field() { printf '%s\n' "$1" | tr ' ' '\n' | sed -n "s/^$2=//p" | head -n 1; }

rr_status() {
  local log="${1:-}" n="${2:-12}" line state pid now start
  [ -n "$log" ] || { _rr_err "usage: rr_status <logfile> [lines]"; return 2; }
  case "$log" in /*) ;; *) log="$PWD/$log" ;; esac
  if [ ! -f "$log.status" ] && [ ! -f "$log" ]; then
    echo "STATUS missing - no $log (sandbox reset or wrong path; restore state and rerun)"; return 4
  fi
  line="$(head -n 1 "$log.status" 2>/dev/null)"
  state="$(_rr_field "$line" state)"
  now="$(date +%s)"; start="$(_rr_field "$line" start)"
  case "$state" in
    done)   echo "STATUS done rc=0 in $(_rr_field "$line" secs)s" ;;
    failed) echo "STATUS failed rc=$(_rr_field "$line" rc) after $(_rr_field "$line" secs)s" ;;
    running)
      pid="$(cat "$log.pid" 2>/dev/null)"
      if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
        sleep 1; line="$(head -n 1 "$log.status" 2>/dev/null)"; state="$(_rr_field "$line" state)"
        if [ "$state" = running ]; then echo "STATUS died - pid $pid gone without a final status (killed / lease expired)"; state=died; fi
      fi
      [ "$state" = running ] && echo "STATUS running $((now - ${start:-$now}))s pid=${pid:-?}"
      [ "$state" = done ] && echo "STATUS done rc=0 in $(_rr_field "$line" secs)s"
      [ "$state" = failed ] && echo "STATUS failed rc=$(_rr_field "$line" rc) after $(_rr_field "$line" secs)s" ;;
    *) echo "STATUS unknown (no status file; log only)"; state=unknown ;;
  esac
  if [ -f "$log" ] && [ "$n" != 0 ]; then
    tail -c 6000 "$log" | tr '\r' '\n' | grep -v '^[[:space:]]*$' | tail -n "$n" | cut -c1-240
  fi
  case "$state" in done) return 0 ;; failed) return 1 ;; running) return 3 ;; died) return 5 ;; *) return 4 ;; esac
}

rr_wait() {
  local log="${1:-}" secs="${2:-20}" t0 rc
  [ -n "$log" ] || { _rr_err "usage: rr_wait <logfile> [max_secs<=45]"; return 2; }
  # capped at 45 s: a ~100 s foreground wait made the MCP connector drop the call (VERIFIED live 2026-10-08)
  [ "$secs" -gt 45 ] 2>/dev/null && secs=45
  t0="$(date +%s)"
  while :; do
    rr_status "$log" 0 >/dev/null; rc=$?
    [ $rc -ne 3 ] && break
    [ $(( $(date +%s) - t0 )) -ge "$secs" ] && break
    sleep 3
  done
  rr_status "$log" "${3:-8}"
}

# ---------------------------------------------------------------------------------------------
rr_info() {
  echo "RR=$RR (v$RR_VERSION)"; echo "W=${W:-<unset>}  RR_ROOT=$RR_ROOT"
  echo "CHROME=${CHROME:-<none>}"
  echo "python: $("$PY" -c 'import sys,numpy;print(sys.version.split()[0],"numpy",numpy.__version__)' 2>/dev/null || echo '?')"
  echo "ffmpeg: $(ffmpeg -hide_banner -version 2>/dev/null | head -n 1 | cut -d' ' -f1-3)"
  echo "disk:   $(df -h "$RR_HOME" 2>/dev/null | tail -n 1 | tr -s ' ' | cut -d' ' -f2-5)"
  echo "load:   $(uptime 2>/dev/null | sed 's/.*load average[s]*: //')"
  echo "workspaces (shared sandbox - other chats may own some):"
  local d f
  for d in "$RR_ROOT"/*; do
    [ -d "$d" ] || continue
    echo "  $(basename "$d")  $(du -sh "$d" 2>/dev/null | cut -f1)"
    for f in "$d"/logs/*.status; do
      [ -f "$f" ] || continue
      grep -q 'state=running' "$f" && echo "    running: $(basename "${f%.status}")"
    done
  done
}

rr_du() {
  [ -n "${W:-}" ] && [ -d "$W" ] || { _rr_err "rr_du: no workspace"; return 1; }
  du -sh "$W" 2>/dev/null; du -sh "$W"/* 2>/dev/null | sort -h 2>/dev/null || du -sh "$W"/* 2>/dev/null
}

if [ -z "${CHROME:-}" ] || [ ! -x "${CHROME:-}" ]; then
  CHROME="$(rr_chrome 2>/dev/null || true)"
fi
export CHROME

export _RR_SEQ_NAMES
export -f rr_ws rr_get rr_put rr_mime rr_save rr_load rr_restore rr_rebuild rr_chrome rr_pip rr_bg rr_kill rr_status \
  rr_wait rr_info rr_du _rr_err _rr_size _rr_lower _rr_state_find _rr_lean_scan _rr_pending _rr_print_pending \
  _rr_field _rr_children _rr_tree 2>/dev/null || true
