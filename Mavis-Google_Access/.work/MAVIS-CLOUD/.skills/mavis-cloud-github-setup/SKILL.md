---
name: mavis-cloud-github-setup
description: Cum este configurat GitHub pentru MAVIS-CLOUD - workflow, Live Review, LiveCopilot. Live Review ruleaza DOAR dupa push spre GitHub.
---

# GitHub · MAVIS-CLOUD

Repo: **apvizual-max/MAVIS-CLOUD** · ramura `main` · cont `apvizual-max`

## Ce rulează automat

| Ce | Când | Unde |
|---|---|---|
| `Verificare` (5 verificări) | la fiecare push pe main | `.github/workflows/verify.yml` |
| **Live Review** | **după push spre GitHub** | hexmos.com, plan free |

## Live Review — regula exactă

> **Live Review privește PUSH-urile către GitHub. Nu privește fișierele mele
> locale. Nu privește commit-urile mele. Rulează după ce apare pe GitHub.**

Deci ordinea e fixă:

```
eu lucrez local → commit pe main → PUSH pe GitHub → Live Review vede push-ul
```

**Nu rulează niciodată înainte de push.** Dacă nu am împins, nu a văzut nimic.

### Prima rulare

Live Review n-a rulat încă pentru că **nu a existat pull request**. E normal.

```bash
git checkout -b verificare-lr      # doar dacă POPY cere ramură
# o schimbare mică, reală
git commit -m "..."
git push -u origin verificare-lr
gh pr create --base main --head verificare-lr \
  --title "Verificare Live Review" --body "Test de flux."
```

### LiveCopilot

Pe contul `apvizual-max` (free) nu e disponibil prin API. POPY l-a activat din
interfața web. **Nu încerc să-l activez eu prin API — răspunde `Not Found`.**

## Workflow-ul de verificare

Cinci verificări, la fiecare push:

1. niciun secret în commit
2. toate JSON-urile valide
3. sintaxa JavaScript intactă
4. site-ul se construiește
5. șabloanele CV nu conțin nume de firmă

**Toate au trecut.** Prima rulare a fost `failure` — workflow-ul a prins o
sintaxă stricată în `email-sort.js` pe care eu o ratasem. **Asta e R0.**

## Cheile

| Cheie | Unde stă |
|---|---|
| `GITHUB_TOKEN` | manager de secrete, **nu** în repo |
| `JULES_API_KEY` | manager de secrete, **nu** în repo |

## Repositories

Nu ating alt repository. `mavis-google` e clone al lui
`taylorwilsdon/google_workspace_mcp` — **dependință, nu sursă.** Nu se scrie în el.