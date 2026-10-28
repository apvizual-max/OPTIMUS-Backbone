# 05 · Rotește cheia API Google expusă

**Data:** 2026-10-22 · **Tip:** configurări + acces
**Perspectivă lipsă:** niciuna — dar **consola cere sesiunea ta cu 2FA**
**Stare:** ⏳ așteaptă pe tine

---

## Ce s-a întâmplat (măsurat, nu estimat)

Repo-ul `hermes-agent-temp` era **public din august**. În istoricul lui (nu în HEAD)
se află o cheie API Google **verificată vie**:

```
AIzaSyAyimku…(restul in secret manager: GOOGLE_API_KEY_EXPOSED_HERMES_TEMP)
```

**Cum am verificat că e vie** (metoda e calibrată, nu ghicită):
- cheia asta → `GET https://www.googleapis.com/discovery/v1/apis?key=…` → **HTTP 403**
  = Google o recunoaște, dar API-ul e restricționat pentru ea
- placeholder-ul `AIzaSyB-abc123def456ghi789jklmno012345` din același repo →
  **HTTP 400 „API key not valid"** = mort

Deci 403 = **vie**.

## Ce am făcut deja

| Acțiune | Stare |
|---|---|
| Repo-ul `hermes-agent-temp` → **privat** | ✅ făcut (oprește expunerea nouă) |
| Refresh token Google din `hermes-local-backup` | ✅ **revocat** (era viu) |
| Refresh token din `hermes-agent-temp` | era deja mort — fără acțiune |
| Cheia API de mai sus | ⏳ **nevoie de tine** |

**Ce a rămas:** cine a clonat repo-ul în trecut are cheia. Rotirea e obligatorie —
containment-ul nu o anulează.

## Ce ai de făcut

**Google Cloud Console → APIs & Services → Credentials** → găsești cheia
`AIzaSyAy…` → **Delete** sau **regenerează**.

- **Delete** e varianta mai curată: cheia n-a fost folosită în producție.
- Dacă e folosită de ceva (Maps, un site, un script), **regenerează** și
  actualizează referința.

## De ce nu pot face eu

Consola Cloud cere **sesiunea ta** pe `apvizual@gmail.com`, cu verificare în doi
pași. Am un OAuth *client*, nu sunt administrator de proiect. Nu pot ajunge la
pagina de administrare a proiectului.

## Cum verificăm că s-a rezolvat

```bash
# dupa rotire, cheia VECHE trebuie sa dea "API key not valid" (HTTP 400)
# cheia completa e in secret manager: GOOGLE_API_KEY_EXPOSED_HERMES_TEMP
KEY=$(cat ~/.secrets/GOOGLE_API_KEY_EXPOSED_HERMES_TEMP 2>/dev/null)   # sau din panoul de secrete
curl -s -o /dev/null -w "%{http_code}\n" "https://www.googleapis.com/discovery/v1/apis?key=$KEY"
# asteptat: 400  (403 = inca vie, 200 = activata fara restrictii)
```

**Unde o iei:** Mavis Cloud → Environmental Information → Secrets →
`GOOGLE_API_KEY_EXPOSED_HERMES_TEMP`. **De ce e acolo, nu în acest doc:** un
repo public nu conține valori de secrete — nici revocate, nici de rotit. GitHub
secret-scanning blochează push-ul și e corect că o face.

După aceea, cheia nouă (dacă ai făcut regenerate) o pui în secret manager, **nu**
în repo.

## Bonus — ce am învățat azi

**`git clone --depth 1` ascunde exact ce cauți.** Auditul meu inițial pe
`pkms-vault-automation` a fost pe un clone shallow — și tot pe acolo, 177 de
commituri și 27 de ramuri n-au fost scanate. Abia `git fetch --unshallow` +
`git fetch origin "+refs/heads/*:refs/remotes/origin/*"` a acoperit tot.
**Procedura de audit e acum în `docs/AUDIT-VIZIBILITATE-REPO-URI.md`.**

---

*2026-10-22 · Mavis Cloud · singurul lucru rămas din tot ce am făcut azi*
