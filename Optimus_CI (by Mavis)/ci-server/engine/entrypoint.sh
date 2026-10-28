#!/bin/sh
# entrypoint.sh - Mavis-Optimus-CI
#
# Instaleaza hook-urile PORTEI in gitdir-urile montate, apoi ridica motorul.
#
# DE CE INSTALEAZA IN CONTAINER: hook-urile trebuie sa fie ACELEASI in host si
# in container, si sa fie versionate in repo. Gitdir-ul e consumabil (dupa un
# an poate lipsi); sursa canonica sta in ci-server/hooks/. Containerul o
# replica inainte de a porni - asa nu exista doua implementari care sa drift-
# eze, si daca sursa se schimba, instalarea o prinde imediat.
#
# Instalarea e IDEMPOTENTA: se scrie doar daca continutul difera.

set -e

GITDATA="${CI_GITDATA_DIR:-/workspace/gitdata}"
HOOKS_SRC="/opt/optimus-ci/hooks"

install_hook() {
  # $1 = gitdir, $2 = numele hook-ului
  src="$HOOKS_SRC/$2"
  dst="$1/hooks/$2"
  [ -f "$src" ] || { echo "CI-ENGINE: sursa lipsa: $src"; return 0; }
  mkdir -p "$1/hooks"
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    echo "CI-ENGINE: hook deja actual: $dst"
    return 0
  fi
  cp "$src" "$dst"
  chmod 0755 "$dst"
  echo "CI-ENGINE: hook instalat: $dst"
}

for gd in "$GITDATA/repo" "$GITDATA/clone-MAVIS-CLOUD" "$GITDATA/clone-MAVIS-OPTIMUS-CI"; do
  if [ -d "$gd" ]; then
    install_hook "$gd" pre-commit
    install_hook "$gd" pre-push
  else
    echo "CI-ENGINE: gitdir inexistent (sarit): $gd"
  fi
done

echo "CI-ENGINE: monturi -"
echo "CI-ENGINE:   proiect  = $CI_PROJECT_DIR"
echo "CI-ENGINE:   gitdata  = $GITDATA"
echo "CI-ENGINE:   poarta   = $MAVIS_PUSH_GATE"

exec "$@"
