# Handoff către Local — 2026-10-12

**De la:** Mavis Cloud

## 1. Creafac curatat

Eliminat din 10 fișiere. Zero apariții rămase în repo.
`dist/` neatins, cum s-a cerut.

## 2. IL PASSO — `URL 404`

`SITE/date/graphic-designer.json`:
- `status`: `"de verificat URL"` → `"URL 404"`
- `url`: `""` (ancora dezactivată în HTML)
- notă: link mort + dovezi la cerere

Cele 14 carduri rămân.

## 3. PR #4 respins

Nu e igienizare. E proiectul `actionlint` vărsat în repo:
binar 5 MB, tarball 2 MB, 4154 linii documentație.
**Nu atinge niciun workflow.** Adăugat în `.gitignore`.

PR #3 (teste `cv-mutator`) a fost auditat și integrat — acela a fost bun.

## Ce faci

```powershell
.\scripts\mavis-sync.ps1
python SITE\build.py graphic-designer
```

Verifică în `dist\graphic-designer.index.html` că IL PASSO n-are ancoră activă.

**Deploy: neexecutat, blocat.** Nicio publicare fără R0 de la Popy.