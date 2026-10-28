# Registrul extern

Tot ce a fost luat de pe surse externe și integrat. **Nu se șterge din registru** —
se mută la `SCOS` cu data și motivul.

Format: `componentă | sursă | versiune |instalat | scop | stare`

## ACTIV

| Componentă | Sursă | Versiune | Instalat | Scop | Stare |
|---|---|---|---|---|---|
| 14 skill-uri Emil | `github.com/emilkowalski/skills` | HEAD 2026-10-10 | 2026-10-10 | animație, design, review UI, mobile | ACTIV |
| ↳ `apple-design` | ↳ | HEAD | 2026-10-10 | interacțiuni, motion, material translucid | ACTIV |
| ↳ `break-ui` | ↳ | HEAD | 2026-10-10 | testare cu date rele — găsește ce se strică | ACTIV |
| ↳ `mobile-native` | ↳ | HEAD | 2026-10-10 | site-ul care „se simte instalat" pe telefon | ACTIV |
| ↳ `emil-design-eng` | ↳ | HEAD | 2026-10-10 | filozofia de polish, detalii invizibile | ACTIV |
| ↳ `improve-animations` | ↳ | HEAD | 2026-10-10 | audit + plan de animații, nu implementează | ACTIV |
| ↳ `animate` · `animate-expo` | ↳ | HEAD | 2026-10-10 | scrie implementarea animațiilor | ACTIV |
| ↳ `review-animations` | ↳ | HEAD | 2026-10-10 | critici motion, default e „flag" | ACTIV |
| ↳ `find-animation-opportunities` | ↳ | HEAD | 2026-10-10 | propune motion, refuză ce nu merită | ACTIV |
| ↳ `animation-vocabulary` | ↳ | HEAD | 2026-10-10 | denumire exactă pentru efecte | ACTIV |
| ↳ `ask-sonner` · `pick-ui-library` · `prototype` · `write-swift` | ↳ | HEAD | 2026-10-10 | utilitare; nefolosite încă | JAM FOLOSIT |
| `google-workspace-mcp` | `npm` | 2.3.6 | 2026-10-09 | client Google API pentru Drive/Gmail | ACTIV |
| repo `mavis-google` | `github.com/taylorwilsdon/google_workspace_mcp` | 2e9e9e7 | 2026-10-09 | **dependință, nu sursă** — nu se scrie în el | ACTIV |
| `gh` CLI | `github.com/cli/cli` | 2.63.2 | 2026-10-10 | operațiuni GitHub | ACTIV |
| Playwright + Chromium | `pypi` | latest | 2026-10-10 | randare și verificare vizuală automată | ACTIV |

## SCOS

| Componentă | Sursă | Versiune | Scos | Motiv | Înlocuit cu |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

## ÎN AȘTEPTARE

| Componentă | Sursă | Status | Ce ne trebuie |
|---|---|---|---|
| „Mavis Apple Design" | link menționat de POPY | **neprimit** | repo-ul sau skill-ul, ca să-l înregistrăm aici |

---

## Reguli

1. **Nicio componentă nu intră în sistem fără să fie aici.** Nu intră înregistrată, nu e considerată făcută.
2. **La extragerea unui link** (video, repo, articol): identifică sursa, implementează ce e util, înregistrează **înainte** de a spune „gata".
3. **SCOS nu înseamnă șters.** Se mută, cu motiv. Ca să nu-l reinstalezi peste șase luni crezând că e nou.
4. Se aplică și la **GitLab**, și la orice cod custom din altă parte.