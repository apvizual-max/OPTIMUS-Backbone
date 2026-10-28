#!/usr/bin/env bash
# Setup pentru Jules - MAVIS-CLOUD
# REPARAT: Jules ruleaza ca utilizator normal, NU ca root.
# De aceea apt-get si pip au nevoie de sudo explicit.
set -uo pipefail

echo "1/6  cine sunt: $(whoami)"
cd /app 2>/dev/null || { echo "nu pot intra in /app"; exit 1; }

echo "2/6  instalez dependintele..."
# TOATE comenzile de sistem au sudo. Fara, primesc 'Permission denied'
# pe /var/lib/apt/lists/lock - exact eroarea pe care ai vazut-o.
if ! sudo -n true 2>/dev/null; then
  echo "     sudo fara parola NU merge. Ramane fara instalare de sisteme."
else
  sudo apt-get update -qq 2>&1 | tail -2
  sudo apt-get install -y -qq git ripgrep 2>&1 | tail -2
fi

echo "3/6  verific node si python..."
command -v node  && node --version  || echo "     node LIPSA - deja instalat in imagine"
command -v npm   && npm --version   || echo "     npm LIPSA"
command -v python3 && python3 --version || echo "     python3 LIPSA - deja instalat"

echo "4/6  dependinte npm locale, fara sudo..."
npm install --silent --no-audit --no-fund 2>&1 | tail -3 || echo "     fara package.json, se sare"

echo "5/6  dependinte python, cu --user..."
pip3 install --quiet --user requests 2>&1 | tail -2 || echo "     requests deja e acolo"

echo "6/6  verific ca proiectul e complet..."
echo "     commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'fara git')"
echo "     fisiere: $(find . -maxdepth 1 -type f | wc -l) in radacina"
echo "     docs/: $(ls docs/*.md 2>/dev/null | wc -l) documente"
echo "     site/: $(ls SITE/dist/*.html 2>/dev/null | wc -l) pagini"

echo ""
echo "Mediu pregatit."
