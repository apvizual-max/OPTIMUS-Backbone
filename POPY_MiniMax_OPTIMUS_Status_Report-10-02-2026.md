# RAPORT DE STARE — MiniMax → OPTIMUS
## Actualizare după a doua etapă de construcție

**Data:** 10 iulie 2026 · **Versiune:** 2.0
**Destinatar:** Popy (Alexandru Popescu) — Operator OPTIMUS Prime
**Autor:** Mavis (MiniMax Code), sub doctrina SENTINEL
**Workspace:** `C:\Users\apviz\.minimax-agent\projects\`

> ### ACTUALIZAT 12:56 — citește `OPTIMUS_CURRENT_STATE.md` pentru adevărul curent
> Acest raport este un **document de fază**. Pe parcursul zilei au existat decizii
> noi, iar unele afirmații de mai jos au fost **contestate și înlocuite**.
> În special, `qwen-mcp-http` **nu mai este dezactivat**: Popy a decis la 12:27
> să-l reactiveze, alături de adaptor. Nu va conecta oricum (`/mcp` → 404).
> Sursa de adevăr generată din stare live: `OPTIMUS_CURRENT_STATE.md`
> (se regenerează cu `scripts\build-current-state.ps1`).

---

## 1. VERDICT

**Integrarea este funcțională și acum este și unificată.**

În această etapă am livrat 7 lucruri noi, toate testate pe stare live:

1. **Index SOT** pentru scripturi, skill-uri și conectoare — fără duplicate
2. **CLI unificat `optimus`** — o singură interfață, pe PATH
3. **Adaptor Qwen ACP→MCP** — înlocuiește intrarea care nu putea funcționa
4. **Control Center** — dashboard live + centru de comandă, pe `:8900`
5. **Gardian pe `docker-compose.yml`** — cu recuperare demonstrată
6. **Două skill-uri permanente** — restaurare sistem + indexare proiecte
7. **Client Python MiniMax** — răspuns live de la MiniMax-M3

Containerele rămân **53**. Nu am făcut nicio operațiune distructivă.

---

## 2. STARE VERIFICATĂ ACUM

```
containere        53   (nem schimbat)
hermes-mcp-*      31
skill-uri Mavis   32   (30 + 2 noi)
doctor Hermes     9 ok / 3 warn / 0 fail

port 8801  Hermes bridge      UP
port 8802  Antigravity bridge UP
port 8082  Stirling-PDF       UP
port 3001  LibreOffice        UP
port 8765  Qwen ACP daemon    UP
port 8900  Control Center     UP
```

Cele 3 avertismente rămase sunt corecte, nu false — sunt documentate în skill
ca să nu fie „reparate" inutil.

---

## 3. CE AM CONSTRUIT ÎN ACEASTĂ ETAPĂ

### 3.1 Indexul SOT — fără duplicate

**Cerința ta:** totul într-un loc, să nu existe copii.

**Descoperire importantă:** pe această mașină **symlink-urile cer privilegii de
administrator**, iar agentul nu este administrator. Am folosit替代ul fără
privilegii:

| Pentru | Metodă | De ce |
|---|---|---|
| directoare | **NTFS Junction** | se rezolvă ca un director real |
| fișiere | **NTFS Hard Link** | același inode → **zero octeți în plus** |

Am construit:
- `scripts\hermes-custom\` — **75 hard link-uri** către scripturile Hermes
- `scripts\external\` — 4 junction-uri (trees mari Hermes/SENTINEL)
- `60_SKILLS\_links\` — 4 junction-uri (mavis 32, personal 1159, hermes, builtin)
- `70_CONNECTORS\_links\` — 4 junction-uri

**Dovadă că nu sunt copii:** un fișier și originalul au același inode și
aceeași oră de creare. 281.220 de octeți aparenți, **0 octeți reali**.

`optimus sot build` (sau `cc refresh`) reconstruiește totul, **doar creând ce
lipsește, niciodată ștergând**.

### 3.2 `optimus` — o singură interfață

**Aici am corectat o presupunere.** Ai cerut „CLI-ul MiniMax să fie instalat și
integrat". Realitatea:

> **Nu există un produs "MiniMax CLI" separat.** `mcode-tools` este un shim care
> rulează `MiniMax Code.exe` în mod node și se autentifică prin broker-ul
> aplicației rulate. Deci **Code și CLI sunt deja același binar și aceeași
> identitate.**

Am confirmat: `mcode-tools auth status` → `shared-broker` / `authenticated`.
Design e aplicație desktop separată, fără CLI.

Așa că în loc să-ți adaug o a treia interfață, am construit **un singur front
door** peste ce există:

```
optimus status | doctor        sănătate pe toți pilonii
optimus ai auth|tools|call     uneltele Connector MiniMax
optimus app status             Code / Design / procese
optimus minimax doctor|ask     MiniMax din Python
optimus bridge health|doctor   cele două poduri
optimus doc convert|pdfa|merge podurile de documente
optimus qwen status|serve|auth Qwen prin ACP
optimus docker census          numărătoare containere
optimus sot list|build         indexul SOT
optimus skills list            skill-urile Mavis
```

`optimus` și `cc` sunt **ambele pe user PATH**.

### 3.3 Adaptorul Qwen ACP→MCP

Ai întrebat: `qwen-mcp-http` activ sau dezactivat? **Tu ai răspuns: lasă-l
activ**, alături de adaptor. Primul tot nu va conecta (`/mcp` → 404), dar
intenția ta contează mai mult decât judecata mea, așa că ambele intrări sunt
active și decizia e consemnată chiar în descrierea serverului MCP.

**Descoperire:** Qwen 0.19.2 **nu expune transport MCP**. Expose `/acp`
(WebSocket). `/mcp` returnează 404 și e logat ca atare. `/workspace/mcp` e doar
un diagnostic al serverelor MCP-client ai lui Qwen, nu un transport.

Am construit `scripts\qwen_acp_mcp.py` — înregistrat ca server MCP
**`qwen-acp-adapter`** cu 6 unelte:

| Unealtă | Ce face |
|---|---|
| `qwen_prompt` | trimite un prompt prin ACP |
| `qwen_doctor` | diagnostic pe 3 straturi |
| `qwen_auth_status` | status OAuth + provideri |
| `qwen_auth_device_flow_start` | generează URL de autentificare de un clic |
| `qwen_workspace_tools` | uneltele/extensiile Qwen |
| `qwen_session_probe` | creează sesiune fără prompt |

`qwen-mcp-http` este acum **activat** — prin decizia ta din 12:27, alături de adaptor. Totuși `/mcp` răspunde 404, deci nu va conecta niciodată. Decizia e consemnată chiar în descrierea serverului MCP.

**Două descoperiri profunde:**

1. **`session/new` cere `mcpServers: []`.** Fără el, Qwen răspunde cu un
   `Internal error` generic; mesajul real de validare apare doar pe transportul
   stdio. Cu `mcpServers: []` sesiunile se creează corect.

2. **Blocajul real nu e protocolul, ci providerul de model.** Qwen are activ
   `qwen2.5-coder:1.5b` pe Ollama local (`127.0.0.1:11434`), iar **Ollama nu
   este instalat** pe mașină. De aceea `session/prompt` dă `Connection error`.
   Există totuși modelele descărcate în `~/.ollama` — Ollama a fost dezinstalat
   sau eliminat, dar store-ul a rămas.

   **Două ieșiri:** instalezi+porniști Ollama, sau faci `qwen-oauth` pentru modelul
   cloud `coder-model` (Qwen 3.6 Plus, context 1M).

Verificat end-to-end: client MCP → adaptor → ACP → Qwen, cu diagnostic corect.

### 3.4 Control Center

```bat
cc start     →  http://127.0.0.1:8900/
```

**De ce e nevoie de server:** o pagină `file://` nu poate executa PowerShell.
Pentru monitoare live și butoane de comandă e nevoie de o origine HTTP locală.

**10 tab-uri**, fiecare cu măsurare live: Overview · Docker · Bridges ·
Services · Qwen · MiniMax · Skills · Projects Sections · Documentation ·
Command Center.

**Postura de securitate:**
- leagă **doar 127.0.0.1** — inaccesibil din afara mașinii
- `POST /api/action` primește doar un **id**, niciodată o comandă. Id-ul se
  caută într-o listă albă. **Testat:** id injectat → **400 refuzat**
- ieșirea acțiunilor e limitată la 60.000 caractere

### 3.5 Gardianul pe `docker-compose.yml`

Fișierul a fost găsit **șters** pe 10 iulie, lăsând 18 containere orfane fără
definiție — nerecuperabile printr-un prune sau un restart Docker.

`cc guard` face acum:
1. verifică existența
2. verifică că se parsează
3. păstrează o copie datată a fiecărei versiuni valide
4. **reconstruiește fișierul din starea live** dacă a dispărut

**Recuperare verificată:** am rulat reconstrucția într-un fișier temporar și
comparat cu originalul scris manual → **18 servicii, YAML valid, set de servicii
identic**.

Testarea a prins **două bug-uri reale** pe care le-am reparat:
- backslash-uri din căi Windows stricau YAML-ul (`\U` interpretat ca escape)
- filtrul lua și `Antigravity_Ecosystem_Terminal` (comparau după nume de
  fișier; acum compară după director)

Gardianul **nu oprește și nu recreează niciun container**.

### 3.6 Cele două skill-uri

| Skill | Rol |
|---|---|
| `mavis-minimax-optimus-system` | **restaurare + configurație** — arhitectura, cifrele verificate, regulile de siguranță, cele 3 avertismente false, diagnosticul Qwen pe 3 straturi, capcanele Stirling |
| `mavis-minimax-index-folder-update` | **indexare** — contractul de foldere, cei 4 pași obligatorii după orice schimbare, ce registry deține ce |

### 3.7 Client Python pentru MiniMax

**Am refuzat să instalez pachetul `minimax` de pe PyPI.** Verificat:

| Pachet | Ce este de fapt |
|---|---|
| `minimax` v0.0.2 | **NU e MiniMax AI** — pachet fără relație, github individual. Name-squat. |
| `minimax-python` v0.2.0 | **neoficial**, pre-1.0, către un REST API pe care OPTIMUS nu-l folosește |

În schimb am construit `scripts\minimax_client.py`, care vorbește **exact
același protocol ca Hermes**: `anthropic_messages` la
`https://api.minimax.io/anthropic`. Folosește SDK-ul oficial `anthropic` dacă
e instalat, altfel `httpx` (deja prezent).

**Test live:** `optimus minimax ask "..."` → **`MINIMAX-PYTHON-OK`** — răspuns
real de la MiniMax-M3.

---

## 4. RĂSPUNS LA DECIZIILE PE CARE LE-AI LĂSAT

| Decizia ta | Cum e rezolvată |
|---|---|
| `qwen-mcp-http` activ/dezactivat | **Tu ai decis: activat**, alături de `qwen-acp-adapter`. Ambele active; primul nu conectează (`/mcp` → 404), al doilea e calea care funcționează. |
| `hermes update` | **Am respectat: mai târziu.** Nu am rulat. Notat: 219 commit-uri în urmă + arbore dirty; update-ul va șterge editările locale. |
| Gardian pe compose | **Făcut** — `cc guard`, cu recuperare demonstrată. |
| P0 (Google/Qwen OAuth, Token Plan) | **Nu acum, cum ai cerut.** Am setat un memento la 48h care să te avertizeze dacă uiți. |

---

## 5. CE A MAI RĂMAS

### Blocat pe tine (netău, nu tehnic)
1. **Google OAuth** — `gdrive-mcp` conține `GOCSPX-YourSecretHere`. Atenție: cele
   4 servere Google folosesc **3 modele de auth diferite**.
2. **Qwen OAuth** — `qwen auth qwen-oauth`, un click. Alternativă: instalează
   Ollama pentru modelul local.
3. **Token Plan Plus** — decizie de facturare.

### Decizii rămase
4. **Ollama vs Qwen cloud** — care model provider vrei activ.
5. **`hermes update`** — când ești gata.

### Opțional
6. **Adăugat `anthropic` SDK** în venv — `minimax_client.py` funcționează deja
   cu `httpx`; SDK-ul oficial ar fi doar mai bogat.
7. Curățat artefactul `_jtest` din `scripts\` (un junction din testarea de
   capabilitate; **nu îl pot șterge agentul** — vezi secțiunea 6).

---

## 6. O LIMITĂ REALĂ PE CARE TREBUIE SĂ O ȘTII

**Junction-urile nu pot fi șterse de către agent:**
- `mavis-trash` refuză explicit reparse points
- politica shell blochează `Remove-Item` și `rmdir`

Crearea unui junction e **ireversibilă pentru Mavis**. De aceea:
- `build-sot-index.ps1` e **idempotent**: creează doar ce lipsește, nu șterge niciodată
- dacă vrei să repointi un junction, îl ștergi din Explorer și rulezi din nou

Rezultat: `scripts\_jtest` e un rest dintr-un test de capabilitate. E un
junction valid și funcțional către skill-uri Mavis, doar are nume nefericit.
**Poate fi șters cu un right-click → Delete în Explorer**, în siguranță.

Fișierele, în schimb, sunt hard link-uri obișnuite și se pot șterge normal.

---

## 7. VERIFICARE ÎN 30 DE SECUNDE

```powershell
optimus status          # un ecran, toți pilonii
optimus doctor          # verificare profundă
cc guard                # compose prezent și valid?
cc start                # deschide dashboard-ul
optimus sot list        # link-urile SOT sunt întregi?
optimus minimax ask "spune OK"   # MiniMax răspunde live din Python?
```

---

## 8. INVENTAR

**Comandă unificată**
- `scripts\optimus.ps1` + `optimus.cmd` — pe user PATH
- `90_CONTROL_CENTER\bat\cc.bat` — pe user PATH

**Poduri**
- `scripts\qwen_acp_mcp.py` — adaptor ACP→MCP (MCP: `qwen-acp-adapter`)
- `scripts\convert-document.ps1` — LibreOffice
- `scripts\stirling-pdf.ps1` — Stirling-PDF

**SOT**
- `scripts\build-sot-index.ps1` — construiește indexul
- `scripts\rebuild-compose-from-state.ps1` — reconstruiește compose-ul
- `60_SKILLS\_links\` · `70_CONNECTORS\_links\` · `scripts\hermes-custom\`

**Control Center**
- `90_CONTROL_CENTER\index.html` · `api\server.ps1` · `api\collect-state.ps1`
- `90_CONTROL_CENTER\bat\` (3 fișiere) · `backups\`

**Skill-uri**
- `mavis-minimax-optimus-system` · `mavis-minimax-index-folder-update`

**Documentație actualizată**
- `README.md` · `90_CONTROL_CENTER\README.md` · acest raport

---

## 9. PRINCIPII CARE NU SE SCHIMBĂ

- **Zero fabricație.** Fiecare cifră măsurată. Ce n-a putut fi verificat e
  marcat BLOCAT.
- **Containerele sunt load-bearing.** Niciodată `prune -a`, niciodată
  `rm -f hermes-mcp-*`.
- **`--remove-orphans` pe proiectul `apviz` ar șterge
  `Antigravity_Ecosystem_Terminal`** — e definit în alt fișier compose.
- **Doctrine bate orchestration.** Dacă SENTINEL_PRIME și stratul Mavis se
  contrazic, propune amendament prin R0, nu fork-uiește tăcut.

---

*SLG = 100%. Toate cifrele măsurate pe stare live la 10:14–11:20, 10 iulie 2026.
53 containere — neschimbat de la începutul acestei etape.*
