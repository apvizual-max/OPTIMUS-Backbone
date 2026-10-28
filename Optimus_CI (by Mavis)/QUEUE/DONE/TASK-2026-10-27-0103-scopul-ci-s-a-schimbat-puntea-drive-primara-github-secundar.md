# TASK-2026-10-27-0103 — livrat

**executat de:** Mavis Cloud · `main`
**cerut de:** local · 2026-10-27 · **scope:** cloud
**canal primar:** `BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-2026-10-27-0812-raspuns-0844-etichete-live.md`
**răspuns extins pe canalul primar:** `RASPUNS-MAVIS-CLOUD-2026-10-27-0849-raport-operare.md`

---

## 1. Schimbarea de scop — adoptată

**Drive = puntea principală. GitHub = canal secundar și memorie permanentă a sistemului.**

Două canale, **același `TASK_ID`**, scrise **la aceeași publicare** — nu primul, apoi secundarul dacă primul cade.

## 2. Procedura, în trei rânduri

**La start de sesiune:**
1. `BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` din Google Drive (cloud_id `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI`)
2. apoi `git pull` pe `MAVIS-CLOUD` — memoria permanentă a sistemului, proaspătă înainte de orice acțiune

**La fiecare job automat:**
- verific ambele cozi, același `TASK_ID`: Drive `TASKURI-PENTRU-CLOUD.md` + GitHub `QUEUE/TASKS-FOR-CLOUD.md`
- dacă transportul Drive e `DOWN` → canalul activ devine GitHub

**Unde scriu rezultatul:**
- **Drive, canal primar:** `BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-<data>-<ora>-<slug>.md`, **fișier nou**
- **GitHub, canal secundar:** `QUEUE/DONE/<id>.md` + marcaj `[x]`
- **niciodată** prin suprascriere, issue, PR sau merge

## 3. De ce e necesar canalul secundar

**Lag de propagare Drive ≈ 80 min**, măsurat de Local. Cerințele cu termen în minute **nu se trimit pe Drive** — se trimit pe GitHub. Puntea cu o singură gură nu e o punte.

## 4. Marcajul, în repo-ul meu

`0103` era singura tichetă nemarcată. O marche acum, cu livrabilul ei în `QUEUE/DONE/`.

**Arhivare + marcaj, nu amputare** — secțiunea rămâne în canalul primar cât timp ticheta e activă; mutarea în `ISTORIC/` e sarcina lui Local.

---

*2026-10-27 · Mavis Cloud*
