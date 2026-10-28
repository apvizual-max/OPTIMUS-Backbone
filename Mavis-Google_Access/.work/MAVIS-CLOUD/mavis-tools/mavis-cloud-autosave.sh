#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# mavis-cloud-autosave.sh
#
# REGULA GENERALĂ A PROIECTULUI:
#   Tot ce fac ajunge în repo. AUTOMAT. Fără aprobări, fără întrebări.
#
# Pornește o buclă care:
#   1. ia ce a scris agentul local
#   2. rulează R0 (verificări) pe ce scrie Cloud
#   3. comitează
#   4. împinge pe main
#
# POPY nu are nevoie să știe git. Pornește scriptul o dată.
# ---------------------------------------------------------------------------
set -uo pipefail

REPO="${MAVIS_REPO:-/workspace/Mavis}"
GH="$REPO/mavis-tools/bin/gh"
export GIT_TERMINAL_PROMPT=0
export PATH="$REPO/mavis-tools/bin:$PATH"

INTERVAL="${MAVIS_SYNC_INTERVAL:-300}"   # 5 minute
[ -d "$REPO" ] || { echo "repo inexistent: $REPO"; exit 1; }
cd "$REPO"

echo "╔══════════════════════════════════════════════════════╗"
echo "║  Mavis Cloud — salvare automată în repo            ║"
echo "║  Repo:  $REPO"
echo "║  Ritm:  ${INTERVAL}s"
echo "║  Ctrl+C pentru oprire                                ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ── R0: verificări înainte de push ────────────────────────────────────────
r0() {
  local erori=0
  for f in $(find . -name "*.js" -not -path "*/node_modules/*" -not -path "*/vendor/*"); do
    node --check "$f" >/dev/null 2>&1 || { echo "  R0 FAIL: sintaxă JS în $f"; erori=1; }
  done
  python3 - <<'PY' >/dev/null 2>&1 || return 1
import ast, io, glob
for f in glob.glob('SITE/*.py') + glob.glob('mavis-tools/*.py'):
    ast.parse(io.open(f, encoding='utf-8').read())
PY
  [ $? -ne 0 ] && { echo "  R0 FAIL: sintaxă Python"; erori=1; }

  python3 SITE/build-hub.py >/dev/null 2>&1 || { echo "  R0 FAIL: build site"; erori=1; }

  if git diff --cached --name-only 2>/dev/null | grep -qiE "secret|token|credential|\.env"; then
    echo "  R0 STOP: fișier de secret în commit"; return 1
  fi
  return $erori
}

# ── scrie în log ───────────────────────────────────────────────────────────
note() { python3 mavis-tools/log.py "$1" "$2" --rol="autosave" >/dev/null 2>&1 || true; }

# pragul 50 - PROTOCOL C2. Aplica pentru instanta LOCAL.
# Pentru CLOUD nu se aplica: containerul e volatil, datele trebuie impinse imediat.
PRAG="${MAVIS_PRAG:-50}"
ROLE="${MAVIS_ROLE:-CLOUD}"

prag_check() {
  [ "$ROLE" = "LOCAL" ] || return 0
  local x; x=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo 0)
  if [ "$x" -ge "$PRAG" ]; then
    echo "" >> "$REPO/.prag-alert"
    echo "[ALERTĂ PRAG GIT]: $x commituri locale neîmpinse (prag >= $PRAG)." >> "$REPO/.prag-alert"
    echo "  Solicit rezoluție R0: push pe remote sau continuăm acumularea locală?"
  fi
}

while true; do
  # 1. ia ce a venit de la Local
  if git pull --rebase origin main >/dev/null 2>&1; then
    [ -n "$(git log --oneline @{u}.. 2>/dev/null)" ] && note info "Cloud: primit commituri noi de la Local"
  else
    note eroare "git pull a picat - posibil conflict cu Local"
    echo "  pull picat, verific manual"
    sleep "$INTERVAL"; continue
  fi

  # 2. vezi dacă e ceva de salvat
  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    if git diff --cached --quiet; then
      : # nimic real
    else
      # 3. R0 înainte de commit+push
      if r0; then
        N=$(git diff --cached --name-only | wc -l)
        git commit -q -m "autosave: $N fișiere actualizate de Cloud"
        if git push origin main >/dev/null 2>&1; then
          note info "Cloud: $N fișiere salvate și împinse"
          echo "  $(date '+%H:%M:%S')  salvat și împins: $N fișiere"
        else
          note eroare "push a picat după commit"
          echo "  $(date '+%H:%M:%S')  push picat"
        fi
      else
        git reset -q
        note eroare "R0 a picat - commit oprit, fișierele rămân necomitate"
        echo "  $(date '+%H:%M:%S')  R0 a picat, nimic salvat"
      fi
    fi
  fi
  # circuit breaker
  [ -f "$REPO/.prag-alert" ] && { echo ""; cat "$REPO/.prag-alert"; echo ""; }
  prag_check

  sleep "$INTERVAL"
done