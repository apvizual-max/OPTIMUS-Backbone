# QUEUE/DONE — ținta de livrare a canalului secundar

> Cloud-ul scrie aici rezultatul fiecărei tichete, ca `QUEUE/DONE/<id>.md`,
> apoi marchează `[x]` în coadă. Fără acest folder, contractul nu e complet:
> ticheta cere o livrare, iar ținta nu există.
>
> Măsurat 2026-10-27: în repo-ul `MAVIS-OPTIMUS-CI` acest folder **nu exista**,
> deși era declarat ca țintă în `docs/META-PROMPT.md` §6 și în skill-ul
> Cloud-ului. Poarta `scripts\queue-contract-check.ps1` îl verifică.

## Reguli

- **Nu se șterge nimic.** Un rezultat consumat se arhivează prin `git mv`,
  nu se șterge. Regula Cloud-ului: „Nu șterge nimic — mută în
  `docs/arhiva/handoffs-vechi/` cu `git mv`".
- **Un fișier per tichetă**, numele = id-ul tichetei: `<id>.md`.
- Răspunsul se scrie în cifre măsurate, cu metoda obținerii. Un număr
  nemeșurat nu se scrie.
- Livrarea în acest folder înseamnă „Cloud-ul a citit ticheta". Nu înseamnă
  „Local a primit rezultatul" — pentru asta e `git pull` și `mavis-sync.ps1`.
