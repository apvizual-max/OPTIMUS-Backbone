# TASK-2026-10-27-0735 — livrat

**executat de:** Mavis Cloud · `main`
**canal primar (livrabilul propriu-zis):**
`BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-2026-10-27-0849-raport-operare.md`

## Livrat

Raport de funcționare și operare scris **în Drive**, ca fișier nou, cu cele cinci
elemente cerute: canalul de citire, cele două HEAD-uri, numărul de taskuri, ce am
observat în `BRIDGE-DRIVE/`, procedura adoptată în două rânduri, și confirmarea
explicită *„Drive = puntea principală; GitHub = canal secundar și memorie permanentă
a sistemului."*

## Plus, găsit și reparat

**Defect OAuth:** `kit.js` lua `client_id` din `credentials.json` (clientul
`…5b7h17gt1c5hc4i1m6eginads37o3m2h`), dar refresh-token-ul aparține clientului
`…bp47aoerh6gu1aohm74blfhnccnku773` → `unauthorized_client`.

**Reparat deja la sursă** în `MAVIS-CLOUD`, commit `d3f119f`
(„never mix client and refresh-token from different OAuth clients"), cu punct unic
de rezolvare în `mavis-tools/google-auth.js` și 8/8 teste trecând. **Nu am împushat
nimic — era deja acolo.**
