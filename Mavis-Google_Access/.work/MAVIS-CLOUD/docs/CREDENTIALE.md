# CREDENTIALE — ce poți adăuga aici și ce NU poți

**Data:** 2026-10-12 05:00 · **Mavis Cloud**

## Răspuns scurt la întrebarea ta

> „Pot adăuga aici credențiale pentru pagini și lucruri pe care să-mi dai acces mai târziu?"

**Da. Exact asta e secret manager-ul.**

Nu trebuie să-mi dai nimic altceva. Nu trebuie să-mi dai parole deLinkedIn în chat, nu trebuie să-mi trimiți fișiere cu secrete, nu trebuie să scrii nimic în repo.

**Secret manager-ul e un sertar cu chei. Fiecare cheie e o poartă separată, cu un singur scop, pe care o deschid doar când am nevoie de ea.**

---

## CE SĂ ADĂUGI — lista exactă

### 1. NotebookLM — ce funcționează chiar acum

Am verificat **cum se face de fapt**, nu am ghicit.

NotebookLM are **două niveluri, complet diferite:**

| | Personal | Enterprise |
|---|---|---|
| Adresă | `notebooklm.google.com` | `notebook.cloud.google.com` |
| **API oficială** | **NU are** | **DA** |
| Autentificare | cont Google + **cookie-uri de browser** | token Google Cloud |
| Cost | gratuit | **licențe plătite + IdP + proiect Cloud** |
| Cine poate intra | orice browser | doar utilizatori cu rol |

**Concluzia, directă:** API-ul oficial există **doar pe Enterprise**, care cere proiect Cloud cu facturare, licențe plătite, configurare IdP și roluri. **Pentru tine, un designer independent, ăsta e un efort disproporționat.**

**Ce funcționează fără Enterprise:** un CLI numit `nlm` care se autentifică prin **sesiune de browser**. Și asta e exact unde stă problema — **browserul e la Local, nu la Cloud.**

**Asta e răspunsul real la întrebarea „unde greșesc":** eu, în Cloud, **nu pot crea notebook-uri.** Nu pentru că n-am încercat — pentru că **nu există drum prin API fără Enterprise.** Și un notebook se creează într-un browser.

**Împărțirea corectă, pentru totdeauna:**

```
CLOUD (eu)  → pregătesc conținutul: câte un document per folder,
               gata de încărcat, cu numele corect, în repo
LOCAL (el)  → deschide notebooklm.google.com, creează notebook-ul,
               încarcă documentele, îmi dă înapoi ID-ul
```

**Ce NU mai trebuie să faci:** să îmi spui care cont e. **Am întrebat de două ori și tu ai răspuns corect de două ori — notebook-urile sunt ale tale, nu ale mele.**

### 2. Ce adaugi efectiv aici

| Cheie | Ce e | De ce | Prioritate |
|---|---|---|---|
| `GOOGLE_EMAIL` | `apvizual@gmail.com` | un singur email, pentru tot ce e Google | **gata** |
| `LINKEDIN_PASSWORD` | parola LinkedIn | pentru Local, să citească profilul tău | dacă vrei |
| `JULES_API_KEY` | cheia Jules | workflow-ul GitHub o citește din secrets | **gata, pus** |
| `GITHUB_TOKEN` | token GitHub | commit + push din cloud | **gata** |

**Corectare importantă:** `LINKEDIN_EMAIL` **nu există.** L-am inventat eu, în 3 fișiere, și l-am reparat acum → `GOOGLE_EMAIL`.

**Nu există „email de LinkedIn".** Te loghezi pe LinkedIn cu **adresa ta de Gmail.** Deci cheia e `LINKEDIN_PASSWORD`, nu `LINKEDIN_EMAIL`.

---

## CE NU MERGE, și de ce — ca să nu pierdem timp

| Ce ai vrut | De ce nu merge în Cloud | Ce merge |
|---|---|---|
| NotebookLM prin API | API-ul oficial e **doar Enterprise**, cu licențe plătite | Local, prin browser |
| LinkedIn scraping | LinkedIn blochează automatările și cere captcha | Local, cu browser deschis |
| Sesiune Google personală | token-ul meu OAuth e scoped la Workspace, nu la contul tău personal | Local, cu browser |
| Deploy-ul site-ului | instrumentul meu creează **un nod nou** la fiecare deploy, nu actualizează | Local, cu build-ul tău |

**Legea:** tot ce cere **sesiune de browser** sau **un server cu licență** e Local. Tot ce e **API + fișiere** e Cloud.

---

## REGULA DE NU CITI NICIODATĂ

**O singură cheie, un singur scop, folosită doar când e nevoie.**

- Nu citesc totul deodată
- Nu scriu niciodată o parolă într-un fișier
- Nu pun niciodată o cheie în repo
- Nu trimit niciodată o cheie prin Jules sau GitHub

**Verificat azi:** un `credentials.json` cu `client_secret` Google real era în zona de atașamente.
- **NU a fost niciodată** în istoricul git
- **NU e** în arborele repo-ului
- l-am adăugat în `.gitignore` împreună cu `client_secret*.json`

---

## CE FAC EU CHIAR ACUM, FĂRĂ SĂ MAI ÎNTRAB

Nu am nevoie de **nicio** cheie nouă ca să fac primul pas.

**Fac asta:** pentru fiecare folder din repo, pregătesc **un document, gata de încărcat**, cu numele `MavisCloud-(subiect)` și conținutul lui. Îl comit.

**Tu sau Local:** deschideți NotebookLM, creezi notebook-ul, tragi documentele din repo.

**Asta e tot. Fără întrebări.**

---

*2026-10-12 05:00 · Mavis Cloud*