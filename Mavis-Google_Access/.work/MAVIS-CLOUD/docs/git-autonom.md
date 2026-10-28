# Git autonom — protocoale de execuție

## Cloud — fluxul complet, fără aprobări

```bash
cd /workspace/Mavis
git pull origin main          # ia ce a scris Local
# ... lucrez ...
git add -A
git commit -m "ce s-a făcut"
git push origin main          # ÎMPING DIRECT. nu cer voie.
python3 mavis-tools/log.py info "ce am făcut" --rol="cloud"
```

**De ce push imediat:** containerul e volatil. sesiunea se termină, totul se pierde.
Push-ul nu e o cerere, e **asigurarea** că datele există.

## Local — fluxul cu poarta R0

```bash
cd ~/Mavis
git pull origin main
# ... lucrez ...
git add -A
git commit -m "ce am făcut"     # commit automat, fără aprobare

git rev-list --count origin/main..HEAD
#   < 50  → continui, tac
#   >= 50 → AVERTISMENT la finalul raspunsului

git push origin main            # DOAR la comanda scrisa a lui POPY
```

## Circuit breaker

```bash
X=$(git rev-list --count origin/main..HEAD)
if [ "$X" -ge 50 ]; then
  echo "[ALERTĂ PRAG GIT]: $X commituri locale neîmpinse. Cer rezoluție R0."
fi
```

## Ce nu se face niciodată

- branch fără cerere scrisă
- push de pe Local fără porția R0
- ștergere definitivă
- `git push --force`
- amend peste commituri deja împinse
