---
name: Review de schimbare
about: Folosit la orice pull request din repo-ul Mavis
labels: review
---

## Ce se schimbă

<!-- un rând, în română -->

## De ce

<!-- ce nu merge fără asta -->

## Ce am verificat

- [ ] Comandat și văzut rezultatul, nu presupus
- [ ] Fiecare număr din `PROGRES.md` a fost numărat, nu estimat
- [ ] Niciun secret în diff (`git diff --cached --name-only | grep -iE "secret|token|credential"`)
- [ ] `PLAN.md` și `PROGRES.md` actualizate în același commit

## Ce NU am verificat

<!-- spune explicit, nu taci -->
