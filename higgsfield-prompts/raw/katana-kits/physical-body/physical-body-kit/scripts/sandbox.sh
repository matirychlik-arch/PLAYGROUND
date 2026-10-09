#!/usr/bin/env bash
# sandbox.sh - the physical-body pipeline for the ephemeral Higgsfield sandbox (Linux, /home/user).
# The sandbox can be discarded between calls, so every step rebuilds the job from the clip URL when needed
# (deterministic: same clip + same options + same fixes.json -> same edit).
#
#   sandbox.sh prepare <slug> <clip_url> [--start S] [--max-dur S]
#       clip -> template media + doctor -> init -> prep -> edit -> review thumbnails (pb-jobs/<slug>/qa/small/edit_NN.jpg)
#   sandbox.sh edit <slug> <clip_url> [--start S] [--max-dur S]
#       re-run edit after writing pb-jobs/<slug>/fixes.json (rebuilds the job first when it is missing or the options changed)
#   sandbox.sh render <slug> <clip_url> [--start S] [--max-dur S] [--sfx] --upload <presigned PUT url>
#       (rebuild if needed, apply a newer fixes.json) -> render -> QA -> PUT out/<slug>.mp4 -> comparison thumbnails
#   sandbox.sh upload <slug> <clip_url> --upload <presigned PUT url>
#       PUT the already rendered out/<slug>.mp4 again (after an expired or used upload URL)
#   sandbox.sh srcsheet <slug> <clip_url> [--start S] [--max-dur S]
#       source contact sheets for choosing pins (pb-jobs/<slug>/qa/small/src_KK.jpg)
#   sandbox.sh frames <slug> <clip_url> [--start S] [--max-dur S] --at N,N,...
#       up to 12 chosen source frames side by side (pb-jobs/<slug>/qa/small/frames.jpg)
#
# Progress lines start with "PB:"; the run ends with exactly one "PB: DONE <step> ..." or "PB: FAILED <step> <reason>".
set -uo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
PB=(python3 -I "$KIT/scripts/pb.py")
JOBS="${PB_JOBS:-/home/user/pb-jobs}"
step="${1:-}"; slug="${2:-}"; url="${3:-}"
fail() { echo "PB: FAILED ${step:-?} $*"; exit 1; }
[ $# -ge 3 ] || fail "usage: sandbox.sh prepare|edit|render|upload|srcsheet|frames <slug> <clip_url> [options]"
shift 3
INIT=(); SFX=(); UPLOAD=""; AT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --start|--max-dur)
      [ $# -ge 2 ] && [[ "$2" =~ ^[0-9]+(\.[0-9]+)?$ ]] || fail "$1 needs a number of seconds"
      INIT+=("$1" "$2"); shift 2 ;;
    --sfx) SFX=(--sfx); shift ;;
    --upload) [ $# -ge 2 ] || fail "--upload needs the presigned URL"; UPLOAD="$2"; shift 2 ;;
    --at)
      [ $# -ge 2 ] && [[ "$2" =~ ^[0-9]+(,[0-9]+)*$ ]] || fail "--at needs source frame numbers like 12,40,96"
      AT="$2"; shift 2 ;;
    *) fail "unknown option $1" ;;
  esac
done
[[ "$slug" =~ ^[a-z0-9][a-z0-9_-]{0,47}$ ]] || fail "bad slug '$slug' (a-z 0-9 _ -, starts with a letter or digit, max 48)"
[[ "$url" =~ ^https:// ]] || fail "the clip URL must start with https://"
job="$JOBS/$slug"
mkdir -p "$JOBS"
LAST="$JOBS/.$slug.last.log"
args="${INIT[*]:-}"

run() {   # run <label> <command...>: stream its output; on failure report its ERROR line
  local label="$1"; shift
  echo "PB: $label"
  "$@" 2>&1 | tee "$LAST"
  local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then
    local err; err="$(grep -E 'ERROR|Error|Traceback|failed' "$LAST" | tail -1)"
    fail "$label: ${err:-exit $rc}"
  fi
}

prepare() {
  "${PB[@]}" assets > "$LAST" 2>&1 || { cat "$LAST"; fail "assets (template media download / sha256)"; }
  echo "PB: assets ok"
  "${PB[@]}" doctor > "$JOBS/doctor.txt" 2>&1
  grep -q '^doctor: OK' "$JOBS/doctor.txt" || { grep -E '^FAIL' "$JOBS/doctor.txt"; fail "doctor: $(grep -E '^FAIL' "$JOBS/doctor.txt" | head -1)"; }
  echo "PB: doctor ok"
  if [ ! -s "$JOBS/$slug.clip" ] || [ "$(cat "$JOBS/$slug.url" 2>/dev/null)" != "$url" ]; then
    rm -f "$JOBS/$slug.clip"
    curl -fsSL --retry 3 --max-time 600 -o "$JOBS/$slug.clip.part" "$url" || fail "clip download (the URL is not reachable from the sandbox)"
    mv "$JOBS/$slug.clip.part" "$JOBS/$slug.clip"
    printf '%s' "$url" > "$JOBS/$slug.url"
    echo "PB: clip downloaded ($(du -h "$JOBS/$slug.clip" | cut -f1))"
  fi
  if [ -s "$job/fixes.json" ] && [ -f "$job/init.args" ] && [ "$(cat "$job/init.args")" != "$args" ]; then
    mv "$job/fixes.json" "$job/fixes.old.json"
    echo "PB: NOTE the clip range changed: the old fixes.json (frame pins) was moved to fixes.old.json"
  fi
  # a fixes.json written for this clip and range (e.g. re-written after a sandbox reset) is kept across the rebuild
  local stash="$JOBS/.$slug.fixes.json"
  rm -f "$stash"
  [ -s "$job/fixes.json" ] && mv "$job/fixes.json" "$stash"
  run init "${PB[@]}" init "$job" --video "$JOBS/$slug.clip" --slug "$slug" --force "${INIT[@]}"
  printf '%s' "$args" > "$job/init.args"
  if [ -s "$stash" ]; then mv "$stash" "$job/fixes.json"; echo "PB: fixes.json kept for the rebuilt job (same clip and range)"; fi
  run prep "${PB[@]}" prep "$job"
  run edit "${PB[@]}" edit "$job"
  run thumbs "${PB[@]}" thumbs "$job"
}

fresh() {   # the job exists for this clip and these options
  [ -s "$job/features.json" ] && [ -s "$job/web/plan.json" ] && [ "$(cat "$job/init.args" 2>/dev/null)" = "$args" ] \
    && [ "$(cat "$JOBS/$slug.url" 2>/dev/null)" = "$url" ]
}

put() {
  [ -s "$job/out/$slug.mp4" ] || fail "no rendered video (the sandbox was reset): run the render step with this unused upload URL"
  local code
  code=$(curl -s -o "$JOBS/.$slug.put" -w '%{http_code}' --max-time 600 -X PUT -H 'Content-Type: video/mp4' \
         -H 'If-None-Match: *' --upload-file "$job/out/$slug.mp4" "$UPLOAD")
  echo "PB: upload http $code"
  case "$code" in
    200) ;;
    403|412) fail "upload (http $code: the upload URL expired or was already used; call media_upload again and run: sandbox.sh upload)" ;;
    *) fail "upload (http $code)" ;;
  esac
}

case "$step" in
  prepare)
    prepare ;;
  edit)
    if fresh; then run edit "${PB[@]}" edit "$job"; run thumbs "${PB[@]}" thumbs "$job"; else prepare; fi ;;
  render)
    [ -n "$UPLOAD" ] || fail "render needs --upload <presigned PUT url> (call media_upload first)"
    if [ -f "$job/init.args" ] && [ "$(cat "$job/init.args")" != "$args" ]; then
      fail "the clip range changed since the last prepare: run prepare with the new range and review before rendering"
    fi
    if ! fresh; then prepare
    elif [ -s "$job/fixes.json" ] && [ "$job/fixes.json" -nt "$job/web/plan.json" ]; then run edit "${PB[@]}" edit "$job" --no-sheet
    fi
    run render "${PB[@]}" render "$job" --no-qa "${SFX[@]}"
    grep -E '^audio:' "$LAST" | sed 's/^/PB: /'
    "${PB[@]}" qa "$job" > "$job/qa/qa.txt" 2>&1; qa=$?
    cat "$job/qa/qa.txt"
    echo "PB: qa $([ $qa = 0 ] && echo pass || echo FAIL)"
    put
    "${PB[@]}" thumbs "$job" > /dev/null 2>&1 && echo "PB: comparison thumbnails in $job/qa/small (cmp_*.jpg)" \
      || echo "PB: NOTE comparison thumbnails unavailable" ;;
  upload)
    [ -n "$UPLOAD" ] || fail "upload needs --upload <presigned PUT url>"
    put ;;
  srcsheet)
    fresh || prepare
    run srcsheet "${PB[@]}" srcsheet "$job"
    grep -E 'src_[0-9]+\.jpg' "$LAST" | sed "s|^$(dirname "$JOBS")/||; s|^|PB: |" ;;
  frames)
    [ -n "$AT" ] || fail "frames needs --at N,N,... (source frame numbers)"
    fresh || prepare
    run frames "${PB[@]}" frames "$job" "$AT"
    grep -E 'frames\.jpg' "$LAST" | sed "s|^$(dirname "$JOBS")/||; s|^|PB: |" ;;
  *) fail "unknown step '$step' (prepare|edit|render|upload|srcsheet|frames)" ;;
esac
echo "PB: DONE $step $job"
