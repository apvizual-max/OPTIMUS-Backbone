# 🚨 REGULI DE PLATFORMĂ — nu te mai știi fără ele

**De ce există:** POPY a descoperit singur o confuzie care m-a costat timp. Nu o mai repetăm.
**Data:** 2026-10-12 05:00

---

## 1. CRONURILE — Cloud și Local sunt locuri DIFERITE

### Regula, pe scurt

> **Când vorbim de programe programate (cron), uită-te pe platforma ONLINE.**

### De ce

| | Cronuri Cloud | Cronuri Local |
|---|---|---|
| Unde rulează | container stateless, online 24/7 | calculatorul tău |
| Unde le vezi | **platforma online** | interfața Local |
| Le vezi din Local? | **NU.** vezi doar cronurile locale | da |
| Le vezi din Cloud? | da | **NU** |

**Ce înseamnă asta, concret:**

Când deschizi ecranul **Schedules** din Local și nu găsești ce am programat eu, **nu e o eroare.** Programarea e în cloud. Trebuie să o cauți **online**.

**Aceeași regulă în sens invers:** dacă Local programează ceva și eu nu îl găsesc în cloud, e tot corect — e cron local.

### Trapul, spus direct

> Am programat „Raport zilnic" **în cloud**. Ai căutat în interfața Local. Nu ai găsit.
> **Concluzia ta corectă a fost „nu există". Concluzia greșită ar fi fost „nu e programat".**
> **Corect: e programat, dar în altă parte.**

### Regula pentru mine

**Când POPY întreabă „ai programat ceva?", răspund ÎNTOTDII cu:** *pe ce platformă e?*

- „e programat" → e în cloud, se vede online
- „nu e programat" → n-a fost făcut deloc

**Nu amestec niciodată cele două.**

---

## 2. NOTEBOOKLM — browser, nu API

### Regula, pe scurt

> **NotebookLM se creează într-un browser. Browserul e la Local.**
> **Cloud pregătește conținutul. Local pune fișierele înăuntru.**

### De ce — verificat, nu ghicit

NotebookLM are două niveluri:

| | Personal | Enterprise |
|---|---|---|
| Adresa | `notebooklm.google.com` | `notebook.cloud.google.com` |
| **API oficial** | **NU are** | **DA** |
| Autentificare | cont + **cookie-uri de browser** | token Google Cloud |
| Cost | gratuit | **licențe plătite** + IdP + proiect Cloud |

**API-ul oficial există DOAR pe Enterprise**, care cere proiect Cloud cu facturare activă, licențe plătite, configurarea unui furnizor de identitate și roluri IAM.

**Pentru un designer independent, asta e un efort disproporționat.**

Calea reală, fără Enterprise: CLI-ul `nlm`, care se autentifică prin **sesiune de browser reală**.

### Ce știu sigur

**Nu am creat niciun notebook. Nu am acces la NotebookLM în cloud.**
Conectorii mei în cloud sunt, verificat acum: **github, matrix, cloudflare, figma.** Atât.

### Ce NU mai fac

**Nu mai întreb care cont e notebook-ul. Nu mai caut notebook în Drive.**
Am întrebat de două ori. De două ori am presupus că e o problemă de acces. **Nu e.** E o limită de platformă.

### Împărțirea, pentru totdeauna

```
CLOUD (eu)    pregătesc  câte un document per folder, gata de încărcat,
                          numit MavisCloud-(subiect), conținut complet.
                          Comit în repo.

LOCAL (el)   deschide    notebooklm.google.com
             creează     notebook-ul cu numele corect
             încarcă     documentele din repo
             îmi dă      ID-ul notebook-ului
```

**Cloud nu creează notebookuri. Local nu scrie conținut. Nimeni nu întreabă pe cine.**

---

## 3. DEPLOY — nu e control de versiuni

Instrumentul de deploy din cloud **creează un nod nou** la fiecare rulare. Nu actualizează site-ul existent.

**Deci:** site-ul îl construiește Local. Cloud nu mai face deploy-uri.

Singurul deploy existent: `https://4nsxl2or95u1a.space.minimax.io`. **Nu se creează altul** fără cerere explicită.

---

## 4. NUME DE VARIABĂ — nu inventa identificatori

Am scris `LINKEDIN_EMAIL` în trei fișiere. **Nu există un asemenea identificator.**

Corect, reparat acum:

| Greșit | Corect | Ce e |
|---|---|---|
| `LINKEDIN_EMAIL` | `GOOGLE_EMAIL` | `apvizual@gmail.com` |
| — | `LINKEDIN_PASSWORD` | parola, pentru Local cu browser |

**Regula:** nu inventez nume de chei ca să sune bine. Verific ce există efectiv.

---

## 5. SECRET MANAGEMENT — cum se lucrează

**Da, poți adăuga aici credențiale pentru pagini și servicii.**

Secret manager-ul e un sertar cu chei. **O cheie, un singur scop, deschisă doar când trebuie.**

- Nu citesc totul deodată
- Nu scriu parole în fișiere
- Nu pun chei în repo
- Nu trimit chei prin Jules sau GitHub

Vezi `docs/CREDENTIALE.md` pentru lista exactă.

---

## REGULI DE NU UITA

1. **Cron → platforma online.** Cloud și Local sunt locuri diferite.
2. **NotebookLM → browser.** Cloud scrie conținutul, Local pune fișierele.
3. **Deploy → Local.** Cloud nu mai face deploy-uri.
4. **Nume de variabile → verifică,** nu inventa.
5. **Secrete → sertar,** nu chat, nu repo.

---

*Creat: 2026-10-12 05:00 · Mavis Cloud · pentru Mavis Local și pentru orice agent nou*
*Aceasta se citește la pornire, alături de AGENTS.md*