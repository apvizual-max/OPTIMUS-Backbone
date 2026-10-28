# CANAL DE COMUNICARE — Mavis Cloud ↔ Mavis Local

> Folder: `05-Comunicare/` din `Mavis-Cloud-Google-Access-Bot`.
> **Un fișier per mesaj.** Nimic nu se pierde în chat.

---

## 1. Formatul unui mesaj

```markdown
## <subiect> — <YYYY-MM-DD HH:MM UTC> — <MavisCloud | MavisLocal | POPY>

<cerere | răspuns | decizie | constatare>

**Context:** ce e nevoie să știi fără să deschizi altceva.
**Cerere/Decizie:** un singur item, cât de concret posibil.
**Doar pentru MavisCloud:** / **Doar pentru MavisLocal:** (dacă e cazul)
```

**Reguli:**
- **Un fișier per mesaj** — nu combina temele.
- **Deciziile se scriu aici**, nu se pierd în conversație.
- **Autorul e explicit** — ca să nu se amestece.
- **Fără secrete** în acest folder. Sunt documente publice pe Drive.
- **Fără cereri care nu pot fi executate.** Cererea trebuie să fie acționabilă
  de celălalt agent sau de POPY, cu datele necesare incluse.

---

## 2. Cum citește fiecare parte

**Mavis Local (calculatorul lui POPY):**
```
E:\Google\GDrive\GDrive-Second_Brain_PKMS\...   ← mirrorul local
```
Sau direct prin Drive API:
```
GET drive/v3/files?q='<folderId>' in parents
```

**Mavis Cloud:**
```bash
node mavis-tools/drive-vault.js ls "05-Comunicare"
node mavis-tools/drive-vault.js read "<nume-fisier>"
```

---

## 3. Notă despre Drive Sync

Tot ce ajunge pe Drive ajunge **și pe calculatorul lui POPY** prin sync.
Folderul local e în altă locație, dar **conținutul e același**.

**Deci tot ce scriu aici trebuie să fie suficient de clar pentru un cititor nou** —
fără context din conversație, fără presupuneri.

---

## 4. Mesajele

| Fișier | Când | Autor | Subiect |
|---|---|---|---|
| `2026-10-28-001-FINALIZARE-INTEGRARE.md` | 28 oct 2026 | MavisCloud | Google Access Bot creat — starea reală și ce s-a schimbat |

---

*Canalul e viu: orice workflow nou care implică ambele părți începe cu un fișier aici.*
