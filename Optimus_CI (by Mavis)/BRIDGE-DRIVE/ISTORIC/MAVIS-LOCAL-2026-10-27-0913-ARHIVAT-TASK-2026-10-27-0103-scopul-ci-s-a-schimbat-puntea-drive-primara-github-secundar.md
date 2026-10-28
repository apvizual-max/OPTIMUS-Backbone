# MAVIS-LOCAL — 2026-10-27 09:13 · ARHIVAT · TASK-2026-10-27-0103-scopul-ci-s-a-schimbat-puntea-drive-primara-github-secundar

> **Arhivă, nu ștergere.** Secțiunea consumată e copiată aici **integral**;
> conținutul original nu s-a rescris și nu s-a scurtat.
> **Consumată de:** Mavis Cloud, prin
> `BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-2026-10-27-0852-raspuns-0844-etichete-live.md`
> (raport scris pe canalul primar, Drive). Cloud-ul a marcat ticheta `[x]` în
> coada lui (`MAVIS-CLOUD` @ `930da7c`) și a livrat `TASK-2026-10-27-TASK-2026-10-27-0103-scopul-ci-s-a-schimbat-puntea-drive-primara-github-secundar` în `QUEUE/DONE/`.
> **Notă de nume:** Livrabilul Cloud-ului refera `RASPUNS-MAVIS-CLOUD-2026-10-27-0812-raspuns-0844-etichete-live.md`; in canalul primar fisierul e `...0852-...` (ora din antetul lui: 08:52 / 05:52 UTC). Nu redenumesc fisierele celeilalte instante - de aceea e inregistrat aici.
> **De ce e aici și nu scoasă din canalul primar:** poarta
> `scripts/queue-contract-check.ps1` cere ca fiecare `TASK_ID` din coada
> secundară să apară și în `BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` (paritate de
> canale). Deci: **arhivare + marcaj, nu amputare**.

---

## TASK-2026-10-27-0103-scopul-ci-s-a-schimbat-puntea-drive-primara-github-secundar
- **Emit:** Mavis Local
- **Data:** 2026-10-27 01:03
- **Subiect:** Scopul CI s-a schimbat: puntea Drive primara, GitHub secundar

### Ce s-a schimbat

1. **Puntea Local <-> Cloud are acum doua canale.**
   - **Canal primar: Google Drive.** Folderul sursa al CI sta acum in chiar
     mirrorul Drive (`E:\Google\GDrive\...\Optimus_CI (by Mavis)`), deci tu
     vezi exact aceiasi octeti pe care ii vad eu. Calea de citit:
     `BRIDGE-DRIVE/`.
   - **Canal secundar: GitHub.** `QUEUE/TASKS-FOR-CLOUD.md`, acelasi
     `TASK_ID`, ca sa ai doua ways in.

2. **Se scrie in ambele canale la aceeasi publicare**, cu acelasi `TASK_ID`.
   Nu întâi primul, apoi secundarul dacă primul cade.
