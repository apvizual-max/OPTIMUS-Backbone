#!/usr/bin/env bash
# MAVIS CLOUD — bootstrap pentru o sesiune nouă.
#
#   bash mavis-tools/bootstrap.sh
#
# De ce există (2026-10-22): o sesiune nouă pornește cu HOME gol, fără config
# git. Primul `git clone` pică cu:
#   "server certificate verification failed. CAfile: none"
# pentru că sandboxul are un proxy pe care git nu-l onorează (curl îl onorează).
# Fixul e o singură linie de config — dar trebuie să știe cineva de ea.
#
# Scriptul face, în ordine:
#   1. config git (dacă lipsește)
#   2. clone sau pull MAVIS-CLOUD
#   3. verdict pe starea Google (un singur rând)
#   4. verdict pe drift repo ↔ secret manager
#
# READ-ONLY, cu excepția lui git pull. Nu șterge nimic.

set -u
REPO_URL="https://github.com/apvizual-max/MAVIS-CLOUD.git"
BRANCH="main"
DIR="${MAVIS_CLOUD_DIR:-$HOME/mavis-cloud}"
C="\033[32m"; Y="\033[33m"; R="\033[31m"; D="\033[2m"; B="\033[1m"; N="\033[0m"

echo "${B}=== MAVIS CLOUD — bootstrap ===${N}"

# --- 1. config git (proxy) ---
if ! git config --global http.sslVerify 2>/dev/null | grep -q false; then
  git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt 2>/dev/null
  git config --global http.sslVerify false
  echo "  ${D}git config: sslVerify=false setat (proxy de sandbox)${N}"
else
  echo "  ${D}git config: deja configurat${N}"
fi
git config --global user.name "Mavis Cloud" >/dev/null 2>&1
git config --global user.email "mavis-cloud@apvizual-max.local" >/dev/null 2>&1

# --- 2. repo ---
if [ -d "$DIR/.git" ]; then
  echo "  ${D}repo: pull in $DIR${N}"
  ( cd "$DIR" && git pull --ff-only origin "$BRANCH" 2>&1 | tail -2 )
else
  echo "  ${D}repo: clone in $DIR${N}"
  git clone --depth 1 "$REPO_URL" "$DIR" 2>&1 | tail -2
fi

if [ ! -d "$DIR/.git" ]; then
  echo "${R}  Repo-ul nu s-a clonat. Verifică rețeaua / tokenul GITHUB_TOKEN.${N}"
  exit 1
fi

cd "$DIR"
echo "  ${C}repo OK${N} ${D}$DIR @ $(git rev-parse --short HEAD)${N}"

# --- 3 + 4. verdict pe Google ---
export HOME="${HOME}"
node mavis-tools/google-preflight.js 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' | grep -E '^[[:space:]]*\[[0-4]\]' || echo "  (preflight nu a raspuns - poate reteaua)"

echo ""
echo "${D}  Google: node mavis-tools/google-preflight.js   (verdict detaliat)"
echo "  Drive : node mavis-tools/drive-vault.js root"
echo "  Gmail : node mavis-tools/google-verify.js"
echo "  Repo  : git log --oneline -3${N}"
echo ""
